# Architecture audit — claims-ledger 0.1.0

Structural and performance pass, 2026-09-07, from the `architect` scope. Every number
below was produced by a command that is quoted next to it; every file:line was read.
The findings are ranked by consequence, not by effort to fix.

> **Disposition — 2026-09-07, finding 1.** Fixed in this branch: `check_history` reads
> the whole ledger's history in three git processes instead of two plus one per revision
> for every entry, and `load_entries(cached=True)` reads the index in one. `check` over a
> thousand-entry, thousand-commit ledger went from **5m18s to 2.79s**; the process count
> for `validate` is 4 at any size, held by `tests/test_history_batch.py`. Findings 2–8
> are open, and belong to their own branches.
>
> **The fix-review gate on finding 1** (`qe`, ticket `a04b8860f9764902`) returned
> merge-but-fix-first, and the branch merged before any of it was fixed. First repaired:
> the rewrite had dropped the text-level comparison of the frozen region, so a preamble
> edit was reported as a line-endings difference and, under `--cached` with no staged
> blob, not reported at all. Restored, with both cases pinned in
> `tests/test_immutability.py`. Then: the `-m` mechanism, stated wrongly below and now
> corrected in place (it is `--full-history`, and the extras are not merges only); the
> `--cached` byte check and its reference blob, each now pinned by a test its mutant
> fails; and the append-only check, which linearized the walk's order and so compared
> siblings under full history — a `-s ours` merge that discarded a branch's verdict was
> reported as a removal at the *other* branch's commit. It compares each revision with
> its own parents now (`git_history` returns them from the same walk; the parents' blobs
> ride the same `cat-file --batch`), and the failure names the merge. Re-measured after:
> N=1000 `check` 2.89s, `validate` still 4 git processes. Still owed from the gate: a
> sha256-repository test and a walk-timeout test; and the legal two-branch union merge
> false-fails on the ordering of appended verdicts, which predates this work.

> **Disposition — 2026-09-07, findings 2, 3 and 6.** Fixed on branch
> `arch/checks-that-did-not-happen`, which is the three of them because they are one
> property: a check that did not happen must not report as if it did.
>
> **Finding 2, and 6 with it.** `now_text` returned the text and threw away the reason,
> so `scoped()` mapped an artifact it could not read onto `moved`. It returns
> `(text, unreachable)` now and `scoped` returns `(finding, why)`, so `drift` answers
> `unknown` — the class it already had. The distinction finding 6 asks for is a new
> `schema.unreadable_artifact()`: bytes that are there and are not UTF-8 stay `moved`,
> because that artifact really did change and simply cannot be narrowed to a section,
> and bytes that cannot be reached at all are a comparison that did not happen.
> `file_problem` cannot draw that line — `os.stat` succeeds on a mode-000 file — which
> is why finding 6's two guards stay two. The plain-pin branch had the same false
> confidence one surface out, since git reports a file it cannot open as modified, and
> it is fixed too; the audit's remedy named only the sectioned one.
>
> **Finding 3 — and the finding under it, which is worse than the one reported.** The
> stated repro is a ledger with `.git` removed, where `validate` exits 0 and `resolve`
> and `freshness` exit 1. Measured while fixing it: with no repository *anywhere*,
> exit 0 is right — no entry has a creating commit, so nothing was skipped, and
> `resolve` and `freshness` exit 1 over real pinned pointers they cannot resolve, which
> is a different question. The real defect is next door. `open_ledger` calls a project a
> repository when `<root>/.git` is there, so a ledger one directory inside one —
> `--root <subdir>`, or a ledger vendored in a larger project — reads as having no
> history at all. Measured on such a ledger: `sha --write` rewrote the frozen region of
> an entry that repository had already committed and exited 0, and `validate` then
> reported `0 failure(s)` over it. That is L0007 not holding, silently, on an ordinary
> layout. `schema.enclosing_repository()` answers the narrow question — is there a
> history nobody looked at? — and `check_history` and `is_committed` both report it.
> Nothing *adopts* the repository: every evidence path in the package is written
> relative to the ledger root and `git show <pin>:<path>` reads its path from the
> repository's top, so adopting one means rebasing every git path in the package. That
> is its own branch, and until it exists this refuses rather than guesses.
>
> Regressions: three in `tests/test_freshness.py` (mode-000 under a sectioned pin, the
> same under a plain pin, and the not-text case that must keep saying `moved`), two in
> `tests/test_failure_paths.py`. The report-site inventory in
> `tests/test_corpus_integrity.py` moves 75 to 76 for the one new site. Gates: 850
> passed, 2 xfailed, 79/79 seeds, ruff and ty clean. Superseding L0008 is part of this
> branch: its pinned section is `freshness.py § "scoped"`, which the fix rewrites.

