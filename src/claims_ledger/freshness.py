"""Every ground still names the artifact the claim was established on.

`resolve` asks whether a pointer resolves, and asks it of the past: the pin names a
commit, so `git show <pin>:<path>` keeps its answer forever. An entry may therefore rest
on a test that has since been deleted, or on a module whose behaviour has been inverted,
and stay green — the evidence is still there, at the revision nobody works on any more.
The pin does not merely fail to detect drift; it immunizes the claim against it.

This checker asks the other question. For each evidence ground of an entry that has not
fallen: the anchor names a datum — a digest stated by value, or a commit that is not a
name that moves (`unstable pin`, flag); the path is still in the tree (`withdrawn`,
fail); and the section there digests to the anchor (`moved`, flag). Every anchor is
reduced to the same digest, whichever way it was written, so one comparison serves both
forms. It never judges whether a difference matters — that is the warrant's job, and
the warrant is prose a person reads. `drift` decides which of those a ground is; `run`
settles what the whole pass does, and states the rules it holds.

A finding is discharged by a `contested` verdict by the propagation author naming the
pointer and recording the digest this run sees, which `--write` appends; a verdict
recording the anchor itself, or one on a fresh ground that records something this run
does not see, is an orphan. Nothing more is needed, because a contested entry cannot be
cited `cites-as-live` and `references` fails every document that still does.

Run:  claims-ledger freshness [--write] [--cached]
      With --cached the artifact is compared as the index has it rather than as the
      working tree does, matching what the rest of a `check --cached` is reading.
Exit 1 on a withdrawn ground, a ground that could not be checked, a refutable orphan
verdict, or a --write that appended something; flags print and exit 0.
Proven against the red-team corpus by `claims-ledger corpus`.

The specification this implements is docs/FRESHNESS.md, which the repository has at
https://github.com/Ybx-jp/claims-ledger/blob/main/docs/FRESHNESS.md.
"""

from __future__ import annotations

import dataclasses
import hashlib
import os
import stat
from datetime import datetime

