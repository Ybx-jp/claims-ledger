"""Where the ledger is and what its local vocabulary is.

Everything a project can legitimately name differently lives here: where the entries
sit, which documents may cite them, what an evidence pointer is called, which id
prefixes are quarantined, and which authors may write a verdict. The schema itself —
grades, kinds, statuses, citation acts, the fingerprint, the immutability rules — is not
configurable, because those are the claims model rather than a project's naming.

A project declares its configuration in `claims-ledger.toml` at the project root, or in
a `[tool.claims-ledger]` table in `pyproject.toml`. With neither, the defaults below
apply and the ledger is expected at `<root>/ledger`.
"""

from __future__ import annotations

import dataclasses
import tomllib
from pathlib import Path

CONFIG_FILENAMES = ("claims-ledger.toml", ".claims-ledger.toml")
PYPROJECT = "pyproject.toml"
TABLE = "claims-ledger"

# Pointer type names the schema reserves for itself; a project cannot use one of these
# as the name of an evidence type.
RESERVED_POINTER_TYPES = ("entry", "source", "search", "defect")

DEFAULT_DOCUMENTS = ("*.md", "docs/*.md")
DEFAULT_DOCUMENT_EXCLUDES = ()
DEFAULT_EVIDENCE_SECTIONED = ("lab",)
DEFAULT_EVIDENCE_PLAIN = ("experiment",)
DEFAULT_VERDICT_AUTHORS = ("main", "propagation")
DEFAULT_PROPAGATION_AUTHOR = "propagation"
DEFAULT_ROSTER = "ROSTER.md"


class ConfigError(Exception):
    """A configuration file that cannot be honoured. Raised rather than defaulted: a
    checker that silently ran under a configuration nobody wrote proves nothing."""


@dataclasses.dataclass(frozen=True)
class Config:
    """A project's ledger configuration, with every path resolved against `root`."""

    root: Path
    ledger_dir: Path
    entries_dir: Path
    registry: Path
    cache: Path | None
    documents: tuple = DEFAULT_DOCUMENTS
    document_excludes: tuple = DEFAULT_DOCUMENT_EXCLUDES
    roster: str = DEFAULT_ROSTER
    archived_prefixes: tuple = ()
    evidence_sectioned: tuple = DEFAULT_EVIDENCE_SECTIONED
    evidence_plain: tuple = DEFAULT_EVIDENCE_PLAIN
    verdict_authors: tuple = DEFAULT_VERDICT_AUTHORS
    propagation_author: str = DEFAULT_PROPAGATION_AUTHOR
    source: Path | None = None  # the file these values were read from, when there was one

    @property
    def evidence_types(self):
        """Pointer type names that name an artifact — the ones a `measured` grade
        requires and an `asserted` grade forbids."""
        return tuple(self.evidence_sectioned) + tuple(self.evidence_plain)

    @property
    def ground_types(self):
        return (*self.evidence_types, "entry", "source", "search")

    def is_sectioned(self, type_name):
        return type_name in self.evidence_sectioned

    def relative(self, path):
        """`path` as the project sees it, for a message a reader has to act on."""
        try:
            return str(Path(path).resolve().relative_to(self.root.resolve()))
        except ValueError:
            return str(path)


def default_config(root):
    """The configuration of a project that has not written one down."""
    root = Path(root).resolve()
    ledger = root / "ledger"
    return Config(
        root=root,
        ledger_dir=ledger,
        entries_dir=ledger / "entries",
        registry=ledger / "sources.jsonl",
        cache=ledger / "cache",
    )


def find_config_file(start):
    """The nearest configuration file at or above `start`, or None. A `pyproject.toml`
    counts only when it carries a `[tool.claims-ledger]` table, so a package that merely
    depends on this one is not mistaken for the project root."""
    start = Path(start).resolve()
    for directory in (start, *start.parents):
        for name in CONFIG_FILENAMES:
            if (directory / name).is_file():
                return directory / name
        candidate = directory / PYPROJECT
        if candidate.is_file() and _pyproject_table(candidate) is not None:
            return candidate
    return None


def _pyproject_table(path):
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"{path}: {exc}") from exc
    return data.get("tool", {}).get(TABLE)