> **The fix-review gate on findings 2, 3 and 6** (`qe`, ticket `88bb70784a8746da`)
> returned **do not merge**, with three HIGHs, all against the finding-3 half. Fixed on
> the branch before merge, each re-measured:
>
> - **QE11-1.** `enclosing_repository` asked "is there a work tree above me", not "is
>   there a history nobody read". The corpus stages seeds through `tempfile`, so a
>   `TMPDIR` inside any repository took it from 79/79 to **18/79** and the suite to 146
>   failures — and `claims-ledger init` in any repository subdirectory, with zero entries,
>   exited 1. The predicate is now `git log -1 -- <entries>` in the nearest `.git`-bearing
>   ancestor: a directory that merely sits under a work tree, untracked, has no history.
>   Re-measured: 79/79 both ways, and the negative case has a test.
> - **QE11-2.** A failed `rev-parse` was read as "there is no repository", which put back
>   the exact false pass this branch removes: with an enclosing repository git refuses to
>   open — `detected dubious ownership` is the everyday one — `sha --write` rewrote a
>   committed entry's frozen region and exited 0 again. It returns `(holder, why)` now and
>   both callers report the `why`.
> - **QE11-3.** `git rev-parse --show-toplevel` with `GIT_DIR` set answers with the
>   directory it was run in, so a ledger with no repository anywhere reported *itself* as
>   the repository holding it. (This first said "every git hook exports `GIT_DIR`", which
>   round 2 measured as false on git 2.43.0: a hook gets `GIT_INDEX_FILE`, and `GIT_DIR`
>   reaches one when git itself was invoked with `--git-dir`.) The walk is the
>   filesystem's now: `.git` above the root, no git process for a project that is not
>   under version control, a strict ancestor by construction.
> - **QE11-4, MED-HIGH.** `in_this_run` was `path.is_file()`, which raises PermissionError
>   out of pathlib on 3.12 when the artifact's *directory* is unsearchable — `freshness`
>   exit 2 printing nothing, `check` silently omitting it — and on 3.13 swallows the EACCES
>   for a confident false `withdrawn`. `os.stat` is asked directly and the three states are
>   three answers.
> - **QE11-5, MED.** The classification read the file twice, at +319 MB peak RSS on a
>   300 MB artifact and with a race between the reads. `read_artifact` does it in one; the
>   plain-pin branch, which never wants the text, probes one byte.
> - **QE11-6, MED.** `docs/FRESHNESS.md` step 5 still said any diff output means `moved`.
>   Corrected for both halves. **Open:** the plain-pin half is claimed by no entry — L0009's
>   cohort is sectioned grounds — so that behaviour is documented and unledgered.
> - **QE11-7, LOW, open.** Both mode-000 guards skip under root, so a contributor in a
>   default container gets a green suite with this branch's headline guards unrun.
> - **QE11-9, LOW, standing.** The supersession record survives attack — `contested` was
>   right, `refuted` would have been wrong — with two nits now uncorrectable because they
>   are in append-only regions: L0009's `verbatim_change` says "Backing is unchanged",
>   true of the fingerprint and false of the section bytes (`'\n\n\n'` → `'\nnone\n\n\n\n'`),
>   and the Warrant changed without being named. `validate.py` checks that
>   `verbatim_change` is present, never what it says.
>
> **Environment-dependent tests, pre-existing, and one of them fixed here because it
> blocked two merges in a day.** `test_e` and `test_e2` in `tests/test_git_degradation.py`
> degrade git by deleting one loose object, which degrades nothing once the object is in a
> pack. On the runners this failed twice in one day on different legs and never locally:
> `test_e` raised FileNotFoundError unlinking a path for a blob `rev-parse` had just
> resolved, and `test_e2` unlinked HEAD's commit object and watched `git log` go on
> answering. Both say the object was packed. Auto-packing is now off for those fixtures
> and each unlink is preceded by a precondition that names the cause, so a future git that
> packs anyway fails with a sentence rather than a `FileNotFoundError`.
> `test_f_a_pin_git_could_not_classify_is_not_taken_for_a_commit` is the same class and is
> **not** fixed: it builds a directory it calls `not-a-repository` and asserts git fails
> there, which is false when `TMPDIR` is inside a checkout. Finding 7's subject — a test
> whose verdict depends on where and on what it was launched — is wider than either.

