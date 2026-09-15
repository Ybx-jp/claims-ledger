"""The ledger entry as everything that reads one reads it.

One parser, one normalization, one fingerprint and one status derivation, defined here
and imported by every module that reads an entry — the rule that keeps them the only
ones is stated at `parse_entry`, where the parsing starts.

The schema itself is stated in full in docs/SCHEMA.md, which an installed copy does not
carry and the repository has at
https://github.com/Ybx-jp/claims-ledger/blob/main/docs/SCHEMA.md. It is restated in
corpus/README.md (the parts the red-team seeds depend on), and proven by corpus/run.py;
nothing here is trusted beyond what that corpus exercises.

Nothing outside the standard library is imported, so the checkers run from a plain
`python3` in a pre-commit hook (L0011-no-runtime-dependencies, cites-as-live).
"""

from __future__ import annotations

import contextlib
import dataclasses
import fnmatch
import glob
import hashlib
import json
import os
import posixpath
import re
import shutil
import stat
import subprocess
import unicodedata
from datetime import datetime
from pathlib import Path, PurePath

from .config import ANY_NAME, NAME_SLOT, Config, default_config, load_config


class LedgerError(Exception):
    """A file the user maintains cannot be read or parsed: an entry that is not UTF-8, a
    registry line that is not JSON. Distinct from a checker's Report, which is a finding
    about a well-formed ledger; this is the ledger being unreadable in the first place."""


GRADES = ("asserted", "argued", "measured", "controlled", "preregistered")
MEASURED_AND_ABOVE = ("measured", "controlled", "preregistered")
KINDS = ("claim", "prediction", "hypothesis")
STATUSES = (
    "open",
    "corroborated",
    "contested",
    "refuted",
    "superseded",
    "retracted",
    "non-comparable",
)
TERMINAL = ("refuted", "superseded", "retracted", "non-comparable")
FALLEN = ("refuted", "superseded", "retracted")
ACTS = ("cites-as-live", "cites-as-contested", "cites-as-fallen", "challenges")
ENTRY_ACTS = (*ACTS, "distinguishes")
# Written below the assignment, not above it: a section starts at its own line, so a
# comment above `ENTRY_ACTS` is the tail of `ACTS` and a citation there would sit outside
# the span its entry pins.
#
# `distinguishes` is an act one entry performs on another and a document may not: it says
# the two are about the same artifact and are different claims, and the Warrant says how.
# A document has no Scope to hold apart from anything, so there is nothing for it to
# distinguish (L0157-distinguishes-is-an-act-between-entries, cites-as-live).
ACT_ALLOWS = {
    # Which target statuses each act is legal against. `distinguishes` takes any, for the
    # reason `cites-as-fallen` does and a different one: it is a claim about two Scopes
    # rather than about a truth, so no verdict on the target can make it wrong
    # (L0158-a-distinction-is-legal-against-any-status, cites-as-live).
    "cites-as-live": {"open", "corroborated"},
    "cites-as-contested": {"contested"},
    "challenges": {"open", "corroborated", "contested"},
    "cites-as-fallen": set(STATUSES),
    "distinguishes": set(STATUSES),
}
VERDICT_ENTRY_ACTS = ("fallen", "challenges", "supersedes")
SECTIONS = ("Assertion", "Scope", "Grounds", "Warrant", "Backing")
TAIL_SECTIONS = ("Verdicts", "References")
SCOPE_KEYS = ("metric", "cohort", "condition")
APPEND = "<!-- APPEND BELOW THIS LINE ONLY -->"

