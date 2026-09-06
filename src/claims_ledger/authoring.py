"""Writing an entry, not checking one.

Everything here is a convenience for an author: the next free id, a scaffolded entry
file, the recomputation of `verbatim_sha` after Scope or Backing is edited, and the
registration of a source together with the bytes a quotation is checked against.

Two rules the checkers enforce shape what this module will and will not do. The region
above the APPEND marker is immutable once committed, so `restamp` refuses to touch an
entry that git already has; and a registry row without its bytes is a check that cannot
run, so registering a source stores the bytes in the same call that writes the row.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path

from .config import leaves_root
from .schema import (
    APPEND,
    ID_RE,
    PREFIX_RE,
    fingerprint,
    git,
    git_problem,
    load_entries,
    load_registry,
    parse_entry,
    read_text_exact,
    write_bytes_atomically,
    write_text_atomically,
)

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# POSIX NAME_MAX. A slug long enough to overrun it used to reach write_text() and come
# back as `unexpected OSError: File name too long`, which is a bug report asked of a user
# who mistyped a slug.
NAME_MAX = 255

TEMPLATE = """---
id: {id}
kind: {kind}
stated: {stated}
author: {author}
grade: {grade}
{extra}supersedes: {supersedes}
verbatim_sha: {sha}
---

## Assertion

{assertion}

## Scope

metric: {metric}
cohort: {cohort}
condition: {condition}

## Grounds

{grounds}

## Warrant

{warrant}

## Backing

{backing}

{append}

## Verdicts

