---
id: L0007-sha-write-refuses-a-committed-entry
kind: claim
stated: 2026-09-07T13:30:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: f116faacee4e27ef92166f0bcd2309462802c5210039b29c3b07e56c125db046
---

## Assertion

sha --write refuses to rewrite the fingerprint of an entry git already has, and of an entry whose commit state git could not establish, unless --force is passed.

## Scope

metric: whether sha --write rewrites verbatim_sha
cohort: entries under the ledger's entries directory
condition: the entry is in a commit, or whether it is could not be established

## Grounds

- code: src/claims_ledger/authoring.py § "restamp" @4023af4006273319aec9ae2512d197e4a99fce8c

## Warrant

restamp asks is_committed before writing and raises AuthoringError both for a committed entry and for an unanswered question, in each case unless force is set.

## Backing

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- README.md · standing · cites-as-live
- src/claims_ledger/authoring.py · standing · cites-as-live
