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

- 2026-09-08T14:17:14-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/__init__.py § "__all__" @989493fa4655725014cedb6408b4ff9c7e680498
  artifact: 263bfd4931fa02984416181466f88f64e7c03355
  note: propagated from a moved ground

- 2026-09-08T14:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/__init__.py § "__all__" @ee234ed85969dcc0c8400721f9a16162d6cee9f5
  note: read against commit ee234ed: the citing comment moved into this section from outside it, so the section now carries the sentence it always managed, into the list literal; both act lists are still named in it
- 2026-09-20T13:22:53-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/__init__.py § "__all__" @ee234ed85969dcc0c8400721f9a16162d6cee9f5
  artifact: sha256:e68f195e3420d000c760257f7a0c0fa4eb15d1ac5e0414dc31274fd5e5a2117e
  note: propagated from a moved ground

- 2026-09-20T13:23:13-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/__init__.py § "__all__" =sha256:e68f195e3420d000c760257f7a0c0fa4eb15d1ac5e0414dc31274fd5e5a2117e
  note: re-read after the commit that converts this file's markers to the short form. The only change inside the section is the citation itself, which lost the entry's slug and now names the id alone; it resolves to the same entry, under the same act, and the References row is unchanged. The list still carries both ACTS and ENTRY_ACTS.


## References

- src/claims_ledger/__init__.py · standing · cites-as-live
