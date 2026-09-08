---
id: L0144-a-command-that-does-not-answer-in-time-is-an-unanswered-question
kind: claim
stated: 2026-09-08T02:46:26-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 58d4f1905b9dd2378f514b0c8d910dd51b560d087f0b6fba6886e55018da3b78
---

## Assertion

A version-control command that does not answer within the timeout, and one that could not be started, both come back as a question left unanswered rather than as a negative.

## Scope

metric: what a timed-out or unstartable command produces
cohort: every version-control invocation in the package
condition: a checker may run inside a commit hook, where a hang produces no output

## Grounds

- code: src/claims_ledger/schema.py § "git_call" @4af0acd253eeef1571cd7615ea3a041eda9e945e
- code: src/claims_ledger/schema.py § "GIT_TIMEOUT" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

git_call runs with a timeout and turns both the timeout and a failure to start into an answer carrying no exit code and a reason a message can print. A checker wedged behind a subprocess is a hook that has stopped with nothing said, and a timeout read as a negative is the false pass the whole answer type exists to prevent. The reason travels with the answer, so the caller reports what happened rather than what it assumed.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
