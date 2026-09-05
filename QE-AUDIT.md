# Pre-publication audit — claims-ledger 0.1.0

Adversarial quality pass ahead of the first PyPI release. 2026-09-05.
Findings only: no `src/` change was made. Every item below was reproduced by hand
against an **installed wheel**, not against the source tree.

Suite went **235 → 535 passing, 9 strict xfails**. Each xfail records a confirmed
bug and flips to a failure the moment that bug is fixed, so none of this can rot
quietly.

> **Disposition — 2026-09-05, after this audit.** Every finding below is fixed: HIGH-1
> through HIGH-3, MEDIUM-4 through MEDIUM-7 and the LOW-8 packaging and documentation
> items. The nine xfails flipped and are kept as the regression tests for their fixes,
> and MEDIUM-4, MEDIUM-5, MEDIUM-6 and the `ledger`-names-a-file row of MEDIUM-7 — which
> the audit reported without a test — have tests now, each checked to fail against the
> unfixed code. The suite is 548 passing, no xfails, corpus 62/62 from an installed
> wheel. HIGH-2 took the operator's agreed fix: a `ConfigError` naming the key and the
> path. What follows is the audit as it was written, unedited; the changes are in
> `CHANGELOG.md` under Unreleased.

---

## Verdict

Publishable once the two High items are dealt with. The packaging itself is in
better shape than most first releases; the defects are in input handling at the
edges, not in the thing the package is for. No defect found produces a **false
pass** — every failure path exits non-zero. For a tool whose entire value is
refusing to say "fine" over something it did not check, that is the property that
mattered most, and it held everywhere it was tested.

---

## Verified good

| Claim | How it was checked |
|---|---|
| `claims-ledger` is free on PyPI | HTTP 404 on both hyphen and underscore spellings |
| `twine check --strict` | passes on wheel and sdist |
| Corpus data ships and works from an installed wheel | run from a scratch dir, 62/62, on three interpreters |
| Zero runtime dependencies | asserted from `importlib.metadata.requires()` inside the cell |
| No leaked host paths, e-mail or secrets in artifacts | grep over unpacked wheel and sdist |
| No `__pycache__`, no stray executable bits in the wheel | zipfile inspection |
| Read-only install dir (system/root install) | `chmod -R a-w site-packages/claims_ledger`, corpus still 62/62 |
| Missing `$HOME` | `env -u HOME`, corpus still 62/62 |
| Pre-commit hook end to end | blocks an incomplete entry with a real diagnostic; allows a clean scaffold |
| `pip` 24.0 and newer | clean install + run |

`pip` 23.0.1 fails, but that is pip's own `pkgutil.ImpImporter` breakage on Python
3.12 and not attributable to this package.

## The interpreter matrix

`requires-python = ">=3.11"` and three `Programming Language :: Python :: 3.x`
classifiers are a promise to strangers. This development box has only 3.12, so the
promise was unverified. It was run in a throwaway VM booted through
`thalamus-notes/ops/cell-producer`, with a new reusable caller at
`thalamus-notes/ops/qe-pypi-cell/`:

| | 3.11.16 | 3.12.14 | 3.13.15 |
|---|---|---|---|
| wheel install, zero runtime deps | pass | pass | pass |
| version agreement across `__version__` / metadata / artifact | pass | pass | pass |
| console script and `python -m claims_ledger` | pass | pass | pass |
| every name in `__all__` resolves | pass | pass | pass |
| corpus from installed wheel, run from elsewhere | 62/62 | 62/62 | 62/62 |
| full first-use journey (`init`/`new`/`status`/`hook`/`check`) | pass | pass | pass |
| `--help` on all 12 subcommands | pass | pass | pass |
| sdist installs, its shipped tests pass | 242 | 242 | 242 |

51/51 checks. Clean shutdown, per-file manifest verified, no divergences.

---

## Findings

### HIGH-1 — a FIFO named `*.md` hangs the tool forever

    mkfifo ledger/entries/A0001-fifo.md
    claims-ledger status        # never returns; killed at timeout, exit 124

