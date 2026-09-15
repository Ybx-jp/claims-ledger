---
id: L0243-the-merge-time-policy-is-configured-and-defaults-to-refusing
kind: claim
stated: 2026-09-14T19:20:55-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: bceef746edd83ecc18d9334b7ae1b21eb247604b3b62047fe6b4e9e473048b75
---

## Assertion

What a merge guard does about a colliding number is configured as merge-renumber, which is one of off, refuse or rewrite and defaults to refusing the merge.

## Scope

metric: the value of merge-renumber a configuration yields, and what a value outside the three does
cohort: every project configuration this package reads
condition: the key is absent, one of the three, or something else

## Grounds

- code: src/claims_ledger/config.py § "DEFAULT_MERGE_RENUMBER" =sha256:91f27b29d551fa941c628f02f8876fb13d351fb9552ddcb9fe486fba75c02d56
- code: src/claims_ledger/config.py § "from_table" =sha256:d46a203a53a75db2dc9e6de29e3ccfbfa9ea1402096166bf293a295d5d09af67

## Warrant

DEFAULT_MERGE_RENUMBER is refuse and MERGE_RENUMBER_POLICIES is the three values; from_table reads the key against that list and raises ConfigError naming the value and the three, so a misspelled policy stops the command rather than being read as one of them.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-14T20:21:10-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:d46a203a53a75db2dc9e6de29e3ccfbfa9ea1402096166bf293a295d5d09af67
  artifact: sha256:222a65392276c0cc61e35fec1bfabd395dee5590c848b57d4303b30b4f3ec738
  note: propagated from a moved ground

- 2026-09-14T20:21:11-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:222a65392276c0cc61e35fec1bfabd395dee5590c848b57d4303b30b4f3ec738
  note: re-read after the commit that fixes what the pre-merge gate found. The duplicate of this very check is gone and one copy remains, which is what this claim asserts of it: the key is read against MERGE_RENUMBER_POLICIES and a value outside the three raises ConfigError naming both.

## References

- src/claims_ledger/config.py · standing · cites-as-live
- src/claims_ledger/cli.py · standing · cites-as-live
- docs/OPERATING.md · standing · cites-as-live
