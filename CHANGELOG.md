# Changelog

Notable changes, newest first. The format is [Keep a Changelog][kac]; the versions are
[semantic][semver].

One rule is specific to this package: **a change that moves a red-team corpus seed's
expected outcome is a methodology change**, not a bug fix, and is recorded here as such
with the seed named. The corpus is the argument that the checkers work, so a silent
change to what it expects would dissolve the argument.

[kac]: https://keepachangelog.com/en/1.1.0/
[semver]: https://semver.org/spec/v2.0.0.html

## [0.1.0] — 2026-09-05

First public release. Extracted from the claims ledger built for a research project on
dynamic graph embedding refresh, where the schema, the checkers and the corpus were
developed together. All 62 corpus seeds pass unchanged from the ledger it came out of.

Everything below is in this release: the three adversarial passes recorded in
`QE-AUDIT.md` all ran before it was tagged, so their fixes are part of the first
published artifact rather than a change to one.

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


### Found and fixed by the pre-publication audit

Three adversarial passes, recorded in `QE-AUDIT.md`: nine defects, then nine more found
by attacking those fixes, then six more found by attacking the second round. All
twenty-four are fixed, and every one of them is a strict-xfail test that flipped and is
kept as the regression for its fix in `tests/test_hostile_inputs.py` — sections A-E for
the first pass, F for the second, G for the third.

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

#### The third pass, against the second round of fixes

Three of the six were the same defect class as a second-pass fix, one surface over. The
fixes had been applied at the site each was reported at rather than to the class, so this
round asked of every fix which other surfaces reach the same code by a different route.

- **A git that is present but broken no longer drops the immutability checks in
  silence.** `git()` answers `None` for every failure — a non-zero exit, a timeout, a
  damaged object store, a checkout git refuses as `dubious ownership` — and the history
  checks read `None` as *this entry is not committed yet*. So a broken git was quieter
  than a missing one: an entry whose frozen region had been tampered with came back
  `0 failure(s)` at exit 0 with empty stderr, where an absent git at least printed a note.
  A false pass on the frozen-region and append-only guarantee, which is the immutability
  claim the package exists to make. `git_problem()` now asks the repository a cheap
  question instead of asking `PATH` for a binary, and `skipped_checks()` names what it
  says.
- **An unreadable *documents directory* is no longer a clean pass.** HIGH-9's listability
  check went to the entries directory and not to the documents glob, so `chmod 000 docs`
  turned a failing citation check into `0 failure(s)` at exit 0 with no note at all. The
  directories a `documents` pattern reaches into are walked now, where the `EACCES` is
  visible instead of swallowed by `glob()`.
- **`init --force` no longer hangs on a FIFO named `claims-ledger.toml`.** The
  regular-file guard went into the registry append and not into the config write, and
  opening a FIFO for writing blocks until a reader appears — in CI, a wedged job with no
  output.
- **Nothing is written through an entry that is a symlink out of the project root.**
  `confined()` follows symlinks for the five configuration keys; an entry file reached by
  globbing inside `entries/` was not checked at all, so `sha --write` rewrote a file
  outside the project at exit 0. `propagate --write` reached the same files by a different
  route and is guarded with it. Reads are deliberately unchanged: an entry symlinked in
  from outside is still read normally.
- **An entries directory that lists but will not open is a clean error.** Mode `0o444`
  leaves the read bit on and takes the execute bit off, so the names list and none of them
  stat — `unexpected PermissionError` and a request for a bug report over an ordinary
  permission problem. Reads go through `os.stat` now rather than `Path.is_file()`, which
  answers `False` for everything from a FIFO to a permission error and answers it
  differently on different interpreters.
- **`--root` pointing at a symlink loop is a clean error**, as the entries directory
  already was.
- Smaller, from the same pass: a document that is not a regular file, and one that is not
  UTF-8, are reported by name rather than dropped before the count; a slug that fits
  `NAME_MAX` but overruns `PATH_MAX` under a deep root is a specific error rather than
  `unexpected OSError`; and a source registry that is not a regular file is refused on
  read as it already was on write.

#### Known, and left as it is

- A document reached through a symlink that leaves the root is still read. The
  `documents` confinement is lexical by design: what it closes is a configuration that
  addresses outside the project, not every route a link inside the tree can take.
- An entry that is a *hardlink* to a file outside the root is written through. A hardlink
  is the file, not a reference to it, and there is nothing at the path to refuse.
- `GIT_TIMEOUT` bounds each git call, not a whole command: `validate --cached` over N
  entries can wait N × 30s on a git that hangs. A per-command deadline would be the
  stronger promise; per-call is the one made here.

### Packaging and documentation

- The README's link to `docs/SCHEMA.md` is absolute, so it resolves on the PyPI project
  page instead of 404ing; the package docstring, `schema.py`'s docstring and `new`'s help
  point at the same URL rather than at a path no installed copy carries. The URL sits in
  argparse's epilog, which is printed as written — as an option's help text it was wrapped
  mid-token at the terminal width, and a link that cannot be copied is not a link.
- `CHANGELOG.md` ships in the sdist, which `[project.urls]` already promised.
- A tag-triggered release workflow publishes to PyPI through Trusted Publishing, after
  the built wheel has proved itself by running the corpus from a clean environment. It
  needs a publisher configured once on PyPI naming this repository, `release.yml` and
  the `pypi` environment. Two gates the third pass asked for: the whole suite — ruff,
  `ty`, pytest — runs before anything is built, because a tag matches neither of CI's
  triggers and publication was otherwise gated on the corpus alone; and the `publish` job
  is guarded on the ref being a tag, because Trusted Publishing binds the repository, the
  workflow file and the environment but never the ref, so a manual dispatch from any
  branch would have published with the tag-agrees-with-package check skipped.
- **3.14 is tested and classified.** It is the interpreter this package is developed on,
  and it was not in the matrix. Three of the third pass's findings turn on pathlib
  behaviour that changed between 3.12 and 3.14 — a symlink loop, a file that will not
  stat, a path too long — and one of them had been recorded as fixed by a pass that
  checked it on the interpreter where it cannot occur.

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

[0.1.0]: https://github.com/Ybx-jp/claims-ledger/releases/tag/v0.1.0
