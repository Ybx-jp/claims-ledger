---
id: L0027-one-function-appends-every-verdict
kind: claim
stated: 2026-09-07T23:17:47-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 2b2227db7500da6a88f0bc608e01fce8a23847c3fc334c084d86a74cab640353
---

## Assertion

Both checkers that write verdicts write them through the same function: freshness reaches its append through the one propagate defines rather than through an append of its own.

## Scope

metric: the number of definitions in the package that insert text into an entry's appendable region
cohort: propagate --write and freshness --write
condition: the package as it ships

## Grounds

- code: src/claims_ledger/propagate.py § "append_verdict" @0af113005f955a4e120d71338993a94cc6efeb7b
- code: src/claims_ledger/freshness.py § "run" @0af113005f955a4e120d71338993a94cc6efeb7b

## Warrant

append_verdict is the definition that performs the insertion, and freshness's run reaches its write through the imported append_verdict and grouped rather than composing one, so the marker guard, the line-ending handling and the root check are established once and hold for both checkers.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:42-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "run" @0af113005f955a4e120d71338993a94cc6efeb7b
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

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
