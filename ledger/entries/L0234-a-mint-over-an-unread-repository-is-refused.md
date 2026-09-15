---
id: L0234-a-mint-over-an-unread-repository-is-refused
kind: claim
stated: 2026-09-14T19:01:40-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: b4427f90fb32afd834837726ab7da698cfba5ecd487d9455707c36d7e3d60f36
---

## Assertion

A mint whose repository could not be read is refused, naming the question git declined, rather than allocating from the one directory it could see.

## Scope

metric: the outcome of claims-ledger new when a git question fails
cohort: every mint in a project version control holds
condition: no --id is given, so an id is being allocated

## Grounds

- code: src/claims_ledger/authoring.py § "create_entry" =sha256:9fd1548f22c2ddd0db37c5760efc60c442f2a918faf9fb364f3d118bb35b1bf3

## Warrant

create_entry allocates only when ids_in_the_repository reports nothing unasked, and raises AuthoringError naming what could not be asked otherwise; the id is chosen at no other point, so there is no path on which a mint proceeds over a repository it could not read.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
