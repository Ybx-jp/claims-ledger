---
id: L0053-the-evidence-types-are-disjoint-and-there-is-one
kind: claim
stated: 2026-09-08T02:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: c5feda5bd35b0860130fa0bdec2ab67d52a8bb4e4315d30f7df671061d339564
---

## Assertion

The declared evidence types are held to being disjoint and to being at least one: a type declared both sectioned and plain is refused, and a configuration declaring none at all is refused.

## Scope

metric: the outcome of declaring an evidence type twice, and of declaring zero
cohort: the sectioned and plain evidence type lists
condition: a measured grade requires an evidence ground

## Grounds

- code: src/claims_ledger/config.py § "from_table" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

from_table intersects the two lists and raises on any type in both, then raises when their union is empty. A type in both lists has two answers to whether a pointer of that type carries a section, and the checkers would take whichever they asked for. An empty union is a project where a measured grade has nothing it could rest on, which is a configuration that silently forbids the grade the ledger is mostly written in.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/config.py · standing · cites-as-live
