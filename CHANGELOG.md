# Changelog

Notable changes, newest first. The format is [Keep a Changelog][kac]; the versions are
[semantic][semver].

One rule is specific to this package: **a change that moves a red-team corpus seed's
expected outcome is a methodology change**, not a bug fix, and is recorded here as such
with the seed named. The corpus is the argument that the checkers work, so a silent
change to what it expects would dissolve the argument.

[kac]: https://keepachangelog.com/en/1.1.0/
[semver]: https://semver.org/spec/v2.0.0.html

## [0.1.0] — 2026-09-06

First public release. Extracted from the claims ledger built for a research project on
dynamic graph embedding refresh, where the schema, the checkers and the corpus were
developed together. All 62 corpus seeds passed unchanged from the ledger it came out of;
the release ships 79.

**Everything below is in this release, and this file has one version heading rather than
several on purpose.** The five adversarial passes recorded in `docs/audits/0.1.0.md`, the fifth
checker and section scoping all landed before anything was tagged or uploaded, so there
was no earlier release for any of them to be a change to. Splitting them across versions
would have put a `0.1.0` on the record that nobody could ever install.

### The schema and the checkers

- An entry separates Assertion, Scope, Grounds, Warrant and Backing, with no quotation
  mark permitted in the Assertion, and derives its status from an append-only verdict
  list rather than storing one.
- Five checkers — `validate`, `resolve`, `references`, `propagate`, `freshness` — and
  `check`, which runs all five. The first four are described here; `freshness` has its own
  section below, because it was written after this one.
- A red-team corpus, 62 seeds at extraction and 79 at release, with committed expected
  outcomes, shipped inside the package and runnable from an installed copy as
  `claims-ledger corpus`. The contract is symmetric: an unlisted catch is a finding about
  the seed or the checker, never a bonus, and one row is satisfied by one report.
- Authoring: `init`, `new`, `sha`, `source add`, `source list`, `status`, `hook`.
- An executable four-repository example portfolio demonstrates every entry kind, evidence
  grade, derived status and citation act, custom section scoping, real Git pins, hooks,
  and content-addressed provenance across repository boundaries.
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

Three adversarial passes, recorded in `docs/audits/0.1.0.md`: nine defects, then nine more found
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

- **The package keeps a ledger of the claims about itself**, under `ledger/`: eight entries
  for design commitments the README states and a docstring explains, each pinned to the
  function or table that keeps it true and cited from both sites. `claims-ledger check`
  runs in CI beside the tests and the corpus, so a pinned function that moves fails the
  sentence and the docstring that rest on it. The four places that showed the citation
  syntax with a literal example id show it with a `<slug>` placeholder instead: the
  references checker reads a document as text, and the ledger reported all four as
  citations of an entry that does not exist.
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

### The fifth checker, and section scoping

Written after the section above, and before anything was tagged.

- **A fifth checker, `freshness`.** `resolve` asks whether a ground's pointer resolves,
  and asks it of the past: the pin names a commit, so once an entry resolves it resolves
  for good. The ledger could therefore not notice that the world had moved — an entry
  could rest on a test that had since been deleted and every checker stayed green,
  because the evidence was still there at the revision nobody works on. `freshness`
  compares each pinned ground to the working tree: a path that is gone fails, bytes that
  differ from the pin flag, and a pin that is a branch or a tag rather than an object id
  flags, because a pin that follows the work can never go stale. It never judges whether
  a difference matters. A `contested` verdict by the propagation author naming the
  pointer discharges the finding, `--write` appends it, and a verdict naming a ground
  that has not drifted is an orphan and fails. The specification is `docs/FRESHNESS.md`.
- Eight corpus seeds for it — `D45`–`D48`, `K19`–`K22`. Every one was falsified by
  deleting the rule it covers and re-running the corpus.
- History seeds may write `@commit01` in an entry; the runner substitutes that commit's
  real short object id before the state is committed. A seed cannot name an object the
  runner has not created yet, and drift, like immutability, is a property of history.

- **Section patterns.** A `§ "<section>"` pointer used to mean a Markdown heading and
  nothing else, so a claim could not rest on a named function of a source file, and the
  drift comparison treated every edit anywhere in an artifact as a moved ground. A
  sectioned evidence type may now carry a regex with a `{name}` slot under
  `[tool.claims-ledger.section-patterns]`; omitted, it gets the heading it always meant.
  `resolve` and `freshness` read a section through the same pattern, and `freshness`
  compares only the named section, so an edit elsewhere in the artifact is no longer
  drift. A pattern that does not compile, does not mention `{name}`, or names a type that
  is not sectioned is refused where the configuration is read.
- Two more seeds, `D49` and `K23`.
- A drifted ground in an uncommitted working tree says so, rather than reporting that
  `0 commits have touched it` — which, of a file the author is editing right now, reads
  as a checker that has lost track of its own subject.

### Changed by the fifth checker

- `validate` admits one more verdict shape under the propagation author: a `contested`
  verdict whose evidence is an evidence ground carrying a pin, which is what `freshness`
  writes. `entry:` evidence with `· fallen` or `· challenges` remains the only other one,
  so a person still cannot write under the machine's name.
- `resolve` reads a pinned artifact from the repository holding the entries rather than
  from the project root. `git show <pin>:<path>` resolves the path from the repository
  root; the two are the same directory in a real project, and are not in a corpus
  history seed. No seed's expected outcome moves: every pin in the 62 seeds written
  before this is `@corpus`, which reads from the working tree and never reached that call.
- `claims-ledger check` and the installed pre-commit hook run five checkers, not four.

### Fixed by the fourth and fifth adversarial passes

- **A git that stops answering is no longer read as good news** — the fourth adversarial
  pass, `docs/audits/0.1.0.md` HIGH-23 … MEDIUM-28. `git_problem()` was asked once at the start of
  a run and every command after it was trusted, so a failure that `rev-parse --git-dir`
  cannot see — a required clean filter that exits non-zero, a truncated index, a loose
  object removed, a diff that outlives the timeout — came back as `None` from `git()` and
  was read by its caller as a benign negative: unchanged, not staged, not committed. A
  check that never ran, reported as a check that passed. `git_call()` answers with the
  exit status beside the output, so a caller can tell *no* from *could not ask*, and each
  surface was changed to ask in that form: `freshness` reports a comparison it could not
  make instead of a fresh ground, and does not turn the same silence into an orphan
  verdict; `validate` reports a revision whose blob it could not read instead of waiving
  the append-only check across it, and says when `--cached` fell back to the working tree
  because the index could not be parsed; `sha --write` refuses to rewrite an entry when
  git cannot say whether it is committed, rather than rewriting an immutable frozen
  region and exiting 0; and `resolve` reports a git it could not ask once, for the
  ledger, rather than telling the author that every pinned pointer they wrote is wrong.
  Two surfaces of the same class, found while fixing rather than reported: an entry whose
  history `git log` cannot list was read as one that had never been committed, and so
  dropped out of both history checks; and `drift()` could not tell a path that is not at
  the pin from a git that could not look for it.
