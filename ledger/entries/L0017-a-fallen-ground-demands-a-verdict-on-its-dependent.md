---
id: L0017-a-fallen-ground-demands-a-verdict-on-its-dependent
kind: claim
stated: 2026-09-07T23:17:46-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 67b7cdd1eae6d9f164bb5e51eb2e115b2230db9229d502f646738e3c12871cb5
---

## Assertion

An entry citing a ground `cites-as-live` must carry a contested verdict by the propagation author naming that ground once the ground has fallen, and propagate reports the entry by name while it does not.

## Scope

metric: the reports propagate returns for a dependent whose live-cited ground has fallen
cohort: entries carrying an `entry:` ground with the cites-as-live act
condition: the ground's derived status is refuted, superseded or retracted, and the dependent's own is not

## Grounds

- code: src/claims_ledger/propagate.py § "run" @0af113005f955a4e120d71338993a94cc6efeb7b

## Warrant

run's first pass walks each entry's `entry:` grounds and, for a cites-as-live act whose target's derived status is in FALLEN, asks has_propagated for a matching verdict; when there is none it reports the dependent, names the target and the status it fell to, and queues the verdict the entry is owed.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T09:41:22-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/propagate.py § "run" @0af113005f955a4e120d71338993a94cc6efeb7b
  artifact: d7edcf2d43d01f126a1240c49607dcd4d379e414
  note: propagated from a moved ground

- 2026-09-08T09:50:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/propagate.py § "run" @5ee55ae6992f10c834510759f026644f42614025
  note: read against the change in commit 5ee55ae, which narrowed the dependent exemption from FALLEN to TERMINAL in that one branch; this claim names a different part of the same section and is unaffected
- 2026-09-11T03:09:46-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/propagate.py § "run" @5ee55ae6992f10c834510759f026644f42614025
  artifact: sha256:0ca4d23c82c30d940fab79c0e6c5feb672853f2c9f34db3401c9efbd0d9f8e59
  note: propagated from a moved ground
- 2026-09-11T03:09:46-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/propagate.py § "run" =sha256:0ca4d23c82c30d940fab79c0e6c5feb672853f2c9f34db3401c9efbd0d9f8e59
  note: read against the working tree after run gained a docstring carrying the citations for the rules it holds, moved into the span the grounds pin, since the reading at 5ee55ae: the code of the section is byte-identical once the docstring is set aside, so a dependent citing a fallen ground cites-as-live is still reported by name until it carries the contested verdict; the assertion holds as written.

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
