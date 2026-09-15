---
name: track-open-work
description: File unfinished work as a GitHub issue rather than leaving it in a session's final message or a graph write — what belongs in the tracker versus in the ledger, the register an issue body is written in, and the reproduction a defect is filed with. Use when work is found that this session will not finish, when a defect is measured but out of scope, and before reaching for any graph write to record it.
argument-hint: "What should be tracked?"
---

# Track Open Work — the tracker is the entrypoint

## The boundary

**A session does not write its own memory.** Episodic writes happen *after* a session
ends, by `thalamus extract` over the retained transcript, and `write-guard.sh` blocks a
live write from inside one. A thread written mid-session gets a fresh id, so it and the
one distillation writes afterwards both stay open in `memory_open_threads` — the surface
the next session reads first.

The one write verb a session holds is **closing** a thread, through approval:
`thalamus thread propose` writes a ledger row and nothing to the graph. Report the title,
a one-to-two sentence description, **and** the proposal id — all three, because the
operator approves remotely and cannot read the ledger to see what they are approving.

## Where a thing goes

This repository has more places to put a thing than most, and most of them are not the
tracker. Getting this table wrong is how a commitment ends up as an issue nobody acts on,
or how a repair that costs one verdict is deferred into one that costs a supersession.

| It is… | Where | Not |
|---|---|---|
| Work a future session should pick up | **A GitHub issue** | — |
| A commitment the code now makes | **A ledger entry, in the same commit**, cited from the prose that states it | an issue; nothing comes back for a deferred entry, because prose that promises and cites nothing passes every check |
| A ground that has drifted | **A verdict** — `repair-a-drifted-pin` | an issue; the flag is already the report |
| A claim that stopped being true | **A supersession** — a successor plus a `superseded` verdict | an issue, and never an edit |
| A design not yet settled | `docs/design/`, which is `.gitignore`d and local | the tracker, until there is something to act on |
| A measured audit finding | `.qe/`, and the issue if a future session must act | — |
| Something this session learned | The final message; distillation writes it once, properly | a graph write |
| A thread that is finished | `thalamus thread propose` → operator approves | — |

The split is about *audience*. The ledger is what the project is answerable for; the
tracker is what the operator reads to decide what a session does next. An entry is not a
to-do and an issue is not a claim.

## Filing

GitHub Issues on `Ybx-jp/claims-ledger`. One command, from anywhere in the checkout:

```bash
gh issue create --title "<descriptive title>" --body-file /tmp/issue.md --label bug
```

- **Write the body to a file first** and pass `--body-file`. A body passed inline through
  `--body` goes through shell quoting, and backticks, `$` and newlines in a
  multi-paragraph body are exactly what that mangles — and an issue about this project is
  nearly always full of all three.
- Check `gh issue list --search "<a distinctive term>"` before filing. A duplicate costs
  the next session the same triage.
- **Labels:** this repository carries GitHub's defaults — `bug`, `documentation`,
  `enhancement`, `question`, `wontfix`, `duplicate`, `invalid`, `help wanted`,
  `good first issue`, `accessibility`. There is no `type:`/`area:` scheme here. `gh issue
  create` fails outright on a label the repository does not carry; if it errors, re-run
  without `--label` and say which you would have applied.

## The register — this is the part that goes wrong

An issue is a technical record read by someone who was not in your session. Write the
**problem, what it affects, and what a reader has to do differently.** Nothing else.

- **No verdict framing.** "the case was unbeaten", "this cuts against the proposal",
  "ships flagged" — cut every one.
- **No session narrative.** Who proposed what, which round found it, what you tried
  first. None of it is actionable.
- **No grading anyone's decisions**, the operator's least of all.
- **Constraints, counter-evidence and known gaps stay in**, as facts with their numbers.

**Titles are descriptive, not literary.** They are the only thing a reader scanning a
list sees, and this project's own commit messages are the wrong register for them.

- Good: `check_numbers reports a shared number for two entries whose ids do not parse`
- Bad: `The number that named nothing`

## A defect that can be reproduced is filed with its reproduction

Ask which instrument reaches it. This project has two, and they answer different
questions.

| The defect is… | Reproduction goes in |
|---|---|
| A rule a checker enforces, fails to enforce, or enforces wrongly — anything expressible as a small ledger and an expected verdict | **A corpus seed**, `src/claims_ledger/corpus/seeds/` |
| Anything else — a CLI surface, a write path, a degraded or hostile git, the harness, the installed hooks, allocation, a rewrite | **A test module** under `tests/` |

**A seed costs four places agreeing**, and the tests enforce three: the seed directory,
a row naming it in `src/claims_ledger/corpus/README.md`, the count in
`tests/test_corpus_integrity.py`, and the counts in `README.md` and `QUALITY.md`. A seed
builds linear, append-only history and cannot make a commit unreachable, so a defect that
depends on a rewrite is seeded by writing the end state the rewrite would produce.

**A new report site must be swept.** If the fix adds a `Report(...)`,
`test_every_report_site_has_been_through_the_sweep` goes red until its count moves, and
the comment beside that count has to say what deleting the site reddens. Establish it by
deleting the site and watching something fail — not by reasoning that it would.

**Never claim a reproduction you have not watched redden.** Mutate in place in the
worktree whose `.venv` resolves the package: copy the file, `sed` the mutant, run,
restore from the copy. A copied *tree* does not work — the editable install resolves
`claims_ledger` back to the original `src/`, so the mutant is never imported and the suite
reports its usual green.

**Say so when it does not qualify**, in the issue, rather than filing untagged and silent.
Shapes that genuinely do not: a defect that needs a rewritten history the corpus cannot
build; a question that still needs a measurement designed; and a gap in coverage, where
writing the check *closes* the issue rather than reproducing it.

## Issue template

Follow this. Drop a section only when it genuinely has no content — do not pad it.

```markdown
## What

The defect or gap, stated as a claim about the system. Name the file, function or
section. Not "look into X".

## Evidence

How it was measured, with the command and the output. `validate` at 0 failures over a
tree that holds a duplicate, not "seems wrong". If it was not measured, say what was
observed and how often.

## Reproduction

The seed or the test that holds it, and what reddens when the fix is removed. If there
is none, say which of the three shapes above it is.

## Impact

What this affects, and what a reader has to do differently while it stands. Include any
workaround that works today.

## Already decided

Constraints that are settled and must not be re-litigated, and where that decision is
recorded — an entry id, a `docs/design/` note, a consultation ticket.

## Deliberately not to be done

Approaches ruled out and why. The most expensive thing to rediscover.

## Open decision

What is still undecided and whose call it is. If it is the operator's, say so — the issue
is then open on the decision, not on the work.
```

## Before you file

Two checks, and they catch different duplicates.

- **The graph**: `memory_exchanges(query=...)` for a question an expert has settled,
  `memory_open_threads(topic=...)` for work already tracked.
- **The ledger**: `claims-ledger neighbours '<type>: <path> § "<section>" =?'` for the
  entries already resting on the artifact you are about to file against. A defect in a
  span an entry pins is often a claim that has drifted rather than a gap in the code, and
  that is a verdict rather than an issue.