- **The immutability check covers the whole frozen region** (`docs/audits/0.1.0.md` HIGH-22). It
  compared parsed sections, and a section runs from its own heading to the next — so
  every byte above the first `## ` heading of a committed entry belonged to no section
  and was compared against nothing. The scaffold leaves that region empty, which is what
  made it a hiding place. The bytes above the APPEND marker are compared now, with the
  section-by-section diff kept for the diagnostic so a changed section is still named.
- The configuration `claims-ledger init` writes is now checked to be parseable TOML. The
  template is filled with `str.format` and then read by a parser, and an escape that
  survives one and not the other is unparseable in a way nothing else would notice: a
  `\b` in a commented-out example became a real backspace, which `tomllib` refuses even
  inside a comment.
- `propagate --write` lost verdicts. Two verdicts destined for one entry were two writes
  built from the same in-memory text, so the second overwrote the first — an entry citing
  two fallen grounds kept one flag and silently lost the other. Blocks are now grouped by
  entry and written once. Found while building `freshness`, which would have inherited it.
- **Every write is a temp file and a rename** — the fifth adversarial pass, `docs/audits/0.1.0.md`
  HIGH-39 … LOW-52. `create_entry`, `restamp`, `append_verdict`, `cmd_init` and `cmd_hook`
  each truncated their destination before knowing they could fill it, so a write that
  failed partway — a full disk, a quota, a resource limit — left a committed entry cut off
  mid-verdict with its `## References` gone. The diagnostic was already right; the state
  left behind was not.
- **A `--write` no longer rewrites the frozen region of a CRLF entry, and `check` can see
  it if anything does.** The write paths read and wrote through universal newlines, so
  appending three lines to an entry committed with CRLF rewrote all forty above the APPEND
  marker — and `check_history` compared `git show`'s decoded output against decoded text,
  so the "compared as bytes" immutability check could not see a newline change on either
  side. The write paths keep the file's own endings; the frozen region is compared as
  bytes as well as as sections. `append_verdict` also chooses its insertion point below
  the APPEND marker rather than by the first `## References`, which on a layout `validate`
  rejects put the verdict inside the frozen region, and refuses the write outright if the
  bytes above the marker would change.
- **`source add` writes a line as a line.** Onto a `sources.jsonl` with no final newline it
  glued its row onto the previous one, destroyed both, printed `registered …` and exited 0,
  and every later command exited 2 with `not a JSON object`. A failed append is now rolled
  back to the length the file had. Retrying an interrupted `source add` also kept the
  truncated cache file — `if not stored.exists()` trusted the name of a content-addressed
  file — and exited 0 over bytes it never wrote; the bytes are checked against the digest.
- **`sha --write a b c` no longer stops at the first path it cannot write.** Each path is
  its own write, and the ones after a refusal were neither attempted nor named.
- **`freshness`:** a discharge verdict names a section, so one verdict no longer silences
  every ground on the same file and pin; `--write` exits non-zero, so the verdicts it
  appends are looked at before they are committed; `--cached` reaches it, so
  `check --cached` compares the index the commit will carry rather than the working tree;
  an uppercase object id is an object id and a `@v9.9` that names nothing is `resolve`'s
  finding, because git is now asked about every pin rather than only the hex-shaped ones;
  paths reach `git diff` as `:(literal)` pathspecs, so an edit to `docs/note1.md` is not
  reported as drift in `docs/note[1].md`; and undoing an edit no longer turns the
  checker's own discharge into an orphan failure that no legal edit could clear.
- **A `###` subsection no longer ends its parent `##` section.** The shipped default
  section pattern ended a section at a heading of *any* depth, so a claim's own evidence
  could be inverted under a subheading with `resolve` and `freshness` both green — and a
  project that had configured nothing had no anchoring available to it, because `#+` is
  every depth. A pattern that can nest now says so with a group named `depth`.
- **Frontmatter fences may carry trailing whitespace.** `--- ` was read as no frontmatter
  at all, which is one report followed by every check that needed a key cascading behind
  it. YAML permits it and editors leave it there.

### Fixed by the sixth adversarial pass

Four of these are in code the fifth pass's own fixes introduced one day earlier, which is
why the pass ran a revert experiment over that commit rather than a seventh audit.

- **A propagated discharge states what caused it, and is held to it** — `docs/audits/0.1.0.md`
  HIGH-53. Closing the wedge in MEDIUM-34 introduced `ever_drifted()`, which asked whether
  any commit since the pin had *touched* the artifact and read a yes as proof that the
  verdict was caused. That is a question the forger controls: one commit that edits the
  artifact and one that puts it back — or a `chmod +x`, or a rename away and back —
  laundered a pre-emptively written discharge permanently, while the artifact stayed
  byte-identical to the blob at the pin. The rule had traded a loud false positive for a
  silent false negative. `freshness --write` now records an `artifact:` line in the verdict
  — the object id git would store the artifact under at the moment the drift was seen, or
  `absent` for a ground that had been withdrawn — and the orphan rule asks whether the
  artifact really was that between the pin and here. A verdict that records nothing, or
  that records the artifact as the pin itself has it, is an orphan.
- **The `artifact:` line is checked, in every state, and is required where it is
  written** — QE7-70 and QE7-75, from the check that stands between the fixer and the
  merge. As first written the field was consulted only once the ground looked fresh again,
  and the rule that silences a `moved` report matched a verdict to a ground by the pointer
  alone: over a live, committed drift a propagated verdict carrying forty zeros, a value
  the artifact had never been, or no `artifact:` line at all held every checker at exit 0.
  `validate` now holds every verdict's `artifact:` to a shape — required, and a 40-hex
  object id or `absent`, on the propagated shape that records a drift; forbidden on every
  other verdict, where it claims a check that did not run; and written twice is malformed
  rather than resolved to the last one. A drift is silenced only by a verdict that
  describes it: one recording what the run reads the artifact as, or one whose record the
  artifact really was between the pin and here.
