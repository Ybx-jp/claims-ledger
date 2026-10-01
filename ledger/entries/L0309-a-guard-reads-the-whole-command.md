---
id: L0309-a-guard-reads-the-whole-command
kind: claim
stated: 2026-10-01T00:54:12-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 95b1bddca074e014a2a479439437d0ec5fbaf80eac86bda082a73ed40128a639
---

## Assertion

A shipped guard decides on the whole of the input it is handed, however much of it follows the line that matches.

## Scope

metric: the verdict the merge guard returns on a rewriting merge
cohort: a command whose matching line is followed by more than a pipe buffer of further lines
condition: the guard runs under `set -o pipefail`, as every shipped hook does

## Grounds

- code: tests/test_harness.py § "test_a_guard_reads_the_whole_command_however_much_follows_the_match" =sha256:7b75b611d85e63801e99184c5f51ede2df5cdc33deabaf90ca1c15cdeaebf678

## Warrant

`grep -q` exits at its first match. Fed through `printf | grep -q` under `pipefail`, a writer still holding more than a pipe buffer dies of SIGPIPE, the pipeline takes the writer's status, and the test reads as no match: the guard allowed `gh pr merge --squash` and `git merge --squash` with 200 KB of further lines behind them, measured in a sibling project's copy of the same guard in 2000 runs of 2000 and reproduced here by the test before the fix. The hooks now hand `grep` its input as a here-string, which it reads whole. The test sends both rewriting merges with more than 200 KB behind them and asserts a refusal in each, and was red against the pipe.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- CLAUDE.md · standing · cites-as-live
