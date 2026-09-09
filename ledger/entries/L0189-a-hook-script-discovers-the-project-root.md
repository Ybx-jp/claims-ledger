---
id: L0189-a-hook-script-discovers-the-project-root
kind: claim
stated: 2026-09-08T21:44:39-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 9d0517eaff6f6f8314b05f9b532c32c7834f801393cd3d0f73b35a172453dfb9
---

## Assertion

No hook script the package ships counts directories to the project root; each one discovers it.

## Scope

metric: how a hook script determines the project root
cohort: every hook script in the shipped harness that needs a root
condition: the same file runs from inside the installed package and from a project's own hook directory

## Grounds

- code: tests/test_harness.py § "test_no_hook_script_counts_directories_to_the_project_root" @52859264d2caa6d447021f4cda3c8b26e7d72c1f

## Warrant

The search is the ground: the test reads every shipped script and fails on one that walks a fixed number of parents. A script that counted them would guard the wrong tree from one of the two places it now runs, and the root is asked of the harness first, then found by walking up for a directory that looks like a project, and never taken from the working directory, which is wherever the session happens to be.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- CLAUDE.md · standing · cites-as-live
