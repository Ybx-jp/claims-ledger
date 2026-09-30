---
id: L0306-a-renumber-recomputes-a-fingerprint-the-substitution-moved
kind: claim
stated: 2026-09-24T22:03:10-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 8429140ca601a99685a63011087def4c24aa863bd38782541f89b885be6383b6
---

## Assertion

A renumber that moves an id named in an entry's Scope recomputes that entry's verbatim_sha in every rewritten commit, and only where the declared value matched the entry's text before the substitution.

## Scope

metric: the verbatim_sha a rewritten entry carries
cohort: every entry file claims-ledger renumber --write rewrites
condition: the substitution changed the entry's Scope; an entry whose declared value was already wrong keeps it

## Grounds

- code: src/claims_ledger/renumber.py § "refingerprint" =sha256:fb0bb93ebbf325c4a9af527279168f864a902b2a2b71bc596464bf34e28deb42
- code: src/claims_ledger/renumber.py § "rewrite" =sha256:9b3dc8e9d4b8136dec2db1f8d76ed7c7cb3ba8213843f7a178127308c528dd01
- code: tests/test_renumber.py § "test_a_fingerprint_the_substitution_moved_is_recomputed" =sha256:a629fcd0233293fd175ecf55a15632a9f178617cc4e47485720bf5d48c869705

## Warrant

rewrite passes every entry file of every commit through refingerprint after substituting and re-anchoring it; refingerprint returns the text unchanged unless the declared verbatim_sha equals the fingerprint of the text before substitution, and otherwise replaces the declared line with the fingerprint of the substituted text. The fingerprint reads only Scope and Backing, which are frozen, so the same text yields the same value in every commit that holds the entry. The test carries the entry in a commit after the one that creates it, so a recompute made only at the tip fails `check` over the history; the `qe` fix-review round (ticket `2b977a218b5f4e13`) measured that mutant green against the test as first written, where the tip was the only commit holding the entry. Backing is not claimed: an entry id can sit there only inside a `quote:`, which is verbatim third-party text, and a substitution there falsifies the quotation, which `resolve` still reports and a recomputed fingerprint does not repair (#78).

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
- docs/OPERATING.md · standing · cites-as-live