from .propagate import append_verdict, grouped
from .schema import (
    ABSENT,
    PENDING_ANCHOR,
    TERMINAL,
    UNPINNED,
    Report,
    digest_of,
    git,
    git_call,
    git_env,
    git_problem,
    load_entries,
    read_artifact,
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
        if p.digest == PENDING_ANCHOR:
            continue  # names no datum yet; `validate` refuses it, and there is nothing to compare
        out.append((i, raw, p))
    return out


def readings(entry, pointer, config, repo=None, placed=None):
    """The corroborating verdicts that re-read this ground, in file order: each names the
    ground's type, path and section, anchored by value or at a commit. A corroboration at
    an unpinned reference is a reading nothing here can hold to anything, and is passed
    over.

    A reading anchored by value is the datum it read, stated in full, and needs no place
    in history to be held to: it is the baseline whether or not any commit carries it,
    which is what lets a reading be written in the same commit as the edit it read
    (L0204-a-reading-anchored-by-value-needs-no-place-in-history, cites-as-live). A
    reading anchored at a commit, with a repository to ask,
    has to sit in this history — on a branch, and strictly after the ground's own commit
    where the ground names one — and be pinned to a commit rather than a name. A commit
    on no branch — `commit-tree` makes one in a moment — would otherwise be the baseline
    every checker compares from until a prune turned it into a rewritten history; a
    reading older than the pin would report an untouched ground as moved; one at the
    pin's own commit in a longer spelling would carry the comparison away from the
    discharge recorded at the pin; and a name follows the work, which `drift` reports as
    an unstable pin. All are passed over, so the ground is compared from its own anchor,
    or from the last reading that is in the history. `placed` memoises that question for
    a run: the same reading is asked about by `run` and again by `orphans`, and a
    ledger's readings cluster on a few commits.
    """
    out = []
    placed = {} if placed is None else placed
    for v in entry.verdicts:
        if v.malformed or v.status != "corroborated":
            continue
        q = v.pointer
        if (
            q is None
            or q.type != pointer.type
            or q.target != pointer.target
            or q.section != pointer.section
            or q.pin in UNPINNED
        ):
            continue
        if not q.by_value and repo is not None:
            key = (pointer.pin, q.pin)
            if key not in placed:
                after_the_pin = pointer.by_value or (
                    git_call(repo, "merge-base", "--is-ancestor", pointer.pin, q.pin).code == 0
                    and git_call(repo, "merge-base", "--is-ancestor", q.pin, pointer.pin).code != 0
                )
                placed[key] = (
                    is_object_name(repo, q.pin)[0] is True
                    and after_the_pin
                    and git_call(repo, "merge-base", "--is-ancestor", q.pin, "HEAD").code == 0
                )
            if not placed[key]:
                continue
        out.append(v)
    return out


def effective_pointer(entry, pointer, config, repo=None, placed=None):
    """(the pointer this checker compares against, the corroborating verdict that set it).

    A ground's pin is frozen, and a drift against it, once recorded, is recorded for good:
    `discharges()` asks whether the acknowledged artifact really was what the path held
    between the pin and here, and that range only grows. So the reference point has to be
    something that can advance, and the ledger already writes one. The acknowledgement
    `docs/FRESHNESS.md` prescribes for an artifact that moved while the claim did not is a
    `corroborated` verdict naming the artifact as it now stands, and `validate` refuses one
    that restates a ground, so its evidence is a fresh reading of the same section at a
    later commit. The latest such verdict is where the ground was last read, and a change
    after it is news. Measured before this existed: 93 of 270 live grounds were silent for
    the life of their entries, and 49 of them had moved again since the reading that
    silenced them (L0195-the-latest-corroboration-is-where-a-ground-was-last-read,
    cites-as-live).

    The Ground itself when no verdict re-reads it, so an entry that was never acknowledged
    is compared exactly as before.
    """
    found = readings(entry, pointer, config, repo, placed)
    if not found:
        return pointer, None
    return found[-1].pointer, found[-1]


def acknowledgements(entry, pointer, author):
    """The propagated verdicts this entry carries against this pointer, in file order.

    The section counts. `§ "<section>"` is part of a pointer's identity everywhere else
    in this checker — `drift()` compares that span alone, `orphans()` looks a ground up
    by its raw text, the message names the section — and a comparison that dropped it let
    one verdict discharge every ground on the same file and pin. Verdicts do not expire,
    so the second drifted ground would have been reported fresh for the life of the
    entry (L0102-a-verdict-discharges-only-the-ground-whose-section-it-names,
    cites-as-live). The anchor counts the same way, whichever form it takes: a verdict
    names the pointer the run that wrote it compared against.
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
        and q.digest == pointer.digest
        and q.section == pointer.section
    ]


def discharges(verdict, seen):
    """Whether this verdict discharges the drift in front of it: it records the artifact
    as this run reads it.

    Matching a verdict to a ground by the pointer alone was the whole of the suppression
    rule, and it made the `artifact:` line unreachable in the state a discharge normally
    lives in: with the drift live, `orphans()` did not ask, so nothing read the value at
    all and a verdict carrying forty zeros, or any plausible id, silenced a real,
    committed, ongoing drift with every checker at exit 0. A pointer is *which* drift a
    verdict is about; it is not evidence that the verdict is about this one.

    So the verdict is held to what it states, and what it states is the digest of the
    section as the run that wrote it read it — or `absent`, for a ground that was gone.
    It discharges the drift in front of this run when that is what this run reads too,
    and nothing else does: not a record of some earlier drift the artifact has since
    moved on from, which is news since the last reading and is reported as such, and not
    an object id recorded before anchors could be stated by value, which names a whole
    file and can be compared with no section
    (L0198-a-discharge-records-the-digest-this-run-sees, cites-as-live). A drift that is
    not discharged is reported, and under `--write` the run appends a verdict that does
    describe it, which is what keeps the pre-commit path from wedging when the staged
    bytes are edited again before the commit is made. No history is asked: a record is
    either the artifact in front of the run or it is not.
    """
    recorded = (verdict.artifact or "").strip()
    return bool(recorded) and seen is not None and recorded == seen


def verdict_block(grade, pointer, note, author, seen):
    """The block `--write` appends, including what the artifact was when the drift was
    seen — the digest of the section as this run read it, or `absent` for a ground that
    had been withdrawn. `discharges()` and `orphans()` hold the verdict to that later,
    and it is the whole of what separates a discharge this checker caused from one
    written pre-emptively."""
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    return (
        f"- {stamp} · contested · grade: {grade} · author: {author}\n"
        f"  evidence: {pointer.raw}\n"
        f"  artifact: {seen}\n"
        f"  note: {note}\n"
    )


def now_text(repo, pointer, path, cached):
    """(text, unreachable) — the artifact as this run reads it: the working tree, or the
    index blob under `--cached`, matching whatever the rest of the run is reading.

    `unreachable` is why the bytes could not be had at all, and is `None` for an artifact
    that is there and is not UTF-8 text: that one really did change and simply cannot be
    narrowed to a section, which is what `moved` already says. This returned the text
    alone and threw the reason away, so `chmod 000` on an evidence file came back as a
    confident `has moved` at exit 0
    (L0106-an-artifact-that-cannot-be-read-is-unknown-and-not-moved, cites-as-live).
    (docs/audits/ARCH-AUDIT.md, finding 2.)
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
    (docs/audits/ARCH-AUDIT.md finding 2, QE11-4.)
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


def anchor_digest(repo, pointer, config, memo=None):
    """(the digest the pointer's anchor names, why git could not say) — `(None, None)`
    when the anchor names nothing to compare, which is `resolve`'s finding.

    Stated by value, the anchor is the digest and nothing is asked of anybody. Stated at a
    commit, it is the digest of the section as that commit has it, read once per pointer
    for the run and kept in `memo`: `git show <pin>:<path>` through the configured
    section pattern and the same `digest_of` a by-value anchor was computed with, so the
    two forms name the same kind of thing and one comparison serves both
    (L0199-an-anchor-at-a-commit-is-the-digest-of-the-section-there, cites-as-live).
    `drift` has already had `rev-parse --verify` say the blob is there, so a `show` that
    fails here is git failing to hand it over rather than a pin that names nothing.
    """
    if pointer.by_value:
        return pointer.digest, None
    key = (pointer.pin, pointer.target, pointer.section)
    if memo is not None and key in memo:
        return memo[key]
    at_pin = git_call(repo, "show", f"{pointer.pin}:{pointer.target}")
    if not at_pin.ok:
        answer = None, f"git could not read `{pointer.target}` at the pin: {at_pin.why}"
    elif pointer.sectioned:
        found = section_text(at_pin.out, config, pointer.type, pointer.section)
        # The section was never there at the pin. `resolve` fails on that; saying it
        # again here would make one defect look like two.
        answer = (None, None) if found is None else (digest_of(found), None)
    else:
        answer = digest_of(at_pin.out), None
    if memo is not None:
        memo[key] = answer
    return answer


@dataclasses.dataclass
class Drift:
    """What `drift` found for one pointer: the finding — `None` for a fresh ground,
    `unstable-pin`, `withdrawn`, `moved` or `unknown` — its detail, and `seen`, the
    digest of the artifact as this run read it, `absent` for a ground that is gone, or
    None where nothing was read."""

    finding: str | None
    detail: str | None = None
    seen: str | None = None


def drift(repo, pointer, tree, config, cached=False, memo=None):  # `tree` is the working tree
    """The finding for one pointer, and what this run read the artifact as.

    A pin or a path that does not resolve at all is not this checker's finding — `resolve`
    reports it, and reporting it twice under two names would make one defect look like
    two.

    Both sides are read through one decode and compared by digest: the anchor's side is
    the digest the anchor names, stated in the pointer or read out of the commit it
    names, and this run's side is the digest of the same section as the working tree, or
    the index under `--cached`, holds it. An edit elsewhere in the file leaves the
    section's digest alone and is not this ground's drift; a side that could not be read
    at all is reported as a comparison that did not happen rather than as drift
    (L0200-a-ground-is-compared-by-the-digest-of-its-section-on-both-sides,
    cites-as-live). The digest of what was read is what a discharge is held to, so it is
    computed here, once, from the same read the comparison used — of the section, of the
    whole text for a plain anchor, or of the bytes where the artifact is not text — and
    `absent` where the ground is gone, so a recorded drift always states the artifact it
    was seen at (L0201-a-recorded-drift-states-the-digest-it-was-seen-at, cites-as-live).

    `unknown` is git declining to answer a question this checker asked, and its detail is
    the reason. `git_problem()` is asked once before the run and clears a git that cannot
    work at all; these are the failures it cannot see, because `rev-parse --git-dir` goes
    on succeeding through them — a required clean filter that exits non-zero, a pack the
    reader can no longer open, an object removed from under a revision that names it. The
    comparison did not happen, and a comparison that did not happen is never a fresh
    ground (L0109-a-question-git-declined-is-unknown-and-never-a-fresh-ground,
    cites-as-live).
    """
    if not pointer.by_value:
        named, why = is_object_name(repo, pointer.pin)
        if named is None:
            return Drift(
                "unknown", f"git could not say whether `{pointer.pin}` is a commit or a name: {why}"
            )
        if not named:
            return Drift("unstable-pin")
        # `--quiet` is what makes the difference between the two answers legible, and the
        # exit status is where it is read: exit 1 is `there is nothing at that pin`, which
        # `resolve` reports, and 128 or no answer at all is git failing to look.
        at_pin = git_call(
            repo, "rev-parse", "--verify", "--quiet", f"{pointer.pin}:{pointer.target}"
        )
        if at_pin.code == 1:
            return Drift(None)
        if not at_pin.ok:
            return Drift(
                "unknown", f"git could not read `{pointer.target}` at the pin: {at_pin.why}"
            )
    anchor, why = anchor_digest(repo, pointer, config, memo)
    if why is not None:
        return Drift("unknown", why)
    if anchor is None:
        return Drift(None)
    path = tree / pointer.target

    def since():
        """Only asked once something has drifted, and only of an anchor at a commit,
        which gives the count a lower bound: it walks history, and the answer is for the
        message rather than for the finding."""
        if pointer.by_value:
            return None
        out = git(
            repo, "rev-list", "--count", f"{pointer.pin}..HEAD", "--", literal(pointer.target)
        )
        return (out or "").strip()

    present, unreachable = in_this_run(repo, pointer, path, cached)
    if unreachable:
        return Drift("unknown", f"`{pointer.target}` {unreachable}, so it was not compared")
    if not present:
        # Deleted, or replaced by something that is not a file to read. Either way there
        # is nothing left for a person to look at and judge.
        return Drift("withdrawn", since(), ABSENT)
    now, unreachable = now_text(repo, pointer, path, cached)
    if unreachable:
        return Drift("unknown", f"`{pointer.target}` {unreachable}, so it was not compared")
    if now is None:
        # There, and not UTF-8 text: that artifact did change, whatever it holds now, and
        # it cannot be narrowed to a section. What was seen is the digest of its bytes.
        try:
            raw = path.read_bytes()
        except OSError as exc:
            return Drift("unknown", f"`{pointer.target}` cannot be read ({exc.strerror or exc})")
        return Drift("moved", since(), "sha256:" + hashlib.sha256(raw).hexdigest())
    if pointer.sectioned:
        after = section_text(now, config, pointer.type, pointer.section)
        if after is None:
            return Drift("withdrawn", since(), ABSENT)
        seen = digest_of(after)
    else:
        seen = digest_of(now)
    if seen == anchor:
        return Drift(None, None, seen)
    return Drift("moved", since(), seen)


def since_phrase(count, where, origin="the pin"):
    """How the artifact got from the anchor — or from the reading it is compared from — to
    here, for the message.

    A count of zero is the ordinary pre-commit case — the edit is in the working tree and
    no commit has been made yet — and saying `0 commits have touched it` of a file the
    author is editing right now reads as a checker that has lost track of its own subject
    (L0113-a-count-of-zero-commits-is-said-as-uncommitted, cites-as-live). An anchor
    stated by value names no commit to count from, so the message says only that the
    section differs."""
    if count is None:
        return f"{where} differs from {origin}"
    if count and count.isdigit() and int(count) == 0:
        return f"{where} differs from {origin} in the working tree, uncommitted"
    if not count or not count.isdigit():
        return f"an unknown number of commits have touched {where} since {origin}"
    n = int(count)
    verb = "1 commit has" if n == 1 else f"{n} commits have"
    return f"{verb} touched {where} since {origin}"


def run(ledger, write=False, cached=False, entries=None):
    """The pass over every ground, and the four things it settles before asking about any
    of them.

    Grounds anchored at commits with no repository to ask about them is a failure and not
    a silence: a check that did not run, reported as one that passed, is the failure mode
    this package exists to refuse
    (L0114-pinned-grounds-without-a-repository-are-a-failure-and-not-silence,
    cites-as-live); a ground anchored by value names its datum in full and is compared
    against the working tree whether or not there is a repository. A fallen entry's
    grounds are history — what it was established on, not what anyone should now
    believe — and are left alone
    (L0117-a-fallen-entrys-grounds-are-exempt-from-freshness, cites-as-live). Each pointer
    is evaluated once, keyed on the whole pointer rather than on the path it names,
    because two grounds on one file naming two sections are two questions
    (L0118-each-pointer-is-evaluated-once-per-run, cites-as-live). And a comparison that
    read nothing is `unknown`: reported as a failure, never discharged by any verdict, and
    nothing is appended for it, because a drift is only ever established from the artifact
    this run read (L0202-an-unknown-comparison-is-reported-and-never-discharged,
    cites-as-live).

    Without `--write` nothing is modified. With it the missing verdicts are appended, each
    attributed to the propagation author, and the run still exits non-zero so the change is
    looked at before it is committed
    (L0115-a-write-that-appended-still-exits-non-zero, cites-as-live).
    """
    entries = load_entries(ledger, cached=cached) if entries is None else entries
    config = ledger.config
    author = config.propagation_author
    reports = []
    pending = []  # (entry, block)

    pinned = [(e, t) for e in entries for t in checked_pointers(e, config)]
    if not pinned:
        return reports

    repo = ledger.repo
    at_commits = [p for _, (_, _, p) in pinned if not p.by_value]
    if repo is None and at_commits:
        # Anchors that name commits, and no repository to ask about them. Silence here
        # would be the failure mode this package exists to refuse: a check that did not
        # run, reported as a check that passed.
        return [
            Report(
                "fail",
                None,
                "freshness",
                f"{len(at_commits)} ground(s) are pinned to a commit and there is no git "
                "repository holding the entries; freshness did not run",
            )
        ]
    if repo is not None and (problem := git_problem(repo)) is not None:
        return [Report("fail", None, "freshness", f"{problem}; freshness did not run")]
    tree = repo if repo is not None else ledger.tree

    asked = {}
    anchors = {}  # (pin, path, section) -> the digest an anchor at a commit names
    placed = {}  # (pin, reading) -> whether the reading sits between the pin and HEAD

    def drifted(pointer):
        """`drift()` for one pointer, computed once for the whole run.

        The findings are a function of the pointer, the repository and the tree, all of
        which are fixed here, so a second caller asking about the same pointer gets the
        same answer for 4 to 6 more git processes. `orphans()` below asked again for every
        ground this loop had already evaluated, and two entries resting on one artifact
        asked twice over. (docs/audits/ARCH-AUDIT.md, finding 4.)

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
            asked[pointer.raw] = drift(repo, pointer, tree, config, cached=cached, memo=anchors)
        return asked[pointer.raw]

    for e, (i, raw, ground) in pinned:
        if e.status() in TERMINAL:
            # A fallen entry's Grounds are history: they record what it was established
            # on, not what anyone should now believe. `references` exempts them for the
            # same reason.
            continue
        part = f"Grounds {i}"
        # Compared from where the ground was last read, which is the Ground itself until
        # a corroborating verdict re-reads it.
        p, reading = effective_pointer(e, ground, config, repo, placed)
        found = drifted(p)
        if found.finding is None:
            continue
        if found.finding == "unknown":
            # Not discharged and not a flag: a verdict discharges a
            # drift that was established, and nothing here was established.
            reports.append(
                Report(
                    "fail",
                    e.prefix,
                    part,
                    f"`{raw}` was not checked: {found.detail}",
                )
            )
            continue
        if found.finding == "unstable-pin":
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
        # What the artifact is as this run reads it is half of what makes a verdict a
        # discharge of *this* drift, and it is what `--write` records.
        if any(discharges(v, found.seen) for v in acknowledgements(e, p, author)):
            continue
        where = f"section {p.section!r}" if p.sectioned else "it"
        origin = "the anchor" if p.by_value else "the pin"
        if reading is not None:
            origin = f"the reading verdict {reading.index}"
            if not p.by_value:
                origin += f" recorded at {p.pin[:12]}"
        if found.finding == "withdrawn":
            where_it_was = "the index" if cached else "the working tree"
            gone = (
                f"section {p.section!r} is no longer in `{p.target}`"
                if p.sectioned and in_this_run(repo, p, tree / p.target, cached)[0]
                else f"`{raw}` is not in {where_it_was}"
            )
            reports.append(
                Report(
                    "fail",
                    e.prefix,
                    part,
                    f"{gone}; the ground it names is gone "
                    f"({since_phrase(found.detail, 'the artifact', origin)})",
                )
            )
            note = "propagated from a withdrawn ground"
        else:
            reports.append(
                Report(
                    "flag",
                    e.prefix,
                    part,
                    f"`{raw}` has moved: {since_phrase(found.detail, where, origin)}",
                )
            )
            note = "propagated from a moved ground"
        if write:
            pending.append((e, verdict_block(e.grade, p, note, author, found.seen)))

    reports += orphans(entries, config, repo, author, drifted, anchors, placed)

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


def orphans(entries, config, repo, author, drifted, anchors, placed=None):
    """A ground whose acknowledgement states a cause that did not happen. Without this the
    discharge is forgeable: write the verdict first and the ground never has to be looked
    at again.

    **Asked of the ground rather than of each verdict**
    (L0110-an-orphan-is-asked-of-the-ground-and-not-of-each-verdict, cites-as-live),
    because what the rule protects is a ground — that a drifted one is never silently
    fresh — and an entry may legitimately carry more than one propagated verdict against
    the same ground. The pre-commit path produces exactly that: the hook records the
    staged section, the author stages one more edit before committing, and the next run
    appends a verdict naming what was finally committed. It costs the rule its accusation
    against a verdict that is refutable while a truthful sibling stands, and that
    accusation is kept below rather than given up.

    **Two outcomes, because "not caused" is two answers.** A record that states no drift
    — the digest its own pointer's anchor names — is the pre-emptive forgery, the value a
    forger can read off the entry without running anything, and it fails whatever stands
    beside it and whether or not the comparison has moved past that pointer. A record on
    a ground that is fresh where it is compared from, stating something this run does not
    see, is what an ordinary drift leaves behind when it is never committed, or when it
    is committed and then undone: `freshness --write` records the section, the ledger is
    committed, the author abandons the edit, and no later run appends anything because
    the ground is fresh. Failing that left a permanent red no legal edit could clear on
    the documented workflow and an author who changed their mind, so it flags
    (L0203-a-record-is-refuted-against-its-anchor-and-confirmed-against-the-tree,
    cites-as-live). The flag is not a softening of the forgery rule: a verdict nothing
    can confirm cannot silence a drift either, because `discharges()` accepts only the
    digest in front of the run. No history is asked, so nothing here can be laundered by
    a commit that edits the artifact and one that puts it back, and a git that answers is
    not needed for the accusation to be made or withheld.
    """
    reports = []
    for e in entries:
        pointers, moved_past = {}, set()
        for _, _, p in checked_pointers(e, config):
            # Where the ground was anchored and every reading since: a propagated verdict
            # names whichever of them the run that wrote it compared against, and a
            # reading that a later reading has replaced is still the cause of the drift
            # recorded against it. `moved_past` is the anchor and the readings the
            # comparison has since moved on from.
            pointers[p.raw] = p
            found = readings(e, p, config, repo, placed)
            for v in found:
                pointers.setdefault(v.pointer.raw, v.pointer)
            if found:
                moved_past.add(p.raw)
                moved_past.update(v.pointer.raw for v in found)
                # By pointer and not by position: two readings at one commit are one
                # pointer, and the last of them is where the comparison is, not past it.
                moved_past.discard(found[-1].pointer.raw)
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
            found = drifted(ground)
            if found.finding == "unknown":
                # An orphan is a verdict whose stated cause did not happen. Whether it
                # happened is exactly what git declined to say, and `run()` reports that;
                # forging the accusation out of the silence would make a correctly
                # discharged verdict fail.
                continue
            # The refutable half is asked of every pointer, moved-past or not. A verdict
            # recording the digest its pointer's anchor names stated no drift when it was
            # written; a real drift afterwards, and then a reading that moves the
            # comparison on, would otherwise take the flag that exposed it with them.
            anchor, _ = anchor_digest(repo, ground, config, anchors)
            refuted = [v for v in all_verdicts if anchor and (v.artifact or "").strip() == anchor]
            if refuted:
                # Kept even when a truthful sibling stands: no run of this checker writes
                # a verdict recording the digest the anchor already names, so there is no
                # honest flow to wedge, and a forged verdict beside a caused one is
                # exactly the thing a reader needs told.
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
            if raw in moved_past:
                continue
            if found.finding not in (None, "unstable-pin"):
                # Moved, or withdrawn, and still where the ground is compared from: the
                # drift is reported beside whatever these verdicts say, and a record that
                # does not describe it is not called an orphan against it. The pre-commit
                # flow lives here — a verdict recording a staged section, or `absent` for
                # a deletion not yet committed, before the commit is made.
                continue
            reports.append(
                Report(
                    "flag",
                    e.prefix,
                    "Verdicts",
                    f"{naming(all_verdicts)} by {author} names `{raw}` as its cause and "
                    "records an artifact this run does not see; the drift it discharges "
                    "is not in front of the run, so nothing can confirm it and nothing "
                    "can refute it",
                )
            )
    return reports
