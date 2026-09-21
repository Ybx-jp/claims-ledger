---
id: L0114-pinned-grounds-without-a-repository-are-a-failure-and-not-silence
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: d6f976844f9225ba666b56748e87baae5de9f04488af5cf2f22badf277af2f41
---

## Assertion

A ledger holding grounds pinned to commits, with no repository to ask about them, is a failure naming how many grounds went unchecked.

## Scope

metric: what a run reports when there are pinned grounds and no repository
cohort: ledgers outside version control, or whose repository is unreadable
condition: the ledger holds at least one pinned evidence ground

## Grounds

- code: src/claims_ledger/freshness.py § "run" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

run counts the pinned grounds and, finding no repository, returns a single failure saying that freshness did not run over them; a repository that cannot answer at all is reported the same way. Silence here would be the failure mode this package exists to refuse — a check that did not run, reported as a check that passed — and it would be silence over exactly the grounds the checker was written for.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:43-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "run" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
  artifact: 7bf8ce83b6bb554674722efe7e644aa962b022ef
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed
- 2026-09-09T13:28:16-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "run" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  artifact: d3839ddf380073c420e1b127e402cf5d058cad26
  note: propagated from a moved ground
- 2026-09-09T13:28:16-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" @825902da5293a5d7121cfa0a7b9cc6d3d4eb5ef0
  note: read against commit 825902d, which compares each ground from the pointer effective_pointer returns and names that reading in the flag; how a verdict is appended, what a missing repository or an unstatable artifact or a terminal entry gets, and the once-per-run memo are unchanged; the assertion holds as written.
- 2026-09-09T14:03:34-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "run" @825902da5293a5d7121cfa0a7b9cc6d3d4eb5ef0
  artifact: f66a2097acc62a3f20e2c68d4e597975ee945f95
  note: propagated from a moved ground
- 2026-09-09T14:03:35-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" @54aa2e467954028f16a77e1a3d15d9d4b37a40ff
  note: read against commit 54aa2e4, which passes the run's ancestry memo to effective_pointer and orphans; nothing else in the loop changed, and the appends, the failure without a repository, the exit after a write, the unstatable artifact, the terminal exemption and the once-per-run memo hold; the assertion holds as written.
- 2026-09-10T22:05:57-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "run" @54aa2e467954028f16a77e1a3d15d9d4b37a40ff
  artifact: sha256:e95965ef764409d49cfc0a68bcbf017e722714e5427d9bb10082f5f6110e1793
  note: propagated from a moved ground
- 2026-09-10T22:06:17-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" =sha256:e95965ef764409d49cfc0a68bcbf017e722714e5427d9bb10082f5f6110e1793
  note: read against the working tree after freshness began comparing by digest on both sides: the failure now counts the grounds anchored at commits, since a ground anchored by value is compared against the working tree with or without a repository; the assertion is true of the grounds it names, which are the pinned ones, and holds as written.

- 2026-09-11T22:04:31-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" =sha256:5845bd95fa9dbd8dfddbd89e398428975cac3ba77376d3ff4263898772561d03
  note: re-read after the commit answering the fix-review gate on this branch (qe ticket e9b7d35601214a1b). The same: the entries come through `entries_for` now. The comparison, what it records and when it writes are unchanged.

- 2026-09-12T15:32:58-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" =sha256:9b25e634a8f1b63fa4fdcf8d7f11ce70d7110ce3e78cf93ad24d03ee23c3efa7
  note: acknowledged: the run threads the ledger into `drift` for the cached reads. This claim is untouched by that (L0232).
- 2026-09-20T17:44:02-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "run" =sha256:9b25e634a8f1b63fa4fdcf8d7f11ce70d7110ce3e78cf93ad24d03ee23c3efa7
  artifact: sha256:52b08359937b4d1b390b0c2a0f9b6861f9d188c23cd83fbc9b16ebbcdf6b8faf
  note: propagated from a moved ground

- 2026-09-20T17:45:59-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" =sha256:52b08359937b4d1b390b0c2a0f9b6861f9d188c23cd83fbc9b16ebbcdf6b8faf
  note: The no-repository branch above is untouched — pinned grounds with no repository still report a failure by name. The line added below it is guarded on the same condition and falls back to `("HEAD",)` where there is no repository to ask, so it cannot be reached in the state this claim is about.

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