> **Round 2 of the gate** (`qe`, ticket `39e244285f044346`) returned **safe to merge**,
> and recommended taking two of its own findings first because the fix was in hand. Both
> taken:
>
> - **QE12-1, MED-HIGH — the false negative, and the worse direction of QE11-1.** The walk
>   stopped at the *first* `.git` above the root, so a repository between the ledger and
>   the one that actually committed it read as "no history". Measured: one `git init` in an
>   intervening directory took `validate` from exit 1 to exit 0 and `sha --write` from
>   refusing to rewriting a committed frozen region — a check somebody else's `git init`
>   turns off, silently, on a branch whose whole subject is that this must not happen.
>   Every `.git` above the root is asked now.
> - **QE12-3, MEDIUM — two of the seven new rules were held by nothing.** The `env=` scrub
>   and the containment guard each survived deletion at 857 passed. Both have tests now,
>   each reddened by deleting its own rule; the walk has one too, and the first version of
>   *that* test was wrong — `git init` on the directory the fixture had already committed
>   in is a no-op, so it never built the intervening repository it claimed to. Replaced
>   with one that builds the three-level layout.
>
> **Two findings left open, both wider than this branch and both pre-existing.**
>
> - **QE12-2, MED-HIGH — the scrub stops at discovery.** `enclosing_repository` scrubs and
>   finds the right repository; `git_problem` and the `cat-file` that follow ask *that*
>   repository through the ambient environment. Under `GIT_DIR`/`GIT_WORK_TREE`,
>   `is_committed` flips to "not committed" and `sha --write` rewrites a committed frozen
>   region at exit 0 — measured identically on `main` at `b142311`, on the ordinary layout
>   with the ledger's own repository, so it is not this branch's. It is a question about
>   every `git_call` in the package: which of them are asking about the directory they
>   name, and which about whatever the environment names. Its own branch.
> - **QE12-4, MEDIUM — finding 2's class is still live in `resolve.py`.**
>   `text = read_document(path)[0] if path.is_file() else None`, under a comment reading
>   "never a crash". With the artifact's directory at mode 000 and an `@working` ground:
>   `check` exit 2, `unexpected PermissionError … this is a bug. Please report it`, four of
>   five checkers unrun. The same `is_file()` that QE11-4 replaced in `freshness`.

