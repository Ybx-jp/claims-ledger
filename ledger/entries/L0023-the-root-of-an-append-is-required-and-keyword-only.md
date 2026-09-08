---
id: L0023-the-root-of-an-append-is-required-and-keyword-only
kind: claim
stated: 2026-09-07T23:17:47-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 191535fff6425c4a5ccb5eeef16ae238a5a669f1b64ed00fa44ea9b53268cc68
---

## Assertion

The root an append is confined to is a required keyword-only parameter, so a caller cannot reach the write without stating it.

## Scope

metric: the signature of the append, and what a call omitting the root does
cohort: every call site of the verdict append
condition: a caller written without the guard in mind

## Grounds

- code: src/claims_ledger/propagate.py § "append_verdict" @0af113005f955a4e120d71338993a94cc6efeb7b
- entry: L0022-nothing-is-written-through-a-link-that-leaves-the-root · cites-as-live

## Warrant

append_verdict places root after a bare `*` and gives it no default, so a call omitting it raises at the call site rather than writing unguarded. A default would make the guard optional, and the guard is the whole of the confinement L0022 states; three write sites had already been found that never asked the question.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
