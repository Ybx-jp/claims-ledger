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