- **The orphan question is asked of the ground, not of each verdict** — QE7-74. Two of
  this pass's own fixes combined into a wedge: `freshness --cached --write` records the
  *index* blob, `caused()` looks only at committed history, and staging one more edit
  before the commit — `git add -p`, an amend, a formatter — left a verdict naming an id no
  commit ever held. Held verdict by verdict, that was an orphan the moment the ground came
  back, and unrepairable: verdicts append and only append, and the pin above the marker is
  frozen. A ground is now an orphan when *no* propagated verdict against it states a cause
  that happened, which is the question the rule was always about, and the second verdict
  the next run appends repairs the record by ordinary means.
- **"Not caused" is two answers, and only one of them is a forgery** — QE8-82, from the
  second round of the same gate. The wedge above has a sibling the per-ground rule cannot
  reach, because there is no second verdict to reach with: edit a ground, run
  `freshness --write`, commit the ledger, and then *abandon* the edit. The recorded blob
  was never in any commit, the ground is fresh, and `--write` appends nothing more — so
  the discharge was a permanent failure no legal edit could clear, on the documented
  workflow and an author who changed their mind. A record git can **refute** — the blob
  the pin itself has, or `absent` over a history holding no deletion — is the pre-emptive
  forgery and still fails. A record git can only fail to **confirm** now flags. This is a
  weakening of one outcome and is recorded as one; what it does not weaken is what the
  forgery buys, because the suppression rule requires the same `caused` and a verdict
  nothing can confirm silences no drift either.
- **The hook is installed where git actually looks for it** — QE8-83. `core.hooksPath`
  moves the hooks directory, and `hook --install` wrote to `.git/hooks` regardless,
  printing `installed …` and exiting 0 for a file git would never execute: a gate reported
  as installed that does not exist, which is this package's own cardinal failure at the
  surface the sixth pass had just fixed. `git rev-parse --git-path hooks` is the question
  git asks itself, and it also fixes the linked-worktree and `--separate-git-dir` cases,
  where `.git` is a file and the install failed with `Not a directory`.
- **A git that cannot say whether the drift happened says so** — HIGH-54. `ever_drifted()`
  read a `rev-list` that failed, raised or outlived the 30-second timeout as "it drifted",
  and retired the forged-discharge check with no report that it had not run. That is the
  class the fourth pass closed across six findings, reopened in new code. The check now
  reports that the cause *could not be established* and exits non-zero, the way every other
  git question in the package already did.
- **A file the filesystem says may not be written is not written** — HIGH-55. Routing every
  write through a temporary file and `os.replace` — the fifth pass's fix for the truncating
  writes — moved the permission question from the file to the directory, so `sha --write`
  rewrote a mode-444 entry, exited 0, and left the mode still saying the file was
  protected. The funnel now asks the kernel, by opening the target for writing without
  truncating it, before anything is written.
- **`source add` no longer writes outside the project root** — HIGH-56. A symlink planted
  at the content-addressed cache slot sent the stored bytes wherever it led, exit 0, with
  the run naming the in-root path it had not written to. Pre-existing rather than
  introduced. `register_source` and `create_entry` now ask
  `refuse_to_write_outside_the_root`, `append_verdict` requires the root rather than
  defaulting it away, and a test now asks the question of every write site at once, so the
  next one cannot be added without either asking or saying why it does not have to.
- **`init` and `hook --install` no longer write outside the project either** — QE7-72. The
  test above had an allowlist, and both names on it were excused for a reason about the
  *directory* rather than about the write: `init` creates the root, but the root exists by
  the time the source registry lands in it, and `hook --install` must leave the root but
  not leave the git directory. A symlink planted at `ledger/sources.jsonl` or at
  `.git/hooks/pre-commit` took a scaffolded registry and 1690 bytes of mode-755 shell
  outside, exit 0, each naming the in-root path it had not written to. Both now ask, each
  against the boundary its own write has, and the allowlist is empty.
- **A `#` inside a fenced code block is not a heading** — HIGH-58. `section_span()` read one
  as a depth-1 heading, so a `## Observation` section ended at the fence and everything
  below it — including the sentence the claim rests on — was outside the comparison for
  `freshness` and `resolve` both. A Markdown lab note carrying a code snippet is the
  ordinary shape of the artifact this checker compares. The entry parser was blind the same
  way: a fenced `## Verdicts` after the real one replaced it with an empty section, so an
  entry carrying a `refuted` verdict read as `open` (loudly — `validate` reported the
  sections as out of order — but read as `open` by everything downstream of the parse).
- **An option-shaped pin is one defect under one name** — LOW-65.
  `git rev-parse --symbolic-full-name --upload-pack=x` exits 0 and echoes its own argument,
  which is git's parse-options behaviour for an unrecognised double-dash argument and not a
  refname; read as one, a pin beginning with a dash drew an unstable-pin flag *and*
  `resolve`'s "does not resolve", which is the pair LOW-36 was fixed to stop. The answer is
  now read as what `--symbolic-full-name` is documented to print.
