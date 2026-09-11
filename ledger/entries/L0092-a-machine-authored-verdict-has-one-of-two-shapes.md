---
id: L0092-a-machine-authored-verdict-has-one-of-two-shapes
kind: claim
stated: 2026-09-08T02:30:57-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 5e4c95790de850c706a091ec6ba16e567d17966df9a774655262a4eab5a3b0fc
---

## Assertion

A verdict written under the propagation author is refused unless it takes one of the two shapes the machinery produces.

## Scope

metric: whether a hand-written verdict under the machine's author name is reported
cohort: verdicts whose author is the configured propagation author
condition: the two shapes are propagate's entry evidence and freshness's pinned ground

## Grounds

- code: src/claims_ledger/validate.py § "check_verdicts" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_verdicts recognizes contested with entry evidence acting fallen or challenges, and contested with an evidence ground carrying a pin; anything else under that author fails. Those two are what propagate and freshness write. A verdict of any other shape under the machine's name is a person claiming a check that did not run, and a reader takes a machine-authored verdict as exactly that claim.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-10T22:05:56-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_verdicts" @34f416118e10a14169475fe23d3176d347d0ed8d
  artifact: sha256:cf64b57b2a6d1b3aad822325eaa3371cbbb7adf635f773ad6e7b53c12cb4341a
  note: propagated from a moved ground
- 2026-09-10T22:06:16-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_verdicts" =sha256:cf64b57b2a6d1b3aad822325eaa3371cbbb7adf635f773ad6e7b53c12cb4341a
  note: read against the working tree after freshness began comparing by digest on both sides: the artifact-shape branch now also accepts a section digest; the two shapes a machine-authored verdict may take are unchanged, and the assertion holds as written.
- 2026-09-11T03:57:56-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_verdicts" =sha256:cf64b57b2a6d1b3aad822325eaa3371cbbb7adf635f773ad6e7b53c12cb4341a
  artifact: sha256:2cc50a11f18089b10ca35b6968d534962c348565f1c4911bc74d46621f6af10b
  note: propagated from a moved ground
- 2026-09-11T03:58:17-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_verdicts" =sha256:2cc50a11f18089b10ca35b6968d534962c348565f1c4911bc74d46621f6af10b
  note: read against the working tree after the restatement rule in check_verdicts began exempting a corroboration stated by value, which may name the ground's own digest: the two machine shapes and the refusal of anything else under the propagation author are unchanged; the assertion holds as written.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
