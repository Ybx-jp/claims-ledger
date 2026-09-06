"""Every ground still names the artifact the claim was established on.

`resolve` asks whether a pointer resolves, and asks it of the past: the pin names a
commit, so `git show <pin>:<path>` keeps its answer forever. An entry may therefore rest
on a test that has since been deleted, or on a module whose behaviour has been inverted,
and stay green — the evidence is still there, at the revision nobody works on any more.
The pin does not merely fail to detect drift; it immunizes the claim against it.

This checker asks the other question. For each evidence ground of an entry that has not
fallen: the pin is a commit and not a name that moves (`unstable pin`, flag); the path is
still in the tree (`withdrawn`, fail); and the artifact there is byte-identical to the
artifact at the pin (`moved`, flag). It never judges whether a difference matters — that
is the warrant's job, and the warrant is prose a person reads.

A finding is discharged by a `contested` verdict by the propagation author naming the
pointer, which `--write` appends; a verdict naming a ground that has not drifted is an
orphan and fails, as in `propagate`. Nothing more is needed, because a contested entry
cannot be cited `cites-as-live` and `references` fails every document that still does.

Run:  claims-ledger freshness [--write]
      Without --write nothing is modified. With it the missing verdicts are appended,
      each attributed to the propagation author, and the run still exits non-zero so the
      change is looked at before it is committed.
Exit 1 on a withdrawn ground or an orphan verdict; flags print and exit 0.
Proven against the red-team corpus by `claims-ledger corpus`.

The specification this implements is docs/FRESHNESS.md, which the repository has at
https://github.com/Ybx-jp/claims-ledger/blob/main/docs/FRESHNESS.md.
"""

from __future__ import annotations

import re
from datetime import datetime

from .propagate import append_verdict, grouped
from .schema import (
    TERMINAL,
    UNPINNED,
    Report,
    git,
    git_problem,
    load_entries,
)

# A pin that names an object rather than a name that follows the work. Git will resolve
# `main`, `HEAD`, `HEAD~2` and `v1.0` just as readily as a sha, and a pointer written
# that way resolves forever and can never go stale, which is the guarantee this checker
# exists to provide. Abbreviated object names are accepted from git's own floor of four.
OBJECT_NAME_RE = re.compile(r"^[0-9a-f]{4,40}$")


def is_object_name(repo, pin):
    """Whether `pin` names a commit by its object id. A hex string long enough to be an
    abbreviation is not proof on its own — `beef` is a legal branch name — so git is
    asked whether the same text also resolves as a ref."""
    if not OBJECT_NAME_RE.match(pin):
        return False
    # `--symbolic-full-name` prints a refname for anything that is one and nothing for an
    # object id, so a hex-looking branch is caught here rather than trusted.
    return not (git(repo, "rev-parse", "--symbolic-full-name", pin) or "").strip()


def checked_pointers(entry, config):
    """(index, raw, pointer) for the grounds this checker has anything to say about:
    evidence pointers carrying a real pin. Reserved pointer types name no artifact —
    `entry:` staleness is `propagate`'s subject, `source:` bytes are held to the registry
    sha by `resolve`, and `search:` and `defect:` name nothing in the tree."""
    out = []
    for i, (raw, p) in enumerate(entry.grounds, start=1):
        if p is None or p.type not in config.evidence_types or p.pin in UNPINNED:
            continue
        out.append((i, raw, p))
    return out


def has_acknowledged(entry, pointer, author):
    """Whether the entry already carries a propagated verdict naming this pointer."""
    return any(
        v.author == author
        and v.status == "contested"
        and (q := v.pointer)
        and q.type == pointer.type
        and q.target == pointer.target
        and q.pin == pointer.pin
        for v in entry.verdicts
    )


def verdict_block(grade, pointer, note, author):
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    return (
        f"- {stamp} · contested · grade: {grade} · author: {author}\n"
        f"  evidence: {pointer.raw}\n"
        f"  note: {note}\n"
    )


