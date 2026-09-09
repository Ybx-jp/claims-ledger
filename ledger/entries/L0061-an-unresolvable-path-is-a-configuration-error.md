---
id: L0061-an-unresolvable-path-is-a-configuration-error
kind: claim
stated: 2026-09-08T02:13:07-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 6b90c606435d1834d56c01fcebdab959a6a0ca7075e869d4991558f7478722dc
---

## Assertion

A path the interpreter cannot resolve is reported as a configuration error naming the path, rather than reaching the caller as an internal error.

## Scope

metric: what a symlink loop or a path walking through a non-directory produces
cohort: the project root and the configuration file path
condition: the failure reaches pathlib differently across interpreter versions

## Grounds

- code: src/claims_ledger/config.py § "resolved" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

resolved catches both the OSError and the RuntimeError that resolution can raise and converts them into a ConfigError naming the path and what it was. A root pointing at a symlink loop is a misconfigured root on every interpreter, whichever way that version happens to report it, and the reader needs the path rather than a traceback asking them to file a bug.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/config.py · standing · cites-as-live
