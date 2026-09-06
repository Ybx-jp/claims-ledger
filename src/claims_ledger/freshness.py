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

Run:  claims-ledger freshness [--write] [--cached]
      Without --write nothing is modified. With it the missing verdicts are appended,
      each attributed to the propagation author, and the run still exits non-zero so the
      change is looked at before it is committed. With --cached the artifact is compared
      as the index has it rather than as the working tree does, matching what the rest of
      a `check --cached` is reading.
Exit 1 on a withdrawn ground, a ground that could not be checked, an orphan verdict, or a
--write that appended something; flags print and exit 0.
Proven against the red-team corpus by `claims-ledger corpus`.

The specification this implements is docs/FRESHNESS.md, which the repository has at
https://github.com/Ybx-jp/claims-ledger/blob/main/docs/FRESHNESS.md.
"""

from __future__ import annotations

from datetime import datetime

from .propagate import append_verdict, grouped
from .schema import (
    TERMINAL,
    UNPINNED,
    Report,
    git,
    git_call,
    git_problem,
    load_entries,
    read_document,
    section_text,
)


def is_object_name(repo, pin):
    """(whether `pin` names a commit by its object id, why git could not say).

    Git is the arbiter, for every pin and not only for the hex-shaped ones. A pin that
    names an object rather than a name that follows the work is what this checker needs:
    git resolves `main`, `HEAD`, `HEAD~2` and `v1.0` just as readily as a sha, and a
    pointer written that way resolves forever and can never go stale. The shape of the
    text does not settle it in either direction — `beef` is a legal branch name, an
    uppercase object id is an object id, and `v9.9` in a repository that has no such tag
    is neither. The answer is None when git could not classify the pin at all, which is
    not the same as `it is not a ref` and must not be read as one: a broken repository
    would otherwise retire every unstable-pin flag in the ledger without saying a word.
    """
    # `--symbolic-full-name` prints a refname for anything that is one and nothing for an
    # object id, so a hex-looking branch is caught here rather than trusted.
    named = git_call(repo, "rev-parse", "--symbolic-full-name", pin)
    if named.ok:
        return not named.out.strip(), None
    # It also exits non-zero for a pin this repository does not have at all — `deadbe`, a
    # dangling symref — which is `resolve`'s finding and not this checker's. `--verify
    # --quiet` says that `no` with exit 1, where a git that cannot look exits 128 or does
    # not return, so the exit status is what tells a pin that is not there from a git that
    # could not answer. (Not stderr: a dangling symref warns on it and a plainly absent
    # name does not, which separates two kinds of `no` rather than `no` from a failure.) A
    # pin that is not there is passed on as an object name, for the next question to find
    # nothing at.
    if git_call(repo, "rev-parse", "--verify", "--quiet", pin).code == 1:
        return True, None
    return None, named.why


def literal(path):
    """A path as a pathspec that means only itself.

    `git diff … -- docs/note[1].md` reads the brackets as a wildcard, so an edit to an
    unrelated `docs/note1.md` — which no entry pins — was reported as this ground's
    drift. `:(literal)` is git's own way of saying that the text is a filename.
    """
    return f":(literal){path}"


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
    """Whether the entry already carries a propagated verdict naming this pointer.

    The section counts. `§ "<section>"` is part of a pointer's identity everywhere else
    in this checker — `scoped()` compares that span alone, `orphans()` looks a ground up
    by its raw text, the message names the section — and a comparison that dropped it let
    one verdict discharge every ground on the same file and pin. Verdicts do not expire,
    so the second drifted ground would have been reported fresh for the life of the
    entry.
    """
    return any(
        v.author == author
        and v.status == "contested"
        and (q := v.pointer)
        and q.type == pointer.type
        and q.target == pointer.target
        and q.pin == pointer.pin
        and q.section == pointer.section
        for v in entry.verdicts
    )


def verdict_block(grade, pointer, note, author):
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    return (
        f"- {stamp} · contested · grade: {grade} · author: {author}\n"
        f"  evidence: {pointer.raw}\n"
        f"  note: {note}\n"
    )


def now_text(repo, pointer, path, cached):
    """The artifact as this run reads it: the working tree, or the index blob under
    `--cached`, matching whatever the rest of the run is reading."""
    if cached:
        return git(repo, "show", f":{pointer.target}")
    return read_document(path)[0]


def in_this_run(repo, pointer, path, cached):
    """Whether the artifact is still there to be read — in the index under `--cached`,
    and in the working tree otherwise."""
    if cached:
        return git_call(repo, "ls-files", "--error-unmatch", "--", literal(pointer.target)).ok
    return path.is_file()


def scoped(repo, pointer, path, config, cached=False):
    """Whether the pointer's own section moved, for a pointer that names one.

    The artifact changed; the question this answers is whether the change was inside the
    section the claim actually rests on. `None` means the section is untouched and the
    edit was somewhere else in the file — the whole reason for naming a section.
    `withdrawn` means the file is still there and the section is not.

    A side that cannot be read as text is not a finding of its own: the artifact did
    change, and `moved` is what the comparison already said before sections narrowed it.
    """
    was = git(repo, "show", f"{pointer.pin}:{pointer.target}")
    now = now_text(repo, pointer, path, cached)
    if was is None or now is None:
        return "moved"
    before = section_text(was, config, pointer.type, pointer.section)
    after = section_text(now, config, pointer.type, pointer.section)
    if before is None:
        # The section was never there at the pin. `resolve` fails on that; saying it
        # again here would make one defect look like two.
        return None
    if after is None:
        return "withdrawn"
    # Trailing whitespace is the gap between one section and the next, not part of
    # either. The last section of an artifact runs to the end of it, so appending a new
    # section to the file would otherwise lengthen the one before it by the blank lines
    # separating them, and report a section nobody touched as moved.
    return None if before.rstrip() == after.rstrip() else "moved"


def drift(repo, pointer, tree, config, cached=False):  # `tree` is the working tree
    """(finding, detail) for one pointer, or (None, None) when the ground is fresh.

    `finding` is `unstable-pin`, `withdrawn`, `moved` or `unknown`. A pin or a path that
    does not resolve at all is not this checker's finding — `resolve` reports it, and
    reporting it twice under two names would make one defect look like two.

    `unknown` is git declining to answer a question this checker asked, and its detail is
    the reason. `git_problem()` is asked once before the run and clears a git that cannot
    work at all; these are the failures it cannot see, because `rev-parse --git-dir` goes
    on succeeding through them — a required clean filter that exits non-zero, a pack the
    reader can no longer open, an object removed from under a revision that names it. The
    comparison did not happen, and a comparison that did not happen is never a fresh
    ground.
    """
    named, why = is_object_name(repo, pointer.pin)
    if named is None:
        return "unknown", f"git could not say whether `{pointer.pin}` is a commit or a name: {why}"
    if not named:
        return "unstable-pin", None
    # `--quiet` is what makes the difference between the two answers legible, and the exit
    # status is where it is read: exit 1 is `there is nothing at that pin`, which `resolve`
    # reports, and 128 or no answer at all is git failing to look.
    at_pin = git_call(repo, "rev-parse", "--verify", "--quiet", f"{pointer.pin}:{pointer.target}")
    if at_pin.code == 1:
        return None, None
    if not at_pin.ok:
        return "unknown", f"git could not read `{pointer.target}` at the pin: {at_pin.why}"
    path = tree / pointer.target

    def since():
        """Only asked once something has drifted: it walks history, and the answer is for
        the message rather than for the finding."""
        out = git(
            repo, "rev-list", "--count", f"{pointer.pin}..HEAD", "--", literal(pointer.target)
        )
        return (out or "").strip()

    if not in_this_run(repo, pointer, path, cached):
        # Deleted, or replaced by something that is not a file to read. Either way there
        # is nothing left for a person to look at and judge.
        return "withdrawn", since()
    # git's own comparison of the pin's tree against the tree this run is reading — the
    # working tree, or the index under `--cached` — so that whatever the repository does
    # to a file on its way in and out, line endings and clean filters included, is done to
    # both sides. Empty output means the path is unchanged there, and no section inside it
    # can have moved either, so the text is never read.
    diff = ["diff", "--cached"] if cached else ["diff"]
    changed = git_call(repo, *diff, "--name-only", pointer.pin, "--", literal(pointer.target))
    if not changed.ok:
        return "unknown", f"git could not compare `{pointer.target}` against the pin: {changed.why}"
    if not changed.out.strip():
        return None, None
    if pointer.sectioned:
        finding = scoped(repo, pointer, path, config, cached=cached)
        return (finding, since()) if finding else (None, None)
    return "moved", since()


def since_phrase(count, where):
    """How the artifact got from the pin to here, for the message.

    A count of zero is the ordinary pre-commit case — the edit is in the working tree and
    no commit has been made yet — and saying `0 commits have touched it` of a file the
    author is editing right now reads as a checker that has lost track of its own
    subject."""
    if count and count.isdigit() and int(count) == 0:
        return f"{where} differs from the pin in the working tree, uncommitted"
    if not count or not count.isdigit():
        return f"an unknown number of commits have touched {where} since the pin"
    n = int(count)
    verb = "1 commit has" if n == 1 else f"{n} commits have"
    return f"{verb} touched {where} since the pin"


def run(ledger, write=False, cached=False):
    entries = load_entries(ledger, cached=cached)
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
        finding, detail = drift(repo, p, repo, config, cached=cached)
        if finding is None:
            continue
        if finding == "unknown":
            # Not `has_acknowledged`-suppressed and not a flag: a verdict discharges a
            # drift that was established, and nothing here was established.
            reports.append(
                Report(
                    "fail",
                    e.prefix,
                    part,
                    f"`{raw}` was not checked: {detail}",
                )
            )
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
        where = f"section {p.section!r}" if p.sectioned else "it"
        if finding == "withdrawn":
            where_it_was = "the index" if cached else "the working tree"
            gone = (
                f"section {p.section!r} is no longer in `{p.target}`"
                if p.sectioned and in_this_run(repo, p, repo / p.target, cached)
                else f"`{raw}` is not in {where_it_was}"
            )
            reports.append(
                Report(
                    "fail",
                    e.prefix,
                    part,
                    f"{gone}; the ground it names is gone ({since_phrase(detail, 'the artifact')})",
                )
            )
            note = "propagated from a withdrawn ground"
        else:
            reports.append(
                Report("flag", e.prefix, part, f"`{raw}` has moved: {since_phrase(detail, where)}")
            )
            note = "propagated from a moved ground"
        pending.append((e, verdict_block(e.grade, p, note, author)))

    reports += orphans(entries, config, repo, repo, author, cached=cached)

    if write:
        for e, block in grouped(pending):
            append_verdict(e, block, root=config.root)
            n = block.count("\n\n") + 1
            # A `fail`, and not because a claim is wrong: a file in the ledger has just
            # been changed by machinery, and docs/FRESHNESS.md requires the run to exit
            # non-zero afterwards so the appended text is looked at before it is
            # committed. `propagate` gets that for free, because every block it queues
            # sits beside a failure; the `moved` case here sits beside a flag, so without
            # this the ledger was modified and the run exited 0.
            reports.append(
                Report(
                    "fail", e.prefix, "Verdicts", f"appended {n} contested verdict(s) by {author}"
                )
            )
    return reports


def ever_drifted(repo, pointer):
    """Whether the artifact has been touched by any commit between the pin and HEAD.

    The orphan rule exists to stop a *pre-emptive* forgery — a verdict written before the
    ground moved, so that the ground never has to be looked at again. A verdict this
    checker wrote itself, because the ground had moved, is not that; and undoing the edit
    afterwards used to turn the discharge into a failure no legal edit could clear, since
    verdicts append and only append and the pin above the APPEND marker is frozen.

    So the question asked of a verdict whose ground is fresh right now is whether the
    ground could have drifted since the pin at all. A pin nothing has touched cannot have
    drifted, and a verdict naming it is the forgery the rule is for.
    """
    out = git(repo, "rev-list", "--count", f"{pointer.pin}..HEAD", "--", literal(pointer.target))
    count = (out or "").strip()
    return not count.isdigit() or int(count) > 0


def orphans(entries, config, repo, tree, author, cached=False):
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
            else:
                finding = drift(repo, ground, tree, config, cached=cached)[0]
                if finding == "unknown":
                    # An orphan is a verdict whose stated cause did not happen. Whether it
                    # happened is exactly what git declined to say, and `run()` reports
                    # that; forging the accusation out of the silence would make a
                    # correctly discharged verdict fail.
                    continue
                if finding not in (None, "unstable-pin"):
                    continue
                if ever_drifted(repo, ground):
                    # It has drifted since the pin, and the edit has been undone since.
                    # The verdict was caused; nothing about it is pre-emptive.
                    continue
                why = "that ground has not drifted"
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
