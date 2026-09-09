---
id: L0190-a-built-distribution-carries-every-shipped-resource
kind: claim
stated: 2026-09-08T21:44:39-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 75a0f2174bb465fe210952f487bb486d770679a874e742382c4577906b71aacc
---

## Assertion

What a built distribution carries of the shipped harness is measured against the tree rather than assumed.

## Scope

metric: the resource files present in a built wheel, against the resource files in the source tree
cohort: every build of this package
condition: the build decides for itself which files it takes, and says nothing about the ones it drops

## Grounds

- code: tests/test_harness.py § "test_a_built_distribution_carries_every_shipped_resource" @52859264d2caa6d447021f4cda3c8b26e7d72c1f

## Warrant

The test builds a wheel and compares the resource files in it with the resource files on disk, because what the wheel holds is exactly what an installed copy can write. The build once dropped three directories without an error, and an installer whose payload is missing has no way to tell that from an empty plan.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- CLAUDE.md · standing · cites-as-live