> **Disposition — 2026-09-07, finding 4.** Fixed on branch `arch/process-counts`, measured
> on `examples/research-repo` (12 entries) with a PATH shim counting `git` executions:
>
> | | before | after |
> |---|---|---|
> | `check`, git processes | 31 | **22** |
> | `freshness`, git processes | 17 | **8** |
> | `check`, `load_entries` calls | 5 | **1** |
>
> `drift()` is asked once per pointer per run and remembered: the findings are a function
> of the pointer, the repository and the tree, all fixed for the run, so `orphans()`
> asking again for every ground `run()` had already evaluated bought 4 to 6 more git
> processes for the same answer — and two entries resting on one artifact asked twice
> over, which the memo also closes. The five checkers take the entries the caller already
> parsed; `check` parses once for all five, and twice only under `--cached`, where
> `validate` and `freshness` read what is staged and the other three read the working
> tree. That is the difference `--cached` exists to make and it is not collapsed.
>
> **What this cost the ledger, and what that says.** `cmd_validate` is one of L0005's two
> grounds, so loading the entries once and passing them down drifted it and cost a
> supersession — L0010. That is the second time in a day this ledger has priced a design
> decision, and both times the pinned section was a *caller* rather than the code carrying
> the rule: `guard` is where "a missing entries directory stops the command" actually
> lives, and `cmd_validate` is named as the pattern its callers follow. A ground on a
> caller goes stale for every edit to that caller, whatever it was for. Worth weighing
> against `docs/OPERATING.md`'s own advice to pin narrowly, which this obeys in letter.
>
> **The pin-width exposure, measured and half repaired.** The observation above was
> checked against every live ground rather than left as a pair of anecdotes. Line counts
> of the pinned sections, against the claims resting on them:
>
> | lines | ground | what the claim is about |
> |---|---|---|
> | 66 | `config.py § from_table` | one rule: an unknown key is refused |
> | 47 | `authoring.py § restamp` | the refusal, which is most of the function |
> | 31 | `pyproject.toml § [project]` | two keys |
> | 29 | `cli.py § HOOK_TEMPLATE` | the shebang and `-m` |
> | 9 | `cli.py § cmd_validate` | nothing; it is a caller |
>
> One of these is now repaired: a `toml-key` section pattern names a single key, and
> L0011 supersedes L0002 on `dependencies` (3 lines) and `requires-python` (1) rather
> than the table (31). The successor's `verbatim_sha` is byte-identical, which is the
> record saying the claim did not move and only its ground narrowed.
>
> The others are open, and two of them cannot be closed the same way. `HOOK_TEMPLATE` is
> a string literal, so a line-anchored pattern cannot reach inside it — and a ninth-pass
> finding already says the ~20 lines of audit commentary in it should be deleted, which
> will move L0001. `from_table` and `restamp` would need a pattern matching something
> narrower than a top-level `def`, which is exactly what the `code` pattern's docstring
> warns against anchoring loosely. `cmd_validate` is not a width problem at all: it is a
> caller, pinned to evidence a cohort clause, and no pattern makes a caller stop changing.
>
> Not done, and named rather than left implicit: the pre-commit hook still runs the five
> checkers as five interpreter processes. One process would need the hook to call a single
> entry point, which is a change to what is installed in every generated repository and to
> `HOOK_TEMPLATE`, which L0001 pins. Its own branch.

---

## Verdict

The shape is healthy. One hub (`schema.py`) that every module imports and nothing
imports back into; five checkers sharing one `Report` type and one pointer and section
grammar; a CLI that is orchestration over the same `run()` functions the library
exports, with no logic of its own; every write funnelled through `os.replace`; and
comments that read as a changelog of bugs fixed and the reason each fix took the shape
it did. Refactors that were tried and rejected are recorded in place (no `--follow` on
`git log`, corpus K18; keyword-only `root` on `append_verdict`, HIGH-11/MEDIUM-19/HIGH-56;
`ConfigError` raised rather than defaulted), which is the institutional memory a
newcomer needs and usually does not get.

The rot is not in the shape. It is in one hot path that scaled as the product of
entries and commits, and in two places where a check that did not happen reports as if
it did — the property this project calls cardinal.

---

## Map

```
config.py ──► schema.py ◄── validate.py  resolve.py  references.py  propagate.py ◄── freshness.py
                  ▲                                                                       │
                  │                        authoring.py ◄──┐                              │
                  └──────────── cli.py ────────────────────┘ ◄── corpus/run.py (lazy, both ways)
```

`schema.py` (1,250 lines) holds three layers with no dependency reason to be together:
entry/pointer/section parsing (its stated purpose); a git subprocess client
(`GIT_TIMEOUT`, `GitAnswer`, `git_call`, `git`, `git_bytes`, `git_history`, `git_blobs`,
`git_problem`, `index_problem`); and atomic-write and file-safety
(`file_problem`, `write_bytes_atomically`, `_refuse_a_target_this_process_may_not_write`).
Neither of the last two imports a schema type. The only import cycle in the package —
`cli.py` ⇄ `corpus/run.py`, both ends function-local — exists because
`soften_output_encoding` lives in `cli.py` and the corpus runner needs it.

Baseline, root checkout: 807 tests in 79s wall (26s user, 14s sys — the suite waits on
subprocesses); corpus 76/76 in 1.7s.