Affects everything that loads entries (`status`, `validate`, `check`, …). A
directory or a dangling symlink named `*.md` is already handled cleanly; a FIFO is
not. In a pre-commit hook this wedges the commit with no output at all.

*Suggested fix*: `stat` the candidate and skip or refuse anything that is not a
regular file, in the same place the existing not-a-file cases are handled.
*Test*: `test_a_fifo_named_dot_md_does_not_hang_the_tool`.

### HIGH-2 — config paths escape the project root

    # claims-ledger.toml
    ledger = "/tmp/EVIL"          # or "../../../outside-root"

    claims-ledger --root /tmp/proj new escape-attempt
    → wrote /tmp/EVIL/entries/A0001-escape-attempt.md      (exit 0, no warning)

`Path(root) / "/abs"` discards `root` outright — pathlib semantics. `..` traversal
is likewise never normalised or contained. Applies to `ledger`, `entries`,
`registry` and `cache`, since all four are built the same way in
`config.from_table`, and to every write path (`new`, `init`, `source add`,
`sha --write`, `propagate --write`).

The realistic shape of this is cloning an untrusted repo that carries its own
`claims-ledger.toml`. It is not remote code execution, but for a tool whose thesis
is confinement and verifiability, unbounded config paths are a design gap rather
than a rough edge.

*Agreed fix (operator decision, 2026-09-05)*: **refuse with a clear error.** Any
of those four keys resolving outside `root` raises `ConfigError` naming the key and
the path.
*Tests*: `test_an_absolute_ledger_path_cannot_escape_the_project_root`,
`test_a_traversal_ledger_path_cannot_escape_the_project_root`.

### HIGH-3 — `status` reports success over a root that does not exist

    claims-ledger --root /totally/nonexistent status
    → "no entries under ledger/entries"                    exit 0

    claims-ledger --root /totally/nonexistent validate
    → "no entries directory at ledger/entries; nothing was checked…"   exit 2

