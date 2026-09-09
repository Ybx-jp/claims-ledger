---
id: L0187-an-install-with-nothing-to-install-refuses
kind: claim
stated: 2026-09-08T21:44:39-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: bad84eec5f157a3e12ccd6b401e55e90d22113a5cc17160518894c07a81783af
---

## Assertion

An install refuses when the package it is installing from carries no skills or no hook scripts, rather than writing nothing and reporting success.

## Scope

metric: what an install does when the packaged resources are missing
cohort: every run of the harness installer
condition: a distribution may be built without the resource tree in it

## Grounds

- code: src/claims_ledger/harness.py § "resources_or_refuse" @52859264d2caa6d447021f4cda3c8b26e7d72c1f

## Warrant

The resources are read before anything is planned, and their absence is an error naming what is not there. This is not hypothetical: a symbolic link from an agent directory into the package made the build follow it, count each skill as seen at a path no distribution includes, and drop all three, so an install from the released copy wrote nothing and printed a clean report of a plan with no files in it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/harness.py · standing · cites-as-live
