---
id: L0106-an-artifact-that-cannot-be-read-is-unknown-and-not-moved
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 9dbef7eaa8c4250270d85b8a14e1b3f27a1c5ad810ccf81000bbdddfd36a7880
---

## Assertion

An artifact that could not be read at all yields an unknown finding, and never a moved or a withdrawn one.

## Scope

metric: the finding for an artifact whose bytes could not be obtained
cohort: evidence artifacts in the working tree or the index
condition: an artifact that is present and is not text is a different case

## Grounds

- code: src/claims_ledger/freshness.py § "now_text" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
- code: src/claims_ledger/freshness.py § "in_this_run" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
- code: src/claims_ledger/freshness.py § "drift" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

now_text returns the reason the bytes could not be had alongside the text, and drift turns any such reason into unknown with the reason attached. An artifact that is there and is not UTF-8 text is deliberately not one of these: it really did change and simply cannot be narrowed to a section, which is what moved already says. Throwing the reason away is what made an unreadable evidence file come back as a confident finding of movement at exit 0.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T19:39:25-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "now_text" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
  artifact: e2386c2564c931207a03de464b78a3bae971afac
  note: propagated from a moved ground

- 2026-09-08T19:39:25-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "in_this_run" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
  artifact: e2386c2564c931207a03de464b78a3bae971afac
  note: propagated from a moved ground

- 2026-09-08T19:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "now_text" @225f5867b2591ffc5b3020dfe20ca407d81ee06f
  note: read against commit 225f586, which moved `ARCH-AUDIT.md` into `docs/audits/` and rewrote the mentions of it in this section; the section was parsed at the pin and at that commit and compared with comments and docstrings set aside, and the two are identical, so nothing the claim rests on changed

- 2026-09-08T19:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "in_this_run" @225f5867b2591ffc5b3020dfe20ca407d81ee06f
  note: read against commit 225f586, which moved `ARCH-AUDIT.md` into `docs/audits/` and rewrote the mentions of it in this section; the section was parsed at the pin and at that commit and compared with comments and docstrings set aside, and the two are identical, so nothing the claim rests on changed
- 2026-09-10T22:05:57-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "drift" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
  artifact: sha256:ec78ecef0788830e1fe16fe77e34d9d23292efbc3622b7af29e1defa9a216ff6
  note: propagated from a moved ground
- 2026-09-10T22:06:17-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "drift" =sha256:ec78ecef0788830e1fe16fe77e34d9d23292efbc3622b7af29e1defa9a216ff6
  note: read against the working tree after freshness began comparing by digest on both sides: drift keeps its unknown branches for a path that cannot be reached and a file that cannot be read, in front of the digest comparison that replaced git's diff; the assertion holds as written.

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
