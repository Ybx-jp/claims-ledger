"""The ledger entry as the four checkers read it.

One parser, one normalization, one fingerprint, one status derivation, shared by
validate, resolve, references and propagate so that no two checkers can disagree about
what an entry says. The schema itself is stated in full in docs/SCHEMA.md, which an
installed copy does not carry and the repository has at
https://github.com/Ybx-jp/claims-ledger/blob/main/docs/SCHEMA.md. It is restated in
corpus/README.md (the parts the red-team seeds depend on), and proven by corpus/run.py;
nothing here is trusted beyond what that corpus exercises.

Nothing outside the standard library is imported, so the checkers run from a plain
`python3` in a pre-commit hook.
"""

from __future__ import annotations

import dataclasses
import fnmatch
import glob
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import unicodedata
from datetime import datetime
from pathlib import Path, PurePath

from .config import Config, default_config, load_config


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
# Which target statuses each citation act is legal against.
ACT_ALLOWS = {
    "cites-as-live": {"open", "corroborated"},
    "cites-as-contested": {"contested"},
    "challenges": {"open", "corroborated", "contested"},
    "cites-as-fallen": set(STATUSES),
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
# A plain decimal number, in ASCII digits. `float()` is wider than the schema: it accepts
# any Unicode decimal digit, so a credence written in Arabic-Indic numerals would pass as
# an ordinary 0.5, and it accepts `nan` and digit-grouping underscores as well.
DECIMAL_RE = re.compile(r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$")
HEADING_RE = re.compile(r"^## (.+?)\s*$", re.MULTILINE)
VERDICT_HEAD_RE = re.compile(r"^- (\S+) · (\S+) · grade: (\S+) · author: (\S+)$")
BACKING_BLOCK_RE = re.compile(r"^- source: (.*)\n\s+speaker: (.*)\n\s+quote: (.*)$", re.MULTILINE)
REFERENCE_RE = re.compile(r"^- (\S+) · (standing|record) · (\S+)$")
# A citation in a document: `(A0007-slug, cites-as-live)`.
CITATION_RE = re.compile(r"\(([A-Z][0-9]{3,}(?:-[a-z0-9-]+)?),\s*(" + "|".join(ACTS) + r")\)")

ELISIONS = ("[…]", "[...]")
QUOTE_MARKS = '"“”„«»'


def archived_id_re(config):
    """An archived id anywhere in a document is a quarantine breach by prefix alone.
    None when the project quarantines no series."""
    if not config.archived_prefixes:
        return None
    return re.compile(r"\b[" + "".join(config.archived_prefixes) + r"]\d{3}\b")


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
        (os.path.relpath(d, config.root), f"{problem}; the documents under it were not checked")
        for d, problem in sorted(unlistable_document_dirs(config).items())
    ]
    docs, seen = [], {}
    for path in sorted(set(paths)):
        norm = path.replace(os.sep, "/")
        if any(x in norm for x in config.document_excludes):
            continue
        if os.path.commonpath([os.path.realpath(path), os.path.realpath(config.ledger_dir)]) == str(
            os.path.realpath(config.ledger_dir)
        ):
            continue  # the ledger does not cite itself
        rel = os.path.relpath(path, config.root)
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


def open_ledger(root=None, config_path=None, config=None):
    """The project's ledger: its configuration, the documents that may cite it, and the
    git repository its history checks read."""
    config = config or load_config(root=root, config_path=config_path)
    repo = config.root if (config.root / ".git").exists() else None
    docs, unreadable = tree_documents(config)
    return Ledger(config=config, docs=docs, repo=repo, unreadable_docs=unreadable)


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
    Backing block (`source | speaker | quote`), blocks sorted. Grounds are excluded."""
    scope = [normalize(ln) for ln in scope_text.splitlines() if ln.strip()]
    lines = sorted(
        f"{normalize(s)} | {normalize(sp)} | {normalize(q)}" for s, sp, q in backing_blocks
    )
    payload = "\n".join(scope) + "\n\n" + "\n".join(lines)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# --- pointers ------------------------------------------------------------------


@dataclasses.dataclass
class Pointer:
    type: str
    raw: str
    target: str = ""  # path, entry id, registry id
    section: str = ""  # evidence pointer § "section"
    pin: str = ""  # evidence pointer @commit
    act: str = ""  # entry: · act
    locator: str = ""  # source: · locator
    sectioned: bool = False  # the pointer was written in the § "section" form
    fields: dict = dataclasses.field(default_factory=dict)  # search: key=value


# Evidence pointers are named by the project (`lab:`, `experiment:`, `run:`), so the
# grammar is generic and config.py says which names are legal and which take a section.
SECTIONED_RE = re.compile(r'^([a-z][a-z0-9_-]*): (\S+) § "([^"]+)" @(\S+)$')
ARTIFACT_RE = re.compile(r"^([a-z][a-z0-9_-]*): (\S+) @(\S+)$")
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
            pin=m.group(4),
            sectioned=True,
        )
    if (m := ARTIFACT_RE.match(raw)) and m.group(1) not in RESERVED:
        return Pointer(m.group(1), raw, target=m.group(2), pin=m.group(3))
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
    order, sections = [], {}
    matches = list(HEADING_RE.finditer(body))
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
            fm = re.match(r"^\s+(evidence|note): (.*)$", ln.rstrip())
            if not fm:
                v.malformed = v.malformed or f"unrecognized line {ln.strip()!r}"
                continue
            setattr(v, fm.group(1), fm.group(2).strip())
        verdicts.append(v)
    return verdicts


def file_problem(path, what):
    """Why `path` is not a regular file this tool can read, or None when it is one.

    `os.stat` rather than `Path.is_file()`, for two reasons. is_file() answers False for
    everything from a FIFO to a permission error, and which of them it was is the
    difference between a message someone can act on and `unexpected PermissionError`. And
    it answers differently on different interpreters — with the execute bit off a
    directory, 3.12 lets the EACCES out of is_file() and 3.13 swallows it — while the
    syscall underneath says the same thing everywhere.
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
    thing to report, not a traceback."""
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


def parse_entry(path, text=None):
    path = Path(path)
    if text is None:
        text = read_text_or_raise(path, "entry")
    problems = []
    front, front_order = {}, []
    body = text
    if text.startswith("---\n") and "\n---\n" in text[4:]:
        head, body = text[4:].split("\n---\n", 1)
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
    exactly one `superseded`, because reinstatement is supersession."""
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


def git(repo, *args, check=False):
    """stdout of a git command in `repo`, or None on failure."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT,
            # Explicit, because `text=True` alone decodes with the locale's codec: under
            # LC_ALL=C an entry carrying the schema's own `·` separator would take the
            # frozen-region and append-only checks down with a UnicodeDecodeError.
            encoding="utf-8",
            errors="replace",
            check=check,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    return out.stdout if out.returncode == 0 else None


def git_available():
    """Whether a `git` binary is on PATH. `git()` swallows its absence and returns None,
    which the history checks read as `not yet committed` — so a caller that reports what
    it checked has to ask separately."""
    return shutil.which("git") is not None


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
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=GIT_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return f"git did not answer within {GIT_TIMEOUT}s"
    except OSError as exc:
        return f"git could not be run ({exc.strerror or exc})"
    if out.returncode != 0:
        detail = (out.stderr or "").strip().splitlines()
        why = detail[-1] if detail else f"exit {out.returncode}"
        return f"git cannot read the repository ({why})"
    return None


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


def load_entries(ledger, cached=False):
    """Every entry under entries_dir, sorted by filename. With `cached`, an entry that is
    in the git index is read from the index instead of the working tree, which is what a
    pre-commit hook wants to check."""
    entries = []
    if isinstance(
        entries_dir_listing_error(ledger.entries_dir), (FileNotFoundError, NotADirectoryError)
    ):
        return entries  # a ledger not created yet; `guard()` is what refuses to report
    for path in sorted(list_entry_files(ledger.entries_dir)):
        text = None
        if cached and ledger.repo:
            rel = os.path.relpath(path, ledger.repo)
            text = git(ledger.repo, "show", f":{rel}")
        entries.append(parse_entry(path, text))
    return entries


def by_id(entries):
    return {e.id: e for e in entries if e.id}


def load_registry(path):
    """sources.jsonl as {id: row}. A missing file is an empty registry; a malformed row
    is reported by resolve when something points at it."""
    rows = {}
    path = Path(path)
    if not os.path.lexists(path):
        return rows  # a ledger with no sources registered yet
    problem = file_problem(path, "the source registry")
    if problem is not None:
        raise LedgerError(f"{path}: {problem}")
    for lineno, ln in enumerate(read_text_or_raise(path, "the source registry").splitlines(), 1):
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


def read_document(path):
    """(text, problem). A document that cannot be read is not an empty document: the
    caller has to say so, because a citation nobody read is a citation nobody checked."""
    try:
        return Path(path).read_text(encoding="utf-8"), None
    except UnicodeDecodeError as exc:
        return None, f"is not UTF-8 text (byte {exc.start}: {exc.reason})"
    except OSError as exc:
        return None, f"cannot be read ({exc.strerror or exc})"
