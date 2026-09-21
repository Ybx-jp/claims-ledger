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
- 2026-09-11T03:57:56-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "run" =sha256:3abb7abd6286ca9b9d146f430c1723b8be318754b5c247bcfcd5369c5df8adc0
  artifact: sha256:46ff53ce04ef51ab0c8664adc2690f80426a469e4d4df265094310a9c67f133b
  note: propagated from a moved ground
- 2026-09-11T03:58:17-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "run" =sha256:46ff53ce04ef51ab0c8664adc2690f80426a469e4d4df265094310a9c67f133b
  note: read against the working tree after run began passing --cached through to resolve_by_value, so a by-value anchor is held to the index under the hook: the unasked gate is still asked once for the ledger and honoured by both paths; the assertion holds as written.

- 2026-09-11T19:50:54-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "run" =sha256:1afa6db071f8945b7597ec1f0a6e820cb7c492a0ceb8f12a824bd26f1c9b7352
  note: re-read after the same commit, which passes the cached flag to the registry reader and to the entry load this function falls back on. Every rule this claim is about is untouched.

- 2026-09-11T21:12:37-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "run" =sha256:b990e60091c0928d78bbb6d5733fe0354c6f242962eab2644ca770fc0cd96eba
  note: re-read after the same commit, which passes the cached flag on to the pointer reader at both of this function's call sites. Every rule this claim is about is untouched.

- 2026-09-11T21:12:37-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "resolve_pointer" =sha256:fc0a18fb75dbff09becb8ca4c1722262b0bde177a4bc084884ee11dcf75a8f5c
  note: re-read after the commit that has a ground pinned at working read from the tree the run reads — the index under the flag, the working tree for a path the index does not hold, and the staged bytes decoded strictly so that an artifact which is not UTF-8 is not resolved where the working-tree read would refuse it. The rule this claim states is untouched and is the one that decided the strict decode.

- 2026-09-11T22:04:31-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "resolve_pointer" =sha256:19bcb888815f2f87524700a5797837a53eecd7d27c0e9462981a29caee410876
  note: re-read after the commit answering the fix-review gate on this branch (qe ticket e9b7d35601214a1b). An artifact git was asked for and did not answer is reported on the pointer's own line instead of being read from the working tree. The `working` rule, the strict decode and the section rule are unchanged.
- 2026-09-15T17:25:45-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "run" =sha256:b990e60091c0928d78bbb6d5733fe0354c6f242962eab2644ca770fc0cd96eba
  artifact: sha256:2bfa357fbe8fda54952652567afb5536943e32f65bbd43cfa63ae739b9b7caf3
  note: propagated from a moved ground

- 2026-09-15T17:26:29-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "run" =sha256:2bfa357fbe8fda54952652567afb5536943e32f65bbd43cfa63ae739b9b7caf3
  note: re-read after the per-entry loop gained a pass over the entry's held passages, which resolves each witness and compares the prose against the version it names. The grounds, verdict-evidence and Backing passes above it are unchanged, and so is the one question asked of git before any pinned pointer is read.
- 2026-09-20T15:29:16-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "run" =sha256:2bfa357fbe8fda54952652567afb5536943e32f65bbd43cfa63ae739b9b7caf3
  artifact: sha256:6174cdacc1864c2cbb4b6e9c87ebfa0125f4553476f8b1c981269fb73e78636b
  note: propagated from a moved ground

- 2026-09-20T15:29:43-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "run" =sha256:6174cdacc1864c2cbb4b6e9c87ebfa0125f4553476f8b1c981269fb73e78636b
  note: re-read after the commit that widens what `is_committed` asks. The only change inside the section is the argument that call takes. every pointer is still resolved and a source still read once.
- 2026-09-20T17:44:01-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "run" =sha256:6174cdacc1864c2cbb4b6e9c87ebfa0125f4553476f8b1c981269fb73e78636b
  artifact: sha256:5d6ce8d6b0de9d60202f47fdb33e743ea031cd0a0d38469595ce8d861beb8150
  note: propagated from a moved ground

- 2026-09-20T17:45:59-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "run" =sha256:5d6ce8d6b0de9d60202f47fdb33e743ea031cd0a0d38469595ce8d861beb8150
  note: The `unasked` probe and the single report built from it are byte-identical and still asked once for the ledger. The line added after them binds the reach handed to `effective_pointer`, for the same once-per-run reason.

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