## References
"""

PLACEHOLDER_ASSERTION = "TODO: the claim, in this project's words. No quotation marks."
PLACEHOLDER_WARRANT = "TODO: the rule by which the grounds support the assertion."
PLACEHOLDER_GROUNDS = "- TODO: one typed pointer per line"
TODO_SCOPE = "TODO"


class AuthoringError(Exception):
    """Something an author has to fix before the file can be written."""


def next_id(entries, archived_prefixes=()):
    """The next free id in the highest series in use, rolling over to the next letter
    when a series is exhausted and skipping any quarantined prefix."""
    used = {}
    for e in entries:
        m = PREFIX_RE.match(e.id or e.path.stem)
        if m:
            letter, digits = m.group(1)[0], m.group(1)[1:]
            used.setdefault(letter, set()).add(int(digits))
    letters = [chr(c) for c in range(ord("A"), ord("Z") + 1) if chr(c) not in archived_prefixes]
    if not letters:
        raise AuthoringError("every series letter is quarantined")
    active = max((letter for letter in used if letter in letters), default=letters[0])
    number = max(used.get(active, {0})) + 1
    if number > 9999:
        remaining = [letter for letter in letters if letter > active]
        if not remaining:
            raise AuthoringError(f"series {active} is exhausted and there is no letter after it")
        active, number = remaining[0], 1
    return f"{active}{number:04d}"


def now_stamp():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def render_entry(
    ident,
    slug,
    kind="claim",
    grade="measured",
    author="main",
    stated=None,
    supersedes="none",
    credence=None,
    resolves_when=None,
    assertion=PLACEHOLDER_ASSERTION,
    scope=None,
    grounds=None,
    warrant=PLACEHOLDER_WARRANT,
    backing="none",
):
    """The text of an entry, with `verbatim_sha` computed from the Scope and Backing it
    is written with. A scaffolded entry is a draft: the checkers will have plenty to say
    about its placeholders, which is the point of writing them as placeholders."""
    scope = scope or {}
    metric = scope.get("metric", TODO_SCOPE)
    cohort = scope.get("cohort", TODO_SCOPE)
    condition = scope.get("condition", TODO_SCOPE)
    scope_text = f"metric: {metric}\ncohort: {cohort}\ncondition: {condition}"
    extra = ""
    if kind in ("prediction", "hypothesis"):
        extra = f"credence: {credence if credence is not None else 0.5}\n"
        extra += f"resolves_when: {resolves_when or 'TODO: what settles this'}\n"
    text = TEMPLATE.format(
        id=f"{ident}-{slug}",
        kind=kind,
        stated=stated or now_stamp(),
        author=author,
        grade=grade,
        extra=extra,
        supersedes=supersedes,
        sha=fingerprint(scope_text, []),
        assertion=assertion,
        metric=metric,
        cohort=cohort,
        condition=condition,
        grounds="\n".join(grounds) if grounds else PLACEHOLDER_GROUNDS,
        warrant=warrant,
        backing=backing,
        append=APPEND,
    )
    return text


def create_entry(ledger, slug, **kwargs):
    """Write a scaffolded entry and return its path."""
    if not SLUG_RE.match(slug or ""):
        raise AuthoringError(f"`{slug}` is not a lowercase-and-hyphens slug")
    entries = load_entries(ledger)
    ident = kwargs.pop("ident", None) or next_id(entries, ledger.config.archived_prefixes)
    name = f"{ident}-{slug}"
    if not ID_RE.match(name):
        raise AuthoringError(f"`{name}` is not <letter><four digits>-<slug>")
    filename = f"{name}.md"
    if len(filename.encode("utf-8")) > NAME_MAX:
        raise AuthoringError(
            f"`{slug[:32]}…` is too long: the entry would be named {filename[:38]}…, "
            f"{len(filename.encode('utf-8'))} bytes, over the {NAME_MAX} a filename holds"
        )
    path = ledger.entries_dir / filename
    try:
        # `exists()` is inside the funnel, not before it: it re-raises ENAMETOOLONG, which
        # a name that fits NAME_MAX can still provoke by overrunning PATH_MAX under a deep
        # root — an `unexpected OSError` asked of someone who chose a long slug.
        if path.exists():
            raise AuthoringError(f"{path} already exists")
        path.parent.mkdir(parents=True, exist_ok=True)
        write_text_atomically(path, render_entry(ident, slug, **kwargs))
    except OSError as exc:
        raise AuthoringError(f"cannot write {path} ({exc.strerror or exc})") from exc
    return path


def refuse_to_write_outside_the_root(ledger, path):
    """A write is refused when the file it lands on is not under the project root.

    `confined()` establishes this for the paths a configuration names; an entry file is
    the other way in. A clone carries `ledger/entries/A0001-x.md -> ../../../elsewhere` as
    readily as it carries a `claims-ledger.toml`, and following one on `sha --write` or
    `propagate --write` rewrites a file the project does not contain. Reads are left
    alone: an entry symlinked in from outside is read normally, and only the write is
    the thing this package promises not to do.
    """
    outside = leaves_root(ledger.config.root, path)
    if outside is not None:
        raise AuthoringError(
            f"{path} leads to {outside}, outside the project root {ledger.config.root}; "
            "nothing is written through a link that leaves the project"
        )


def computed_sha(path):
    return parse_entry(Path(path)).computed_sha()


def is_committed(repo, path):
    """(whether git already holds this file at HEAD, why it could not be asked).

    An entry that is committed has an immutable frozen region, and rewriting its
    fingerprint there is not an edit the checkers will forgive. `git()` answers None for
    a file git does not have and for a git that could not be run, and read as the first,
    a `sha --write` with no git on PATH rewrote the frozen region of a committed entry,
    exited 0 and said nothing. The answer is None when git could not be asked, which is
    not a `no`.
    """
    if not repo:
        return False, None  # no repository: nothing is committed and nothing was skipped
    try:
        rel = Path(path).resolve().relative_to(Path(repo).resolve())
    except ValueError:
        return False, None  # outside the repository: git has nothing to say about it
    if (problem := git_problem(repo)) is not None:
        return None, problem
    return git(repo, "cat-file", "-e", f"HEAD:{rel}") is not None, None


def restamp(ledger, path, write=False, force=False):
    """(declared, computed, changed). With `write`, the declared value is replaced by
    the computed one — refused on an entry git already has, unless `force`."""
    path = Path(path)
    entry = parse_entry(path)
    declared = entry.front.get("verbatim_sha", "")
    computed = entry.computed_sha()
    if declared == computed or not write:
        return declared, computed, False
    committed, unasked = is_committed(ledger.repo, path)
    if unasked is not None and not force:
        raise AuthoringError(
            f"{unasked}, so whether git already has {ledger.config.relative(path)} could not "
            "be established. The region above the APPEND marker is immutable once the entry "
            "is committed, and this run has no way to find out whether it is; nothing was "
            "written. Pass --force to write anyway."
        )
    if committed and not force:
        raise AuthoringError(
            f"{ledger.config.relative(path)} is committed: the region above the APPEND marker "
            "is immutable, and a new fingerprint there is a new entry. Supersede it, or pass "
            "--force if the commit is not yet pushed and you are fixing it in place."
        )
    # Read and written with the file's own line endings: `sha --write` replaces one
    # line, and every other byte of the entry — including the ones that say how its lines
    # end — is none of its business. A CRLF entry rewritten as LF is a rewrite of an
    # immutable frozen region that no checker used to be able to see.
    text = read_text_exact(path)
    new, n = re.subn(
        # The trailing `\r` of a CRLF line is looked at and left alone.
        rf"^verbatim_sha: {re.escape(declared)}(?=\r?$)",
        f"verbatim_sha: {computed}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if not n:
        raise AuthoringError(f"no `verbatim_sha: {declared}` line to replace in {path}")
    refuse_to_write_outside_the_root(ledger, path)
    try:
        write_text_atomically(path, new)
    except OSError as exc:
        raise AuthoringError(f"cannot write {path} ({exc.strerror or exc})") from exc
    return declared, computed, True


def register_source(
    ledger,
    source_id,
    bytes_path,
    source_type,
    citation,
    authors=None,
    speaker=None,
    retrieved=None,
    url=None,
    extraction=None,
    keep_path=False,
):
    """Append a registry row and put the bytes where the resolver will look for them.

    With `keep_path` the row names the file (a committed fixture); otherwise the bytes
    are copied into the cache under their sha256, which is what a real source gets:
    the row is committed and the bytes are not.
    """
    bytes_path = Path(bytes_path)
    if not bytes_path.is_file():
        raise AuthoringError(f"no file at {bytes_path}")
    # Checked before anything is written, and before the append that would otherwise meet
    # it: open("a") on a FIFO with no reader blocks forever, which in a hook is a wedged
    # commit with no output, and a directory there is an IsADirectoryError asking the user
    # to file a bug. The reads already refuse a registry that is not a regular file.
    if ledger.registry.exists() and not ledger.registry.is_file():
        raise AuthoringError(
            f"{ledger.config.relative(ledger.registry)} is not a regular file; "
            "the source registry is a JSON-lines file this command appends to"
        )
    rows = load_registry(ledger.registry)
    if source_id in rows:
        raise AuthoringError(f"source id `{source_id}` is already registered")
    data = bytes_path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AuthoringError(f"{bytes_path} is not UTF-8 text; quotations resolve in text") from exc

    row = {"id": source_id, "type": source_type}
    if authors:
        row["authors"] = list(authors)
    if speaker:
        row["speaker"] = speaker
    row["citation"] = citation
    row["retrieved"] = retrieved or datetime.now().astimezone().date().isoformat()
    if url:
        row["url"] = url
    if extraction:
        row["extraction"] = extraction
    row["sha256"] = digest
    if keep_path:
        row["bytes"] = ledger.config.relative(bytes_path)
        stored = bytes_path
    else:
        if not ledger.cache:
            raise AuthoringError("this ledger has no cache; register with --keep-path instead")
        stored = ledger.cache / digest
        try:
            ledger.cache.mkdir(parents=True, exist_ok=True)
            # The cache is content-addressed, so a file already under this name should be
            # these bytes — but an interrupted `source add` leaves one that is not, and
            # trusting the name meant the retry exited 0 over bytes it never wrote and
            # wrote a row whose sha256 described nothing on disk. The bytes are checked,
            # and the copy goes through a temporary name so a second interruption cannot
            # leave a third state.
            if not stored.exists() or hashlib.sha256(stored.read_bytes()).hexdigest() != digest:
                write_bytes_atomically(stored, data)
        except OSError as exc:
            raise AuthoringError(
                f"cannot store the bytes at {ledger.config.relative(stored)} "
                f"({exc.strerror or exc})"
            ) from exc

    append_registry_row(ledger, row)
    return row, stored


def append_registry_row(ledger, row):
    """One JSON line onto `sources.jsonl`, as a line.

    The registry is JSON lines, and a line needs a newline before it. Appended without
    one — after an editor, a script, or this command's own interrupted write left the
    file without a final newline — the new row was glued onto the previous one, both were
    destroyed, every later command exited 2 with `not a JSON object`, and the run that
    did it printed `registered …` and exited 0.

    A write that fails partway is undone rather than left: the file is put back to the
    length it had, so a registry this command could not extend is still a registry. A
    read-only ledger directory is an ordinary condition — a shared checkout, a directory
    owned by someone else — and not one to ask for a bug report over.
    """
    addition = json.dumps(row, ensure_ascii=False) + "\n"
    try:
        ledger.registry.parent.mkdir(parents=True, exist_ok=True)
        size = ledger.registry.stat().st_size if ledger.registry.exists() else 0
        if size and not _ends_in_a_newline(ledger.registry):
            addition = "\n" + addition
        try:
            with ledger.registry.open("a", encoding="utf-8") as fh:
                fh.write(addition)
        except OSError:
            with contextlib.suppress(OSError), ledger.registry.open("r+b") as fh:
                fh.truncate(size)
            raise
    except OSError as exc:
        raise AuthoringError(
            f"cannot append to {ledger.config.relative(ledger.registry)} ({exc.strerror or exc})"
        ) from exc


def _ends_in_a_newline(path):
    """The last byte of a non-empty file, read as one byte rather than as the whole
    registry: a project with thousands of sources appends to this file every time."""
    with path.open("rb") as fh:
        fh.seek(-1, os.SEEK_END)
        return fh.read(1) == b"\n"
