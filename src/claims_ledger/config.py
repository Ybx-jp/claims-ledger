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
import os
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
        except (ValueError, OSError, RuntimeError):
            # OSError/RuntimeError: resolving a symlink loop. A message about a path we
            # cannot resolve still has to print, so fall back to the path as written.
            return str(path)


def default_config(root):
    """The configuration of a project that has not written one down.

    The default layout is confined the same way a configured one is: a project with no
    `claims-ledger.toml` at all can still have a `ledger` that is a symlink out of the
    tree, and the containment is a property of the tool rather than of the file.
    """
    root = resolved(root)
    ledger = confined(root, "ledger", "ledger")
    return Config(
        root=root,
        ledger_dir=ledger,
        entries_dir=confined(root, "entries", ledger / "entries"),
        registry=confined(root, "registry", ledger / "sources.jsonl"),
        cache=confined(root, "cache", ledger / "cache"),
    )


def find_config_file(start):
    """The nearest configuration file at or above `start`, or None. A `pyproject.toml`
    counts only when it carries a `[tool.claims-ledger]` table, so a package that merely
    depends on this one is not mistaken for the project root."""
    start = resolved(start)
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


def _escapes(root, path):
    """Whether `path` lands outside `root`, comparing the two as written."""
    return path != root and root not in path.parents


def resolved(path, what="root"):
    """`path` with its symlinks followed, or a ConfigError naming it.

    A symlink loop reaches pathlib as a RuntimeError on 3.12 and earlier and as the
    unresolved path on 3.14; `--root` pointing at one is a misconfigured root either way,
    not an internal error to ask for a bug report over.
    """
    try:
        return Path(path).resolve()
    except (OSError, RuntimeError) as exc:
        raise ConfigError(
            f"{what} {path} cannot be resolved ({exc}); a symlink loop, or a path that "
            "walks through something that is not a directory"
        ) from exc


def _followed(path):
    """`path` with its symlinks followed, or `path` itself when they cannot be. A loop
    reaches us as an OSError or a RuntimeError depending on the interpreter, and a path
    we cannot resolve is not evidence that it escapes."""
    try:
        return Path(path).resolve()
    except (OSError, RuntimeError):
        return Path(path)


def confined(root, key, value):
    """`root / value` for a path a configuration file names, refused if it leaves `root`.

    An absolute value discards `root` outright — that is what `Path("/a") / "/b"` means —
    and a `..` value walks out of it. For a tool whose subject is confinement, a cloned
    repository's own `claims-ledger.toml` writing entries into /tmp is a hole, so both are
    a ConfigError naming the key rather than a path we quietly honour.

    A symlink is the same hole with a different spelling: a clone carries `ledger ->
    /tmp/outside` as readily as it carries a configuration file, and a lexical check alone
    says yes to it. So the path is checked twice — as written, and with its symlinks
    followed — and the value returned is the one as written, so a ledger reached through a
    symlink that stays inside the root goes on working.
    """
    lexical = Path(os.path.normpath(root / value))
    if _escapes(root, lexical):
        raise ConfigError(
            f"{key} path `{value}` resolves to {lexical}, outside the project root "
            f"{root}; every path a configuration names must stay under the root"
        )
    followed = _followed(lexical)
    if _escapes(_followed(root), followed):
        # Phrased without "a configuration": the default layout is confined too, and a
        # project that never wrote a configuration file can still carry this symlink.
        raise ConfigError(
            f"{key} path `{value}` is a symlink to {followed}, outside the project root "
            f"{root}; a ledger outside the root is not one this tool will write to"
        )
    return lexical


def leaves_root(root, path):
    """Where `path` really is, when that is outside `root`; None when it is not.

    The same question `confined()` asks of a configured path, asked of a file the tool is
    about to write. A configuration is not the only thing a clone carries: an entry inside
    `entries/` can be a symlink to anywhere, and following one on a write is a write
    outside the project root — which is the property this package states it has.
    """
    followed = _followed(path)
    return followed if _escapes(_followed(Path(root)), followed) else None


def confined_pattern(root, key, value):
    """A glob pattern a configuration names, refused if it addresses outside `root`.

    Lexical, and only lexical: a pattern is not a path — there is no `*` on disk to
    follow — and what is being closed here is a configuration that points the checkers at
    a file the project does not contain, printing its path and its citations into a
    report. Where a symlink inside the tree leads is the document's own business.
    """
    if not isinstance(value, str):
        raise ConfigError(f"{key} pattern `{value}` is {type(value).__name__}, expected str")
    lexical = Path(os.path.normpath(root / value))
    if _escapes(root, lexical):
        raise ConfigError(
            f"{key} pattern `{value}` addresses {lexical}, outside the project root "
            f"{root}; every path a configuration names must stay under the root"
        )
    return value


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

    root = resolved(root)
    ledger = confined(root, "ledger", table.get("ledger", "ledger"))
    documents = tuple(table.get("documents", DEFAULT_DOCUMENTS))
    for pattern in documents:
        confined_pattern(root, "documents", pattern)
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
        entries_dir=confined(root, "entries", ledger / table.get("entries", "entries")),
        registry=confined(root, "registry", ledger / table.get("registry", "sources.jsonl")),
        cache=confined(root, "cache", ledger / cache) if cache else None,
        documents=documents,
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
    if root is not None and not str(root).strip():
        raise ConfigError("root is empty; give a directory or omit --root")
    if config_path is not None:
        path = resolved(config_path, what="the configuration file")
        if not path.is_file():
            raise ConfigError(f"no configuration file at {path}")
        return from_table(_read_table(path), root or path.parent, source=path)
    path = find_config_file(root or Path.cwd())
    if path is None:
        return default_config(root or Path.cwd())
    return from_table(_read_table(path), root or path.parent, source=path)
