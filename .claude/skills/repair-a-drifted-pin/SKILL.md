---
name: repair-a-drifted-pin
description: Repair this repository's self-hosted ledger when a pinned ground drifts — reading a freshness finding, writing the contested verdict, re-judging, and superseding an entry with its citations moved. Use when `claims-ledger freshness` or `check` reports a moved, withdrawn or unstable ground, when the pre-commit hook refuses a commit for any of the five checkers, when an edit lands inside a section named by a `code:` or `toml:` ground, and BEFORE hand-editing any file under `ledger/`.
---

# Repair a drifted pin

**The procedure is `docs/OPERATING.md` §"Repairing a drifted pin". Read it and follow it.**
It ships with the package and is the authority; this file exists to get you there with the
repository-specific parts already answered, and to say the two things that are easiest to
get wrong under time pressure.

## Before anything

Run the checkers and read what they actually said:

    .venv/bin/python -m claims_ledger freshness

Named as an interpreter plus `-m`, never as the `claims-ledger` console script — the
virtualenv is not active in every context this runs from.

`freshness` reports five things and only two of them are drift. **`unstable pin` and
`unknown` must never be given a verdict**: the first has no revision to compare against,
the second is git declining to answer, and a verdict over either records a judgement
nobody made. `docs/OPERATING.md` has the table.

If the failure came from `resolve` rather than `freshness`, read its sentence to the end.
It now names which of three things went wrong, and they are not the same repair: a commit
this repository does not have is a rewritten history and a supersession per entry; a
commit that is there with the path missing is one pin on one entry.

## Ask what moved before you write the successor

`docs/OPERATING.md` has this now; it is repeated here because it is the step that was
skipped in practice. If the pinned section changed for a reason the claim does not name,
the ground is wrong, and giving the successor the same ground buys one more supersession
on the next unrelated edit — which is exactly what L0010 did, carrying `cmd_validate`
forward after an edit to `cmd_validate` that the claim had nothing to say about.

The tell is mechanical and the tool already prints it: `sha --write` on the successor
computing a `verbatim_sha` **byte-identical** to its predecessor's means the claim never
moved and only its ground did. In that case narrowing the ground *is* the repair — pin the
code carrying the rule rather than a caller that follows it, and configure a
`section-pattern` if the claim is about something narrower than a table or a function.

## Two things not to do

**Do not edit an entry above the `<!-- APPEND BELOW THIS LINE ONLY -->` marker**, and do
not delete a verdict or change a ground to make a checker pass. `validate` compares
against git history over the whole history, so it is caught on the next run anywhere, and
by then it is in the record.

**Do not write the `contested` verdict by hand.** `freshness --write` appends it with the
`artifact:` provenance the checker is entitled to; a hand-written one under the propagation
author is a person borrowing the authority of a check that did not run.

## This repository's specifics

- Interpreter: `.venv/bin/python -m claims_ledger`.
- Entries are `ledger/entries/L000n-<slug>.md`, eight of them, all pinned into commit
  `4023af40`.
- Citation sites are README sentences and docstrings in `src/claims_ledger/*.py`. The
  reference check names them for you once the entry goes contested.
- Landing the repair: two commits, the first with `--no-verify`, then
  `.venv/bin/python -m claims_ledger check` by hand before the second. `docs/OPERATING.md`
  says why.
- Merging: merge commit only. The guard at `examples/agent-harness/merge-guard.sh` will
  refuse the alternatives, and GitHub will too.