`cmd_status` is the one command that never calls `guard()`. That function's own
docstring names this exact failure as the thing the tool must never do — "`0
failure(s)` printed over a check that never happened is the one report this tool
must never produce". `status` reproduces it.

*Suggested fix*: call `guard()` from `cmd_status` as the other five commands do.
*Test*: `test_status_treats_a_missing_entries_directory_like_validate_does`.

### MEDIUM-4 — git output is decoded with the locale encoding

`src/claims_ledger/schema.py:593`

    out = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=check
    )

`text=True` with no `encoding=` decodes with the locale's codec. Under a non-UTF-8
locale that Python does not coerce:

    PYTHONUTF8=0 LC_ALL=C PYTHONCOERCECLOCALE=0 claims-ledger validate
    → claims-ledger: unexpected UnicodeDecodeError: 'ascii' codec can't decode byte 0xc2
    → claims-ledger: this is a bug. Please report it at …            exit 2

Any entry containing the schema's own `·` pointer separator triggers it. The
frozen-region and append-only checks — the core immutability claim — are what
break, and 4 of 62 corpus seeds fail. It **fails loudly and never passes falsely**,
which is why this is Medium and not High.

*Suggested fix*: `encoding="utf-8", errors="replace"` on that call.

### MEDIUM-5 — the failure diagnostic itself crashes on an ASCII stdout

`src/claims_ledger/corpus/run.py:228` prints `f"   · {ln}"`. With an ASCII stdout
encoding this raises `UnicodeEncodeError` — so the crash lands precisely on the
path that was about to explain why a seed failed, replacing the diagnostic with
"this is a bug". The pass path has no `·` and so never shows it.

*Suggested fix*: an ASCII bullet, or reconfigure stdout to UTF-8 at entry.

### MEDIUM-6 — `corpus` does not guard a missing `git`

    PATH=/empty claims-ledger corpus
    → claims-ledger: unexpected FileNotFoundError: … 'git'
    → claims-ledger: this is a bug. Please report it at …            exit 2

The checkers guard this properly via `git_available()` and print "git is not on
PATH, so the frozen-region and append-only checks did not run". `cmd_corpus` does
not, so the advertised self-proof tells a stranger without git to file a bug
report.

### MEDIUM-7 — smaller input-handling gaps

| | Repro | Observed |
|---|---|---|
| Unicode digits pass as ASCII | `new some-slug --id A０００１` | accepted; `ID_RE`'s `\d` matches any Unicode Nd |
| …in `credence` too | `credence: ٠.٥` | `float()` accepts it, treated as a valid 0.5 |
| `--root ""` | `claims-ledger --root "" status` | silently uses cwd (`root or Path.cwd()`) |
| 300-char slug | `new <300 chars>` | `unexpected OSError: File name too long` |
| entries dir is a symlink loop | `os.symlink("entries", entries)` | `unexpected RuntimeError: Symlink loop` |
| `ledger` points at a regular file | `ledger = "not-a-dir"` | `unexpected NotADirectoryError` |

The last three are the catch-all handler firing where a specific `AuthoringError` /
`ConfigError` belongs. Anything printing "this is a bug, please report it" for an
ordinary user mistake is a defect in its own right.

### LOW-8 — packaging and docs

- **README's `[docs/SCHEMA.md](docs/SCHEMA.md)` is relative** → renders as a 404 on
  the PyPI project page. Use an absolute GitHub URL. (Line 102; line 249 refers to
  it in backticks, which is fine.)
- **`CHANGELOG.md` is not in the sdist**, though `[project.urls]` declares a
  Changelog. `[tool.hatch.build.targets.sdist].include` omits it.
- **`docs/SCHEMA.md` is not in the wheel**, though the package docstring and the
  `--grade` help text both point a user at it. Either ship it or point at the URL.
- **No publish workflow.** CI builds and checks the wheel but nothing releases it;
  consider a tag-triggered job using PyPI Trusted Publishing so no long-lived token
  is needed.

---

## What was tested and held

Beyond the failures above, these properties were asserted and passed, and are now
permanent tests:

- **Idempotency** — `propagate --write`, `sha --write`, `init`, `source add`,
  `hook --install` all reach a fixed point; every writer satisfies its own checker
  afterwards.
- **Ordering independence** — identical reports across reversed load order on all
  58 non-history seeds.
- **Normalization invariance** — CRLF, trailing whitespace, NFC/NFD verify
  identically; `verbatim_sha` is stable under what the schema calls irrelevant and
  changes under what it calls relevant.
- **Metamorphic corpus** — a semantics-preserving transform over all 62 seeds
  leaves every expected verdict unchanged.
- **Append-only / monotonicity** — an appended verdict never moves an unrelated
  entry's status; post-terminal verdicts and frozen-region edits are caught.
- **Cross-checker consistency** — `check` equals the four checkers run separately,
  and its exit code is the max of theirs.
- **Crash and concurrency** — truncation at five cut points, a read-only entries
  directory, and four concurrent `propagate --write` processes all leave a
  parseable ledger and never print an internal error.

Two suspected bugs were **disproved** on measurement and are recorded as
regression tests rather than reported as defects: CRLF frontmatter parsing (saved
by universal-newlines translation on every real read path) and iteration-order
dependence in the cross-entry checkers.

One undeclared behaviour, neither promised nor a bug: straight and curly quotation
marks both resolve as span delimiters, but `normalize()` maps neither to the other,
so switching style changes `verbatim_sha` while the quoted text is unchanged.
Documented in a test rather than asserted either way — worth a line in
`docs/SCHEMA.md` if it is intended.

---

# Second pass — 2026-09-05, against the fixes

The nine findings above are fixed, and the fixes were then attacked in their own
right. Nine new defects, recorded as strict xfails in section F of
`tests/test_hostile_inputs.py`. Suite is **548 passing, 9 strict xfails**. Every
case below was reproduced against the working tree by hand before it was written
down; none is inferred from reading.

## What held

| Fix | Attacked with | Result |
|---|---|---|
| `confined()` | absolute value, `..` value, `..` nested under a legal `ledger`, `""`, wrong TOML types | all refused with a `ConfigError` naming the key |
| entry reads refuse non-regular files | FIFO, directory, dangling symlink, symlink loop, mode-000 entry | clean `rc 2`, no hang, no `unexpected` |
| ENAMETOOLONG on slugs | boundary swept 240→5000 bytes | flips at 247, exactly `NAME_MAX`; message is specific |
| `soften_output_encoding()` | `LC_ALL=C PYTHONIOENCODING=ascii` over `validate` and the whole corpus | corpus 62/62 under an ASCII locale |
| `DECIMAL_RE` | `1e400`, `Infinity`, `1_0`, `0b1`, `+.5`, non-ASCII digits | over-range or refused; no form both parses and escapes the range check |
| registry reads | FIFO, directory, mode-000 `sources.jsonl` | no hang; mode-000 is a clean `rc 2` |
| symlink-loop root, read-only entries dir | `--root <loop>`, `chmod 555` | clean `rc 2` |

## HIGH-9 — an unreadable entries directory is a **false pass**

`chmod 0o111 ledger/entries`, then any of `status`, `validate`, `resolve`,
`references`, `propagate`, `check`:

```
validate (0 entries): 0 failure(s), 0 flag(s)      rc 0
```

`Path.glob()` swallows the `EACCES` from `scandir` and yields nothing; `is_dir()`
answers `True`, so `guard()` waves the command through. The new
`schema.list_entry_files()` wraps the glob in `except (OSError, RuntimeError)` —
that handler **cannot fire for this case**, because glob does not raise. A ledger
full of failing entries reports a clean pass at exit 0, and a pre-commit hook
built on `check` lets the commit through.

This is the one the verdict above says was found nowhere: *"No defect found
produces a false pass — every failure path exits non-zero."* That sentence is now
false, and it is the highest-value finding in either pass. Reachable without
hostility: a ledger owned by another user, or a CI runner without the read bit.

Fix shape: `guard()` must establish that the entries directory is *listable*, not
merely that it exists — `os.scandir()` in a `try`, or `os.access(d, os.R_OK|os.X_OK)`
— and refuse at 2 when it is not.

## HIGH-10 — `source add` hangs forever on a FIFO registry

`mkfifo ledger/sources.jsonl`, then `claims-ledger source add …`: the process never
returns. `authoring.add_source()` reaches `ledger.registry.open("a")` with no
`is_file()` guard. This is precisely the defect fixed for entry *reads*, still open
on the registry *write*: the guard went into `read_text_or_raise()`, and the append
path does not go through it. In a hook or CI job it wedges with no output at all.

## HIGH-11 — `confined()` is defeated by a symlink

```
proj/claims-ledger.toml    # untouched defaults
proj/ledger -> /tmp/outside
claims-ledger new escape-by-symlink     ->  rc 0
/tmp/outside/entries/A0001-escape-by-symlink.md   # written, silently
```

`confined()`'s own docstring names the threat as *"a cloned repository's own
`claims-ledger.toml` writing entries into /tmp"*. A clone carries symlinks as
readily as it carries a TOML file, so that threat is still open — the fix closed
the string-shaped half of it. The docstring's reason for going lexical (a
symlinked ledger directory is a legitimate layout) is a real trade-off and this
may be a **won't-fix**; if so, the docstring should say the containment is against
a hostile *config value*, not against a hostile *checkout*, so nobody reads more
into it than it does.

## MEDIUM-12 — `documents` patterns are not confined at all

`documents = ["../outside-root/*.md"]` and an absolute pattern both work:
`tree_documents()` does `glob.glob(os.path.join(root, pattern))`, and
`os.path.join` discards `root` for an absolute pattern. The report then prints the
outside path and the citations found in it. Read-only — no write path follows the
documents — but it is the same property `confined()` was added to establish, on
four keys out of five.

## MEDIUM-13 — an unreadable document is checked as though it were empty

`schema.read_document()` returns `None` for any `OSError` or `UnicodeDecodeError`
and every caller `continue`s, with no note. A document citing a nonexistent entry
fails `references` at rc 1; `chmod 000` on that document and the same run is clean
at rc 0 — while still counting it: `references (1 entry, 1 document): 0 failure(s)`.
A FIFO document is dropped one step earlier by `os.path.isfile` and does not even
reach the count. Same class as HIGH-9, one surface over. The count must not
include a document that was not read, and a skipped document belongs in
`skipped_checks()` beside the git note.

## MEDIUM-14 — four ordinary conditions still ask for a bug report

Each prints `claims-ledger: unexpected <Type>` and the "please report it" line:

| Command | Condition | Exception |
|---|---|---|
| `init` | a regular file already at `ledger/entries` | `FileExistsError` |
| `source add` | a directory at `ledger/sources.jsonl` | `IsADirectoryError` |
| `source add` | read-only `ledger/cache` | `PermissionError` (`shutil.copyfile`) |
| `hook --install` | read-only `.git/hooks` | `PermissionError` |

The audit's first pass fixed the OSError funnel in `create_entry()`. The other
write sites — `cmd_init`, `add_source`, `cmd_hook`, `restamp`,
`propagate.append_verdict` — did not get one.

## LOW-15 — `subprocess` calls have no timeout

`schema.git()` and `corpus/run.py`'s own `git()` run without `timeout=`, so a git
that blocks (a credential prompt, a pack it wants to recover) hangs `validate
--cached`, `check`, `resolve`, `sha` and the corpus with no way out. The corpus
copy also still decodes with `text=True` alone, without the explicit
`encoding="utf-8", errors="replace"` that `schema.git()` was given. *Static: read
from the code, not reproduced.*

## What this means for the release

HIGH-9 is a release gate on its own terms — the package exists to refuse to say
"fine" over something it did not check, and it says "fine" over a ledger it could
not read. HIGH-10 is a hang in a hook. HIGH-11 is a decision, not necessarily a
fix. The rest are diagnostics quality.

---

## Disposition of the second pass — 2026-09-05

All nine are fixed. The nine strict xfails in section F of `tests/test_hostile_inputs.py`
flipped and are kept as the regressions for their fixes; LOW-15, which the audit read
from the code rather than reproducing, has two tests of its own, each checked to fail
against the unfixed code. The suite is **559 passing, no xfails**, corpus 62/62, ruff and
`ty` clean.

| Finding | What was done |
|---|---|
| HIGH-9 | `guard()` lists the entries directory with `scandir` instead of asking `is_dir()` and trusting `glob()`; a directory that will not list stops every command at 2, naming the errno. `list_entry_files()` lists the same way, so `new` can no longer allocate `A0001` over a ledger it could not read. |
| HIGH-10 | `source add` refuses a registry that is not a regular file, before the FIFO append it would otherwise block on and before any bytes are copied. |
| HIGH-11 | Fixed, not waived. `confined()` checks each path as written **and** with its symlinks followed, and refuses a `ledger` that leaves the root either way; a symlink that stays under the root — the legitimate layout the docstring named — still works. The docstring says which of the two checks does what. `default_config()` is confined too: a project with no configuration file at all could carry the same symlink. |
| MEDIUM-12 | `documents` patterns are confined at config load, refused by key like the other four. Deliberately lexical, and the README and the docstring now say so: a pattern has no `*` on disk to follow, and what is being closed is a configuration that addresses outside the project. A document reached through a symlink inside the tree is still read; that is recorded as known in `CHANGELOG.md` rather than left implied. |
| MEDIUM-13 | `read_document()` answers `(text, problem)`. A document that cannot be opened is kept out of `Ledger.docs` — so the `N documents` count is a count of what was read — and `references` fails on it by name. It is also listed in `skipped_checks()`, beside the git note, as the audit asked. |
| MEDIUM-14 | `cmd_init`, `cmd_hook`, `register_source` (cache copy and registry append), `restamp` and `propagate.append_verdict` all funnel `OSError` into a clean message at exit 2. |
| LOW-15 | Both `git()` copies take `timeout=GIT_TIMEOUT` (30s), and the corpus copy decodes with `encoding="utf-8", errors="replace"`. The corpus runner turns a git failure or timeout into a `LedgerError` rather than letting `check=True` raise `CalledProcessError` through the CLI's catch-all — adding a timeout would otherwise have opened a new bug-report path. |

The verdict of the first pass — *"No defect found produces a false pass"* — was false when
it was written, and HIGH-9 is where. That sentence stands above, uncorrected, because the
audit is a record of what was believed at the time; this section is the correction.
