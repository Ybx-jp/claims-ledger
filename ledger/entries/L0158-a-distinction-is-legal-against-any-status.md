---
id: L0158-a-distinction-is-legal-against-any-status
kind: claim
stated: 2026-09-08T12:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 6298ebe2622ba1eb8efe7ea8f741f19a7b9fe9f64108f387db4ceebdbdba6a0e
---

## Assertion

A distinguishes act is legal against a target of every status the schema has, so no verdict on the target can make the act illegal.

## Scope

metric: the target statuses each act is legal against
cohort: the distinguishes act
condition: every status the schema declares

## Grounds

- code: src/claims_ledger/schema.py § "ACT_ALLOWS" @aadceb0aba82a85fe71b15394896c43977751709
- code: src/claims_ledger/references.py § "run" @aadceb0aba82a85fe71b15394896c43977751709

## Warrant

ACT_ALLOWS maps distinguishes to the whole status vocabulary, and references reads that map rather than a rule of its own, so there is one table to change and no second opinion. The reason is not the one cites-as-fallen has: a distinction is a claim about two Scopes rather than about a truth, and a target that is refuted, superseded or non-comparable was still a different claim about the same artifact. Grounds are frozen once committed, so an act that could be made illegal by somebody else's verdict would be a failure with no repair.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
- docs/SCHEMA.md · standing · cites-as-live
- README.md · standing · cites-as-live
