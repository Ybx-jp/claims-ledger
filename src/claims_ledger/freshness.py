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
is the warrant's job, and the warrant is prose a person reads
(L0109-a-question-git-declined-is-unknown-and-never-a-fresh-ground, cites-as-live).

A finding is discharged by a `contested` verdict by the propagation author naming the
pointer, which `--write` appends; a verdict naming a ground that has not drifted is an
orphan and fails, as in `propagate`. Nothing more is needed, because a contested entry
cannot be cited `cites-as-live` and `references` fails every document that still does.

Four things the run itself settles, before any of that. Grounds pinned to commits with no
repository to ask about them is a failure and not a silence: a check that did not run,
reported as one that passed, is the failure mode this package exists to refuse
(L0114-pinned-grounds-without-a-repository-are-a-failure-and-not-silence, cites-as-live).
A fallen entry's grounds are history — what it was established on, not what anyone should
now believe — and are left alone
(L0117-a-fallen-entrys-grounds-are-exempt-from-freshness, cites-as-live). Each pointer is
evaluated once, keyed on the whole pointer rather than on the path it names, because two
grounds on one file naming two sections are two questions
(L0118-each-pointer-is-evaluated-once-per-run, cites-as-live). And a drift this run cannot
say the artifact of is reported rather than discharged, because a verdict recording
nothing is one nothing could ever check
(L0116-a-drift-whose-artifact-cannot-be-stated-is-not-discharged, cites-as-live).

Run:  claims-ledger freshness [--write] [--cached]
      Without --write nothing is modified. With it the missing verdicts are appended,
      each attributed to the propagation author, and the run still exits non-zero so the
      change is looked at before it is committed
      (L0115-a-write-that-appended-still-exits-non-zero, cites-as-live). With --cached the
      artifact is compared as the index has it rather than as the working tree does,
      matching what the rest of a `check --cached` is reading.
Exit 1 on a withdrawn ground, a ground that could not be checked, an orphan verdict, or a
--write that appended something; flags print and exit 0.
Proven against the red-team corpus by `claims-ledger corpus`.

The specification this implements is docs/FRESHNESS.md, which the repository has at
https://github.com/Ybx-jp/claims-ledger/blob/main/docs/FRESHNESS.md.
"""

from __future__ import annotations

import os
import stat
from datetime import datetime

from .propagate import append_verdict, grouped
from .schema import (
    ABSENT,
    NULL_OBJECT_ID,
    OBJECT_ID_RE,
    TERMINAL,
    UNPINNED,
    Report,
    git,
    git_call,
    git_env,
    git_problem,
    load_entries,
    read_artifact,
    section_text,
    unreachable_artifact,
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
    would otherwise retire every unstable-pin flag in the ledger without saying a word
    (L0099-git-is-the-arbiter-of-whether-a-pin-is-an-object-name, cites-as-live).
    """
    # `--symbolic-full-name` prints a refname for anything that is one and nothing for an
    # object id, so a hex-looking branch is caught here rather than trusted.
    named = git_call(repo, "rev-parse", "--symbolic-full-name", pin)
    if named.ok:
        return not names_a_ref(named.out), None
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


def names_a_ref(out):
    """Whether `git rev-parse --symbolic-full-name` answered with a refname.

    It is documented to print a *fully qualified* one — `refs/heads/main`, `refs/tags/v1`,
    or the bare `HEAD` of a detached head — and nothing at all for an object id. It also
    prints, verbatim and with exit 0, any argument it did not recognise: git's
    parse-options echoes an unknown double-dash argument rather than refusing it, so
    `rev-parse --symbolic-full-name --upload-pack=x` answers `--upload-pack=x`. Read as a
    refname that gave an option-shaped pin an unstable-pin flag *and* `resolve`'s "does
    not resolve" — the two contradictory names for one defect that LOW-36 was fixed to
    stop. Pins are free text in the schema, so a leading dash is a typo away.

    So the answer is read as what it is documented to be. Anything else git prints is git
    talking about its own command line, and a pin that is not a ref is passed on as an
    object name for `resolve` to find nothing at
    (L0100-an-option-shaped-pin-is-not-read-as-a-refname, cites-as-live).
    """
    answer = out.strip()
    return answer == "HEAD" or answer.startswith("refs/")


