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

### Fixed

The pre-publication audit in `QE-AUDIT.md` (2026-09-05) found nine defects, each recorded
as a strict-xfail test; all nine are fixed and those tests are now the regressions for
the fixes. A second pass then attacked the fixes themselves and found nine more, listed
after them here; those are fixed too, and section F of `tests/test_hostile_inputs.py`
holds their regressions.

- **A FIFO named `*.md` no longer hangs the tool.** `read_text()` on a FIFO with no
  writer blocks forever, so `status`, `validate` and `check` never returned — in a
  pre-commit hook, a wedged commit with no output at all. Nothing but a regular file is
  opened; a directory, a dangling symlink and a symlink loop report the same way.
- **A configuration cannot name a path outside the project root.** `ledger`, `entries`,
  `registry` and `cache` are refused with a `ConfigError` naming the key when they
  resolve outside `root`, absolutely or through `..`. `Path(root) / "/abs"` discards
  `root`, so a cloned repository's own `claims-ledger.toml` could send every write —
  `new`, `init`, `source add`, `sha --write`, `propagate --write` — anywhere on the
  filesystem, at exit 0 and without a warning.
- **`status` stops on a root it cannot find.** It was the one command that never called
  `guard()`, so a nonexistent root printed `no entries under ledger/entries` and exited
  0 while `validate` exited 2 over the same root.
- **git's output is decoded as UTF-8**, not with the locale's codec. Under a non-UTF-8
  locale an entry containing the schema's own `·` separator took the frozen-region and
  append-only checks down with a `UnicodeDecodeError`.
- **A diagnostic survives an output encoding that cannot hold it.** Printing `·` to an
  ASCII stdout raised `UnicodeEncodeError` on precisely the path that was about to
  explain a failure, replacing the explanation with `this is a bug`. Unencodable
  characters are escaped instead.
- **`corpus` says git is missing instead of asking for a bug report.** Its history seeds
  are applied as commits, so without `git` it now refuses at exit 2 rather than raising
  `FileNotFoundError` through the catch-all handler.
- **An id or a credence written in non-ASCII digits is refused.** `\d` matches any
  Unicode decimal digit and `float()` reads them too, so `A０００１` passed the id check
  as a distinct string that looks like `A0001`, and `credence: ٠.٥` was silently read as
  0.5. The id, prefix, timestamp and citation patterns are ASCII-only, and a credence
  must be a plain decimal number.
- **`--root ""` is refused** rather than read as "no `--root` given" and run against
  whatever directory the process happened to start in.
- **An over-long slug, a symlink loop at the entries directory, and a `ledger` path that
  names a regular file** are specific errors rather than `unexpected OSError`,
  `unexpected RuntimeError` and `unexpected NotADirectoryError`. Anything printing "this
  is a bug, please report it" over an ordinary user mistake is a defect of its own.

#### The second pass, against the fixes

- **A ledger that cannot be listed is no longer a clean pass.** With the read bit off
  `ledger/entries` — a directory owned by another user, a CI runner without it — `is_dir()`
  answered True and `glob()` swallowed the `EACCES` from `scandir` and yielded nothing, so
  `status`, `validate`, `resolve`, `references`, `propagate` and `check` each printed
  `0 entries … 0 failure(s)` and exited 0 over a ledger full of failing entries, and a
  pre-commit hook built on `check` let the commit through. The entries directory is now
  listed rather than asked about, and a directory that will not list stops the command at
  2. This was the only false pass found in either pass of the audit, and the first pass's
  verdict — that no defect produced one — was wrong.
- **A document that could not be read is reported, not treated as empty.** `chmod 000` on
  a document that cited a nonexistent entry turned a `references` failure into a clean run
  at exit 0, while the document was still counted in the `N documents` total. An
  unreadable document is now a failure naming it, it is out of the count, and it is named
  in the skipped-checks note the other commands print.
- **`source add` refuses a registry that is not a regular file.** A FIFO at
  `ledger/sources.jsonl` blocked the append forever — in a hook, a wedged commit with no
  output — and a directory there asked for a bug report. This was the defect fixed for
  entry *reads* in the first pass, still open on the registry *write*.
- **A `ledger` that is a symlink out of the project root is refused.** The containment
  added in the first pass was lexical, so a checkout carrying `ledger -> /tmp/outside`
  wrote real entries outside the project at exit 0 — the very thing the containment was
  written to stop, since a clone carries a symlink as readily as it carries a
  `claims-ledger.toml`. Paths are now checked as written *and* with their symlinks
  followed; a symlink that stays under the root still works.
- **The `documents` globs are confined like every other path.** `documents =
  ["../outside-root/*.md"]`, and an absolute pattern, pointed the checkers at any readable
  file on the machine and printed its path and its citations into the report.
- **Four more ordinary conditions stopped asking for a bug report**: `init` over a regular
  file named `entries` (`FileExistsError`), `source add` with a directory at
  `sources.jsonl` (`IsADirectoryError`) or a read-only `cache` (`PermissionError`), and
  `hook --install` into a read-only `.git/hooks` (`PermissionError`) — an ordinary thing
  in a locked-down or shared checkout. `sha --write` and `propagate --write` were given
  the same funnel.
- **git cannot hang a checker.** `schema.git()` and the corpus runner's own `git()` ran
  with no timeout, so a git that blocks — a credential prompt, a pack it wants to recover
  — hung `validate --cached`, `check`, `resolve`, `sha` and the corpus with no way out.
  Both now give up after 30 seconds, and the corpus decodes git's output as UTF-8
  explicitly, as the checkers already did.

#### Known, and left as it is

- A document reached through a symlink that leaves the root is still read. The
  `documents` confinement is lexical by design: what it closes is a configuration that
  addresses outside the project, not every route a link inside the tree can take.

### Packaging and documentation

- The README's link to `docs/SCHEMA.md` is absolute, so it resolves on the PyPI project
  page instead of 404ing; the package docstring and the `--grade` help text point at the
  same URL rather than at a path no installed copy carries.
- `CHANGELOG.md` ships in the sdist, which `[project.urls]` already promised.
- A tag-triggered release workflow publishes to PyPI through Trusted Publishing, after
  the built wheel has proved itself by running the corpus from a clean environment. It
  needs a publisher configured once on PyPI naming this repository, `release.yml` and
  the `pypi` environment.

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
