# Pre-publication audit — claims-ledger 0.1.0

Adversarial quality pass ahead of the first PyPI release. 2026-09-05.
Findings only: no `src/` change was made. Every item below was reproduced by hand
against an **installed wheel**, not against the source tree.

Suite went **235 → 535 passing, 9 strict xfails**. Each xfail records a confirmed
bug and flips to a failure the moment that bug is fixed, so none of this can rot
quietly.

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
