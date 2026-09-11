---
id: L0030-an-unaskable-git-is-reported-once-for-the-ledger
kind: claim
stated: 2026-09-08T02:02:20-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 31c94b00fb9cff8e408bf8b37061ce7a76ceaeaaa8288eb2e61080ca5d46aad6
---

## Assertion

When git cannot be asked at all, the run says so once for the whole ledger and leaves every pinned pointer unjudged, rather than reporting each of them as a pointer that does not resolve.

## Scope

metric: the number of reports emitted for an unavailable git, and what each pinned pointer is then said to be
cohort: ledgers holding at least one pinned evidence pointer
condition: git absent from PATH, or present and unable to answer for the repository

## Grounds

- code: src/claims_ledger/resolve.py § "run" @ec82c16045421ce5a6cb71befe8ddbe6067489ae
- code: src/claims_ledger/resolve.py § "resolve_pointer" @ec82c16045421ce5a6cb71befe8ddbe6067489ae

## Warrant

run asks git_problem once, and only when some entry actually holds a pinned pointer; the answer becomes a single Grounds-level failure saying the pins were not read out of git and that whether each still names its artifact is unknown. That same answer is handed to resolve_pointer, which returns without judging any pinned pointer. The unavailability is therefore reported as unavailability, and no pin is described as unresolved on the strength of a question git never answered.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-10T21:49:35-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "resolve_pointer" @ec82c16045421ce5a6cb71befe8ddbe6067489ae
  artifact: 380802d3237b2e0a79b628ddda818b883cf042b5
  note: propagated from a moved ground
- 2026-09-10T21:49:48-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "resolve_pointer" =sha256:f01906eb76fb139642ae98df2065ca95a93dceb22e3ed5ee178f036c9203d30b
  note: read against the working tree after the anchor-by-value branch was added: an unaskable git still leaves every pinned pointer unjudged through the same unasked gate, and a pointer stated by value never reaches git at all; the assertion holds as written.
- 2026-09-11T02:49:32-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "run" @ec82c16045421ce5a6cb71befe8ddbe6067489ae
  artifact: sha256:3abb7abd6286ca9b9d146f430c1723b8be318754b5c247bcfcd5369c5df8adc0
  note: propagated from a moved ground

- 2026-09-11T02:49:32-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "resolve_pointer" =sha256:f01906eb76fb139642ae98df2065ca95a93dceb22e3ed5ee178f036c9203d30b
  artifact: sha256:55d28960d1b04ffe2db203a3b19334115b161628741178ffc4ed4882dac5893d
  note: propagated from a moved ground
- 2026-09-11T02:49:51-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "run" =sha256:3abb7abd6286ca9b9d146f430c1723b8be318754b5c247bcfcd5369c5df8adc0
  note: read against the working tree after resolve began resolving a ground anchored by value from the tree or from history: run now routes such a ground to resolve_by_value, asks once per entry whether git holds it, and passes a by-value reading's own evidence over; the unasked gate is asked once for the ledger before either path and both honour it, and the retraction re-check is unchanged; the assertion holds as written.
- 2026-09-11T02:49:51-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "resolve_pointer" =sha256:55d28960d1b04ffe2db203a3b19334115b161628741178ffc4ed4882dac5893d
  note: read against the working tree after the by-value branch was moved out of resolve_pointer into resolve_by_value: what remains is the unpinned read from the tree, the pinned read out of git, and the entry and source branches, and the failure messages now write the pin as @<pin> since no by-value anchor reaches them; the assertion holds as written.

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
