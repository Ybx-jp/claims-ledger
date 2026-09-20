---
id: L0283-the-commented-table-init-writes-is-the-last-one
kind: claim
stated: 2026-09-20T12:13:25-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 9a75dbe36e31949a792c27a75c6809319ed48c5f7f904098463084f4040e049b
---

## Assertion

The commented section-patterns table `claims-ledger init` writes is the last table in the file, so uncommenting it where it stands moves every other key nowhere.

## Scope

metric: which keys are top-level after the scaffold's table is uncommented in place
cohort: the configuration `claims-ledger init` writes
condition: the edit is the one the comment invites, made where the comment is

## Grounds

- code: tests/test_cli.py § "test_uncommenting_the_section_patterns_table_where_it_stands_moves_no_other_key" =sha256:baaed410f9f551ec8dfa2d7cc1bd3027255c148056c061bde94dec5d0b3ddb9b

## Warrant

A TOML table header takes every key below it until the next header, so where the table is written decides what it contains. The test uncomments the two lines exactly as the scaffold writes them, parses the result, and asserts that the table holds `code` alone and that the four keys that used to sit below it are still top-level. Configuring a section pattern is the first edit a project pinning claims to source has to make, so the scaffold put the trap on the one path every such project takes, and the error named a key the user had never written.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