---

## Findings

### 1. `validate` cost the product of entries and commits — **fixed**

`check_history` ran `git log --format=%H -- <entry>` once per entry. Each such log walks
the whole commit graph diffing trees, so its cost is O(commits) whichever entry is asked
about: 0.29s for the first-created entry and 0.29s for the last, on a repository of a
thousand commits. Called once per entry, that is the curve:

    for N in 10 100 1000: time python -m claims_ledger --root /tmp/clscale_snap_$N check

| N entries, N commits | `check` before | `check` after | `validate` git processes |
|---|---|---|---|
| 12 (examples/research-repo) | 77 processes for `check` | 31, output byte-identical | 50 → 4 |
| 100 | 4.14s | **0.27s** | 402 → 4 |
| 1000 | **5m18s** (194.8s user) | **2.79s** (1.13s user) | ~4,002 → 4 |

`status` was flat throughout (0.07s user at every size) because it never touches history,
which located the cost in `check_history` rather than in loading or parsing.

The same blob was also fetched three times per entry — `git(… "show", creating:rel)`
for text, `git_bytes(…)` for bytes, and once more inside the loop over revisions, since
`revisions[0]` is the creating commit — which is where the measured 36 shows over 12
entries came from.

**The fix.** One `git log -z --format=%H --name-only --no-renames -m -- <entries dir>`
lists every commit that touched each entry (`git_history`); one `git cat-file --batch`
reads every blob the walk named (`git_blobs`). Both live in the git layer of
`schema.py`, next to `git_call`. On the same thousand-commit repository the walk answers
in 0.55s and the batch in 0.27s. `load_entries(cached=True)` — the pre-commit hook's
loader — reads the index the same way: `validate --cached` at N=1000 spawned 1,005 git
processes before that change and 5 after.

**One documented difference from the walk it replaces — corrected.** This section first
said that `-m` adds merge commits and nothing else. The fix-review gate measured
otherwise: `-m` is a `--diff-merges` option, and any of those switches history
simplification off, so the walk is `git log --full-history -m` — identical output,
checked with `diff`. It follows every parent of a merge, lists a merge under a file
whenever the file differs from either parent, and lists the commits on a line a merge
resolution discarded, which the per-path log pruned because the merge was TREESAME to
the other side. A verdict that a branch committed and a merge resolution then left out is
therefore compared now and was not before. The creating commit is the oldest either way,
so the frozen-region check is unaffected. `tests/test_history_batch.py` holds this against
a repository with a clean merge, a hand-resolved conflict, a file created on a branch, a
rename and a `-s ours` merge that discards a branch's edit: same creating commit, every
commit the per-path log named in the same order, and the whole list equal to
`--full-history -m` for that path. The first version of the test said "extras are merges
only" and passed because its fixture had no discarded line; that shape is in the fixture
now and the old assertion fails on it. Dropping `--no-renames` or `-m` each fail the
test; reverting the cached loader fails the process-count test.

**What the timeout now bounds.** `GIT_TIMEOUT` is 30s per process. It used to bound one
`git show`; it now bounds one walk and one batch read. A ledger whose history takes
longer than that to walk is reported as a history nobody read, for every entry — which
is what happened before, one entry at a time, only slower.

### 2. An unreadable evidence file is reported as "has moved", exit 0 — **open**

    chmod 000 lab/notes.md; python -m claims_ledger --root /tmp/arch-perm freshness
    FLAG R0007 Grounds 1: `lab: lab/notes.md § "Threshold sweep" @bab039b…` has moved:
      section 'Threshold sweep' differs from the pin in the working tree, uncommitted
    exit 0; `check` exit 0

`git diff --name-only` lists the file as changed (git cannot read it either); `scoped()`
asks `now_text()`, which returns `None` from `read_document`'s `OSError` branch; and
`scoped()` maps `now is None` to `"moved"` (`freshness.py:250–253`). Its docstring
anticipated "cannot be read as text" as *not UTF-8*; a permission error lands in the same
branch and produces a confident, false, soft finding. `drift()` already has the
`unknown` class for a comparison that did not happen; this is that, misfiled. Remedy:
`now_text` returns the reason with the text, and `scoped` answers `unknown` with it.