def literal(path):
    """A path as a pathspec that means only itself.

    `git diff … -- docs/note[1].md` reads the brackets as a wildcard, so an edit to an
    unrelated `docs/note1.md` — which no entry pins — was reported as this ground's
    drift. `:(literal)` is git's own way of saying that the text is a filename
    (L0101-a-path-is-put-to-git-as-a-literal-pathspec, cites-as-live).
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


def acknowledgements(entry, pointer, author):
    """The propagated verdicts this entry carries against this pointer, in file order.

    The section counts. `§ "<section>"` is part of a pointer's identity everywhere else
    in this checker — `scoped()` compares that span alone, `orphans()` looks a ground up
    by its raw text, the message names the section — and a comparison that dropped it let
    one verdict discharge every ground on the same file and pin. Verdicts do not expire,
    so the second drifted ground would have been reported fresh for the life of the
    entry (L0102-a-verdict-discharges-only-the-ground-whose-section-it-names,
    cites-as-live).
    """
    return [
        v
        for v in entry.verdicts
        if v.author == author
        and v.status == "contested"
        and (q := v.pointer)
        and q.type == pointer.type
        and q.target == pointer.target
        and q.pin == pointer.pin
        and q.section == pointer.section
    ]


def discharges(repo, pointer, verdict, seen):
    """(whether this verdict discharges the drift in front of it, why git could not say).

    Matching a verdict to a ground by the pointer alone was the whole of the suppression
    rule, and it made the `artifact:` line unreachable in the state a discharge normally
    lives in: with the drift live, `orphans()` does not ask, so nothing read the value at
    all and a verdict carrying forty zeros, or any plausible id, silenced a real,
    committed, ongoing drift with every checker at exit 0. A pointer is *which* drift a
    verdict is about; it is not evidence that the verdict is about this one.

    Two ways a verdict is about the drift in front of it, and they cover different
    moments. **It records what this run is looking at** — the ordinary pre-commit case,
    where the drift is in the working tree or the index and is in no commit yet, so there
    is no history for `caused()` to find it in. **Or the artifact really was what it says
    it was, between the pin and here** — the case after the drift is committed, which is
    also the one that survives the artifact changing again afterwards.

    A verdict that is neither is not suppressed, and the drift is reported
    (L0103-a-discharge-records-what-this-run-sees-or-what-the-path-held, cites-as-live).
    That is not an accusation: `orphans()` is where a verdict is called a forgery, and
    this only declines to let one silence a finding it does not describe. Under `--write`
    the run then appends a verdict that does describe it, which is what keeps the
    pre-commit path from wedging when the staged bytes are edited again before the commit
    is made.
    """
    recorded = (verdict.artifact or "").strip()
    if recorded and recorded != NULL_OBJECT_ID and seen is not None and recorded == seen:
        return True, None
    state, why = caused(repo, pointer, verdict)
    if state is None:
        return None, why
    return state == CAUSED, None


def verdict_block(grade, pointer, note, author, seen):
    """The block `--write` appends, including what the artifact was when the drift was
    seen — the object id git would store it under, or `absent` for a ground that had been
    withdrawn. `orphans()` holds the verdict to that later, and it is the whole of what
    separates a discharge this checker caused from one written pre-emptively."""
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    return (
        f"- {stamp} · contested · grade: {grade} · author: {author}\n"
        f"  evidence: {pointer.raw}\n"
        f"  artifact: {seen}\n"
        f"  note: {note}\n"
    )


def seen_at(repo, pointer, path, cached, withdrawn):
    """(what the artifact is as this run reads it, why git could not say).

    The object id git would store the artifact under, which is what the comparison later
    has to be against: a commit id would not do, because the ordinary case is a drift
    that is in the working tree and not yet committed at all — that is what a pre-commit
    hook is for. `hash-object --path` rather than a hash of the bytes, so that whatever
    the repository does to a file on its way in, line endings and clean filters included,
    is done here too and the id matches the one a commit would record
    (L0104-the-artifact-is-recorded-as-the-id-a-commit-would-store, cites-as-live).

    A withdrawn ground has no artifact to hash, and its absence is the thing that
    happened; `ABSENT` records that, and `caused()` looks for the deletion in history the
    way it looks for a blob
    (L0105-a-withdrawn-ground-records-absent-and-the-deletion-is-sought, cites-as-live).
    """
    if withdrawn:
        return ABSENT, None
    if cached:
        answer = git_call(
            repo, "rev-parse", "--verify", "--quiet", f":{pointer.target}", env=git_env(index=True)
        )
    else:
        answer = git_call(repo, "hash-object", "--path", pointer.target, "--", str(path))
    if answer.ok and OBJECT_ID_RE.match(answer.out.strip()):
        return answer.out.strip(), None
    return None, answer.why or f"git answered {answer.out.strip()!r}"


def now_text(repo, pointer, path, cached):
    """(text, unreachable) — the artifact as this run reads it: the working tree, or the
    index blob under `--cached`, matching whatever the rest of the run is reading.

    `unreachable` is why the bytes could not be had at all, and is `None` for an artifact
    that is there and is not UTF-8 text: that one really did change and simply cannot be
    narrowed to a section, which is what `moved` already says. This returned the text
    alone and threw the reason away, so `chmod 000` on an evidence file came back as a
    confident `has moved` at exit 0
    (L0106-an-artifact-that-cannot-be-read-is-unknown-and-not-moved, cites-as-live).
    (ARCH-AUDIT.md, finding 2.)
    """
    if cached:
        answer = git_call(repo, "show", f":{pointer.target}", env=git_env(index=True))
        if answer.ok:
            return answer.out, None
        return None, f"git could not read `{pointer.target}` from the index: {answer.why}"
    return read_artifact(path)


def in_this_run(repo, pointer, path, cached):
    """(whether the artifact is still there to be read, why that could not be
    established) — in the index under `--cached`, and in the working tree otherwise.

    `path.is_file()` was the whole of it, and it does not have two answers where three are
    needed. With the artifact's *directory* unsearchable it raises PermissionError out of
    pathlib on 3.12 — `freshness` exited 2 having printed nothing, and `check` printed
    four checkers and silently omitted the fifth — while 3.13 swallows the EACCES and
    answers False, which is a confident `withdrawn` for a file nobody could look at.
    `os.stat` is asked directly, the way `file_problem` asks it and for the same reason
    (L0107-presence-is-asked-of-stat-rather-than-of-is-file, cites-as-live).
    (ARCH-AUDIT.md finding 2, QE11-4.)
    """
    if cached:
        answer = git_call(
            repo,
            "ls-files",
            "--error-unmatch",
            "--",
            literal(pointer.target),
            env=git_env(index=True),
        )
        return answer.ok, None
    try:
        info = os.stat(path)
    except FileNotFoundError:
        return False, None  # gone, or a symlink to nothing: withdrawn, and that is true
    except (OSError, ValueError) as exc:
        return False, f"cannot be reached ({getattr(exc, 'strerror', None) or exc})"
    # A directory or a FIFO where the artifact was is not an artifact to read either, and
    # unlike the case above this one is established rather than guessed at.
    return stat.S_ISREG(info.st_mode), None


def scoped(repo, pointer, path, config, cached=False):
    """(finding, why) for a pointer that names a section — `None`, `moved`, `withdrawn`
    or `unknown`.

    The artifact changed; the question this answers is whether the change was inside the
    section the claim actually rests on. `None` means the section is untouched and the
    edit was somewhere else in the file — the whole reason for naming a section.
    `withdrawn` means the file is still there and the section is not.

    A side that is there and is not text is not a finding of its own: the artifact did
    change, and `moved` is what the comparison already said before sections narrowed it.
    A side that could not be read *at all* is the other thing, and it is `unknown`: the
    docstring here anticipated only the first, and a permission error landed in the same
    branch and produced a confident, false, soft finding. (ARCH-AUDIT.md, finding 2.)

    Ledger: (L0009-a-section-pin-compares-its-section-or-says-it-could-not, cites-as-live).
    """
    at_pin = git_call(repo, "show", f"{pointer.pin}:{pointer.target}")
    if not at_pin.ok:
        # `drift` has already had `rev-parse --verify` say the blob is there, so this is
        # git failing to hand it over rather than a pin that names nothing.
        return "unknown", f"git could not read `{pointer.target}` at the pin: {at_pin.why}"
    now, unreachable = now_text(repo, pointer, path, cached)
    if unreachable:
        return "unknown", f"`{pointer.target}` {unreachable}, so its section was not compared"
    was = at_pin.out
    if now is None:
        return "moved", None
    before = section_text(was, config, pointer.type, pointer.section)
    after = section_text(now, config, pointer.type, pointer.section)
    if before is None:
        # The section was never there at the pin. `resolve` fails on that; saying it
        # again here would make one defect look like two.
        return None, None
    if after is None:
        return "withdrawn", None
    # Trailing whitespace is the gap between one section and the next, not part of
    # either. The last section of an artifact runs to the end of it, so appending a new
    # section to the file would otherwise lengthen the one before it by the blank lines
    # separating them, and report a section nobody touched as moved.
    return (None, None) if before.rstrip() == after.rstrip() else ("moved", None)


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
    ground (L0109-a-question-git-declined-is-unknown-and-never-a-fresh-ground,
    cites-as-live).
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

    present, unreachable = in_this_run(repo, pointer, path, cached)
    if unreachable:
        return "unknown", f"`{pointer.target}` {unreachable}, so it was not compared"
    if not present:
        # Deleted, or replaced by something that is not a file to read. Either way there
        # is nothing left for a person to look at and judge.
        return "withdrawn", since()
    # git's own comparison of the pin's tree against the tree this run is reading — the
    # working tree, or the index under `--cached` — so that whatever the repository does
    # to a file on its way in and out, line endings and clean filters included, is done to
    # both sides. Empty output means the path is unchanged there, and no section inside it
    # can have moved either, so the text is never read.
    # (L0108-the-comparison-against-the-pin-is-gits-own, cites-as-live)
    diff = ["diff", "--cached"] if cached else ["diff"]
    changed = git_call(
        repo,
        *diff,
        "--name-only",
        pointer.pin,
        "--",
        literal(pointer.target),
        env=git_env(index=cached),
    )
    if not changed.ok:
        return "unknown", f"git could not compare `{pointer.target}` against the pin: {changed.why}"
    if not changed.out.strip():
        return None, None
    if pointer.sectioned:
        finding, why = scoped(repo, pointer, path, config, cached=cached)
        if finding == "unknown":
            return finding, why
        return (finding, since()) if finding else (None, None)
    # A plain pin has nothing inside it to narrow to, so git's comparison above is the
    # answer — unless the reason git called it changed is that nothing can read it. git
    # reports a file it cannot open as modified, which is the same false confidence one
    # surface out.
    unreachable = None if cached else unreachable_artifact(path)
    if unreachable:
        return "unknown", f"`{pointer.target}` {unreachable}, so it was not compared"
    return "moved", since()


def since_phrase(count, where):
    """How the artifact got from the pin to here, for the message.

    A count of zero is the ordinary pre-commit case — the edit is in the working tree and
    no commit has been made yet — and saying `0 commits have touched it` of a file the
    author is editing right now reads as a checker that has lost track of its own subject
    (L0113-a-count-of-zero-commits-is-said-as-uncommitted, cites-as-live)."""
    if count and count.isdigit() and int(count) == 0:
        return f"{where} differs from the pin in the working tree, uncommitted"
    if not count or not count.isdigit():
        return f"an unknown number of commits have touched {where} since the pin"
    n = int(count)
    verb = "1 commit has" if n == 1 else f"{n} commits have"
    return f"{verb} touched {where} since the pin"


def run(ledger, write=False, cached=False, entries=None):
    entries = load_entries(ledger, cached=cached) if entries is None else entries
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

    asked = {}

    def drifted(pointer):
        """`drift()` for one pointer, computed once for the whole run.

        The findings are a function of the pointer, the repository and the tree, all of
        which are fixed here, so a second caller asking about the same pointer gets the
        same answer for 4 to 6 more git processes. `orphans()` below asked again for every
        ground this loop had already evaluated, and two entries resting on one artifact
        asked twice over. (ARCH-AUDIT.md, finding 4.)

        **Keyed on the whole pointer, not on its target.** A target-keyed memo passes the
        suite and the corpus and silently loses a finding: this repository's own L0010
        carries two grounds on one file naming two sections, and under the wrong key the
        second one's drift is answered with the first one's verdict. `raw` is the identity
        the rest of this checker already uses — `orphans()` looks a ground up by it.

        Every caller runs before the first write, which is what makes the memo safe: a
        verdict appended mid-run cannot change an answer already given, because no answer
        is given after one. It also removes a hazard the old code had — an edit landing
        during the dozens of subprocesses between the two calls produced two answers to
        one question inside one report.
        """
        if pointer.raw not in asked:
            asked[pointer.raw] = drift(repo, pointer, repo, config, cached=cached)
        return asked[pointer.raw]

    for e, (i, raw, p) in pinned:
        if e.status() in TERMINAL:
            # A fallen entry's Grounds are history: they record what it was established
            # on, not what anyone should now believe. `references` exempts them for the
            # same reason.
            continue
        part = f"Grounds {i}"
        finding, detail = drifted(p)
        if finding is None:
            continue
        if finding == "unknown":
            # Not discharged and not a flag: a verdict discharges a
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
        # What the artifact is as this run reads it, asked before the acknowledgement is
        # weighed rather than only on the `--write` path: it is half of what makes a
        # verdict a discharge of *this* drift, and it is what `--write` records.
        seen, why_unseen = seen_at(repo, p, repo / p.target, cached, finding == "withdrawn")
        acknowledged = False
        for v in acknowledgements(e, p, author):
            state, could_not = discharges(repo, p, v, seen)
            if state:
                acknowledged = True
                break
            if state is None:
                # A git that cannot answer is not a git answering no. Silence here would
                # retire the suppression rule; an accusation here would forge one against
                # a correctly discharged verdict. The run says which, and exits non-zero.
                reports.append(
                    Report(
                        "fail",
                        e.prefix,
                        part,
                        f"`{raw}` has drifted and whether verdict {v.index} by {author} "
                        f"discharges it could not be established: {could_not}",
                    )
                )
                acknowledged = True
                break
        if acknowledged:
            continue
        where = f"section {p.section!r}" if p.sectioned else "it"
        if finding == "withdrawn":
            where_it_was = "the index" if cached else "the working tree"
            gone = (
                f"section {p.section!r} is no longer in `{p.target}`"
                if p.sectioned and in_this_run(repo, p, repo / p.target, cached)[0]
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
        if not write:
            continue
        # A verdict records what the artifact was when the drift was seen, and that record
        # is the whole of what `orphans()` later holds it to. One this run cannot state is
        # one nothing could ever check, so it is not written: the ledger is left as it was
        # and the run says why, rather than appending a discharge that is unfalsifiable
        # from the moment it is made.
        why = why_unseen
        if seen is None:
            reports.append(
                Report(
                    "fail",
                    e.prefix,
                    part,
                    f"no verdict was appended for `{raw}`: git could not say what the "
                    f"artifact is, so the drift could not be recorded ({why})",
                )
            )
            continue
        pending.append((e, verdict_block(e.grade, p, note, author, seen)))

    reports += orphans(entries, config, repo, author, drifted)

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


def blobs_since(repo, pointer):
    """(every object id the artifact has held between the pin and HEAD, why git could not
    say).

    `git log --raw` prints the before and after object id of the path at each commit that
    changed it, so one call answers what a walk of the history would. `--full-history`
    because the omission this is guarding against is the loud one: a version git declined
    to list is a discharge called an orphan, which is MEDIUM-34's wedge again
    (L0112-the-blob-history-is-read-with-full-history, cites-as-live).
    """
    answer = git_call(
        repo,
        "log",
        "--format=%H",
        "--raw",
        "--no-abbrev",
        "--full-history",
        f"{pointer.pin}..HEAD",
        "--",
        literal(pointer.target),
    )
    if not answer.ok:
        return None, answer.why
    seen = set()
    for line in answer.out.splitlines():
        if not line.startswith(":"):
            continue  # a commit id on its own line, which is not a version of the path
        seen |= {tok for tok in line.split() if OBJECT_ID_RE.match(tok)}
    return seen - {NULL_OBJECT_ID}, None


# What a verdict's `artifact:` turns out to be worth, once git has been asked.
CAUSED = "caused"  # the artifact really was that, between the pin and here
STATES_NO_DRIFT = "states-no-drift"  # the pin's own blob, or `absent` over no deletion
UNCONFIRMED = "unconfirmed"  # a blob no commit ever held: refutes nothing, confirms nothing
NO_RECORD = "no-record"  # missing or unreadable, which is `validate`'s to report


def caused(repo, pointer, verdict):
    """(what the drift this verdict states turns out to be, why git could not say).

    The orphan rule exists to stop a *pre-emptive* forgery — a verdict written before the
    ground moved, so that the ground never has to be looked at again. `docs/FRESHNESS.md`:
    "Otherwise the discharge is forgeable by writing the verdict pre-emptively." A verdict
    this checker wrote itself, because the ground had moved, is not that; and undoing the
    edit afterwards must not turn the discharge into a failure no legal edit could clear,
    since verdicts append and only append and the pin above the APPEND marker is frozen.

    The question that separates the two is what the verdict *states*, and the verdict
    states it: `artifact:` records what the ground was when the drift was seen. So this
    asks whether the artifact really was that, between the pin and now — a blob the path
    has actually held, or, for a withdrawn ground, a commit that really deleted it. Asking
    instead whether anything has *touched* the artifact, which is what this function
    replaces, answered a question the forger controls: one commit that edits the artifact
    and one that puts it back laundered a pre-emptive discharge permanently, and a mode
    change or a rename away and back did it just as well.

    **Not caused is two different answers, and collapsing them wedged the ledger.** A
    record git can *refute* — the pin's own blob, which states no drift at all, or
    `absent` over a history holding no deletion — is the pre-emptive forgery this rule was
    written for. A record git can only fail to *confirm* — a well-formed blob no commit
    ever held — is what an ordinary drift looks like when it is never committed: the
    author edits a note, `freshness --write` records the working-tree blob, the ledger is
    committed, and then the edit is abandoned. Read as the first, that left a permanent
    failure no legal edit could clear, since verdicts append and only append, the pin is
    frozen, and `--write` appends nothing for a ground that is fresh. So the two are
    separate answers here and `orphans()` gives them separate outcomes.

    A verdict that records nothing, or records something unreadable, is neither: it is
    malformed, `validate` says so of every verdict in every state, and saying it again
    here would make one defect two to whoever reads the output.
    """
    seen = (verdict.artifact or "").strip()
    if not seen or seen == NULL_OBJECT_ID:
        return NO_RECORD, None
    if seen == ABSENT:
        gone = git_call(
            repo,
            "log",
            "--format=%H",
            "--diff-filter=D",
            "--full-history",
            f"{pointer.pin}..HEAD",
            "--",
            literal(pointer.target),
        )
        if not gone.ok:
            return None, gone.why
        return (CAUSED if gone.out.strip() else STATES_NO_DRIFT), None
    if not OBJECT_ID_RE.match(seen):
        return NO_RECORD, None
    # The artifact as the pin has it is not a drift, whatever else is true of it, so a
    # verdict recording the pin's own blob states nothing. Asked first, because it is the
    # cheap half and the half a forger reaches for.
    at_pin = git_call(repo, "rev-parse", "--verify", "--quiet", f"{pointer.pin}:{pointer.target}")
    if at_pin.code not in (0, 1):
        return None, at_pin.why
    if at_pin.ok and at_pin.out.strip() == seen:
        return STATES_NO_DRIFT, None
    held, why = blobs_since(repo, pointer)
    if held is None:
        return None, why
    return (CAUSED if seen in held else UNCONFIRMED), None


def propagated_by_ground(entry, config, author):
    """{ground pointer as written: the propagated verdicts naming it}, in file order."""
    out = {}
    for v in entry.verdicts:
        q = v.pointer
        if v.author != author or v.status != "contested" or q is None:
            continue
        if q.type not in config.evidence_types or q.pin in UNPINNED:
            continue
        out.setdefault(q.raw, []).append(v)
    return out


def naming(verdicts):
    """`verdict 3`, or `verdicts 1, 3`, for a message that has to name which."""
    if len(verdicts) == 1:
        return f"verdict {verdicts[0].index}"
    return "verdicts " + ", ".join(str(v.index) for v in verdicts)


def orphans(entries, config, repo, author, drifted):
    """A ground whose acknowledgement states a cause that did not happen. Without this the
    discharge is forgeable: write the verdict first and the ground never has to be looked
    at again.

    **Asked of the ground rather than of each verdict**
    (L0110-an-orphan-is-asked-of-the-ground-and-not-of-each-verdict, cites-as-live),
    because what the rule protects is a ground — that a drifted one is never silently
    fresh — and an entry may legitimately carry more than one propagated verdict against
    the same ground. The pre-commit path
    produces exactly that: the hook records the staged blob, the author stages one more
    edit before committing, and the next run appends a verdict naming what was finally
    committed. It costs the rule its accusation against a verdict that is refutable while
    a truthful sibling stands, and that accusation is kept below rather than given up.

    **Two outcomes, because "not caused" is two answers.** A record git can refute — the
    pin's own blob, or `absent` over a history holding no deletion — is the pre-emptive
    forgery, and it fails. A record git can only fail to confirm is what an ordinary drift
    looks like when it is never committed: `freshness --write` records the working-tree
    blob, the ledger is committed, the author abandons the edit, and no later run will
    ever append a second verdict because the ground is fresh. Failing that left a
    permanent red no legal edit could clear on the documented workflow and an author who
    changed their mind, so it flags
    (L0111-a-refutable-record-fails-and-an-unconfirmable-one-flags, cites-as-live). The
    flag is not a softening of the forgery rule: a verdict nothing can confirm cannot
    silence a drift either, because `discharges()` requires the same `caused` that this
    does.
    """
    reports = []
    for e in entries:
        pointers = {p.raw: p for _, _, p in checked_pointers(e, config)}
        for raw, all_verdicts in propagated_by_ground(e, config, author).items():
            ground = pointers.get(raw)
            if ground is None:
                reports.append(
                    Report(
                        "fail",
                        e.prefix,
                        "Verdicts",
                        f"{naming(all_verdicts)} by {author} names `{raw}` as its cause, "
                        f"but {e.id} carries no such ground; a propagated verdict that "
                        "nothing caused is an orphan",
                    )
                )
                continue
            finding = drifted(ground)[0]
            if finding == "unknown":
                # An orphan is a verdict whose stated cause did not happen. Whether it
                # happened is exactly what git declined to say, and `run()` reports that;
                # forging the accusation out of the silence would make a correctly
                # discharged verdict fail.
                continue
            if finding not in (None, "unstable-pin"):
                continue
            states = [(v, *caused(repo, ground, v)) for v in all_verdicts]
            could_not = next((why for _, st, why in states if st is None), None)
            refuted = [v for v, st, _ in states if st == STATES_NO_DRIFT]
            established = any(st == CAUSED for _, st, _ in states)
            # A missing or unreadable `artifact:` is `validate`'s to report, of every
            # verdict in every state rather than only of one that has come back fresh.
            # Saying it here too made three of the four bad shapes two failures under two
            # checker names, the second of them describing the wrong defect.
            unconfirmed = [v for v, st, _ in states if st == UNCONFIRMED]

            if refuted:
                # Kept even when a truthful sibling stands: no run of this checker writes
                # a verdict recording the blob the pin already has, so there is no honest
                # flow to wedge, and a forged verdict beside a caused one is exactly the
                # thing a reader needs told.
                reports.append(
                    Report(
                        "fail",
                        e.prefix,
                        "Verdicts",
                        f"{naming(refuted)} by {author} names `{raw}` as its cause, but "
                        "records the artifact as the pin itself has it, which states no "
                        "drift; a propagated verdict that nothing caused is an orphan",
                    )
                )
                continue
            if established:
                continue
            if could_not is not None:
                # A git that cannot answer is not a git answering no — the class the
                # fourth pass closed across six findings. Whether the drift happened is
                # exactly what git declined to say, and a check that did not run is never
                # a check that passed.
                reports.append(
                    Report(
                        "fail",
                        e.prefix,
                        "Verdicts",
                        f"{naming(all_verdicts)} by {author} names `{raw}` as its cause "
                        f"and whether that drift happened could not be established: "
                        f"{could_not}",
                    )
                )
                continue
            if unconfirmed:
                reports.append(
                    Report(
                        "flag",
                        e.prefix,
                        "Verdicts",
                        f"{naming(unconfirmed)} by {author} names `{raw}` as its cause "
                        "and records an artifact no commit between the pin and here ever "
                        "held; the drift it discharges was never committed, so nothing "
                        "can confirm it and nothing can refute it",
                    )
                )
    return reports
