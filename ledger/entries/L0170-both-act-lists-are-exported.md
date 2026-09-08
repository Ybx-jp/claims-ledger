---
id: L0170-both-act-lists-are-exported
kind: claim
stated: 2026-09-08T13:50:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: b76bb2adbb011abb3cf475f98caed596117e64466840b3605429102312c7ce96
---

## Assertion

Both act lists are declared exports of the package: the citation acts a document may write, and the acts a ground may carry.

## Scope

metric: whether each act list appears in the declared export list
cohort: ACTS and ENTRY_ACTS
condition: the package as it ships

## Grounds

- code: src/claims_ledger/__init__.py § "__all__" @989493fa4655725014cedb6408b4ff9c7e680498

## Warrant

Both names are in __all__ and imported at the top of the module, so asking the package for either is a declared interface rather than a submodule that happens to have been imported first. The difference between the two lists is the one a writer has to get right, and the shipped agent skills tell a reader to print the vocabulary rather than carry a copy — an instruction that is only followable while both lists are reachable from the package root. Exporting one and not the other would leave it true of every part of the vocabulary except the part most easily got wrong.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/__init__.py · standing · cites-as-live
