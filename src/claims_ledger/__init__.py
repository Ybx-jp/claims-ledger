"""A claims ledger: entries that separate assertion, grounds, warrant and backing, hold
every quotation to its source, and derive status from an append-only verdict list, with
four checkers that enforce the schema and a red-team corpus that proves the checkers.

The schema is stated in full in docs/SCHEMA.md.
"""

from . import propagate, references, resolve, validate
from .config import Config, ConfigError, default_config, load_config
from .schema import (
    ACTS,
    GRADES,
    KINDS,
    STATUSES,
    Entry,
    Ledger,
    LedgerError,
    Report,
    default_ledger,
    derive_status,
    exit_code,
    fingerprint,
    load_entries,
    open_ledger,
    parse_entry,
    print_reports,
)

# The single source of truth for the version: pyproject.toml reads it from here
# (`[tool.hatch.version] path`), so `claims_ledger.__version__`, `pip show` and the
# PyPI release can never disagree.
__version__ = "0.1.0"

__all__ = [
    "ACTS",
    "GRADES",
    "KINDS",
    "STATUSES",
    "Config",
    "ConfigError",
    "Entry",
    "Ledger",
    "LedgerError",
    "Report",
    "__version__",
    "default_config",
    "default_ledger",
    "derive_status",
    "exit_code",
    "fingerprint",
    "load_config",
    "load_entries",
    "open_ledger",
    "parse_entry",
    "print_reports",
    # The four checkers, which README.md advertises as the library API. They are listed
    # here because `from claims_ledger import validate` working by implicit submodule
    # import is an accident of Python, not a declared export.
    "propagate",
    "references",
    "resolve",
    "validate",
]