- **What the corpus says it proves is what it proves** — HIGH-59. The fifth pass narrowed
  `corpus/README.md`'s claim rather than faking the coverage, which was the honest move —
  but the narrowed claim was also false. An independent AST sweep counted 116 report sites
  rather than the 99 a text grep had found, and 50 of them are caught by neither the corpus
  nor the unit suite: most are the well-formedness guards the README says the unit suite
  holds, and it did not hold the `kind`, `author`, `grade` or `verbatim_sha`-format ones at
  all. Seven were not well-formedness at all but the "not silently passing" class the README
  names outright. `D05-dead-pointer` now carries two more entries — an `entry:` ground
  naming an id that does not exist, and a malformed `search:` line — the four sites a seed
  cannot express (a git that cannot answer, a document that becomes unreadable between two
  reads, `propagate --write`'s own report) have tests in
  `tests/test_sweep_gap_closures.py`, the four unheld enums have tests in
  `tests/test_schema.py`, and the README's Coverage section now names what is held instead
  of asserting a class.
- **A seed that expects nothing is not a seed that passed** — MEDIUM-64. An `expected.json`
  with an empty `expect` array counted as a full pass — `1/1 seeds pass`, exit 0 — over a
  seed that bound nothing to anything. HIGH-45 put a floor under an empty corpus; this is
  the same floor one level down, and it is in `run.py`, which is what an installed wheel
  runs, rather than in a dev-time assertion.
- **An empty expected `message` pins nothing, and says so** — LOW-69. `matches()` tested
  `message.casefold() in report.message.casefold()`, and `"" in x` is always true, so a row
  written `"message": ""` was indistinguishable from one that omitted the field. It is now a
  non-match, and the runner refuses the row outright rather than leaving the seed author to
  find out downstream.
- **The installed pre-commit hook asks freshness about the index** — HIGH-57. MEDIUM-33
  gave `freshness` a `--cached` flag and wired it through `check`; `HOOK_TEMPLATE` never
  got it, so the hook ran `validate --cached` beside four checkers reading the working
  tree, and a drift staged and then undone before the commit went through in silence. The
  hook's own comment now says which three checkers still read the working tree, because
  `resolve`, `references` and `propagate` have no `--cached` to give them.
- **The README says how many seeds there are, and which interpreters CI runs** —
  MEDIUM-60 and MEDIUM-62. `All 62 corpus seeds pass unchanged` stood over a corpus of 75,
  under a regression that only matched a count directly adjacent to the word; the
  Provenance paragraph now separates what was true at extraction from what is true now.
  The CI line named three interpreters where the matrix runs four.
- **The pre-merge gate is as strong as the one it stands in front of** — MEDIUM-63.
  `ci.yml` ran `twine check`, `release.yml` runs `twine check --strict`, so a metadata
  regression only `--strict` catches passed every PR and first failed at the tag.
- **The publishing instructions work for the publish they are for** — MEDIUM-61, and the
  new `RELEASING.md`. `release.yml` sent the operator to a project-settings page that does
  not exist until after a first upload; a never-published project needs the account-level
  pending publisher, and the `pypi` GitHub environment the publish job names had to exist
  beforehand and was written down nowhere. `RELEASING.md` now carries the whole sequence,
  checked against the workflow rather than written from the generic version of it.
- **The Quickstart is run, not illustrated** — LOW-67. The transcript printed
  `0 failure(s)` over commands that produce a validation failure, and its digests were
  placeholders. It now writes its own source file, fills in the entry, and shows real
  digests — and `tests/test_readme_quickstart.py` parses the console block out of
  `README.md` and runs every command in it against a fresh project, comparing output line
  for line, so the transcript cannot drift from the tool again without the suite saying so.
- **The link the CHANGELOG makes is a link the release makes true** — LOW-68. Every
  version heading here points at `releases/tag/vX.Y.Z`, and nothing in `release.yml`
  created a GitHub Release — only the tag and the PyPI upload. A `github_release` job now
  does, after `publish` and under the same tag gate, with `contents: write` held to that
  one job.
- **The rename that completes an atomic write is flushed** — LOW-66. `write_bytes_atomically`
  fsynced the temporary file and not the directory it was renamed into, so the replacement
  survived a crash of the process and not a power loss. Every interruption the suite can
  produce — `SIGKILL`, `RLIMIT_FSIZE` — was already handled; this is the case a test cannot
  reach.

### The self-hosted ledger

- **L0008 is superseded by L0009.** Its pinned section, `freshness.py § "scoped"`, is the
  one the finding-2 fix rewrites, so the ground moved and the claim had to be
  re-established rather than re-pinned — `docs/OPERATING.md` says why a pin cannot be
  edited. The successor states the same rule and the case the fix added: a side that could
  not be read at all is a comparison that did not happen, not drift. Its `verbatim_change`
  says what moved in the verbatim record. The two citations, in `docs/FRESHNESS.md` and in
  the docstring the claim is about, moved with it. This is the first supersession in this
  package's own ledger, and it cost what the manual says it costs: one entry, one verdict,
  two moved citations, and two commits.

### Fixed by the architecture audit

- **An artifact nobody can read is a comparison that did not happen, not a ground that
  moved** — `ARCH-AUDIT.md` finding 2, and finding 6 with it. `chmod 000` on an evidence
  file came back as `has moved`, at exit 0, naming a section the checker had never read:
  git lists a file it cannot open as changed, and the section comparison mapped a text it
  could not get to onto the finding for a text that differs. `freshness` already has the
  `unknown` class for a comparison it could not make, and this was that, misfiled. The
  distinction the fix rests on is narrow and is stated where it is made: bytes that are
  there and are not UTF-8 keep reporting `moved`, because that artifact really did change
  and simply cannot be narrowed to a section; bytes that cannot be reached at all are
  `unknown`. `os.stat` succeeds on a mode-000 file, so the existing file guard could not
  draw that line. The plain-pin branch had the same false confidence and is fixed too.
- **A ledger inside somebody else's repository says its history was not read** — finding
  3, and the defect under the one that was reported. A project is treated as a repository
  when `<root>/.git` is there, so a ledger one directory inside one — `--root <subdir>`,
  or a ledger vendored in a larger project — read as a ledger with no history at all, and
  "no history" is indexed to "nothing to check" everywhere it matters. Measured on such a
  ledger: `sha --write` rewrote the frozen region of an entry that repository had already
  committed and exited 0, and `validate` then reported `0 failure(s)` over it — which is
  the whole of what L0007 says must not happen. Both commands now ask whether there is a
  history nobody looked at, and refuse rather than guess. Nothing adopts the enclosing
  repository: every evidence path in the package is written relative to the ledger root,
  and `git show <pin>:<path>` reads its path from the repository's top.

  With no repository anywhere the exit code stays 0, deliberately: no entry has a creating
  commit, so nothing was skipped. `resolve` and `freshness` exit 1 in the same place
  because they have real pinned pointers they cannot resolve, which is a different
  question — the finding read that difference as a disagreement.

  The predicate is *history*, not *location*, which took a fix-review gate to establish:
  a first version asked whether a work tree existed above the ledger, and since the corpus
  stages its seeds through `tempfile`, a `TMPDIR` inside any repository took the corpus
  from 79/79 to 18/79. A directory that merely sits under a work tree, untracked, has no
  history and nothing was skipped. The walk is the filesystem's rather than
  `git rev-parse --show-toplevel`, because that answers with the directory it was run in
  when `GIT_DIR` is set — which every git hook exports — and because a project that is
  not under version control should cost no git process at all. And a git that cannot
  answer is reported rather than read as "there is no repository", which is the same rule
  as everywhere else in this checker and was the first version's own worst defect. And
  every repository above the ledger is asked rather than only the nearest: stopping at the
  first was a false negative of the same shape, where one `git init` in a directory
  between the ledger and the repository that committed it turned the frozen-region check
  off without a word.
- **An artifact whose directory cannot be searched is not a withdrawn ground.** The
  presence check was `Path.is_file()`, which raises PermissionError out of pathlib on 3.12
  — `freshness` exited 2 having printed nothing, and `check` printed four checkers and
  silently omitted the fifth — while on 3.13 it swallows the EACCES and answers False,
  which is a confident `withdrawn` for a file nobody could look at. `os.stat` is asked
  directly, and gone, not-a-regular-file and could-not-be-reached are three answers rather
  than two.

### Faster by the architecture audit

- **`freshness` asks git about a pointer once.** `orphans()` re-ran the whole drift
  comparison for every ground `run()` had already evaluated — 4 to 6 git processes per
  pinned pointer, for an answer that cannot have changed inside one run — and two entries
  resting on the same artifact asked twice over. Measured on the 12-entry example research
  repository: `freshness` 17 git processes to 8, `check` 31 to 22.
- **`check` parses the entries once rather than five times.** Each checker loaded them
  itself and each command loaded them a second time for the count in its summary line.
  The checkers now take the entries the caller already has. Under `--cached` there are two
  lists and not one, because `validate` and `freshness` read what is staged while the
  other three read the working tree, and that difference is what `--cached` is for.
  `load_entries` calls per `check`: 5 to 1. The memo is keyed on the whole pointer and not
  on its target, and `check`'s two lists are held by tests rather than by care: a
  target-keyed memo and a swapped or collapsed `--cached` split each passed the whole
  suite and the whole corpus, and the first silently loses a finding on this package's own
  ledger.
- **L0005 is superseded by L0010**, at an unchanged verbatim record: `cmd_validate` is one
  of its two grounds and the change edits it, so the ground moved while the claim did not.
  Both supersessions this package has now cost were forced by a pinned section changing
  for a reason the claim did not care about, and both pinned a *caller* — the code that
  follows the rule — rather than the code carrying it. Recorded in `ARCH-AUDIT.md` as
  something to weigh, not as a defect in the tool.
- **A section pattern can name one key of a TOML table, and L0002 is superseded by L0011
  on that ground.** `toml` names a table, which was the finest ground available for a
  claim about two settings: L0002 asserted no runtime dependencies and a 3.11 floor and
  rested on the whole 31-line `[project]` table, so adding a classifier or editing the
  description moved a claim about `dependencies`. Measured on this file: `[project]` 31
  lines, `dependencies` 3, `requires-python` 1. The successor's `verbatim_sha` is
  byte-identical to its predecessor's, which is the record saying the claim did not move
  and only its ground narrowed. The three lines rather than one are a boundary artefact
  and are stated rather than hidden: one pattern decides both ends of a section, so the
  span runs to the next key assignment and takes the `[project.optional-dependencies]`
  header with it — one line of exposure where there were thirty, and arguably the right
  line, since it is where the runtime dependencies end.

### Changed by the architecture audit

One structural and performance pass, recorded in `ARCH-AUDIT.md` with its numbers and
with what it found and left open.

- **`validate` reads a ledger's history in three git processes**, not two plus one per
  revision for every entry. `check_history` asked `git log -- <entry>` once per entry, and
  each of those walks every commit in the repository, so the cost was the product of
  entries and commits: `check` over a thousand-entry, thousand-commit ledger took 5m18s.
  One walk of the entries directory and one `cat-file --batch` answer the same questions
  in 2.79s, and the process count no longer grows with the ledger. `validate --cached`,
  the pre-commit hook's path, reads the index the same way — 1,005 processes to 5 at that
  size. One difference in what is compared: the walk is a full-history walk — `-m` turns
  history simplification off — so a merge is listed under an entry whenever the file
  differs from either parent, and the commits on a line a merge resolution discarded are
  listed too. A verdict a branch committed and a merge resolution left out is caught, and
  stays caught, since the removal is in the history — and it is attributed to the merge:
  the append-only check compares each revision with its own parents, not with whatever
  the walk listed next to it, which under full history can be a sibling that never held
  the verdict. The frozen-region check is unchanged. Measured
  and recorded in `ARCH-AUDIT.md`, which also records what the same pass found and left
  open. The rewrite first landed without the text-level comparison of the frozen
  region — a preamble edit was reported with the line-endings message, and under
  `--cached` passed outright when the index held no blob for the entry — which the
  fix-review gate found and `tests/test_immutability.py` now pins, both cases checked
  red against the code that dropped it.

### Methodology

Recorded as methodology changes, with the seeds named, under this file's own rule.

- **The corpus runner matches a report's place exactly, and one row is satisfied by one
  report.** A row naming a prefix of the place, or a place two rules both fail at, was held
  up by whichever rule still existed: deleting the terminal-status rule or the
  `resolves_when` rule from `validate` left the corpus at 72/72. A row may also name a
  substring of the report's `message`, for a rule the place alone does not identify.
  `D17-verdict-after-terminal`'s second verdict is `contested` rather than a bare
  corroboration, so the terminal-status rule is the only rule failing at that place, and
  `D19-prediction-without-credence`'s first row is split into the two rules it always
  claimed to bind. No seed's outcome moves; what each row *proves* does.
- **A run that checked nothing exits non-zero.** An empty corpus, or a seed filter matching
  no seed, printed `0/0 seeds pass` and exited 0 — and that command is the release
  workflow's proof that the built artifact still works, so a distribution that shipped no
  seeds would have passed the gate.
- **Three seeds**, for rules no seed held: `D50-document-that-is-not-text` (a document the
  reference checker could not open — the third pass's HIGH-17 fix, which had unit tests and
  no seed), `D51-pin-git-cannot-classify` (a ground the freshness checker could not
  examine, which is this package's stated reason to exist), and
  `D52-mid-sentence-start-without-elision` (the half of D06's class nothing covered). The
  corpus is 75 seeds, and the corpus README now says which rules it does *not* hold up —
  a mutation sweep found most of `validate`'s well-formedness guards survive their own
  deletion. That change said the unit suite held those; the sixth pass measured it and
  found four of the named ones held by nothing, which is HIGH-59 above.
- **One seed**, `D53-laundered-freshness-discharge`, for HIGH-53: a discharge written
  before its ground moved, followed by a commit that edits the artifact and a commit that
  puts it back. It is the forgery the orphan rule exists to refuse, in the history that
  used to launder it, and it fails against the unfixed checker at `commit 04` and passes
  against the fixed one. The corpus is 76 seeds.
- **`D20-bad-ids-and-archived-citation` pins every edge of the archived-id width.** Its
  document planted `C012` — three digits — which is the one width the quarantine rule
  could match and a width no entry id can have, so the seed passed while the rule was
  unreachable from every id the schema mints. It now plants `P0007` and `P00042` beside
  it, and a two-digit `C42` written as a figure label that must *not* be read as an id;
  the row names the three matches in its `message`. Measured: `\d{3}`, `\d{4}`, `\d{3,4}`,
  `\d{2,}` and `\d{5,}` each take the corpus to 78/79, where before only the first two
  did. No seed's outcome moves; what the row proves does.
- **The corpus runner stages by content, not by timestamp.** `shutil.copytree` preserves
  mtime, and git's index skips reading a file whose (mtime, size) pair is unchanged, so a
  history seed that edits a line without changing its length staged a change git did not
  see: `git add -A` picked up nothing and the run died with `nothing to commit`. Found
  while writing `D53`, whose drift is `0.041` to `0.991`.

### Fixed by the ninth adversarial pass

The pass ran over the example portfolio and the documents that advertise it, and found two
rules in `src/` that could not do what they said. Both had shipped because the only
assertion over them was `0 failure(s)`, which an inert rule satisfies.

- **`document-excludes` is matched as a glob, the way `documents` is** — `docs/audits/0.1.0.md`
  QE9-95. It was substring containment: `"docs/draft-*.md"` is not a substring of
  `docs/draft-scratch.md`, so both exclusions in the example portfolio were inert, and
  `examples/templates/documentation-repo/docs/draft-scratch.md` — a file whose text says it
  is excluded from citation scanning — was scanned. The two keys sit one line apart in every
  template this package ships and nothing had ever said they differ, so they no longer do:
  `*` and `?` stop at a separator, `**` spans any number of segments, matched
  segment by segment against the normalized path from the project root — an exclusion
  written `./docs/draft-*.md`, in the same hand as the inclusion beside it, is the same
  defect one level down. A directory that a `documents` pattern reaches and cannot list
  is still reported unless an exclusion takes *everything* under it, which only a pattern
  ending in `*` or `**` does: a pattern that takes some of what is under an unlistable
  directory leaves the rest unchecked, and an unchecked document nobody was told about is
  the one report this package may not lose. Both excluded example documents now carry a
  citation that would fail if it were scanned — an archived `Z0001` in the repository that
  quarantines the `Z` series, an entry that does not exist in the other — so the exclusion
  is load-bearing and the regression names a document rather than only counting them. A
  count-delta alone passes over an exclusion that removes the wrong file; a test that
  asserted `0 failure(s)` is what passed over the inert exclusion in the first place.
- **The archived-prefix rule can fire on the ids the schema mints** — QE9-105. The pattern
  was `[<prefixes>]\d{3}\b`: exactly three digits, with a word boundary that cannot fall
  between the third and fourth. Every entry id is a letter and four digits, so the
  quarantine — a documented rule, with a corpus seed — could not match a single id the
  schema permits. `Q001` failed the check; `Q0001` passed it. The width is now three or
  more, which is what `CITATION_RE` already tolerated, because the rule reads prose and an
  id written a digit wide of the schema is still a citation of the archive.

### Fixed by a consistency review of the ledger's own entries

The review read all 153 entries against each other rather than against the code, looking
for pairs that disagree. It found one, and the disagreement was a real defect: two entries
stating the same exemption with two different status sets, neither citing the other, so no
checker could see the gap between them.

- **A dependent's own terminality, not its fallenness, exempts it.** `references` and
  `propagate` both tested an entry's own status against `FALLEN` — `refuted`, `superseded`,
  `retracted` — where the rule they were implementing is about *terminal* status, which also
  includes `non-comparable`. For an entry that is `non-comparable` and cites a ground that
  has since fallen, `references` reported an act it is impossible to repair (the Grounds sit
  in the frozen region) and `propagate` demanded a contested verdict that `validate` refuses
  as one following a terminal verdict — so `propagate --write` wrote exactly what `validate`
  rejects, and `check` could not be made to pass in either direction. `check` runs in the
  pre-commit hook and in CI, so one such entry wedged the repository. Both tests are now
  `TERMINAL`, matching `freshness`, which already drew the line there. The target side of
  each rule stays `FALLEN`: what propagates is a ground that fell, and what exempts is the
  entry's own terminality. New known-good seed `K24-non-comparable-dependent-needs-no-flag`;
  no existing seed's expected outcome moved. Superseded L0020 and L0043, whose Scope named
  the narrower set.

### Added by the same review

- **`validate` flags an entry that scopes itself to the fallen statuses and then argues
  from terminality.** `FALLEN` and `TERMINAL` are nested — the second is the first plus
  `non-comparable` — and they are one word apart in prose. An entry written that way
  states a rule over one population in its Scope and a rule over another in its Warrant,
  and it is the Warrant a person implements, which is exactly how the defect above got
  written. A flag rather than a failure: the test is on words rather than on sense, and
  widening the Scope and narrowing the Warrant are both legal repairs. Seeds `D57` and
  `K25`, the second being the near-negative that keeps the rule from firing on every entry
  that names a status at all. It flags nothing in this repository's own 155 entries or in
  the 105 entries the corpus holds, and it flags L0020 as that entry stood before the fix
  above.

  This is a check *within* one entry. The gap the review was looking for is between
  entries, and that one is not mechanically decidable here: two entries that name nothing
  of each other are out of range of all five checks by construction, and a heuristic over
  their Scopes flags 261 pairs on this ledger to find two worth reading. Where the schema's
  own controlled vocabulary appears, consistency can be checked; elsewhere it cannot, and
  saying so is more useful than a checker nobody trusts.

### Added for the between-entries half

The two pieces the entry above says are missing. Neither is a checker, and that is the
point: what is mechanically available about two entries nobody has read together is that
they are *near* each other, and near is not inconsistent.

- **`claims-ledger neighbours`** — an authoring-time lookup, asked of one entry, one entry
  file, or one ground pointer written as an entry would write it. It answers with the
  entries that share an evidence span — the same type, path and section, with the pin
  dropped, because two entries about the same function were written at different commits —
  or whose cohort words nest inside another cohort's, in either direction. Containment
  rather than a similarity threshold: nested Scopes are the shape that has actually gone
  wrong in this ledger, and a score tuned until it surfaced that shape would be a number
  chosen to fit the one example it came from.

  It reports nothing, writes nothing, always exits 0, and `check` does not run it. Asked
  of the whole ledger at once the same heuristic names **327 pairs over 169 entries**; asked
  one entry at a time it answers with a **median of 3**, a mean of 3.9, at most 12, and 21
  entries with none. That distribution is not written down anywhere but here: it is asked
  of the installed package with `claims-ledger neighbours --count`, which runs the same
  lookup over every entry. `claims-ledger new` prints the command for the entry it just
  scaffolded, because nothing downstream asks the question and that is the only moment it
  has.

  Each answer names the relation the ledger already records between the pair — a ground
  either way, or a supersession — and orders the pairs with none first. A pair somebody has
  already read is not the pair the lookup exists to surface.

  The answer then writes out the ground line that would record a distinction, once for
  every pair it found no relation for, so acting on one is a paste rather than a
  recollection. That is as far as a lookup goes: the line is the same text whichever
  neighbour it names, and whether to write it at all is the judgement being handed over.

- **A `distinguishes` act**, so that reading a pair lands in the ledger once instead of
  being redone by every reader. One entry performs it on another; a document may not,
  because a document has no Scope to hold apart from anything, and the pattern that reads
  documents is built from the citation acts alone. It is legal against a target of any
  status — it is a claim about two Scopes rather than about a truth, and Grounds are frozen,
  so an act somebody else's verdict could make illegal would be a failure with no repair.
  It propagates nothing when its target falls. And it is not support: an entry whose every
  ground is one has stated a difference and rested on nothing, and it is not a motivation a
  hypothesis can be built on. Seeds `D58` and `K26`.

- **`references` reports a parenthesis shaped like a citation whose act is not one.**
  `CITATION_RE` is built from the four citation acts, so a mistyped `cites-as-liv` — and
  `distinguishes`, written in a document where it does not belong — matched nothing, and no
  other rule reads documents: the sentence sat in a checked document as text nothing looked
  at. The rule is narrow. An id in a parenthesis of its own, or named in running prose, is a
  document mentioning an entry rather than citing it, and is left alone. Seeds `D59` and
  `K27`. It fires on nothing in this repository's own documents or in the corpus.

- **`ENTRY_ACTS` is a declared export**, beside `ACTS`. The two lists differ by exactly the
  new act, and the difference is the one a writer has to get right — what a document may
  write against what a ground may carry — so it is printable rather than memorable:
  `python -c "from claims_ledger import ACTS, ENTRY_ACTS; print(ACTS, ENTRY_ACTS)"`.
  L0170 holds it, because the shipped skills tell a reader to print the vocabulary rather
  than remember it, and that instruction is only true while both lists are exported.

- **The shipped agent skills and hooks cover all of the above.**
  `choosing-a-citation-act` gains the act, the two lists and the parenthetical finding;
  `tagging-prose-with-claims` gains the lookup at the point a ground is chosen and the
  Scope-versus-Warrant flag from the previous release note; `repair-a-drifted-pin` gains
  the supersession no checker asks for. `ledger-orientation.sh` hands over `neighbours`
  and says which commands are checkers and which only answer; `status-guard.sh` reports
  the not-a-citation-act finding on its own throttle and, where a project configured it, the
  misplaced-citation one on a throttle of its own; `pin-guard.sh` names the lookup at
  the moment a new claim is being written.

  A third correction went with them. Measured over the package's Python documents, 48 of
  186 citations sat in a module docstring and 11 in a section other than the one their
  entry pins — a habit the guidance was teaching: the placement section framed the choice
  as a cost trade with drift on one side, and drift was the only quantified thing in it.
  It now says the citation goes inside the section its entry pins, that the flags this
  causes are the mechanism working, and that a module docstring is for a claim about the
  file as a whole. Two mechanical traps are named with it: a comment above `NAME = ...`
  belongs to whatever is defined before it, so a citation there sits outside the span it
  looks adjacent to; and `pin-guard.sh` was telling sessions the pre-commit hook would
  refuse a drifted pin, which it does not — `moved` is a flag and exits 0. Saying so
  taught that drift is a block to clear rather than a report to act on.

  Two rules were added to all of them at once. **An entry that is owed is written in the
  pass that owes it** — prose that promises something and cites nothing passes every
  check, so nothing comes back for a deferred entry, and the citation sits inside the span
  the entry pins, so a later pass pays the two commits again plus the drift its own
  citation causes. And **hand over the line, not the homework**: where a repair has a fixed
  shape, write it out. Printing the text is not deciding to write it.

- Superseded **L0136**, whose cohort named four checkers while its metric counted over the
  package. `freshness`, the authoring side and the command line already read entries through
  the same parser, normalization, fingerprint and status derivation when it was written; the
  neighbours lookup is the reader whose arrival made the gap worth repairing rather than
  restating. The successor states it over every module that reads an entry.

  It was `claims-ledger neighbours` that found it, on its first run over this ledger:
  L0136's cohort nests inside L0005's and L0010's.

### Added, and off unless a project asks for it

- **`citation-placement`** — a setting, not a sixth checker. `references` gains a rule
  that a citation sits inside the section its entry pins, at `off`, `flag` or `fail`, and
  `off` unless the project says otherwise. A rule that reports fifty sites the day it
  ships is one its readers learn to scroll past, so a project turns it on when its
  citations are ready for it; this one is on and failing.

  The question is narrow, and every part of the narrowness carries weight. It is asked
  only of a citation in a document the cited entry *also* rests on, by a sectioned ground
  — then there is a span in this very file the claim is about, and the sentence promising
  it belongs there. A citation of an entry grounded elsewhere is asked nothing. An entry
  resting on several sections of one file satisfies the rule from any of them.

  **Asked at write time too.** `claims-ledger sha --write` reports it for the entry in
  front of you, which is the earliest point it can be asked at all: the citation is
  written in the commit before the entry, so until the Grounds exist there is no span to
  be outside of, and the fingerprint is the step between the two. It prints and does not
  fail — that command's exit code answers whether the fingerprint was written, and
  `references` is what refuses the commit. One function answers both callers, so the two
  cannot come to disagree.

  Seeds `D60` and `K28`, and every other seed is a near-negative by construction — their
  documents and their grounds name different files, which is the case the rule must never
  fire on. Making the two expressible needed a change to the corpus runner: evidence paths
  resolved against the corpus root while documents came from the staged seed, so no seed
  could name one file as both. The shared `fixtures/` and `sources.jsonl` are now staged
  into the seed and everything resolves locally.

  It found something on its first run that the sweep's own script had missed:
  `pyproject.toml` cited L0011 from a comment above `dependencies = []`, and a `toml-key`
  section starts at its own line — the same trap as in Python, in a file that script never
  read because it only looked at `.py`.

### Release

- Every action in both workflows is pinned to a commit, including
  `pypa/gh-action-pypi-publish@release/v1` — a mutable branch, in the one job holding
  `id-token: write`.
- The sdist is installed into a clean environment and made to run the corpus before
  publication, as the wheel already was. An sdist is what pip falls back to wherever
  wheels are refused, and `twine check` reads its metadata rather than running it.
- **The sdist ships the trees its own tests read, and is made to pass them.** The
  `include` list is gitignore-style, so an unanchored `src` or `docs` matched at any
  depth: the tarball carried `tests/test_examples.py` and 10 of the example tree's files —
  the ones that happened to live under a directory with one of those names — and four of
  its tests failed inside it on a missing `examples/FEATURES.md`. Nothing would have caught
  it; the corpus rides in the package rather than in the tarball, and `twine check` reads
  metadata. `/examples` is now named in the list, and `release.yml` extracts the built
  sdist and runs `pytest` there against the copy installed from a clean environment.
  `docs/audits/0.1.0.md`, QE9-94.
- **That gate has an oracle inside the distribution, and the step that runs it is asserted
  line by line.** Nearly every test that reads a repository file reads it through a helper
  that turns "absent from the distribution" into a skip, because it cannot tell that from
  "not a checkout" — so deleting `docs/` from an extracted sdist left the gate at exit 0
  with counts identical to a healthy tree, and `LICENSE`, `QUALITY.md` and `CHANGELOG.md`
  differed only in a skip count nothing pinned. A floor on skips would have caught two of
  those four. One test now reads the `include` list from the tree it is running in and
  requires every entry to be present. Separately, the guard over the workflow asserted
  only that the six letters `pytest` appeared after the extraction, which four mutants of
  the step satisfied — running the checkout's suite instead, `--collect-only`, `|| true`,
  and the literal `echo pytest skipped`. QE10-1 and QE10-2.
- **Seven tests that had never run outside a checkout now run.**
  `tests/test_corpus_integrity.py` derived the repository root from the *installed*
  module rather than from the test file, so inside a source distribution that carries all
  of them — the report-site inventory guard and the four mutation-anchor guards among
  them — every one skipped. QE10-3.

### Known limits

- Tested on Linux and macOS. Windows is neither tested nor claimed: the installed hook is
  `#!/bin/sh`. Every write path now keeps a file's own line endings and the frozen region
  is compared as bytes, so the translation that used to sit between them is gone — but
  that is reasoning, not a run on Windows, and this line says which of the two it is.
- The tool does not decide whether a claim is true. See "What this does not do" in the
  README.

### Operating a pinned ledger

- **The advice that would have prevented a badly-chosen ground is on the path that
  writes an entry, not only on the path that repairs one.** The scaffold's Grounds
  placeholder asks for "the narrowest section that carries the rule, never a caller that
  follows it", `claims-ledger new` prints what a wider ground costs, and this document
  gains a "Choosing a ground" section stating both failures — a ground on a caller goes
  stale for every edit to that caller for the rest of its life, and a ground wider than
  the claim goes stale when something beside it changes — with `section-patterns` named
  as the instrument for the second. The repair path gains the step that is actually
  skipped: ask what moved before writing the successor, because a successor carrying the
  same wrong ground buys one more supersession on the next unrelated edit, and
  `sha --write` computing a byte-identical `verbatim_sha` is the tool already saying the
  claim never moved and only its ground did.

- `docs/OPERATING.md` — running a ledger that pins commits over time. It states the one
  hazard nothing else in the package named: a squash merge, a rebase merge or a force-push
  removes the commit a `code:` or `toml:` ground pins, at which point every ground pinned
  into it fails at once and the only repair is a supersession per entry. It also states the
  two-commit shape for landing an entry — including why the pre-commit hook must refuse the
  first of the two, which is not conservatism but an impossibility: at commit one a citation
  to an entry arriving in the next commit and a citation to an entry that never existed are
  the same bytes — and the order in which a drifted claim is repaired.
- `resolve` names why a pinned pointer failed rather than only that it did. `does not
  resolve` was one sentence for a commit dropped by a rewritten history and for a path that
  was renamed, whose repairs differ by a supersession per entry. It now separates: the pin
  names no revision and the file is not in the tree; the pin is not a commit but some other
  object; the commit is there and the path is not; git has both and still did not answer;
  the name is a prefix of several objects; the clone is shallow, where an absent object
  cannot be told from a rewritten one; and, only when the rest are excluded, that the
  repository has no such commit.

  Every question it asks goes through `git_call` rather than `git()`, which is the whole of
  its honesty: `git()` folds "no" and "could not answer" into one `None`, and a diagnosis
  built on that folding states as fact what it never established. A git broken only in
  `show` passes the `unasked` gate — which asks `rev-parse --git-dir` and nothing more —
  and was told, of a healthy commit and a present path, that the path was not in it.
  `tests/test_git_degradation.py` holds that case, the shallow clone and the non-commit
  object; the ambiguous short name was measured by hand against a repository built to
  contain one, since 120,000 objects is not a fixture.
- Three corpus seeds for the same ground: `D54-pin-names-a-commit-that-is-gone`,
  `D55-pin-resolves-but-the-path-does-not` (its near-negative — the repair is one pin, not a
  supersession per entry) and `D56-unpinned-ground-with-no-file`, which is staged outside a
  repository so that a diagnosis reaching for git reaches out of the seed and is caught.
- `examples/agent-harness/` — two coding-agent hooks this repository runs on itself, with
  the thirteen expected verdicts that hold the merge guard to its matching. Examples, not
  package: not in the wheel or the sdist, and they need `jq`, which the package does not.

[0.1.0]: https://github.com/Ybx-jp/claims-ledger/releases/tag/v0.1.0
