---
id: L0059-a-section-pattern-is-checked-when-it-is-read
kind: claim
stated: 2026-09-08T02:13:07-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: a9de88854051a7a80df9bf9f455716ccb2b45c7f3210d5b7554c2c6a44672310
---

## Assertion

Every configured section pattern is checked as the configuration is read: it must be a string, name a type declared sectioned, contain the name slot, and compile with the slot filled by a section name and by the widened form alike.

## Scope

metric: when and how thoroughly a configured section pattern is checked
cohort: the section-patterns table
condition: the pattern is used twice, once to find a section and once to find where the next begins

## Grounds

- code: src/claims_ledger/config.py § "_section_patterns" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

_section_patterns applies all four tests at load and raises naming the offending type. Deferring them to the entry that happens to use the pattern is what turns a bad pattern into a checker that quietly matched the wrong text: a pattern lacking the name slot finds the same span for every section, and one that compiles only in the narrow substitution leaves a section whose end nothing can locate. Both substitutions are compiled here because both are what the section boundary is made of.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/config.py · standing · cites-as-live
