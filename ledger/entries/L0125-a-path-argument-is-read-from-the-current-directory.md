---
id: L0125-a-path-argument-is-read-from-the-current-directory
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: c77bbfe0b6ba93cf1bdd840e8e23d1a85017ed402e62dc8598c3af49368bfe3a
---

## Assertion

A path argument is read from the current directory, and when the same name would also resolve under the project root that is said rather than left to be discovered.

## Scope

metric: where a path argument is resolved from, and whether the ambiguity is explained
cohort: entry paths given to the fingerprint command
condition: the root may point somewhere other than the current directory

## Grounds

- code: src/claims_ledger/cli.py § "sha_one" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

sha_one resolves the path the way every other command-line tool resolves one, and additionally checks whether the same name exists under the configured root, printing where that entry is. With the root pointing elsewhere the same entry named two ways gave two answers and nothing said why, which is the kind of difference a person spends an afternoon on before finding it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T15:43:46-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "sha_one" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395
  artifact: 35b4942e4e85bac4d174a747be76674c1e9612e0
  note: propagated from a moved ground

- 2026-09-08T16:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "sha_one" @abb827e3cd4a443f4cc9e90f1db52a3d5c853622
  note: read against commit abb827e, which added the call reporting where a citation of the entry being fingerprinted sits; the message about a path read from the current directory, which is what this claim names, is unchanged and still first in the function

## References

- src/claims_ledger/cli.py · standing · cites-as-live
