---
id: L0164-a-shared-span-is-compared-without-its-pin
kind: claim
stated: 2026-09-08T12:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 810e97fc311721e08773b38039f7509062788d80e920bfb68f70b05e7aa1ec21
---

## Assertion

Two grounds are the same span when their type, their normalized path and their section agree, whatever revision each is pinned at.

## Scope

metric: the parts of an evidence pointer compared when two grounds are tested for sameness
cohort: evidence grounds of a declared evidence type
condition: the lookup, which compares them; no checker compares them this way

## Grounds

- code: src/claims_ledger/neighbours.py § "span" @aadceb0aba82a85fe71b15394896c43977751709

## Warrant

span returns the type, the path through posixpath.normpath and the section, and drops the pin. The pin is the one part of a pointer expected to differ between two entries about the same code, because they were written at different commits; comparing it would make the lookup answer nothing in exactly the case it exists for. Freshness reads the pin and this does not, which is the difference between asking whether a claim has gone stale and asking what else is about this function.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/neighbours.py · standing · cites-as-live
