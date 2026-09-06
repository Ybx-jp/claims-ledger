# Fourth-pass QE blitz — shared brief

You are one of five adversarial agents on a fourth audit pass of `claims-ledger`.
Working tree: /home/ybx/code/claims-ledger/.claude/worktrees/qe-blitz-post-freshness
Interpreter: `.venv/bin/python` (already has the package installed editable, plus pytest,
ruff, ty). Run tests with `.venv/bin/python -m pytest`. Suite is currently 611 passed,
0 xfail — three prior passes found 24 defects, all fixed and kept as regressions.

## Read first (do not skip)
- `QE-AUDIT.md` — three prior passes and their dispositions. Its closing finding is your
  method: **every new defect was the class of an old fix, one surface over.** For each
  fix listed there, ask *which other surfaces reach this code by a different route*.
- `tests/conftest.py` — the `project` fixture (a real project root with a ledger,
  sources, `p.cl(...)` calling `cli.main` in-process, `p.git(...)` for git).
- `tests/test_hostile_inputs.py` header — the oracle, restated here:

  Every input may end only one of two ways: (1) a clean non-zero exit with a
  human-readable message on stderr, or (2) a correct successful run. Never acceptable:
  an unhandled traceback reaching a stranger; a hang; a wrong exit code; a message that
  is a raw exception repr; **a false "0 failures" over content that was never actually
  checked**; a write outside the project root.

  The last one is the package's reason to exist. A check that did not run and is
  reported as a check that passed is the most severe class of defect in this codebase.

## Rules
1. **No speculation.** Every finding must have a repro you actually ran, with the real
   command and the real output pasted into your report. A finding you could not
   reproduce is not a finding — say so and drop it.
2. **Do not modify `src/`.** This pass reports; a later commit fixes.
3. Write regression tests for confirmed defects into `tests/_pass4_<YOURDIM>.py`
   (your dimension name, given in your prompt). Use
   `@pytest.mark.xfail(strict=True, reason="BUG: ...")` for a test that fails only
   because of the defect. Every such test must actually fail against current code (i.e.
   report as xfail, not XPASS) — verify by running it.
4. Prefer tests built on the `project` fixture and the CLI surface, as the existing
   suite does. `run_cli` in `test_hostile_inputs.py` runs it as a real subprocess with a
   timeout, for anything that might hang.
5. Distinguish severity honestly: HIGH = silent wrong answer, hang, traceback, or write
   outside root. MEDIUM = wrong/misleading output a user would act on. LOW = cosmetic or
   documentation mismatch. Do not inflate.
6. Stay in your dimension. Note a stray finding in one line and move on.

## Report back
A markdown table: id (`<DIM>-1`…), severity, one-line summary, the surface, the repro
command, expected vs actual. Then a short paragraph per HIGH/MEDIUM explaining the
mechanism in the code (file:line). Finally: which of your findings are the class of an
earlier fix one surface over, and which are new classes. Keep it tight; no preamble.
