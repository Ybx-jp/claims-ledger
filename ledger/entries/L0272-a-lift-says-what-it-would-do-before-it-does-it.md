---
id: L0272-a-lift-says-what-it-would-do-before-it-does-it
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: ff87f35f2cbc7bd4555e9ab2ed82258b52d2f6d987c7e8b620dea05ccab6f2e2
---

## Assertion

A lift writes nothing unless it is asked to, and the run that is not asked prints what it would take.

## Scope

metric: what a lift does without a write flag
cohort: the lift command
condition: a lift run against any entry

## Grounds

- code: src/claims_ledger/cli.py § "cmd_lift" =sha256:1ab0a161b369f62d2077a8c070b998b59e2aed2767d019dbaf3285dffd8161fb

## Warrant

A lift deletes prose from a project's source. Every other command in this package that writes is asked to; this one deletes rather than substitutes, so the run a person gets by default is the one that only reports, and the reverse patch is available in the same breath as the write.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-20T10:23:56-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "cmd_lift" =sha256:1ab0a161b369f62d2077a8c070b998b59e2aed2767d019dbaf3285dffd8161fb
  artifact: sha256:2441087d63ae9b2560f370e35a965436967ae946643e9e7ab656fcfd4bc974a9
  note: propagated from a moved ground

- 2026-09-20T10:24:06-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "cmd_lift" =sha256:2441087d63ae9b2560f370e35a965436967ae946643e9e7ab656fcfd4bc974a9
  note: cmd_lift grew the marker and the References row a lift now writes, and names both in the dry run beside the prose; the writes stay behind --write and the run without it still reports and returns, so the assertion is unaffected

## References

- src/claims_ledger/cli.py · standing · cites-as-live
- README.md · standing · cites-as-live
