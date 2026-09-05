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

import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

from .schema import (
    APPEND,
    ID_RE,
    PREFIX_RE,
    fingerprint,
    git,
    load_entries,
    load_registry,
    parse_entry,
)

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

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
    path = ledger.entries_dir / f"{name}.md"
    if path.exists():
        raise AuthoringError(f"{path} already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_entry(ident, slug, **kwargs), encoding="utf-8")
    return path


def computed_sha(path):
    return parse_entry(Path(path)).computed_sha()


def is_committed(repo, path):
    """Whether git already holds this file at HEAD. An entry that is committed has an
    immutable frozen region, and rewriting its fingerprint there is not an edit the
    checkers will forgive."""
    if not repo:
        return False
    try:
        rel = Path(path).resolve().relative_to(Path(repo).resolve())
    except ValueError:
        return False  # outside the repository: git has nothing to say about it
    return git(repo, "cat-file", "-e", f"HEAD:{rel}") is not None


def restamp(ledger, path, write=False, force=False):
    """(declared, computed, changed). With `write`, the declared value is replaced by
    the computed one — refused on an entry git already has, unless `force`."""
    path = Path(path)
    entry = parse_entry(path)
    declared = entry.front.get("verbatim_sha", "")
    computed = entry.computed_sha()
    if declared == computed or not write:
        return declared, computed, False
    if is_committed(ledger.repo, path) and not force:
        raise AuthoringError(
            f"{ledger.config.relative(path)} is committed: the region above the APPEND marker "
            "is immutable, and a new fingerprint there is a new entry. Supersede it, or pass "
            "--force if the commit is not yet pushed and you are fixing it in place."
        )
    text = path.read_text(encoding="utf-8")
    new, n = re.subn(
        rf"^verbatim_sha: {re.escape(declared)}$",
        f"verbatim_sha: {computed}",
        text,
        count=1,
        flags=re.M,
    )
    if not n:
        raise AuthoringError(f"no `verbatim_sha: {declared}` line to replace in {path}")
    path.write_text(new, encoding="utf-8")
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
        ledger.cache.mkdir(parents=True, exist_ok=True)
        stored = ledger.cache / digest
        if not stored.exists():
            shutil.copyfile(bytes_path, stored)

    ledger.registry.parent.mkdir(parents=True, exist_ok=True)
    with ledger.registry.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row, stored
