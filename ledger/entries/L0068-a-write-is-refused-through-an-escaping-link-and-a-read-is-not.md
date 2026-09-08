---
id: L0068-a-write-is-refused-through-an-escaping-link-and-a-read-is-not
kind: claim
stated: 2026-09-08T02:26:24-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: fc7e810e298d147ea80efc1723dc9fddc681d6dfdd69d25f497abb815dea2ba6
---

## Assertion

A write is refused when the file it would land on resolves outside the project root, while a read through such a link is left alone.

## Scope

metric: whether a write and a read are treated alike when a path leaves the root
cohort: entry files and cache slots this package writes
condition: a file inside the entries directory can be a symlink to anywhere

## Grounds

- code: src/claims_ledger/authoring.py § "refuse_to_write_outside_the_root" @c9f052af09e01b65a2adde51e941ebf24671dcaa

## Warrant

refuse_to_write_outside_the_root asks leaves_root where the destination really is and raises naming both the path and where it led. Only the writers call it: an entry symlinked in from outside is parsed and checked like any other, because reading a file the project points at changes nothing, while writing through the same link edits a file the project does not contain. Confining the entries directory does not settle this — the directory is inside the root, and the individual file is the way out.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