def drift(repo, pointer, tree):  # `tree` is the repository's working tree
    """(finding, detail) for one pointer, or (None, None) when the ground is fresh.

    `finding` is `unstable-pin`, `withdrawn` or `moved`. A pin or a path that does not
    resolve at all is not this checker's finding — `resolve` reports it, and reporting it
    twice under two names would make one defect look like two.
    """
    if not is_object_name(repo, pointer.pin):
        return "unstable-pin", None
    if git(repo, "rev-parse", "--verify", f"{pointer.pin}:{pointer.target}") is None:
        return None, None
    path = tree / pointer.target
    if not path.is_file():
        # Deleted, or replaced by something that is not a file to read. Either way there
        # is nothing left for a person to look at and judge.
        since = git(repo, "rev-list", "--count", f"{pointer.pin}..HEAD", "--", pointer.target)
        return "withdrawn", (since or "").strip()
    # git's own comparison of the pin's tree against the working tree, so that whatever
    # the repository does to a file on its way in and out — line endings, clean filters —
    # is done to both sides. Empty output means the path is unchanged there.
    changed = git(repo, "diff", "--name-only", pointer.pin, "--", pointer.target)
    if changed is None or not changed.strip():
        return None, None
    since = git(repo, "rev-list", "--count", f"{pointer.pin}..HEAD", "--", pointer.target)
    return "moved", (since or "").strip()


def commits_phrase(count):
    """`n commits have` / `1 commit has` / a shrug when git would not say."""
    if not count or not count.isdigit():
        return "an unknown number of commits have"
    n = int(count)
    return "1 commit has" if n == 1 else f"{n} commits have"


def run(ledger, write=False):
    entries = load_entries(ledger)
    config = ledger.config
    author = config.propagation_author
    reports = []
    pending = []  # (entry, block)

    pinned = [(e, t) for e in entries for t in checked_pointers(e, config)]
    if not pinned:
        return reports

    repo = ledger.repo
    if repo is None:
        # Pins that name commits, and no repository to ask about them. Silence here would
        # be the failure mode this package exists to refuse: a check that did not run,
        # reported as a check that passed.
        return [
            Report(
                "fail",
                None,
                "freshness",
                f"{len(pinned)} ground(s) are pinned to a commit and there is no git "
                "repository holding the entries; freshness did not run",
            )
        ]
    if (problem := git_problem(repo)) is not None:
        return [Report("fail", None, "freshness", f"{problem}; freshness did not run")]

    for e, (i, raw, p) in pinned:
        if e.status() in TERMINAL:
            # A fallen entry's Grounds are history: they record what it was established
            # on, not what anyone should now believe. `references` exempts them for the
            # same reason.
            continue
        part = f"Grounds {i}"
        finding, detail = drift(repo, p, repo)
        if finding is None:
            continue
        if finding == "unstable-pin":
            reports.append(
                Report(
                    "flag",
                    e.prefix,
                    part,
                    f"`{raw}` is pinned to a name, not a commit; a pin that follows the "
                    "work resolves forever and can never go stale",
                )
            )
            continue
        if has_acknowledged(e, p, author):
            continue
        if finding == "withdrawn":
            reports.append(
                Report(
                    "fail",
                    e.prefix,
                    part,
                    f"`{raw}` is not in the working tree; {commits_phrase(detail)} touched "
                    f"it since the pin, and the ground it names is gone",
                )
            )
            note = "propagated from a withdrawn ground"
        else:
            reports.append(
                Report(
                    "flag",
                    e.prefix,
                    part,
                    f"`{raw}` has moved: {commits_phrase(detail)} touched it since the pin",
                )
            )
            note = "propagated from a moved ground"
        pending.append((e, verdict_block(e.grade, p, note, author)))

    reports += orphans(entries, config, repo, repo, author)

    if write:
        for e, block in grouped(pending):
            append_verdict(e, block, root=config.root)
            n = block.count("\n\n") + 1
            reports.append(
                Report(
                    "flag", e.prefix, "Verdicts", f"appended {n} contested verdict(s) by {author}"
                )
            )
    return reports


def orphans(entries, config, repo, tree, author):
    """A propagated verdict whose stated cause has not happened. Without this the
    discharge is forgeable: write the verdict first and the ground never has to be
    looked at again."""
    reports = []
    for e in entries:
        pointers = {p.raw: p for _, _, p in checked_pointers(e, config)}
        for v in e.verdicts:
            q = v.pointer
            if v.author != author or v.status != "contested" or q is None:
                continue
            if q.type not in config.evidence_types or q.pin in UNPINNED:
                continue
            ground = pointers.get(q.raw)
            if ground is None:
                why = f"{e.id} carries no such ground"
            elif drift(repo, ground, tree)[0] in (None, "unstable-pin"):
                why = "that ground has not drifted"
            else:
                continue
            reports.append(
                Report(
                    "fail",
                    e.prefix,
                    "Verdicts",
                    f"verdict {v.index} by {author} names `{q.raw}` as its cause, but "
                    f"{why}; a propagated verdict that nothing caused is an orphan",
                )
            )
    return reports
