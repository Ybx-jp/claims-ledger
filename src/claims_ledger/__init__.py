"""A claims ledger: entries that separate assertion, grounds, warrant and backing, hold
every quotation to its source, and derive status from an append-only verdict list, with
five checkers that enforce the schema and a red-team corpus that proves the checkers.

The schema is stated in full in docs/SCHEMA.md, which the repository carries at
https://github.com/Ybx-jp/claims-ledger/blob/main/docs/SCHEMA.md.
"""

from . import freshness, propagate, references, resolve, validate
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

# The five checkers are listed in `__all__` alongside everything else, in sorted order,
# because `from claims_ledger import validate` working by implicit submodule import is an
# accident of Python rather than a declared export, and README.md advertises them as the
# library API.
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
    "freshness",
    "load_config",
    "load_entries",
    "open_ledger",
    "parse_entry",
    "print_reports",
    "propagate",
    "references",
    "resolve",
    "validate",
]
