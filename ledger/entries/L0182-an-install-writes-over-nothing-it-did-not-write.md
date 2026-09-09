---
id: L0182-an-install-writes-over-nothing-it-did-not-write
kind: claim
stated: 2026-09-08T21:44:39-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 6c7e36f92d33258351a02dc5ab129c8284494894369a8d9ef26ceeea09d9c702
---

## Assertion

An install leaves every file it finds already in the project exactly as it was, unless it is asked to write over it.

## Scope

metric: what happens to a file the install would write and the project already has
cohort: every file an install writes, under every agent
condition: the destinations are directories people edit by hand

## Grounds

- code: src/claims_ledger/harness.py § "install" @52859264d2caa6d447021f4cda3c8b26e7d72c1f

## Warrant

Each planned file is compared with what is there: bytes that already match are reported as present, and bytes that differ are left untouched and named, with a flag to say so being what changes that. An agent directory is a place people edit, and an installer that overwrites an edited hook is an installer nobody can safely re-run.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T22:33:29-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/harness.py § "install" @52859264d2caa6d447021f4cda3c8b26e7d72c1f
  artifact: 0acc80e7ea07eb201484a98474918acc7e948dd3
  note: propagated from a moved ground

- 2026-09-08T22:33:30-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/harness.py § "install" @922d6cec6ce535b84b13f651c01225b8242d5ca8
  note: re-read after the citation inside this section moved to L0193, the successor of the entry it named. The three states this section decides between — written, already there with the same bytes, left alone because it differs — are unchanged, and so is the flag that is the only way to write over one.

## References

- src/claims_ledger/harness.py · standing · cites-as-live