### 3. Without git, the checkers disagree about the exit code — **open**

Same ledger with `.git` removed: `validate` exits **0** with a stderr note; `resolve`
and `freshness` exit **1**, each having emitted a failing `Report`. `check_history`
returns `[]` when `not ledger.repo` (`validate.py`), and `guard()`'s note (`cli.py:233`)
never reaches `exit_code()`. `check` is safe because the other two carry it, and the hook
only runs inside git — but standalone `validate`, and any library caller of
`validate.run()`, get a clean result over checks that never ran. `resolve`'s "unasked"
pattern is the convention to converge on.

### 4. Subprocess count is the cost at today's sizes — **partly fixed by 1**

cProfile on the 12-entry research repo, before: `subprocess.run` 0.240s of 0.342s
(70%). Remaining sources after finding 1:

- `freshness.orphans()` re-runs `drift()` (`freshness.py:660`) for every ground that
  `run()` already evaluated at `:379` — 4–6 processes per pinned pointer, twice.
- The pre-commit hook runs the five checkers as **five interpreter processes**
  (`cli.py:60–64`), and each single-checker command loads entries twice
  (`cli.py:314, 322, 344, 352` — the second load is only for the count in the summary
  line). Entries are parsed about six times per commit.

### 5. `schema.py` fuses three layers — **open, deliberately last**

See the map. Both extractions (`gitrepo.py`, `iosafety.py`) are low-risk: neither
target imports a schema type, and both stay standard-library-only. `soften_output_encoding`
belongs beside `print_reports`, which breaks the one cycle. Finding 1 added two readers
to the git layer, which is the argument for lifting it out next rather than first.

### 6. Two file-read guards of unequal strength — **open, see 2**

`file_problem` (`schema.py:711`) is `os.stat`-based and exists *because* `is_file()` and a
bare `read_text()` misbehave across interpreters; it guards entries, the registry and
source bytes. Documents and evidence artifacts go through `Path.is_file()` and
`read_document` (`schema.py`; `resolve.py:93`, `references.py:73,164`,
`freshness.py:228`). The FIFO case was probed on every command and is **closed** — no
hang. What the weaker path still does is turn a permission error into a wrong answer,
which is finding 2.

### 7. The test suite: 75–79s, three files are 57% of it — **open**

    pytest -q --durations=0 | (sum per file)

| file | s | tests |
|---|---|---|
| test_corpus_integrity.py | 24.5 | 17 |
| test_examples.py | 10.3 | 3 |
| test_hostile_inputs.py | 8.9 | 187 |

Fixtures are function-scoped and build a fresh `init` plus `git init` and commits per
test — correctly, since tests mutate the ledger. The lower-risk speedup is a
session-scoped *prebuilt* repository each test copies, not a widened scope. The
corpus-integrity tests each re-run the whole corpus (~1.7s) to prove one rule is
load-bearing.

### 8. Hygiene — **open**

`uv.lock` and `.idea/` are untracked and un-ignored; two stale QE worktrees under
`.claude/worktrees/` hold 185 MB of virtualenvs; `LedgerError`, `ConfigError` and
`AuthoringError` share no base, so `cli.py` catches a tuple; `authoring` is public but
not in `__all__`. `.qe/` (77 tracked files) is deliberate policy per `pyproject.toml`.

---

## Holding well

Named so that nothing here is refactored away by accident: `write_bytes_atomically`
with `_refuse_a_target_this_process_may_not_write` (the kernel as arbiter, mode-444
aware); `append_verdict`'s keyword-only `root` and the three-finding history in its
comment; `Config` threaded explicitly, no module-level mutable state anywhere; one
`Report` type and one grammar; the corpus contract (one row to one report, an unlisted
catch is a finding); `resolve`'s "unasked" pattern. `references.py:210` has the only
O(documents × entries) loop and it is pure Python, unmeasurable at these sizes.

## Suggested order for what remains

2 (`unknown`, not `moved`, when `now_text` fails on `OSError`), then 3 (make
`check_history` report like `freshness`), then the free process cuts in 4, then the
`schema.py` split in 5.
