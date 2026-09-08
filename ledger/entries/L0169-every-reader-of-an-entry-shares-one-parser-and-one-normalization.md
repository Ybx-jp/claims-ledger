---
id: L0169-every-reader-of-an-entry-shares-one-parser-and-one-normalization
kind: claim
stated: 2026-09-08T12:00:00-07:00
author: main
grade: measured
supersedes: L0136-the-checkers-share-one-parser-and-one-normalization
verbatim_change: the cohort was the four checkers named in it; it is now every module in the package that reads an entry, which is the population the metric was always counting over and which the predecessor understated by four
verbatim_sha: 05faee46843522b11186c8ef5f39baba818445b51189812f1ee2a897e9af08f0
---

## Assertion

Every module in the package that reads an entry reads it through one parser, one normalization, one fingerprint and one status derivation, so no two of them can disagree about what an entry says.

## Scope

metric: the number of definitions in the package that parse an entry, normalize text, compute the fingerprint, or derive a status
cohort: every module that reads an entry, which is validate, resolve, references, propagate, freshness, authoring, neighbours and the command line
condition: the package as it ships

## Grounds

- code: src/claims_ledger/schema.py § "parse_entry" @aadceb0aba82a85fe71b15394896c43977751709
- code: src/claims_ledger/schema.py § "normalize" @aadceb0aba82a85fe71b15394896c43977751709
- code: src/claims_ledger/schema.py § "fingerprint" @aadceb0aba82a85fe71b15394896c43977751709
- code: src/claims_ledger/schema.py § "derive_status" @aadceb0aba82a85fe71b15394896c43977751709

## Warrant

Each of those four is defined once here and imported by every module that reads an entry rather than reimplemented in any of them. A second normalization would let the fingerprint and the resolver disagree about what counts as a change; a second status derivation would let one reader call an entry open while another called it contested, and every citation rule is written against the status. Sharing them makes disagreement a thing that has to be introduced rather than a thing that has to be prevented. The predecessor named four checkers, which was true of those four and narrower than the metric it stated: freshness, authoring and the command line already read entries through the same four definitions when it was written, and the neighbours lookup is the reader whose arrival made the gap worth repairing rather than restating.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
