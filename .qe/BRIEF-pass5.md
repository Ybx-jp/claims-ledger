# Fifth-pass QE blitz — shared brief

You are one of three adversarial agents on a fifth audit pass of `claims-ledger`.

Working tree: `/home/ybx/code/claims-ledger/.claude/worktrees/qe-pass5` (branch `qe-pass5`,
off `4a8ee31`). Interpreter: `.venv/bin/python`, package installed editable, with pytest,
ruff and ty. Run tests with `.venv/bin/python -m pytest`.
**Baseline is 648 passed, 0 xfailed. Confirm that before you start.**

Work only inside this worktree. Another session is working in `/home/ybx/code/claims-ledger`
itself — do not touch it, and do not run `git commit`, `git checkout` or `git rebase`
anywhere. Write files; the parent commits.

## The oracle

Every input may end only one of two ways: (1) a clean non-zero exit with a human-readable
message on stderr, or (2) a correct successful run. Never acceptable: an unhandled
traceback reaching a stranger; a hang; a wrong exit code; a message that is a raw
exception repr; **a false "0 failures" over content that was never actually checked**; a
write outside the project root.

The last one is the package's reason to exist. **A check that did not run and is reported
as a check that passed is the most severe class of defect in this codebase.**

## Method

Read `QE-AUDIT.md` first — four prior passes and their dispositions. Its recurring finding
is your method: **every new defect was the class of an old fix, one surface over.** For
each fix listed there, ask *which other surfaces reach this code by a different route.*

The fourth pass's fixes are the newest code and therefore the best target:
- `git_call()` / `GitAnswer` in `schema.py` — exit status kept, each caller deciding which
  non-zero exits are answers. `git()` still exists with the old meaning. **Ask which
  callers still use `git()` where they needed `git_call()`.**
- The frozen region compared as **bytes** above the APPEND marker (`check_history`).
- `is_object_name()` returning None for "could not ask".

## Rules that are not negotiable

1. **Produce real conditions. Do not patch internals.** Configure a real repository, a
   real filesystem, a real environment. `freshness.py` does `from .schema import git`, so
   patching `claims_ledger.schema.git` does not reach it anyway.
2. **Regression files must be named `tests/test_<something>.py`.** This repo leaves
   pytest's `python_files` at its default, so a file named anything else is collected by
   nothing and protects nothing. The fourth pass lost eleven regressions to this and had
   to be rescued. Use one file, yours alone, named in your task.
3. **A genuine defect is kept as `@pytest.mark.xfail(strict=True, reason="BUG: ...")`**,
   never weakened to match the bug. Run it and confirm it xfails. A test that passes today
   because the behaviour is correct is also worth keeping — mark it as the control.
4. **Never leave the suite red.** `.venv/bin/python -m pytest -q` must end in
   `N passed, M xfailed` with no failures before you stop.
5. **Write findings to disk as you get them, not at the end.** Maintain
   `.qe/findings-<your-dimension>.md` and append each finding *when you find it*. The
   fourth pass lost three of five dimensions because the agents held their results until a
   final report they never got to write. Assume you will be interrupted. Your file on disk
   is your report; the message you return is a summary of it.

## Report format, in `.qe/findings-<dimension>.md`

Per finding: a one-line title; severity (HIGH / MEDIUM / LOW) with the oracle clause it
violates; the exact repro; observed vs. required; the test name that holds it; and a
suggested fix shape. Also record, in a "What held" section, the attacks that found nothing
— an unexamined surface and a clean one must not look the same in the record.
