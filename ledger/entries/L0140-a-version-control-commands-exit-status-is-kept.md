---
id: L0140-a-version-control-commands-exit-status-is-kept
kind: claim
stated: 2026-09-08T02:46:26-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: b28d18d071dd47be7b85142a8077d02825f38864bf18e077b06030460c413a36
---

## Assertion

A version-control command's exit status is carried back alongside its output, so a command that could not answer is never read as a benign negative.

## Scope

metric: whether a failed command and a command answering no are distinguishable to a caller
cohort: every version-control call in the package
condition: both produce empty output

## Grounds

- code: src/claims_ledger/schema.py § "GitAnswer" @4af0acd253eeef1571cd7615ea3a041eda9e945e
- code: src/claims_ledger/schema.py § "git_call" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

git_call returns the exit code, the output and a reason as one value, and each caller then says for itself which non-zero exits are answers — a revision that is simply absent — and which are the command failing to answer at all. The convenience wrapper that folds both into nothing is kept for the callers to whom they really are the same thing. A caller reading that fold as a negative turns a broken repository into a report that a check passed, which is the one output this package must never produce.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