def _read_table(path):
    path = Path(path)
    if path.name == PYPROJECT:
        table = _pyproject_table(path)
        if table is None:
            raise ConfigError(f"{path} has no [tool.{TABLE}] table")
        return table
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"{path}: {exc}") from exc
    # A standalone file may use the bare keys or nest them under [tool.claims-ledger],
    # so a table lifted out of a pyproject.toml keeps working when it is moved.
    return data.get("tool", {}).get(TABLE, data)


KEYS = {
    "ledger": str,
    "entries": str,
    "registry": str,
    "cache": (str, type(None)),
    "documents": list,
    "document-excludes": list,
    "roster": str,
    "archived-prefixes": list,
    "evidence-sectioned": list,
    "evidence-plain": list,
    "verdict-authors": list,
    "propagation-author": str,
}


def from_table(table, root, source=None):
    """A Config from a parsed table. Unknown keys are an error, not a silent no-op: a
    misspelled key that changes nothing is how a project ends up unchecked."""
    unknown = sorted(set(table) - set(KEYS))
    if unknown:
        raise ConfigError(f"unknown key(s) {', '.join(unknown)}; known keys are {sorted(KEYS)}")
    for key, want in KEYS.items():
        if key in table and not isinstance(table[key], want):
            names = want if isinstance(want, tuple) else (want,)
            raise ConfigError(
                f"{key} is {type(table[key]).__name__}, expected "
                f"{' or '.join(t.__name__ for t in names)}"
            )

    root = Path(root).resolve()
    ledger = root / table.get("ledger", "ledger")
    cache = table.get("cache", "cache")
    sectioned = tuple(table.get("evidence-sectioned", DEFAULT_EVIDENCE_SECTIONED))
    plain = tuple(table.get("evidence-plain", DEFAULT_EVIDENCE_PLAIN))
    authors = tuple(table.get("verdict-authors", DEFAULT_VERDICT_AUTHORS))
    propagation = table.get("propagation-author", DEFAULT_PROPAGATION_AUTHOR)

    clash = sorted(set(sectioned + plain) & set(RESERVED_POINTER_TYPES))
    if clash:
        raise ConfigError(
            f"evidence type(s) {', '.join(clash)} collide with a reserved pointer type "
            f"{sorted(RESERVED_POINTER_TYPES)}"
        )
    both = sorted(set(sectioned) & set(plain))
    if both:
        raise ConfigError(f"evidence type(s) {', '.join(both)} are both sectioned and plain")
    if not sectioned + plain:
        raise ConfigError("no evidence types; a measured grade would have nothing it could rest on")
    if propagation not in authors:
        raise ConfigError(
            f"propagation-author `{propagation}` is not among verdict-authors {list(authors)}"
        )
    for prefix in table.get("archived-prefixes", ()):
        if not (isinstance(prefix, str) and len(prefix) == 1 and prefix.isupper()):
            raise ConfigError(f"archived prefix `{prefix}` is not a single uppercase letter")

    return Config(
        root=root,
        ledger_dir=ledger,
        entries_dir=ledger / table.get("entries", "entries"),
        registry=ledger / table.get("registry", "sources.jsonl"),
        cache=(ledger / cache) if cache else None,
        documents=tuple(table.get("documents", DEFAULT_DOCUMENTS)),
        document_excludes=tuple(table.get("document-excludes", DEFAULT_DOCUMENT_EXCLUDES)),
        roster=table.get("roster", DEFAULT_ROSTER),
        archived_prefixes=tuple(table.get("archived-prefixes", ())),
        evidence_sectioned=sectioned,
        evidence_plain=plain,
        verdict_authors=authors,
        propagation_author=propagation,
        source=Path(source) if source else None,
    )


def load_config(root=None, config_path=None):
    """The configuration for a project.

    `config_path` names a file directly; `root` overrides the project root that paths
    resolve against. With neither, the nearest configuration file at or above the
    current directory is used, and the defaults apply when there is none.
    """
    if config_path is not None:
        path = Path(config_path).resolve()
        if not path.is_file():
            raise ConfigError(f"no configuration file at {path}")
        return from_table(_read_table(path), root or path.parent, source=path)
    path = find_config_file(root or Path.cwd())
    if path is None:
        return default_config(root or Path.cwd())
    return from_table(_read_table(path), root or path.parent, source=path)