ID_RE = re.compile(r"^([A-Z])([0-9]{4})-[a-z0-9][a-z0-9-]*$")
PREFIX_RE = re.compile(r"^([A-Z][0-9]+)")
TIMESTAMP_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:[+-][0-9]{2}:[0-9]{2}|Z)$"
)
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
DECIMAL_RE = re.compile(r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$")
# A plain decimal number, in ASCII digits
# (L0149-a-decimal-is-checked-in-ascii-digits, cites-as-live).
# `float()` is wider than the schema: it accepts any Unicode decimal digit, so a credence
# written in Arabic-Indic numerals would pass as an ordinary 0.5, and it accepts `nan`
# and digit-grouping underscores as well.
HEADING_RE = re.compile(r"^## (.+?)\s*$", re.MULTILINE)
VERDICT_HEAD_RE = re.compile(r"^- (\S+) · (\S+) · grade: (\S+) · author: (\S+)$")
BACKING_BLOCK_RE = re.compile(r"^- source: (.*)\n\s+speaker: (.*)\n\s+quote: (.*)$", re.MULTILINE)
REFERENCE_RE = re.compile(r"^- (\S+) · (standing|record) · (\S+)$")
# A citation in a document: `(A0007-<slug>, cites-as-live)`.
CITATION_RE = re.compile(r"\(([A-Z][0-9]{3,}(?:-[a-z0-9-]+)?),\s*(" + "|".join(ACTS) + r")\)")
MISCITATION_RE = re.compile(r"\(([A-Z][0-9]{3,}(?:-[a-z0-9-]+)?),\s*([a-z][a-z-]*)\)")
# The same shape as CITATION_RE with any act-shaped word, so that one of them does not
# read as prose: a mistyped `cites-as-liv`, and `distinguishes`, which is an act between
# entries and not a citation. Both used to be a citation nobody checked, because the only
# regex reading documents did not match them and nothing else looked
# (L0176-a-citation-shaped-parenthetical-names-a-citation-act, cites-as-live).

UNPINNED = ("working", "corpus")
# Pins that name no revision: the artifact is read from the working tree as it stands.
# A ledger kept outside version control needs one, and the red-team corpus uses
# `@corpus`. Anywhere else it is an escape hatch, and a pointer that uses it is only as
# reproducible as the working tree it was read in — and, because there is no revision to
# compare against, freshness has nothing to say about it
# (L0150-an-unpinned-pointer-is-outside-what-freshness-can-say, cites-as-live).

ABSENT = "absent"
# What a verdict's `artifact:` line may say: the object id git would store the drifted
# artifact under, or that the ground was gone. Defined here rather than in `freshness`,
# which writes the line, because `validate` is the checker that holds it to a shape and a
# rule enforced only by the code that writes the value is a rule a hand-edit walks past
# (L0151-the-artifact-shape-is-defined-where-it-is-checked, cites-as-live).
OBJECT_ID_RE = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
# Forty hex characters or sixty-four: a hash width is the repository's business and not the
# ledger's, and one created with `--object-format=sha256` names every object in the wider
# one. `_COMMIT_RE` in the history walk has admitted both since it was written, which is
# the tell that the narrow version here was an oversight rather than a decision. Measured,
# it bit one caller and not the one it was predicted to: `digest_in_history` filters
# `git log --raw`'s output through this pattern, so in a sha256 repository every blob id
# was discarded, the set came back empty, and a ground stated by value whose text had left
# the tree was reported as held by no version of the file the repository has — blaming a
# rewritten history that had not happened. The immutability check, `sha --write`'s refusal
# on a committed entry and a plain `check` over a clean ledger were each measured to work
# there before this widening, so what it repairs is that one false report and not a package
# that does not run.

NULL_OBJECT_ID = "0" * 40
NULL_OBJECT_IDS = frozenset({NULL_OBJECT_ID, "0" * 64})
# Both widths, because a ledger is read in whichever repository holds it and the null id is
# all zeros at either. Derived from the one above rather than written out twice, so the two
# cannot drift apart.

DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
PENDING_ANCHOR = "?"
# An anchor stated by value: `=sha256:<64 hex>`, the digest of the section as the checkers
# compare it, so a ground names the datum it rests on without naming a commit — which is
# what lets an entry land in the same commit as the code and the citation. `=?` is the
# placeholder `sha --write` fills from the tree, and `validate` refuses it until then.

ELISIONS = ("[…]", "[...]")
QUOTE_MARKS = '"“”„«»'


def archived_id_re(config):
    r"""An archived id anywhere in a document is a quarantine breach by prefix alone.
    None when the project quarantines no series.

    Three digits or more — `CITATION_RE`'s tolerance rather than `ID_RE`'s exactly four.
    The rule reads prose a person wrote, where an id a digit wide of the schema is still
    a citation of the archive, and the width the schema actually mints has to be among
    the widths that fire. `\d{3}` alone — what this was — put a word boundary where no
    four-digit id has one, so the quarantine could not match a single id the schema
    permits. (docs/audits/0.1.0.md, QE9-105.)

    Wide on the width and narrow on the alphabet: the digits are ASCII, because `\d`
    matches every Unicode decimal digit and `ID_RE` mints none of them: a quarantined
    prefix followed by fullwidth or Arabic-Indic digits is a token no ledger can hold,
    and it was a quarantine breach anyway
    (L0177-the-quarantine-pattern-reads-ascii-digits, cites-as-live).
    """
    if not config.archived_prefixes:
        return None
    return re.compile(r"\b[" + "".join(config.archived_prefixes) + r"][0-9]{3,}\b")


# --- reports -------------------------------------------------------------------------


@dataclasses.dataclass
class Report:
    """One thing a checker has to say. `fail` exits non-zero; `flag` is visible and exits
    zero. `entry` is the id prefix (`A0001`) or None for a document; `part` names the
    place inside it the way corpus/README.md's expectation rows do."""

    outcome: str
    entry: str | None
    part: str
    message: str
    commit: str | None = None

    def place(self):
        return f"{self.entry} {self.part}" if self.entry else self.part

    def line(self):
        return f"{self.outcome.upper():4} {self.place()}: {self.message}"


def exit_code(reports):
    return 1 if any(r.outcome == "fail" for r in reports) else 0


def print_reports(reports, name, quiet_when_clean=False):
    for r in reports:
        print(r.line())
    fails = sum(r.outcome == "fail" for r in reports)
    flags = sum(r.outcome == "flag" for r in reports)
    if fails or flags or not quiet_when_clean:
        print(f"{name}: {fails} failure(s), {flags} flag(s)")


# --- the ledger being checked ----------------------------------------------------


@dataclasses.dataclass
class Ledger:
    """Where a checker looks. The real ledger and a corpus seed are both instances."""

    config: Config
    docs: list = dataclasses.field(default_factory=list)  # [(display name, Path)]
    repo: Path | None = None  # git repository holding entries_dir, for history checks
    # Documents that matched a `documents` pattern and could not be opened, as
    # [(display name, problem)]. They are not in `docs`, because a document that was not
    # read was not checked and must not be counted as though it had been.
    unreadable_docs: list = dataclasses.field(default_factory=list)
    # What a `--cached` open could not ask the index, as plain sentences for the guard to
    # print. A listing that fell back to the working tree says so there or nowhere.
    index_notes: list = dataclasses.field(default_factory=list)
    # `{address: (mode, the path it finally names)}` for the index this run was opened
    # against, or None where nothing has asked yet. Computed ONCE and kept, because three
    # listings and four readers want it and a `ls-files` apiece is three too many in a
    # pre-commit hook.
    index_reach: dict | None = None
    index_why: str | None = None

    @property
    def tree(self):
        """Root that evidence paths and registry `bytes` paths are relative to."""
        return self.config.root

    @property
    def entries_dir(self):
        return self.config.entries_dir

    @property
    def registry(self):
        return self.config.registry

    @property
    def cache(self):
        return self.config.cache


def excluded_document(rel, patterns):
    """Whether `rel` — a path from the project root, `/`-separated — is excluded by one
    of `document-excludes`.

    Matched the way a `documents` pattern is matched, segment by segment: `*` and `?`
    stop at a separator, `**` spans any number of segments. The two keys sit one line
    apart in every template this package ships and nothing has ever said they differ, so
    they do not. This was substring containment, under which `docs/draft-*.md` — the form
    both shipped example configurations wrote, and the only form anything had ever
    demonstrated — excluded nothing at all and said so nowhere. (docs/audits/0.1.0.md,
    QE9-95.)

    Two edges of "the same way", stated because the claim is only worth what it holds:
    a pattern is normalized first, so `./docs/draft-*.md` excludes what `./docs/*.md`
    selects — writing the exclusion in the same hand as the inclusion and having it
    silently match nothing is QE9-95's exact shape. And a directory is not a subtree
    here any more than it is there: `docs/` excludes the file named `docs`, and `docs/**`
    is how a subtree is written. What cannot diverge is the dotfile rule — `glob` never
    selects one, so no dotfile ever reaches this test.
    """
    parts = rel.split("/")
    return any(_segments_match(parts, _pattern_segments(p)) for p in patterns)


def excluded_directory(rel, patterns):
    """Whether *every* document under the directory `rel` is excluded.

    Asked only of a directory nobody can list, which is otherwise reported: a pattern
    that excludes some of what is under it leaves the rest unchecked and unreported, and
    an unreported unchecked document is the one thing this package may not produce. So
    only a pattern that ends in `*` or `**` — one that takes everything below the point
    it matches — suppresses the report.
    """
    parts = rel.split("/")
    for pattern in patterns:
        segments = _pattern_segments(pattern)
        head, last = segments[:-1], segments[-1]
        if last == "**" and len(parts) >= len(head) and _segments_match(parts[: len(head)], head):
            return True
        if last == "*" and len(parts) == len(head) and _segments_match(parts, head):
            return True
    return False


def _pattern_segments(pattern):
    """A `document-excludes` pattern, normalized and split the way a path is."""
    return posixpath.normpath(pattern.replace(os.sep, "/")).split("/")


def _segments_match(parts, segments):
    """`parts` against the pattern `segments`, both already split on `/`."""
    if not segments:
        return not parts
    if segments[0] == "**":  # zero segments or any number of them, as glob reads it
        return any(_segments_match(parts[i:], segments[1:]) for i in range(len(parts) + 1))
    return (
        bool(parts)
        # fnmatchcase, not fnmatch: fnmatch normalizes case for the platform, and a
        # pattern that excluded a document on one machine and not on another would be a
        # checker whose document count depends on where it ran.
        and fnmatch.fnmatchcase(parts[0], segments[0])
        and _segments_match(parts[1:], segments[1:])
    )


def tree_documents(config):
    """(documents, unreadable) — the documents that may cite an entry, addressed from the
    project root, and everything a pattern reached that could not be read.

    A document nobody can read is not an empty document, and neither is a directory
    nobody can list. Both are kept apart here rather than dropped, so that the checkers
    report them and the document count stays a count of what was actually read.
    """
    paths = []
    for pattern in config.documents:
        paths += glob.glob(os.path.join(config.root, pattern), recursive=True)
    # glob() answers `no matches` for a directory it may not read, exactly as it answered
    # `no entries` for an unlistable entries directory. The directories the patterns reach
    # into are therefore walked here, where the EACCES is visible.
    unreadable = [
        (rel, f"{problem}; the documents under it were not checked")
        for rel, problem in (
            (os.path.relpath(d, config.root).replace(os.sep, "/"), problem)
            for d, problem in sorted(unlistable_document_dirs(config).items())
        )
        if not excluded_directory(rel, config.document_excludes)
    ]
    docs, seen = [], {}
    for path in sorted(set(paths)):
        rel = os.path.relpath(path, config.root).replace(os.sep, "/")
        if excluded_document(rel, config.document_excludes):
            continue
        if os.path.commonpath([os.path.realpath(path), os.path.realpath(config.ledger_dir)]) == str(
            os.path.realpath(config.ledger_dir)
        ):
            continue  # the ledger does not cite itself
        if not os.path.isfile(path):
            # A FIFO, a directory or a dangling symlink whose name matched a pattern. Not
            # silently skipped: it was addressed as a document and it was not checked.
            unreadable.append((rel, "is not a regular file; it was not checked"))
            continue
        # Keyed by real path: a tree can reach one document at more than one address
        # through a symlink, and a document is reported at one location only.
        real = os.path.realpath(path)
        if real in seen and len(seen[real]) <= len(rel):
            continue
        seen[real] = rel
        problem = unreadable_document(path)
        if problem:
            unreadable.append((rel, f"{problem}; its citations were not checked"))
            continue
        docs.append((rel, Path(path)))
    return docs, unreadable


def _glob_matches(parts, segments):
    """`_segments_match`, plus the one rule it is documented never to need: `glob` selects
    a name beginning with `.` only through a pattern segment that begins with one, and
    never descends into a hidden directory for `**`.

    The tree listing gets that rule from `glob` itself. The index listing is a list of
    strings, so it has to apply the rule here or `docs/*.md` — which has never selected
    `docs/.draft.md` from the working tree — would start selecting it under the flag, and
    the document count would depend on which tree the run was asked about.
    """
    if not segments:
        return not parts
    if segments[0] == "**":
        return any(
            not any(part.startswith(".") for part in parts[:i])
            and _glob_matches(parts[i:], segments[1:])
            for i in range(len(parts) + 1)
        )
    return (
        bool(parts)
        and not (parts[0].startswith(".") and not segments[0].startswith("."))
        # fnmatchcase for the reason `_segments_match` gives: a document count that
        # depends on the machine's case rules is not a count.
        and fnmatch.fnmatchcase(parts[0], segments[0])
        and _glob_matches(parts[1:], segments[1:])
    )


def selects_document(rel, config):
    """Whether the `documents` patterns select `rel` — a path from the project root,
    `/`-separated — once the excludes and the ledger's own directory are taken off.

    The membership half of what `tree_documents` does, asked of a path rather than of the
    filesystem, so that the index can be asked the same question the working tree is
    (L0228-documents-under-cached-are-the-ones-the-index-holds, cites-as-live).
    """
    parts = rel.split("/")
    if not any(_glob_matches(parts, _pattern_segments(p)) for p in config.documents):
        return False
    if excluded_document(rel, config.document_excludes):
        return False
    # The ledger does not cite itself, the same exclusion the tree listing makes.
    ledger_rel = os.path.relpath(config.ledger_dir, config.root).replace(os.sep, "/")
    inside = ledger_rel != ".." and not ledger_rel.startswith("../")
    return not (inside and (rel == ledger_rel or rel.startswith(ledger_rel + "/")))


MAX_SYMLINK_EXPANSIONS = 4096
SYMLINK_DEPTH = 16


def index_tree(config):
    """({rel: mode}, why) — every path a checkout of the index would make reachable, or
    `({}, why)` when the index could not be asked. `rel` is `/`-separated from the project
    root; `mode` is the mode of the regular file finally reached, so a path reached through
    a symlink carries the mode of its target.

    THE INDEX IS NOT THE SET OF PATHS THE COMMIT MAKES REACHABLE, and the difference is a
    committed symlinked directory. `ls-files` reports the symlink as one blob and its
    target's files as others; a checkout restores the link, and `docs/bad.md` is then a
    real path that `ls-files` never named. Measured before this: with `docs -> real` and
    `real/bad.md` carrying a broken citation, `references --cached` reports `0 documents`
    and `0 failure(s)` at exit 0 while a fresh clone of that very commit fails at exit 1 —
    the cached-clean/committed-fails contrast that the listing exists to close, pointed the
    wrong way (qe ticket 45909368c43c4379, F3). The entry list had the same hole through
    the same door: a symlinked `ledger/entries` made every checker report `0 entries` at
    exit 0 (F1).

    The expansion needs nothing from the working tree, which is what keeps the answer the
    index's own: a symlink's blob IS its target, so the whole shape is readable from the
    commit being built (L0230-a-cached-listing-expands-the-index-symlinks, cites-as-live).

    Bounded on both axes, because a symlink graph is arbitrary: `SYMLINK_DEPTH` passes, so
    a cycle stops rather than growing paths forever, and `MAX_SYMLINK_EXPANSIONS` added
    paths, so a wide fan-out cannot make the listing the slow part of a commit. A target
    that is absolute, or that climbs out of the repository, is no part of this tree and is
    not followed.
    """
    answer = git_call(config.root, "ls-files", "--cached", "-z", "-s", env=git_env(index=True))
    if not answer.ok:
        return {}, answer.why, None
    modes, links = {}, {}
    for record in answer.out.split("\0"):
        # `<mode> SP <object> SP <stage> TAB <path>`; `-z` ends the record at the NUL, so
        # `partition` on the first tab leaves a path holding a tab intact.
        meta, tab, rel = record.partition("\t")
        if not tab or not rel:
            continue
        mode = meta.split(" ", 1)[0]
        # An unmerged path arrives once per stage. One path is one file whatever the
        # conflict, and reading it three times reported every failure three times
        # (qe ticket 45909368c43c4379, F4); the first stage wins, as a dict does.
        modes.setdefault(rel, mode)
        if mode == "120000":
            links[rel] = None
    if links:
        blobs, _failures = git_blobs(
            config.root, (f":{rel}" for rel in links), env=git_env(index=True)
        )
        for rel in list(links):
            data = blobs.get(f":{rel}")
            # A link git did not answer for is simply not followed: it stays a symlink in
            # the listing, which the mode check then names as not a regular file.
            target = None if data is None else _link_target(rel, data)
            if target is None:
                del links[rel]
            else:
                links[rel] = target
    # `{address: (mode, the path it finally names)}`. The second half is what
    # `os.path.realpath` answers for the working tree, and it is free here: an address only
    # exists because this pass built it from the path it reaches.
    reach = {rel: (mode, rel) for rel, mode in modes.items()}
    room, truncated = MAX_SYMLINK_EXPANSIONS, None
    for _ in range(SYMLINK_DEPTH):
        added = {}
        for link, target in links.items():
            for rel, (mode, real) in reach.items():
                if rel != target and not rel.startswith(target + "/"):
                    continue
                through = link + rel[len(target) :]
                # A link to a regular FILE is that file at this address, which is what
                # `os.path.isfile` answers for the working tree and therefore what the
                # tree listing counts. So a resolved link takes its target's mode rather
                # than staying `120000` and being named unreadable — the two listings
                # disagreed about `docs/link.md -> note.md` until this, one reporting the
                # link and one the target.
                was = added.get(through, reach.get(through))
                if was is None or (was[0] == "120000" and mode != "120000"):
                    added[through] = (mode, real)
        if not added:
            break
        if len(added) > room:
            # The cap counts paths ADDED, not paths held: counting the whole listing meant
            # any repository above the cap got no expansion at all, silently, and this
            # repository's 784 tracked files were under it so nothing said otherwise
            # (qe ticket f868273f36b448ab, F2).
            truncated = (
                f"more than {MAX_SYMLINK_EXPANSIONS} paths are reachable only through "
                "symlinks; the listing holds what was reached and not the rest"
            )
            break
        room -= len(added)
        reach.update(added)
        links = {rel: t for rel, t in links.items() if reach[rel][0] == "120000"}
    else:
        if links:
            # A CYCLE, usually, rather than a deep chain: `ln -s . here` reaches one
            # segment further every pass and never runs out. The first wording said
            # "nested more than N deep", which is false of a link nested none deep.
            truncated = (
                f"symlinks were followed {SYMLINK_DEPTH} times and still reach further — a "
                "cycle, or a chain longer than that; the listing holds what was reached "
                "and not the rest"
            )
    return reach, None, truncated


def _link_target(rel, data):
    """Where a symlink blob points, as a path from the project root, or None when it points
    outside the tree the commit carries.

    A target is read relative to the link's own directory, the way the filesystem reads it.
    Absolute, or climbing past the root: the commit does not carry what is there, so the
    listing says nothing about it rather than guessing (a dangling link simply reaches no
    path in the map, which needs no case of its own).
    """
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if not text or text.startswith("/"):
        return None
    target = posixpath.normpath(posixpath.join(posixpath.dirname(rel), text))
    if target == ".." or target.startswith("../") or target == ".":
        return None
    return target


def index_reach(ledger):
    """({address: (mode, real path)}, why) for `ledger`'s index, asked once and kept.

    Every reader of the index goes through `index_spec` below, and every one of them needs
    this map, so it is computed here rather than at each — three `ls-files` per command,
    fifteen per hook run, was the cost of not doing so.
    """
    if ledger.index_reach is None:
        if not ledger.repo:
            ledger.index_reach, ledger.index_why = {}, "the ledger has no repository of its own"
        else:
            reach, why, truncated = index_tree(ledger.config)
            ledger.index_reach, ledger.index_why = reach, why
            if truncated:
                # A TRUNCATION IS NOT A FAILURE, and answering it with one was a false pass
                # of its own: a `why` sends the whole listing to the working tree, so an
                # ordinary `ln -s . here` took a staged-only document off the list entirely
                # and the run reported clean at exit 0 where the commit before it exited 1.
                # A narrower universe than the commit has is not a wrong one; the listing
                # keeps what it reached, and the guard says what it did not.
                ledger.index_notes.append(f"{truncated}; some staged paths were not checked")
    return ledger.index_reach, ledger.index_why


def index_spec(ledger, rel):
    """The `:<path>` git will answer for, given `rel` from the project root.

    THE ONE PLACE A PATH BECOMES AN INDEX READ, and it exists because the listings learned
    to name paths git does not. Expanding the index's symlinks puts `docs/bad.md` on the
    list when the index holds `docs -> real` and `real/bad.md`; git has no blob at that
    address, `cat-file` says missing, `blob_absent` reads missing as "not staged", and the
    reader falls back to the WORKING TREE at exactly the paths the expansion existed to
    add. Measured: an entry staged with `grade: bogus` under a symlinked entries directory
    and corrected in the tree gave `validate --cached` `1 entry` and `0 failure(s)` at
    exit 0, while a fresh clone of the commit it made failed at exit 1 — the listing
    repaired and the read left pointing at the wrong tree
    (L0232-an-index-read-names-the-path-the-index-holds, cites-as-live).

    A path the expansion does not know is asked for as itself, which is every path in a
    repository holding no symlinks and is what this always did.
    """
    reach, _why = index_reach(ledger)
    known = reach.get(rel)
    return f":{known[1] if known else rel}"


def index_specs(ledger, rels):
    """`{rel: spec}` for several paths, so a caller batching `cat-file` asks the reach once
    rather than once per path."""
    reach, _why = index_reach(ledger)
    return {rel: f":{reach[rel][1] if rel in reach else rel}" for rel in rels}


def index_documents(ledger):
    """(documents, unreadable, why) — the configured documents the index holds, in the
    shape `tree_documents` returns them, or `(None, None, why)` when the index could not
    be asked. Asked only where `open_ledger` found a `.git` at the project root, which is
    the only place a `Ledger` ever has a repository.

    Which documents exist is a question about a tree, and under `--cached` the tree is the
    index. Globbing the working tree there was a false pass with the shape this package
    exists to refuse, and it was not even a `--cached` defect: `tree_documents` is the
    document universe for every run, so a document the index holds and the tree does not —
    `git add docs/bad.md && rm docs/bad.md` — was on nobody's list. Measured, with a
    document staged that way carrying a citation of an id nothing minted: `check --cached`
    reports `1 document` and `0 failure(s)` at exit 0, and a fresh clone of the commit it
    was about to make fails `references` at exit 1 naming that document
    (L0228-documents-under-cached-are-the-ones-the-index-holds, cites-as-live).

    The listing is the index's alone rather than added to the tree's, which is the answer
    the entry list gives too and for the same reason: `ls-files` lists every tracked path,
    not what changed, so with the symlinks expanded it is what the commit will carry.
    Adding the tree's matches back would put a document the commit does not carry on the
    list, and a run that reads a file no commit contains is the report this tool must never
    produce, whichever direction it points.

    One root, not two: `ls-files` answers paths relative to the repository it is run in,
    and everything downstream — the patterns, the excludes, the display name, the path a
    document is finally read at — is relative to the project root. Taking the repository
    as a second argument would let those come apart silently the day a ledger sits below
    its repository's root, and every path here would be counted from the wrong place.

    Two things `tree_documents` gets from the filesystem and this gets from the mode and
    the expansion. A path that is not a regular file is named rather than read, because
    `cat-file` hands back a symlink's target as though it were the document's text. And one
    document reached at two addresses is reported at one, the shorter, which is the
    realpath dedup `tree_documents` makes — here the expansion already says which addresses
    reach the same file.
    """
    config = ledger.config
    reach, why = index_reach(ledger)
    if why:
        return None, None, why
    unreadable, by_target = [], {}
    for rel, (mode, real) in sorted(reach.items()):
        if not selects_document(rel, config):
            continue
        if mode not in ("100644", "100755"):
            unreadable.append((rel, "is not a regular file in the index; it was not checked"))
            continue
        # Keyed by the path finally named, so one document addressed twice is reported at
        # one address — the shorter, which is the rule `tree_documents` applies to the
        # realpaths it resolves.
        if real in by_target and len(by_target[real]) <= len(rel):
            continue
        by_target[real] = rel
    docs = [(rel, Path(config.root) / rel) for rel in sorted(by_target.values())]
    return docs, unreadable, None


def unreadable_document(path):
    """Why `path` cannot be read as UTF-8 text, or None.

    The read is done rather than asked about: `os.access` answers for the real uid under
    a setuid binary and for nobody at all under an ACL, and a file that opens and then
    turns out not to be text is just as unchecked as one that never opened. The text is
    discarded — this runs for every command, and the checkers that want the content read
    it themselves.
    """
    try:
        Path(path).read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return f"is not UTF-8 text (byte {exc.start}: {exc.reason})"
    except OSError as exc:
        return f"cannot be read ({exc.strerror or exc})"
    return None


def _subdirectories(directory):
    """(subdirectories, problem) for one directory. Symlinked directories are not
    descended into, the way `**` does not follow them; the question here is which
    directories will not list, and a link that leaves the tree is not one of them."""
    try:
        with os.scandir(directory) as it:
            return [Path(e.path) for e in it if e.is_dir(follow_symlinks=False)], None
    except (OSError, RuntimeError) as exc:
        return [], f"cannot be listed ({getattr(exc, 'strerror', None) or exc})"


def unlistable_document_dirs(config):
    """{directory: problem} for every directory a `documents` pattern reaches into and
    cannot list. The last segment of a pattern names files, so only the segments above it
    are walked; a directory that lists tells us its files list too."""
    problems = {}

    def note(directory):
        subdirs, problem = _subdirectories(directory)
        if problem is not None:
            problems.setdefault(directory, problem)
        return subdirs

    def descendants(directory):
        out = [directory]
        for child in note(directory):
            out += descendants(child)
        return out

    for pattern in config.documents:
        directories = [Path(config.root)]
        for segment in PurePath(pattern).parts[:-1]:
            reached = []
            for directory in directories:
                if segment == "**":  # this directory and every directory under it
                    reached += descendants(directory)
                else:
                    reached += [d for d in note(directory) if fnmatch.fnmatch(d.name, segment)]
            directories = reached
        for directory in directories:
            note(directory)  # the segment that names the files still needs a listing
    return problems


def open_ledger(root=None, config_path=None, config=None, cached=False):
    """The project's ledger: its configuration, the documents that may cite it, and the
    git repository its history checks read.

    `cached` decides which tree the documents are listed from, and it is settled here
    rather than at each reader because the list is also what the run counts and reports
    (L0228-documents-under-cached-are-the-ones-the-index-holds, cites-as-live). An
    index that cannot be answered for falls back to the working tree's listing, and the
    `why` is not carried out of here: it is the fallback `index_problem()` already reports
    through the guard, on the line that says what was not checked.
    """
    config = config or load_config(root=root, config_path=config_path)
    repo = config.root if (config.root / ".git").exists() else None
    docs, unreadable = tree_documents(config)
    notes = []
    ledger = Ledger(config=config, docs=docs, repo=repo, unreadable_docs=unreadable)
    if cached and repo:
        indexed, index_unreadable, why = index_documents(ledger)
        if indexed is None:
            # NOT silence. `index_problem()` asks `ls-files -- .git`, which prints nothing
            # whatever the repository holds, so it cannot fail the way a listing of every
            # tracked path can — a timeout, a pack it cannot open. Measured with a git that
            # fails only this call: `references --cached` went from exit 1 naming a staged
            # document to `0 documents` and `0 failure(s)` with nothing said, which is
            # L0227's finding one listing over (qe ticket 45909368c43c4379, F2).
            notes.append(
                f"the index could not be listed ({why}), so --cached fell back to the "
                "working tree; what is staged was not checked"
                # (L0231-a-listing-that-fell-back-is-named-by-the-guard, cites-as-live)
            )
        else:
            ledger.docs, ledger.unreadable_docs = indexed, index_unreadable
    # Extended, not replaced: the expansion appends its own note during the listing above,
    # and assigning here dropped it on the floor — the truncation went unsaid, which is the
    # whole point of having it.
    ledger.index_notes.extend(note for note in notes if note not in ledger.index_notes)
    return ledger


def default_ledger(tree=None):
    """A ledger under the default layout, with no configuration file involved."""
    config = default_config(tree or Path.cwd())
    return open_ledger(config=config)


# --- normalization and the fingerprint ---------------------------------------------


def normalize(text):
    """NFC, markdown emphasis markers removed, whitespace collapsed. The fingerprint and
    the resolver both use this, so they never disagree about what a change is."""
    text = unicodedata.normalize("NFC", text).replace("*", "").replace("`", "")
    return " ".join(text.split())


def normalize_with_map(text):
    """normalize(), plus for every character of the result the index of the character
    in the NFC text it came from. Lets the resolver find a span in normalized text and
    then look at the original around it."""
    nfc = unicodedata.normalize("NFC", text)
    out, idx = [], []
    pending_space = False
    for i, ch in enumerate(nfc):
        if ch in "*`":
            continue
        if ch.isspace():
            pending_space = bool(out)
            continue
        if pending_space:
            out.append(" ")
            idx.append(i)  # the space stands for the whitespace run ending here
            pending_space = False
        out.append(ch)
        idx.append(i)
    return nfc, "".join(out), idx


def fingerprint(scope_text, backing_blocks):
    """sha256 over the normalized Scope lines, a blank line, then one normalized line per
    Backing block (`source | speaker | quote`), blocks sorted. Grounds are excluded
    (L0137-the-fingerprint-covers-scope-and-backing-and-excludes-grounds, cites-as-live).

    Grounds are excluded because they are the evidence, and evidence is what a
    supersession is allowed to replace; Scope and Backing are what the claim was
    measured over and what it rests its quotations on, and a successor changing either
    of those is stating something else. The blocks are sorted, so reordering Backing is
    not a change to the record.
    """
    scope = [normalize(ln) for ln in scope_text.splitlines() if ln.strip()]
    lines = sorted(
        f"{normalize(s)} | {normalize(sp)} | {normalize(q)}" for s, sp, q in backing_blocks
    )
    payload = "\n".join(scope) + "\n\n" + "\n".join(lines)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def section_header_re(config, type_name, section):
    """Where the named section of an artifact of this type begins."""
    pattern = config.section_pattern(type_name).replace(NAME_SLOT, re.escape(section))
    return re.compile(pattern, re.MULTILINE)


# A fenced code block opens on a line of three or more backticks or tildes indented by at
# most three spaces, and closes on the next line of at least as many of the same character
# with nothing but whitespace after it. CommonMark's rule, and the one every renderer a
# reader of these artifacts will use implements.
CODE_FENCE_RE = re.compile(
    r"^(?P<indent> {0,3})(?P<fence>`{3,}|~{3,})(?P<info>[^\n]*)$", re.MULTILINE
)


def fenced_spans(text):
    """(start, end) for every fenced code block in `text`, in order.

    A `#`-led line inside one is a comment, a shell prompt or a C preprocessor directive
    — not a heading — and a Markdown lab note carrying a code snippet is the ordinary
    shape of the artifact this package compares, not an edge case. Reading such a line as
    a heading ended the section it sat in and left everything below the fence outside the
    comparison, for `freshness` and `resolve` both.

    An unclosed fence runs to the end of the artifact, which is CommonMark's answer and
    the safe one here: text nobody can see the end of is text this tool should not be
    finding headings in.

    Applied to every artifact, including the ones a project reads with its own
    `section-patterns` — a source file, say, whose sections are `def <name>`. Markdown's
    fence grammar is the wrong grammar for a Python file, and a line of three backticks at
    the left margin inside a docstring would be read as one. That is accepted, because the
    alternative is worse in the direction that matters: honouring fences only for the
    default heading pattern would quietly stop honouring them for a project that writes
    its own Markdown pattern, which is this defect back and silent. A false fence in a
    code artifact is loud instead — the section is not found, or is found too long, and
    `resolve` or a `moved` flag says so.
    """
    spans, pos = [], 0
    while (opening := CODE_FENCE_RE.search(text, pos)) is not None:
        marker = opening.group("fence")
        pos = opening.end()
        if marker[0] == "`" and "`" in opening.group("info"):
            # A backtick fence's info string may not contain a backtick, so this line is
            # inline code inside a paragraph rather than the opening of a block.
            continue
        closing = next(
            (
                c
                for c in CODE_FENCE_RE.finditer(text, pos)
                if c.group("fence")[0] == marker[0]
                and len(c.group("fence")) >= len(marker)
                and not c.group("info").strip()
            ),
            None,
        )
        spans.append((opening.start(), closing.end() if closing else len(text)))
        if closing is None:
            break
        pos = closing.end()
    return spans


def _in_a_fence(spans, at):
    return any(start <= at < end for start, end in spans)


def section_span(text, config, type_name, section):
    """(start, end) of the named section in `text`, or None when it is not there.

    The section runs from its own header to wherever the next one begins — the same
    pattern with the name slot widened to some other name — or to the end of the
    artifact. One pattern therefore decides both ends, and a pattern anchored too loosely
    ends the section early and leaves the rest of it uncompared, which is why the
    configuration documents where to anchor.

    What counts as a header is settled twice: by the pattern, which says which headings
    end a section, and by `fenced_spans`, which says what a heading is at all. A line
    that only looks like one because it is inside a code block ends nothing
    (L0138-a-heading-inside-a-code-fence-ends-no-section, cites-as-live), and a heading
    nested under this one is part of it rather than the start of the next
    (L0139-a-nested-heading-is-part-of-the-section-above-it, cites-as-live).
    """
    fences = fenced_spans(text)
    head = next(
        (
            m
            for m in section_header_re(config, type_name, section).finditer(text)
            if not _in_a_fence(fences, m.start())
        ),
        None,
    )
    if head is None:
        return None
    pattern = config.section_pattern(type_name).replace(NAME_SLOT, ANY_NAME)
    nxt = re.compile(pattern, re.MULTILINE)
    depth = head.groupdict().get("depth")
    at = head.end()
    while (m := nxt.search(text, at)) is not None:
        deeper = m.groupdict().get("depth")
        if _in_a_fence(fences, m.start()):
            at = m.end()
            continue
        if depth is None or deeper is None or len(deeper) <= len(depth):
            return head.start(), m.start()
        # A heading nested under this one is part of it, not the end of it: `## Method`
        # ends `## Observation` and `### Detail` does not.
        at = m.end()
    return head.start(), len(text)


def section_text(text, config, type_name, section):
    span = section_span(text, config, type_name, section)
    return None if span is None else text[span[0] : span[1]]


def digest_of(text):
    """`sha256:<hex>` over `text` with its trailing whitespace stripped — the datum a
    by-value anchor names, for a section or for a whole artifact alike."""
    return "sha256:" + hashlib.sha256(text.rstrip().encode("utf-8")).hexdigest()


def section_digest(text, config, type_name, section):
    """The by-value anchor of one section of an artifact, or None when the section is not
    in it.

    sha256 over exactly what the freshness comparison reads and nothing else: the artifact
    decoded as UTF-8 through universal newlines, the section found through the type's
    configured pattern, and trailing whitespace stripped, because the gap between one
    section and the next belongs to neither. No comment, docstring or formatting is set
    aside — that would be a judgement about which edits matter, and the checkers make
    none — so a ground anchored this way moves exactly when the section's text does, and
    it can be computed from the working tree before any commit exists
    (L0196-a-by-value-anchor-is-the-digest-of-the-compared-section, cites-as-live).
    """
    found = section_text(text, config, type_name, section)
    return None if found is None else digest_of(found)


# --- pointers ------------------------------------------------------------------


@dataclasses.dataclass
class Pointer:
    type: str
    raw: str
    target: str = ""  # path, entry id, registry id
    section: str = ""  # evidence pointer § "section"
    pin: str = ""  # evidence pointer @commit — the anchor stated by reference
    digest: str = ""  # evidence pointer =sha256:… — the anchor stated by value; `?` pending
    act: str = ""  # entry: · act
    locator: str = ""  # source: · locator
    sectioned: bool = False  # the pointer was written in the § "section" form
    fields: dict = dataclasses.field(default_factory=dict)  # search: key=value

    @property
    def by_value(self):
        """Whether the anchor states the datum by value rather than by revision."""
        return bool(self.digest)

    @property
    def anchor(self):
        """The anchor as written: `@<pin>` or `=<digest>`."""
        return f"={self.digest}" if self.digest else f"@{self.pin}"


# Evidence pointers are named by the project (`lab:`, `experiment:`, `run:`), so the
# grammar is generic and config.py says which names are legal and which take a section.
# The anchor is the last word of an evidence pointer: `@<revision>` states the datum by
# reference, as the section stood at that commit; `=<digest>` states it by value.
ANCHOR_RE = r"(?:@(\S+)|=(\S+))"
SECTIONED_RE = re.compile(r'^([a-z][a-z0-9_-]*): (\S+) § "([^"]+)" ' + ANCHOR_RE + "$")
ARTIFACT_RE = re.compile(r"^([a-z][a-z0-9_-]*): (\S+) " + ANCHOR_RE + "$")
ENTRY_RE = re.compile(r"^entry: (\S+) · (\S+)$")
SOURCE_RE = re.compile(r"^source: (\S+) · (.+)$")
SEARCH_RE = re.compile(r'^search: corpus=(.+?); query="(.*)"; date=(\d{4}-\d{2}-\d{2})$')
DEFECT_RE = re.compile(r"^defect: (.+)$")
RESERVED = ("entry", "source", "search", "defect")


def parse_pointer(raw):
    """A typed pointer, or None when the line is none of the forms. An evidence type
    name is carried through as written; whether it is one the project declared is a
    question for validate."""
    raw = raw.strip()
    if m := ENTRY_RE.match(raw):
        return Pointer("entry", raw, target=m.group(1), act=m.group(2))
    if m := SOURCE_RE.match(raw):
        return Pointer("source", raw, target=m.group(1), locator=m.group(2).strip())
    if m := SEARCH_RE.match(raw):
        return Pointer(
            "search", raw, fields={"corpus": m.group(1), "query": m.group(2), "date": m.group(3)}
        )
    if m := DEFECT_RE.match(raw):
        return Pointer("defect", raw, target=m.group(1))
    if (m := SECTIONED_RE.match(raw)) and m.group(1) not in RESERVED:
        return Pointer(
            m.group(1),
            raw,
            target=m.group(2),
            section=m.group(3),
            pin=m.group(4) or "",
            digest=m.group(5) or "",
            sectioned=True,
        )
    if (m := ARTIFACT_RE.match(raw)) and m.group(1) not in RESERVED:
        return Pointer(
            m.group(1), raw, target=m.group(2), pin=m.group(3) or "", digest=m.group(4) or ""
        )
    return None


# --- quotes ----------------------------------------------------------------------


@dataclasses.dataclass
class Quote:
    spans: list
    lead_elided: bool
    trail_elided: bool


def parse_quote(value):
    """One or more quoted spans separated by `[…]`, optionally beginning or ending with
    `[…]`. None when the value is anything else."""
    text = value.strip()
    for mark in ELISIONS:
        text = text.replace(mark, "\x00")
    parts = [p.strip() for p in text.split("\x00")]
    if not parts:
        return None
    lead = parts[0] == ""
    trail = len(parts) > 1 and parts[-1] == ""
    inner = parts[1 if lead else 0 : (len(parts) - 1) if trail else len(parts)]
    if not inner:
        return None
    spans = []
    for piece in inner:
        if len(piece) < 2 or piece[0] not in QUOTE_MARKS or piece[-1] not in QUOTE_MARKS:
            return None
        body = piece[1:-1]
        if not body.strip() or any(c in QUOTE_MARKS for c in body):
            return None
        spans.append(body)
    return Quote(spans, lead, trail)


# --- entries ---------------------------------------------------------------------


@dataclasses.dataclass
class Verdict:
    index: int  # 1-based
    raw: str  # the block as written, for the append-only comparison
    timestamp: str = ""
    status: str = ""
    grade: str = ""
    author: str = ""
    evidence: str | None = None
    artifact: str | None = None  # the blob the drift was seen at, for a propagated verdict
    note: str | None = None
    malformed: str | None = None

    @property
    def pointer(self):
        return parse_pointer(self.evidence) if self.evidence else None


@dataclasses.dataclass
class Backing:
    index: int  # 1-based
    source: str  # `<registry id> · <locator>`
    speaker: str
    quote: str

    @property
    def source_id(self):
        return self.source.split("·", 1)[0].strip()

    @property
    def part(self):
        return f"Backing quote {self.index}"


@dataclasses.dataclass
class Reference:
    path: str
    genre: str
    act: str


@dataclasses.dataclass
class Entry:
    path: Path
    text: str
    front: dict  # frontmatter, key -> value (raw string)
    front_order: list
    sections: dict  # heading -> body, in file order
    section_order: list
    has_append: bool
    frozen: str  # everything above the APPEND marker
    grounds: list  # [(raw line, Pointer | None)]
    backing: list  # [Backing]
    backing_none: bool
    verdicts: list  # [Verdict]
    references: list  # [(raw line, Reference | None)]
    problems: list  # [(part, message)] structural defects found while parsing

    @property
    def id(self):
        return self.front.get("id", "")

    @property
    def prefix(self):
        m = PREFIX_RE.match(self.id or self.path.stem)
        return m.group(1) if m else (self.id or self.path.stem)

    @property
    def grade(self):
        return self.front.get("grade", "")

    @property
    def scope_text(self):
        return self.sections.get("Scope", "")

    @property
    def scope(self):
        out = {}
        for ln in self.scope_text.splitlines():
            if ln.strip():
                key, _, value = ln.partition(":")
                out[key.strip()] = value.strip()
        return out

    @property
    def assertion(self):
        return self.sections.get("Assertion", "").strip()

    @property
    def ground_pointers(self):
        return [p for _, p in self.grounds if p is not None]

    def computed_sha(self):
        return fingerprint(self.scope_text, [(b.source, b.speaker, b.quote) for b in self.backing])

    def status(self):
        return derive_status(self.verdicts)

    def superseded_verdicts(self):
        return [v for v in self.verdicts if v.status == "superseded"]


def _split_sections(body):
    """(section names in file order, name -> body).

    A `##` line inside a fenced code block is not a heading, here for the same reason it
    is not one in `section_span`: a Backing quote or a Reference line may legitimately
    contain one, and reading it as a section makes the entry a different entry. The
    direction that matters is the quiet one — a fenced `## Verdicts` *after* the real
    Verdicts section replaced it with an empty one, so an entry carrying a `refuted`
    verdict read as `open`, and `references` would then let a document cite it as live.
    """
    order, sections = [], {}
    fences = fenced_spans(body)
    matches = [m for m in HEADING_RE.finditer(body) if not _in_a_fence(fences, m.start())]
    for i, m in enumerate(matches):
        name = m.group(1)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        chunk = body[m.end() : end]
        order.append(name)
        sections[name] = chunk.replace(APPEND, "") if name == "Backing" else chunk
    return order, sections


def _parse_verdicts(text):
    verdicts = []
    blocks = re.split(r"\n(?=- )", "\n" + text.strip("\n"))
    for raw_block in blocks:
        block = raw_block.strip("\n")
        if not block.strip():
            continue
        v = Verdict(index=len(verdicts) + 1, raw=block.rstrip())
        lines = block.splitlines()
        m = VERDICT_HEAD_RE.match(lines[0].rstrip())
        if not m:
            v.malformed = "header is not `- <timestamp> · <status> · grade: <g> · author: <a>`"
        else:
            v.timestamp, v.status, v.grade, v.author = m.groups()
        for ln in lines[1:]:
            fm = re.match(r"^\s+(evidence|artifact|note): (.*)$", ln.rstrip())
            if not fm:
                v.malformed = v.malformed or f"unrecognized line {ln.strip()!r}"
                continue
            field = fm.group(1)
            # A repeated field used to overwrite silently, so a verdict carrying two
            # `artifact:` lines was read as whichever came last and the other one was
            # invisible to every checker and to `--write`'s own append-only comparison.
            # A block that says a thing twice does not say it once.
            if getattr(v, field) is not None:
                v.malformed = v.malformed or f"a second `{field}:` line"
                continue
            setattr(v, field, fm.group(2).strip())
        verdicts.append(v)
    return verdicts


def file_problem(path, what):
    """Why `path` is not a regular file this tool can read, or None when it is one.

    `os.stat` rather than `Path.is_file()`, for two reasons. is_file() answers False for
    everything from a FIFO to a permission error, and which of them it was is the
    difference between a message someone can act on and `unexpected PermissionError`. And
    it answers differently on different interpreters — with the execute bit off a
    directory, 3.12 lets the EACCES out of is_file() and 3.13 swallows it — while the
    syscall underneath says the same thing everywhere
    (L0146-why-a-path-is-unreadable-is-said-rather-than-collapsed, cites-as-live).
    """
    try:
        info = os.stat(path)
    except FileNotFoundError:
        # A path that is there and points at nothing is a different mistake from a path
        # that is not there: a moved target, against a name that was never written.
        if os.path.islink(path):
            return f"{what} is a symlink to nothing"
        return f"no {what} there"
    except (OSError, ValueError) as exc:
        return f"cannot read {what} ({getattr(exc, 'strerror', None) or exc})"
    if not stat.S_ISREG(info.st_mode):
        return f"{what} is not a regular file"
    return None


def read_text_or_raise(path, what):
    """`path` as UTF-8 text, or a LedgerError naming the file and what is wrong with it.
    Every read of a file the user maintains goes through here: an unreadable entry is a
    thing to report, not a traceback
    (L0145-every-read-of-a-maintained-file-goes-through-one-funnel, cites-as-live)."""
    path = Path(path)
    # Checked before opening: a FIFO named like an entry blocks read_text() forever with
    # no writer on the other end, which wedges a pre-commit hook with no output at all.
    # A directory, a dangling symlink, a symlink loop and a name that will not stat all
    # land here too.
    problem = file_problem(path, what)
    if problem is not None:
        raise LedgerError(f"{path}: {problem}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise LedgerError(
            f"{path}: {what} is not UTF-8 text (byte {exc.start}: {exc.reason})"
        ) from exc
    except OSError as exc:
        raise LedgerError(f"{path}: cannot read {what} ({exc.strerror or exc})") from exc


def read_text_exact(path, what="entry"):
    """`path` as UTF-8 text with its own line endings intact.

    `read_text_or_raise` reads through universal newlines, which is right for a parser —
    every rule in this schema is written against `\\n` — and wrong for a writer: a file
    read that way and written back has had every CRLF in it rewritten, which for a
    committed entry is a rewrite of an immutable region. A path that is about to be
    written is read through here instead, so the bytes it does not change come back out
    as they went in.
    """
    problem = file_problem(path, what)
    if problem is not None:
        raise LedgerError(f"{path}: {problem}")
    try:
        with open(path, encoding="utf-8", newline="") as fh:
            return fh.read()
    except UnicodeDecodeError as exc:
        raise LedgerError(
            f"{path}: {what} is not UTF-8 text (byte {exc.start}: {exc.reason})"
        ) from exc
    except OSError as exc:
        raise LedgerError(f"{path}: cannot read {what} ({exc.strerror or exc})") from exc


def write_text_atomically(path, text, mode=None):
    """Write `text` to `path` through a temporary file in the same directory.

    The text is written with `newline=""`, so the endings the caller composed are the
    endings on disk.
    """
    write_bytes_atomically(path, text.encode("utf-8"), mode=mode)


def write_bytes_atomically(path, data, mode=None):
    """Write `data` to `path` through a temporary file in the same directory.

    Every write in this package used to truncate its destination before it knew it could
    fill it, so a write that failed partway — a full disk, a quota, a resource limit —
    left a committed entry cut off mid-verdict with the rest of it gone. `os.replace` is
    atomic within a filesystem, which is where all of these writes land: the file a
    reader sees is either the old one entire or the new one entire
    (L0147-every-write-lands-through-a-temporary-file-and-a-replace, cites-as-live).

    A symlink is resolved first: replacing the link itself would turn a ledger that
    reaches an entry through one into a ledger with two copies of it
    (L0148-a-write-resolves-a-symlink-before-it-replaces, cites-as-live). Where the link
    leads is the caller's question, and `leaves_root` is where it is asked.
    """
    target = Path(os.path.realpath(path))
    _refuse_a_target_this_process_may_not_write(target)
    tmp = target.with_name(f".{target.name}.claims-ledger-{os.getpid()}")
    try:
        with open(tmp, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        # The replacement keeps the permissions the file had. A file that is not there
        # yet is left with what the umask already gave the temporary one.
        if (keep := mode if mode is not None else _existing_mode(target)) is not None:
            os.chmod(tmp, keep)
        os.replace(tmp, target)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise
    _fsync_directory(target.parent)


def _refuse_a_target_this_process_may_not_write(target):
    """Raise `PermissionError` when the filesystem says `target` may not be written.

    `os.replace` needs write permission on the *directory* and none at all on the file,
    so a funnel that only ever renames onto its target will rewrite a mode-444 entry,
    exit 0, and leave the mode still saying the file is protected. Every write in this
    package used to truncate its destination, which asked the kernel for permission by
    opening it; this asks the same question the same way, and asks it before anything is
    written.

    The kernel is the arbiter rather than `os.access`, because the question is not "do
    the mode bits say so" — root, an ACL, an immutable flag and a read-only mount all
    answer differently from the bits, and a check that disagreed with the write it stands
    in front of would be worse than none. `r+b` opens for writing without truncating.

    Only regular files are asked about. A directory, a FIFO or a device at the target is
    not a permissions question, and `os.replace`'s own error names it better than opening
    it would — a FIFO in particular is a file that opening can block on forever, which in
    a pre-commit hook is a wedged commit with no output.
    """
    try:
        info = os.stat(target)
    except OSError:
        return  # Not there, or not stattable; the temp file and `os.replace` say so.
    if not stat.S_ISREG(info.st_mode):
        return
    with open(target, "r+b"):
        pass


def _fsync_directory(path):
    """Flush the directory entry `os.replace` just made, so the rename survives a power
    loss and not merely a crash of this process.

    Every interruption the package is actually tested against — `SIGKILL`, `RLIMIT_FSIZE`
    — is already handled by the rename itself, and this closes the one case that is not
    reachable by a test. Failures are ignored on purpose: a directory that cannot be
    opened for reading is Windows, and a write that has already landed must not be turned
    into an error by the flush that follows it.
    """
    fd = None
    try:
        fd = os.open(path, os.O_RDONLY)
        os.fsync(fd)
    except OSError:
        pass
    finally:
        if fd is not None:
            with contextlib.suppress(OSError):
                os.close(fd)


def _existing_mode(path):
    """The permissions `path` has, or None when it has none because it is not there."""
    try:
        return stat.S_IMODE(os.stat(path).st_mode)
    except OSError:
        return None


# `---` opens and closes the frontmatter. YAML permits trailing space after a document
# marker and editors leave it there, so the fence is matched as a line rather than as the
# literal `\n---\n`: an entry that plainly has frontmatter must not be read as having
# none, which is one report followed by every check that needed a key cascading behind it.
FENCE_RE = re.compile(r"^---[ \t]*\n", re.MULTILINE)


def split_frontmatter(text):
    """(head, body) around the frontmatter fences, or None when there are none."""
    opening = FENCE_RE.match(text)
    if opening is None:
        return None
    closing = FENCE_RE.search(text, opening.end())
    if closing is None:
        return None
    return text[opening.end() : closing.start()], text[closing.end() :]


def parse_entry(path, text=None):
    """The one parser. It, `normalize`, `fingerprint` and `derive_status` are defined once
    here and imported by every module that reads an entry — the five checkers, the
    authoring side, the neighbours lookup and the command line — rather than reimplemented
    in any of them, so no two of them can disagree about what an entry says
    (L0169-every-reader-of-an-entry-shares-one-parser-and-one-normalization,
    cites-as-live).
    """
    path = Path(path)
    if text is None:
        text = read_text_or_raise(path, "entry")
    problems = []
    front, front_order = {}, []
    body = text
    if (split := split_frontmatter(text)) is not None:
        head, body = split
        for ln in head.splitlines():
            if not ln.strip():
                continue
            key, sep, value = ln.partition(":")
            if not sep or not re.match(r"^[a-z_]+$", key):
                problems.append(("frontmatter", f"unparseable line {ln!r}"))
                continue
            if key in front:
                problems.append(("frontmatter", f"duplicate key {key}"))
            front[key] = value.strip()
            front_order.append(key)
    else:
        problems.append(("frontmatter", "no YAML frontmatter"))

    has_append = APPEND in body
    frozen = text.split(APPEND, 1)[0]
    order, sections = _split_sections(body)

    grounds = []
    for ln in sections.get("Grounds", "").splitlines():
        if not ln.strip():
            continue
        if ln.startswith("- "):
            grounds.append((ln[2:].strip(), parse_pointer(ln[2:])))
        else:
            grounds.append((ln.strip(), None))

    backing, backing_none = [], False
    btext = sections.get("Backing", "")
    if btext.strip() == "none":
        backing_none = True
    else:
        consumed = 0
        for i, m in enumerate(BACKING_BLOCK_RE.finditer(btext), start=1):
            backing.append(Backing(i, m.group(1).strip(), m.group(2).strip(), m.group(3).strip()))
            consumed += len(m.group(0).splitlines())
        nonblank = [ln for ln in btext.splitlines() if ln.strip()]
        if len(nonblank) != consumed:
            problems.append(("Backing", "not `none` and not a list of source/speaker/quote blocks"))

    verdicts = _parse_verdicts(sections.get("Verdicts", ""))

    references = []
    for ln in sections.get("References", "").splitlines():
        if not ln.strip():
            continue
        m = REFERENCE_RE.match(ln.strip())
        references.append((ln.strip(), Reference(*m.groups()) if m else None))

    return Entry(
        path=path,
        text=text,
        front=front,
        front_order=front_order,
        sections=sections,
        section_order=order,
        has_append=has_append,
        frozen=frozen,
        grounds=grounds,
        backing=backing,
        backing_none=backing_none,
        verdicts=verdicts,
        references=references,
        problems=problems,
    )


def derive_status(verdicts):
    """The status of the last legal verdict. Terminal statuses stop the walk; a verdict
    appended after one is malformed (validate reports it) and does not move the
    status — with the one exception that `refuted` or `non-comparable` may be followed by
    exactly one `superseded`, because reinstatement is supersession.
    Ledger: (L0006-status-is-derived-from-the-verdicts, cites-as-live)."""
    status, terminal, reinstated = "open", False, False
    for v in verdicts:
        if v.malformed or v.status not in STATUSES or v.status == "open":
            continue
        if terminal:
            if (
                status in ("refuted", "non-comparable")
                and v.status == "superseded"
                and not reinstated
            ):
                status, reinstated = "superseded", True
            continue
        status = v.status
        terminal = status in TERMINAL
    return status


def parse_timestamp(value):
    if not value or not TIMESTAMP_RE.match(value):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


# --- loading -------------------------------------------------------------------


# A git that blocks — a credential prompt on a submodule url, a pack it wants to recover —
# would otherwise hang `validate --cached`, `check`, `resolve` and `sha` with no way out,
# which in a pre-commit hook is a wedged commit. Generous, because a cold `git show` on a
# large pack is slow, not stuck.
GIT_TIMEOUT = 30


@dataclasses.dataclass(frozen=True)
class GitAnswer:
    """What a git command did, rather than only what it printed.

    `git()` returns None for a command that failed and for one that answered `no`, and a
    caller that reads None as a benign negative — not committed, not in the index,
    unchanged — turns a git that could not answer into an answer that a check passed.
    That is the one report this tool must never produce, so the exit status is kept and
    each caller says for itself which non-zero exits are answers (a revision that is
    simply not there) and which are git failing to answer at all
    (L0140-a-version-control-commands-exit-status-is-kept, cites-as-live).
    """

    code: int | None  # None when git never ran or never finished
    out: str = ""
    why: str = ""  # why it could not answer, in a form a message can carry

    @property
    def ok(self):
        return self.code == 0


# git's own "The Git Repository" environment, entire. Every variable in it answers the
# question "which repository, and where are its parts" — which is the question each git
# call in this package has already answered by naming the directory with `-C`. Left in
# place they override that silently, and silence is the failure mode that matters here.
# Measured on git 2.43.0 against a ledger whose entry a commit already holds: under
# `GIT_DIR`, `GIT_COMMON_DIR` or `GIT_OBJECT_DIRECTORY` naming any other repository,
# `sha --write` rewrote the frozen region of that committed entry and exited 0, and under
# `GIT_DIR` `validate` dropped both immutability failures with nothing said about a check
# it had not made. The scrub used to be one call's argument — the discovery walk's — and
# so it held for finding the repository and for nothing asked of it afterwards.
# (docs/audits/ARCH-AUDIT.md, QE12-2.)
GIT_REPOSITORY_ENV = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_COMMON_DIR",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES",
    "GIT_DISCOVERY_ACROSS_FILESYSTEM",
    "GIT_INDEX_FILE",
    "GIT_INDEX_VERSION",
    "GIT_DEFAULT_HASH",
    "GIT_DEFAULT_REF_FORMAT",
)
# Taken as a documented section rather than assembled from the three that were measured
# to bite: a variable that reroutes the repository is a false pass waiting for a git
# version that reads it, and there is nothing to weigh against dropping one this package
# never wants
# (L0141-the-repository-location-environment-is-scrubbed-on-every-call, cites-as-live).

GIT_PATHSPEC_ENV = (
    # A path written as a literal is asked about as the path it names, so none of these
    # is consulted on any call
    # (L0218-a-pathspec-means-the-path-it-names, cites-as-live).
    "GIT_LITERAL_PATHSPECS",
    "GIT_GLOB_PATHSPECS",
    "GIT_NOGLOB_PATHSPECS",
    "GIT_ICASE_PATHSPECS",
)
# A pathspec this package writes says which path it means, and these four rewrite that
# sentence after it is written. `GIT_LITERAL_PATHSPECS=1` is the one measured to bite: it
# takes `:(literal)` for the *name of a file* rather than for git's own way of saying "the
# text is a filename", so the two calls that use it — the enclosing-repository walk and
# freshness's history question — ask about a path nothing has ever been at and are
# answered, cleanly and at exit 0, that no commit touched it. Measured on git 2.43.0: with
# the variable exported, `validate` over a ledger an enclosing repository has committed
# went from exit 1 naming an immutable region to exit 0 with nothing said. The other three
# are dropped on the same account as the repository list above rather than because each was
# measured — a variable that decides what a pathspec means is a false pass waiting for a
# git version that reads it, and no caller here wants one.

GIT_NOISE_ENV = (
    "GIT_TRACE",
    "GIT_TRACE2",
    "GIT_TRACE2_EVENT",
    "GIT_TRACE2_PERF",
    "GIT_TRACE_PACKET",
    "GIT_TRACE_PACK_ACCESS",
    "GIT_TRACE_PERFORMANCE",
    "GIT_TRACE_SETUP",
    "GIT_TRACE_CURL",
)
# Dropped for the same reason and not for tidiness: each of these makes a command write
# diagnostics onto the streams this package reads, and an operator who exported one while
# debugging something else would have it arrive as though the command had said it.


def git_env(index=False):
    """The environment for a git call about the repository that call names.

    `index=True` keeps `GIT_INDEX_FILE`, and is for the callers whose subject *is* the
    index. Under a pre-commit hook git names the index it is building the commit in, and
    for a partial commit that is not `.git/index`: measured on git 2.43.0, a plain
    `git commit` gives the hook `GIT_INDEX_FILE=.git/index` and `git commit -- <path>`
    gives it `.git/next-index-<pid>.lock`, holding HEAD plus the named paths. Scrubbing it
    there would take the checkers the hook runs with `--cached` — all five of them — off
    the content being committed and onto content that is not, the same false pass as the
    rest of this list, pointed the other way. So the one
    question this package does ask of the environment is asked — by the callers whose
    subject is the index, under `--cached`, and by no others
    (L0142-the-index-variable-is-kept-only-where-the-index-is-the-subject, cites-as-live).
    """
    drop = set(GIT_REPOSITORY_ENV) | set(GIT_PATHSPEC_ENV) | set(GIT_NOISE_ENV)
    if index:
        drop.discard("GIT_INDEX_FILE")
    # `LC_ALL=C` last, over whatever the caller had. Everything this package learns from
    # version control it learns by parsing what a command printed, and a locale decides
    # what that print looks like; pinning it is what makes the same repository answer the
    # same way on two machines
    # (L0194-git-is-asked-in-one-language-and-told-not-to-trace, cites-as-live).
    return {k: v for k, v in os.environ.items() if k not in drop} | {"LC_ALL": "C"}


def git_call(repo, *args, env=None):
    """A git command in `repo`, as a GitAnswer. The environment is `git_env()`, because
    the call is about the directory it names and not about whatever `GIT_DIR` names;
    `env` replaces it, for the callers that read the index
    (L0141-the-repository-location-environment-is-scrubbed-on-every-call, cites-as-live).

    A command that does not answer within the timeout, and one that could not be run at
    all, both come back as a question git did not answer rather than as a negative or a
    hang: a checker wedged behind a subprocess is a pre-commit hook with no output, and a
    timeout read as `no` is the false pass this whole type exists to prevent
    (L0144-a-command-that-does-not-answer-in-time-is-an-unanswered-question,
    cites-as-live).
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args],
            env=git_env() if env is None else env,
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT,
            # Explicit, because `text=True` alone decodes with the locale's codec: under
            # LC_ALL=C an entry carrying the schema's own `·` separator would take the
            # frozen-region and append-only checks down with a UnicodeDecodeError.
            # (L0143-command-output-is-decoded-as-utf-8-rather-than-by-locale, cites-as-live)
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except subprocess.TimeoutExpired:
        return GitAnswer(None, "", f"git did not answer within {GIT_TIMEOUT}s")
    except OSError as exc:
        return GitAnswer(None, "", f"git could not be run ({exc.strerror or exc})")
    if out.returncode == 0:
        return GitAnswer(0, out.stdout)
    detail = (out.stderr or "").strip().splitlines()
    return GitAnswer(out.returncode, "", detail[-1] if detail else f"git exited {out.returncode}")


def git(repo, *args):
    """stdout of a git command in `repo`, or None on failure. For a caller to whom a
    failure and a `no` are the same thing; `git_call` is for every other caller."""
    answer = git_call(repo, *args)
    return answer.out if answer.ok else None


def _git_raw(repo, args, stdin=None, env=None):
    """(code, stdout bytes, why) for a git command in `repo`: `git_call` without the
    decoding, for the two readers below that answer for a whole ledger at once. `env` as
    `git_call` has it — `git_env()` unless the caller is reading the index."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args],
            input=stdin,
            env=git_env() if env is None else env,
            capture_output=True,
            timeout=GIT_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, b"", f"git did not answer within {GIT_TIMEOUT}s"
    except OSError as exc:
        return None, b"", f"git could not be run ({exc.strerror or exc})"
    if out.returncode == 0:
        return 0, out.stdout, ""
    detail = out.stderr.decode("utf-8", errors="replace").strip().splitlines()
    return out.returncode, b"", detail[-1] if detail else f"git exited {out.returncode}"


_COMMIT_RE = re.compile(rb"^[0-9a-f]{40}(?:[0-9a-f]{24})?(?: [0-9a-f]{40}(?:[0-9a-f]{24})?)*$")


@dataclasses.dataclass(frozen=True)
class GitHistory:
    """What one walk of the history says: which commits touched each path, newest
    first, and the parents of every commit it listed."""

    revisions: dict
    parents: dict


def git_history(repo, pathspec):
    """(history, why): the commits that touched each path under `pathspec`, as a
    `GitHistory` — `revisions` `{path: [commit, ...]}` newest first, `parents` `{commit:
    [parent, ...]}` — from one walk of the history, or `(None, why)` when git could not
    walk it.

    The parents are what the append-only check compares along. The walk lists every
    parent of a merge, so two commits next to each other in its order can be siblings
    that never saw each other's work; a comparison between them is a comparison of
    nothing, and a failure it produced would name the wrong commit. Each listed commit
    is compared with each of its own parents instead.

    One walk rather than one `git log -- <path>` per entry: each of those walks the whole
    commit graph, so a ledger of a thousand entries with a thousand commits behind it
    asked git to diff a million trees and `check` took five minutes. The walk here lists
    every commit the per-path log lists for a path, in the same order, and more: `-m` is
    a `--diff-merges` option, and any of those turns history simplification off, so this
    is a `--full-history` walk. It follows every parent of a merge and lists a merge
    under a file whenever the file differs from either parent — and it lists the commits
    on a line a resolution discarded, which the per-path log pruned because the merge
    was TREESAME to the other parent. A verdict that a branch committed and a merge
    resolution then left out is therefore compared here and was not before; the region
    above the APPEND marker is unaffected, because the creating commit is the oldest
    either way. `tests/test_history_batch.py` holds this as equality with
    `git log --full-history -m -- <path>`.

    No `--follow`, for the reason `check_history` gives; `--no-renames`, so a file git
    would pair with another is listed under its own name on both sides of the pairing.
    Paths come back NUL-terminated and unquoted, decoded the way the filesystem's own
    listing was, so a name is matched byte for byte and never against git's C-quoting.
    """
    code, data, why = _git_raw(
        repo, ["log", "-z", "--format=%H %P", "--name-only", "--no-renames", "-m", "--", pathspec]
    )
    if code != 0:
        return None, why
    revisions, parents = {}, {}
    commit = None
    for raw in data.split(b"\0"):
        token = raw.lstrip(b"\n")  # the first path after a commit carries the separator
        if not token:
            continue
        if _COMMIT_RE.match(token.rstrip(b" ")):  # `%H %P` of a root commit ends in a space
            commit, *above = token.decode("ascii").split()
            parents[commit] = above
            continue
        if commit is None:
            continue  # cannot happen: git prints the commit before its paths
        found = revisions.setdefault(os.fsdecode(token), [])
        if not found or found[-1] != commit:  # `-m` prints a merge once per parent
            found.append(commit)
    return GitHistory(revisions, parents), ""


def git_blobs(repo, specs, env=None):
    """(blobs, failures) for the object names in `specs` — `<commit>:<path>`, or `:<path>`
    for the index — read through one `git cat-file --batch`: `{spec: bytes}` for each that
    git produced, and `{spec: why}` for each it did not, so that a blob that could not be
    read is reported by the caller and never taken for a comparison that passed.

    Positional: cat-file answers in the order it was asked, and a name it cannot resolve
    is echoed back with a word (`missing`, `ambiguous`) rather than an object id. Output
    that ends before the last answer — git killed by the timeout, or dying on a pack it
    cannot open — leaves every unanswered name in `failures` with the reason git gave.
    """
    specs = list(specs)
    if not specs:
        return {}, {}
    code, data, why = _git_raw(
        repo,
        ["cat-file", "--batch"],
        stdin=b"".join(os.fsencode(s) + b"\n" for s in specs),
        env=env,
    )
    blobs, failures = {}, {}
    pos = 0
    for spec in specs:
        if code != 0:
            failures[spec] = why
            continue
        end = data.find(b"\n", pos)
        if end < 0:
            failures[spec] = "git stopped answering before it"
            continue
        header = data[pos:end].split(b" ")
        pos = end + 1
        if len(header) == 3 and header[2].isdigit():
            size = int(header[2])
            body = data[pos : pos + size]
            pos += size + 1  # the newline cat-file prints after every object
            if len(body) < size:
                failures[spec] = "git stopped answering partway through it"
            elif header[1] != b"blob":
                failures[spec] = f"it is a {header[1].decode('ascii', 'replace')}, not a file"
            else:
                blobs[spec] = body
        else:
            word = header[-1].decode("utf-8", errors="replace") if header else "unanswered"
            failures[spec] = f"git says it is {word}"
    return blobs, failures


def git_hash_object(repo, path, data, env=None):
    """The object id git stores `data` under for `path`, written into the object store,
    or None when git would not take it.

    `--path` rather than the bytes alone: git applies the attributes of the path it is
    told about, so a blob written here is the blob a checkout of that path would produce.
    Through `_git_raw` like every other call in this module, which is what puts the
    caller's environment on it rather than this process's.
    """
    code, out, _why = _git_raw(
        repo, ["hash-object", "-w", "--stdin", "--path", str(path)], stdin=data, env=env
    )
    return out.decode("utf-8").strip() if code == 0 else None


def blob_text(data):
    """Blob bytes the way `git show` hands them to a text-mode caller: decoded with
    replacement, then through universal newlines — which is also how `read_text` reads
    the working side, so the two compare as the same text. The byte comparison that
    `check_history` makes as well is made on the bytes themselves."""
    return data.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")


def git_available():
    """Whether a `git` binary is on PATH. `git()` swallows its absence and returns None,
    which the history checks read as `not yet committed` — so a caller that reports what
    it checked has to ask separately."""
    return shutil.which("git") is not None


def enclosing_repository(root, entries_dir):
    """(the repository whose history holds `entries_dir`, why git could not say). Both
    None when there is no such repository.

    `open_ledger` calls a project a repository when `<root>/.git` is there, so a ledger in
    a subdirectory of one — `--root <subdir>`, or a ledger vendored inside a larger
    project — reads as a ledger with no history at all, and "no history" is indexed to
    "nothing to check" everywhere it matters. Measured on such a ledger: `sha --write`
    rewrote the frozen region of an entry that repository had already committed and exited
    0, and `validate` then reported `0 failure(s)` over it — which is the whole of what
    L0007 says must not happen. (docs/audits/ARCH-AUDIT.md, finding 3.)

    Three things this asks that the first version of it did not, each measured as a defect
    of that version rather than imagined:

    **The question is not "is there a work tree above me".** It is "is there a *history*
    nobody read", and a directory that merely sits under a work tree, untracked, has none.
    The corpus stages its seeds through `tempfile`, so a `TMPDIR` inside any repository —
    a checkout under a dotfiles `$HOME`, a scratch directory in a project — took the
    corpus from 79/79 to 18/79 and the suite to 146 failures. `git log -1 -- <entries>` is
    the question, and it separates the untracked seed from the committed ledger cleanly.

    **The walk is the filesystem's, not git's.** `git rev-parse --show-toplevel` with
    `GIT_DIR` in the environment answers with the directory it was run in, so a ledger
    with no repository anywhere reported *itself* as the repository holding it. Looking
    for `.git` above the root asks nothing of the environment, needs no git process for a
    project that is simply not under version control, and is a strict ancestor by
    construction. A `.git` file counts: that is how a submodule and a linked work tree
    name their repository. **Every** `.git` above the root is asked, not the first: the
    nearest repository is often not the one that committed the ledger. The two git calls
    it does make used to pass a scrubbed environment as an argument here, alone in the
    package; `git_env()` is what every git call gets now, so they simply take the default.

    **A git that cannot answer is not a git answering no.** Returning None for a failed
    call put back the exact false pass this function exists to remove: with an enclosing
    repository git refuses to open — `detected dubious ownership` is the everyday one —
    `sha --write` rewrote a committed entry's frozen region and exited 0 again. The reason
    comes back, and the callers report it.

    Nothing here *adopts* that repository for the evidence pointers. Every evidence path
    is written relative to the ledger root and `git show <pin>:<path>` reads its path from
    the repository's top, so adopting one would mean rebasing every git path in the
    package against a different origin.
    """
    root, entries_dir = Path(root).resolve(), Path(entries_dir).resolve()
    for parent in root.parents:
        # Every `continue` below is a repository that has nothing to say about these
        # entries, and the walk goes on past it. Stopping at the first one instead was a
        # false negative of exactly the shape this function exists to catch: one
        # `git init` in a directory between the ledger and the repository that committed
        # it took `validate` from exit 1 to exit 0 and let `sha --write` rewrite a
        # committed frozen region. (docs/audits/ARCH-AUDIT.md, finding 3, QE12-1.)
        if not (parent / ".git").exists():
            continue
        if not entries_dir.is_relative_to(parent):
            # The entries are somewhere else entirely — the corpus runner stages seeds
            # into a scratch directory and points a Config at them — so this repository
            # could not be holding them, and asking it would be `git log` on a path
            # outside it.
            continue
        # A repository with no commits in it at all fails `git log` the way a repository
        # nobody can read does, and it is the ordinary state of a project being started
        # around a ledger. Separated here rather than collapsed into the reason string.
        head = git_call(parent, "rev-parse", "--verify", "--quiet", "HEAD")
        if head.code == 1:
            continue
        if not head.ok:
            return None, f"git cannot read the repository at {parent} ({head.why})"
        rel = os.path.relpath(entries_dir, parent).replace(os.sep, "/")
        answer = git_call(parent, "log", "-1", "--format=%H", "--", f":(literal){rel}")
        if not answer.ok:
            return None, f"git cannot read the repository at {parent} ({answer.why})"
        if answer.out.strip():
            return parent, None
        # No commit has ever touched these entries in it: untracked, ignored, or freshly
        # staged into a scratch directory. Nothing here was committed — but a repository
        # further up may still hold them, so this is not the end of the walk.
    return None, None


def git_problem(repo):
    """Why git cannot answer questions about `repo`, or None when it can.

    `git()` answers None for every failure and the history checks read None as `this entry
    is not committed yet`, so a git that is present but broken — a damaged object store, a
    checkout it refuses as dubious ownership, one that timed out — was quieter than a git
    that is missing: it dropped the frozen-region and append-only checks and said nothing.
    Asked once, with the cheapest command there is, so `skipped_checks()` can name it.
    """
    if not git_available():
        return "git is not on PATH"
    answer = git_call(repo, "rev-parse", "--git-dir")
    if answer.ok:
        return None
    if answer.code is None:  # never ran, or never finished; its own words are the reason
        return answer.why
    return f"git cannot read the repository ({answer.why})"


def index_problem(repo):
    """Why the git index cannot be read, or None when it can.

    `--cached` reads staged entries out of the index, and `git show :<path>` fails the
    same way for a path that is not staged as for an index no git can parse. Read as the
    first, a truncated index makes `validate --cached` — the installed pre-commit hook —
    report on the working tree while saying it read what was staged. Asked once, of the
    index itself, with a pathspec that matches nothing: the index is parsed in full and
    a repository with a hundred thousand files still prints nothing.
    """
    answer = git_call(repo, "ls-files", "--", ".git", env=git_env(index=True))
    return None if answer.ok else answer.why


def entries_dir_listing_error(entries_dir):
    """The error that stops us listing `entries_dir`, or None when it lists.

    The directory is listed, not asked about. `is_dir()` answers True for a directory
    whose read bit is off; `glob()` then swallows the EACCES that `scandir` raises and
    yields nothing at all, and the checker prints `0 entries … 0 failure(s)` over a ledger
    it never read — a pass for a check that did not happen, which is the one report this
    tool must never produce. A symlink loop reaches pathlib as an OSError or a
    RuntimeError depending on the interpreter, and neither is an answer either.
    """
    try:
        with os.scandir(entries_dir) as it:
            next(iter(it), None)
    except (OSError, RuntimeError) as exc:
        return exc
    return None


def list_entry_files(entries_dir):
    """The `*.md` paths under `entries_dir`, or a LedgerError naming why they cannot be
    listed. Listing is a separate failure from reading any one of them.

    `scandir` rather than `glob`, for the reason `entries_dir_listing_error` gives; a
    leading dot is excluded to match what `glob("*.md")` used to match.
    """
    try:
        with os.scandir(entries_dir) as it:
            return [
                Path(e.path) for e in it if e.name.endswith(".md") and not e.name.startswith(".")
            ]
    except (OSError, RuntimeError) as exc:
        raise LedgerError(
            f"{entries_dir}: cannot list the entries directory "
            f"({getattr(exc, 'strerror', None) or exc})"
        ) from exc


def index_entry_files(ledger):
    """(paths, why) for the `*.md` entries the index holds under `entries_dir`: the list a
    commit being built would carry, as absolute paths, or `(None, why)` when the index
    could not be asked.

    Which entries exist is a question about a tree, and under `--cached` the tree is the
    index. Globbing the working tree there was a false pass with the shape this package
    exists to refuse: an entry staged and then deleted from the tree is in the commit and
    was in no checker's list, so all five reported `0 failure(s)` over a ledger that was
    about to gain a broken entry — and with the only entry staged that way, `0 entries`
    (L0219-the-entries-under-cached-are-the-ones-the-index-holds, cites-as-fallen).

    What the caller does with this is use it INSTEAD OF the working tree's listing, not
    added to it. The union this replaced was justified here on the ground that checking an
    entry the commit will not carry "can only cost a report nobody needed", and that is
    measurably false: the union does not add a spare report, it supplies a citation
    target. Measured, with `docs/citer.md` citing entry X `cites-as-live` and X taken out
    of the index with `git rm --cached` and left in the tree — all five checkers report
    `2 entries` and `0 failure(s)` at exit 0, and a fresh clone of the commit that made
    holds one entry and fails `references` at exit 1 naming the citation
    (L0229-a-cached-run-checks-the-index-alone, cites-as-live).

    The listing is `index_tree`'s, not a pathspec's, because the entries directory itself
    can be a symlink. A pathspec filtered on the literal `ledger/entries` and git reports
    the real path, so every entry fell off the list: measured, a symlinked entries
    directory gave `resolve --cached` `0 entries` and `0 failure(s)` at exit 0 where the
    bare run read one, which is the report this whole package exists to refuse, restored by
    the very change that was meant to close it (qe ticket 45909368c43c4379, F1). What the
    expansion costs is a listing of the repository rather than of the ledger; what stays
    flat is the number of git processes, which is one, whatever either holds.

    Single-level and no dotfile, to match what the directory listing matches.
    """
    if not ledger.repo:
        return None, "the ledger has no repository of its own"
    rel = os.path.relpath(ledger.entries_dir, ledger.repo).replace(os.sep, "/")
    if rel == ".." or rel.startswith("../"):
        return None, f"{rel} is outside the repository at {ledger.repo}"
    reach, why = index_reach(ledger)
    if why:
        return None, why
    prefix = "" if rel == "." else rel + "/"
    # Keyed by the path, which is what `list_entry_files` lists: an alias inside the
    # directory is a second entry file to the bare run, and a cached run that silently
    # folded it into one would disagree with the run beside it about what the ledger holds.
    # Deduplication that IS owed happens a step earlier, where an unmerged path arrives once
    # per stage and one path is one file whatever the conflict — dropping that loaded a
    # conflicted entry three times and reported every failure in it three times
    # (qe ticket 45909368c43c4379, F4).
    paths = set()
    for name in reach:
        if not name.startswith(prefix):
            continue
        tail = name[len(prefix) :]
        if "/" in tail or not tail.endswith(".md") or tail.startswith("."):
            continue
        paths.add(Path(ledger.repo) / name)
    return sorted(paths), None


def load_entries(ledger, cached=False):
    """Every entry under entries_dir, sorted by filename. With `cached`, the entries are
    the ones the index holds — both which of them there are and what each one says — which
    is what a pre-commit hook wants to check."""
    entries = []
    indexed = None
    if cached:
        indexed, _why = index_entry_files(ledger)
        # A `why` here is the fallback `index_problem()` already reports through the guard,
        # so it is not reported a second time: the listing falls back to the working tree
        # so that a run whose index cannot be read still checks something, having said so.
    in_tree = []
    if isinstance(
        entries_dir_listing_error(ledger.entries_dir), (FileNotFoundError, NotADirectoryError)
    ):
        if indexed is None:
            return entries  # a ledger not created yet; `guard()` is what refuses to report
    else:
        in_tree = list_entry_files(ledger.entries_dir)
    # The index's listing alone, not added to the working tree's: the index is not a delta,
    # it holds every tracked path, so it is what the commit will carry
    # (L0229-a-cached-run-checks-the-index-alone, cites-as-live).
    paths = sorted(in_tree) if indexed is None else sorted(indexed)
    staged = {}
    if cached and ledger.repo:
        # One `cat-file --batch` for every entry rather than one `git show` each: the
        # pre-commit hook runs this over the whole ledger on every commit. A path that is
        # not in the index gets no blob and is read from the working tree, as before.
        rels = {path: os.path.relpath(path, ledger.repo) for path in paths}
        specs = index_specs(ledger, rels.values())
        blobs, failures = git_blobs(ledger.repo, specs.values(), env=git_env(index=True))
        for path, rel in rels.items():
            spec = specs[rel]
            if spec in blobs:
                staged[path] = blobs[spec]
                continue
            why = failures.get(spec, ABSENT_FROM_INDEX)
            if not blob_absent(why):
                # An entry git was asked about and did not answer for. Read from the tree
                # instead, this is a checker reporting on content no commit contains at
                # exit 0 — the report this whole package exists to refuse. There is no
                # per-entry channel to say it on, because the entry has not been parsed,
                # so it stops the run the way an unlistable entries directory does.
                raise LedgerError(f"{path}: could not be read from the index ({why})")
    for path in paths:
        data = staged.get(path)
        entries.append(parse_entry(path, None if data is None else blob_text(data)))
    return entries


def entries_for(ledger, *, cached, write):
    """The entries a checker run should hold, given what it was asked and whether it will
    write.

    `--write` appends to the working tree, so a run that will write decides from the
    working tree even when the comparison it makes is asked of the index. Deciding from the
    index means deciding from a tree that does not hold what the last run just appended:
    measured on both writers before this, three runs of `--write --cached` with no
    `git add` between them left three copies of one verdict, each run re-reading an index
    that never gained the verdict the run before had written. What the flag still decides
    is the artifact a verdict RECORDS, which is read where the comparison is made and is
    the whole reason to ask for the index
    (L0226-a-write-decides-from-the-tree-it-appends-to, cites-as-live).

    One function because the rule has four call sites — the two commands and the two
    writers' own fallbacks — and a rule written out four times is a rule three of them can
    drift from.
    """
    return load_entries(ledger, cached=cached and not write)


def by_id(entries):
    return {e.id: e for e in entries if e.id}


def load_registry(path, text=None):
    """sources.jsonl as {id: row}. A missing file is an empty registry; a malformed row
    is reported by resolve when something points at it.

    `text` is the registry as some other tree has it — the index, under `--cached` — and is
    read in place of the file when given."""
    rows = {}
    path = Path(path)
    if text is not None:
        return _registry_rows(text, path)
    if not os.path.lexists(path):
        return rows  # a ledger with no sources registered yet
    problem = file_problem(path, "the source registry")
    if problem is not None:
        raise LedgerError(f"{path}: {problem}")
    return _registry_rows(read_text_or_raise(path, "the source registry"), path)


def _registry_rows(text, path):
    """The rows of a registry's text, wherever the text came from. `path` names the file
    only so that a malformed line can be reported at a place a person can open."""
    rows = {}
    for lineno, ln in enumerate(text.splitlines(), 1):
        if not ln.strip():
            continue
        try:
            row = json.loads(ln)
        except json.JSONDecodeError as exc:
            raise LedgerError(f"{path}:{lineno}: not a JSON object ({exc.msg})") from exc
        if not isinstance(row, dict) or not row.get("id"):
            raise LedgerError(f"{path}:{lineno}: registry row has no `id`")
        rows[row["id"]] = row
    return rows


def source_bytes(row, ledger):
    """(text, problem). The bytes come from the row's `bytes` path (fixtures) or the
    cache keyed by sha256 (real sources); either way the hash must match the row."""
    if "bytes" in row:
        candidate = ledger.tree / row["bytes"]
    elif ledger.cache:
        candidate = ledger.cache / row["sha256"]
    else:
        return None, f"registry row {row['id']} names no bytes and there is no cache"
    problem = file_problem(candidate, f"bytes for {row['id']}")
    if problem is not None:
        where = ledger.config.relative(candidate)
        if problem.startswith("no "):
            return None, f"bytes for {row['id']} not found at {where}; the check cannot run"
        return None, f"{problem} at {where}; the check cannot run"
    data = candidate.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != row.get("sha256"):
        return None, (
            f"bytes for {row['id']} hash to {digest[:12]}…, registry says "
            f"{str(row.get('sha256'))[:12]}…; re-verify everything citing it"
        )
    try:
        return data.decode("utf-8"), None
    except UnicodeDecodeError:
        return None, f"bytes for {row['id']} are not UTF-8 text"


def read_artifact(path):
    """(text, unreachable) — the artifact as UTF-8 text, and why its bytes could not be
    reached at all.

    The distinction `read_document` collapses into one `problem` string, made here in one
    read because `freshness` has to act on it: bytes that are there and are not UTF-8 are
    an artifact that really did change and cannot be narrowed to a section, and bytes that
    cannot be reached are a comparison that did not happen. `file_problem` cannot draw
    that line — `os.stat` succeeds on a mode-000 file, which is the case that matters.

    One read, not two. Asking `read_document` and then reading the file again to classify
    the failure cost a second full pass over every drifted artifact — measured at +319 MB
    of peak resident memory on a 300 MB one — and left a race in between where the first
    read failed, the second succeeded, and the caller fell through to the answer this
    exists to replace. (docs/audits/ARCH-AUDIT.md finding 2, and finding 6, which is this one.)
    """
    try:
        return Path(path).read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        return None, None
    except OSError as exc:
        return None, f"cannot be read ({exc.strerror or exc})"


def unreachable_artifact(path):
    """Why the artifact's bytes cannot be reached at all, or None.

    One byte rather than the file: the caller — the branch for a pin that names no
    section — never wants the text, only whether a read is possible at all, and git has
    already told it the path differs. Safe to open only because the caller has established
    that `path` is a regular file first; on a FIFO this would block a pre-commit hook
    forever with no writer on the other end.
    """
    try:
        with open(path, "rb") as fh:
            fh.read(1)
    except OSError as exc:
        return f"cannot be read ({exc.strerror or exc})"
    return None


def staged_documents(ledger, paths):
    """{path: (text, problem)} for those of `paths` the git index has something to say
    about, read through one `cat-file --batch`. A path the index simply does not hold is
    absent from the answer and the caller reads it from the tree; a path git could not be
    asked about is present, with the problem, so that it is reported rather than read from
    the wrong tree.

    The documents a citation is read out of, as the commit will carry them. `references`
    checked the working tree whatever it was asked, so a citation staged against one status
    and corrected in the tree alone passed the hook and committed broken — the checker
    reported on text no commit contains
    (L0221-the-documents-a-cached-run-reads-are-the-staged-ones, cites-as-live).

    A path the index does not hold is absent from the answer and the caller reads it from
    the tree, which is the same fallback the entry loader makes: a document that is not
    staged is not being changed by this commit, and the tree's copy is what the commit will
    leave behind.
    """
    paths = list(paths)
    if not paths or not ledger.repo:
        return {}
    rels = {path: os.path.relpath(path, ledger.repo) for path in paths}
    specs = index_specs(ledger, rels.values())
    blobs, failures = git_blobs(ledger.repo, specs.values(), env=git_env(index=True))
    out = {}
    for path, rel in rels.items():
        spec = specs[rel]
        if spec in blobs:
            # Strictly, and reported the way the working-tree read reports it: a document
            # the index holds as bytes nobody can decode is an unreadable document there
            # too, and `blob_text` would hand back text with the real thing's shape.
            out[path] = _strict_text(blobs[spec])
            continue
        why = failures.get(spec, ABSENT_FROM_INDEX)
        if not blob_absent(why):
            out[path] = (None, f"could not be read from the index ({why})")
    return out


ABSENT_FROM_INDEX = "git says it is missing"


def blob_absent(why):
    """Whether `git_blobs` is saying the index does not hold this path, as against saying
    it could not answer.

    The difference is the whole of a `--cached` read's honesty and it was folded away: a
    caller that treats every failure as absence reads a `cat-file` that timed out, died on
    a pack it could not open, or was killed, as "not staged" — and then reads the working
    tree instead and reports a clean run. Measured with a git whose `cat-file` exits 128,
    `resolve --cached` went from exit 1 naming a staged withdrawal to `0 failure(s)` with
    nothing said. A question git did not answer is not a no
    (L0227-an-unanswered-index-read-is-not-an-absent-path, cites-as-live).
    """
    return why == ABSENT_FROM_INDEX


def _strict_text(data):
    """(text, problem) for blob bytes, decoded strictly and with the endings `read_text`
    would give. `blob_text` decodes with replacement, which is right where the subject is a
    comparison of two trees and wrong where the subject is whether a file is readable at
    all: it turns bytes no reader can read into text with the shape of the real thing."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return None, f"is not UTF-8 text (byte {exc.start}: {exc.reason})"
    return text.replace("\r\n", "\n").replace("\r", "\n"), None


def staged_blob(ledger, path):
    """(bytes, problem) for what the index holds at `path`. `(None, None)` when the index
    simply does not hold it.

    Bytes, not text, for the caller that has to tell "the index does not have this" from
    "the index has it and it is not UTF-8" — two answers `blob_text` folds into one,
    because it decodes with replacement.
    """
    if not ledger.repo:
        return None, None
    spec = index_spec(ledger, os.path.relpath(path, ledger.repo))
    blobs, failures = git_blobs(ledger.repo, [spec], env=git_env(index=True))
    if spec in blobs:
        return blobs[spec], None
    why = failures.get(spec, ABSENT_FROM_INDEX)
    return (None, None) if blob_absent(why) else (None, f"could not be read from the index ({why})")


def staged_text(ledger, path):
    """(text, problem) for what the index holds at `path`, decoded strictly.

    One path rather than a batch, for the reader whose subject is a single file the whole
    ledger rests on: the source registry
    (L0223-a-cached-run-reads-the-registry-the-commit-will-carry, cites-as-live).
    """
    data, problem = staged_blob(ledger, path)
    if problem is not None or data is None:
        return None, problem
    return _strict_text(data)


def read_document(path):
    """(text, problem). A document that cannot be read is not an empty document: the
    caller has to say so, because a citation nobody read is a citation nobody checked."""
    try:
        return Path(path).read_text(encoding="utf-8"), None
    except UnicodeDecodeError as exc:
        return None, f"is not UTF-8 text (byte {exc.start}: {exc.reason})"
    except OSError as exc:
        return None, f"cannot be read ({exc.strerror or exc})"
