# Changelog

Notable changes, newest first. The format is [Keep a Changelog][kac]; the versions are
[semantic][semver].

One rule is specific to this package: **a change that moves a red-team corpus seed's
expected outcome is a methodology change**, not a bug fix, and is recorded here as such
with the seed named. The corpus is the argument that the checkers work, so a silent
change to what it expects would dissolve the argument.

[kac]: https://keepachangelog.com/en/1.1.0/
[semver]: https://semver.org/spec/v2.0.0.html

## [Unreleased]

## [0.1.0] — 2026-09-05

First public release. Extracted from the claims ledger built for a research project on
dynamic graph embedding refresh, where the schema, the checkers and the corpus were
developed together. All 62 corpus seeds pass unchanged from the ledger it came out of.

### The schema and the checkers

- An entry separates Assertion, Scope, Grounds, Warrant and Backing, with no quotation
  mark permitted in the Assertion, and derives its status from an append-only verdict
  list rather than storing one.
- Four checkers — `validate`, `resolve`, `references`, `propagate` — and `check`, which
  runs all four.
- A red-team corpus of 62 seeds with committed expected outcomes, shipped inside the
  package and runnable from an installed copy as `claims-ledger corpus`. The contract is
  symmetric: an unlisted catch is a finding about the seed or the checker, never a bonus.
- Authoring: `init`, `new`, `sha`, `source add`, `source list`, `status`, `hook`.
- No runtime dependencies. Python 3.11 or newer.

### Fixed before release

Found by walking the package as a first-time user would, from a clean install.

- **`check` no longer reports success over a ledger it never found.** Pointed at a
  directory with no entries directory — the wrong `--root`, a configuration file moved
  away from its ledger — every checking command now stops with exit 2 and says nothing
  was checked. It previously printed four `0 failure(s)` lines and exited 0, which is
  the one report this tool must never produce.
- **Skipped checks are named rather than counted as passes.** Outside a git repository,
  or with no `git` on PATH, validate's frozen-region and append-only checks cannot run;
  they now say so on stderr instead of contributing silence to a clean result. `--cached`
  outside a repository likewise says it had no effect rather than quietly reading the
  working tree.
- **A malformed `sources.jsonl` is reported, not raised.** A line that is not JSON, or a
  row with no `id`, raised `JSONDecodeError`/`KeyError` as a traceback out of `check`,
  `resolve` and `source list`. It is now a `LedgerError` naming the file and line number.
- **An entry file that is not UTF-8 is reported, not raised.** One stray byte raised
  `UnicodeDecodeError` out of every command that loads entries, `status` included.
- **An unreadable evidence file is a pointer that does not resolve**, reported by
  `resolve`, rather than an exception from inside the checker.
- **No traceback reaches a user.** `main()` now turns any unexpected exception into a
  diagnostic and exit 2, handles `KeyboardInterrupt` (exit 130) and `BrokenPipeError`
  (exit 141, for `claims-ledger status | head`). `CLAIMS_LEDGER_TRACEBACK=1` restores the
  traceback for bug reports.
- **The installed pre-commit hook works for a pip install.** It named the console script
  `claims-ledger`, which git's hook environment does not have on PATH when the tool lives
  in a virtualenv that is not active, so it failed with `not found` on every commit. It
  now names its interpreter absolutely and reaches the package with `-m claims_ledger`.
- **`python -m claims_ledger` works**, which the hook depends on and the README's
  standard-library-only promise implies. There was no `__main__.py`.
- **`--version`.** There was no way to ask the tool what version was installed.
- **`__all__` matches the documented library API.** `validate`, `resolve`, `references`
  and `propagate` are advertised in the README and were reachable only by Python's
  implicit submodule import, not as declared exports. `LedgerError` is exported too.
- **The version has one source of truth.** `pyproject.toml` reads it from
  `claims_ledger.__version__` instead of repeating the literal.
- `1 entries` reads `1 entry`.

### Development

- **`ruff check` and `ruff format` are clean**, against an explicit rule set —
  `E, F, I, B, SIM, UP, RUF, ISC, BLE, PLW, FURB` — pinned in `pyproject.toml` rather
  than tracking ruff's default select, which grows between releases. The set is every
  family ruff raised against this code, kept rather than narrowed. `E731` is in it
  because the `fail = lambda …` suppressions in the checkers were written against it,
  and the schema's own typography (`·`, `§`, en dashes) is declared in
  `allowed-confusables` rather than rewritten.
- **`ty check` runs in CI**, over `src` and `tests`, against the 3.11 floor rather than
  the newest interpreter, so a construct that only exists on a newer Python cannot pass
  here and fail for a user.
- One behaviour change fell out of the ruff pass: `parse_timestamp` no longer rewrites a
  trailing `Z` to `+00:00` before `datetime.fromisoformat`, which has handled `Z` itself
  since 3.11. Nothing covered a `Z` timestamp, so it is covered now.

### Known limits

- Tested on Linux and macOS. Windows is neither tested nor claimed: the installed hook is
  `#!/bin/sh`, and the newline translation `Path.write_text` performs on Windows has not
  been checked against the byte-exact quotation matching.
- The tool does not decide whether a claim is true. See "What this does not do" in the
  README.

[Unreleased]: https://github.com/Ybx-jp/claims-ledger/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Ybx-jp/claims-ledger/releases/tag/v0.1.0
