---
id: L0286-a-path-rule-is-the-first-one-that-matches
kind: claim
stated: 2026-09-20T12:32:14-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: dbba65dcd624b539b4c2aa6624b104bb5a8c3437b948c19f64090b3045a06899
---

## Assertion

Where the slug setting is a list of rules, a document is governed by the earliest rule whose paths match it, and by the default where the list leaves it unmatched.

## Scope

metric: which rule decides the slug question for a given document
cohort: a citation-slug setting written as a list of rules
condition: no rule matches the document, one does, or more than one does

## Grounds

- code: src/claims_ledger/config.py § "_citation_slug" =sha256:4bd5d7b427d61917fbca630b3f64693826afed8e67bd3efa31a231f1992b9c12
- code: src/claims_ledger/schema.py § "citation_slug_policy" =sha256:ec3a3db6a290a06172e44d3024252f97eaecfb30aae6cbb971c5163c4e99368b
- entry: L0285-the-slug-a-marker-carries-is-configured · distinguishes

## Warrant

Precedence is the order the project wrote, which is a list and not a table: TOML gives a list an order and gives a table none, so a rule set whose winner depended on a table's order would be one two readers of the same file could disagree about. The narrow rule therefore goes above the wide one, which is how a person reads a rule list anyway. A document no rule reaches is left at the default rather than refused, because partial coverage is what a project asking for one shape in its prose and another in its source is asking for; a project that wants a rule everywhere writes a final rule whose paths are a catch-all. The match is asked of the path through the same glob matcher the document globs are read with, so a rule's reach does not depend on which tree the run was asked about. L0285 is a different claim about the same setting — what it may be set to, and what a project that set nothing gets — and is distinguished rather than left to be read as this one.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/config.py · standing · cites-as-live
- src/claims_ledger/schema.py · standing · cites-as-live
- README.md · standing · cites-as-live
