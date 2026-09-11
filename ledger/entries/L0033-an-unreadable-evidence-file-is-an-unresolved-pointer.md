---
id: L0033-an-unreadable-evidence-file-is-an-unresolved-pointer
kind: claim
stated: 2026-09-08T02:02:28-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 9eb2368af2d667c428c98629fd0d5b3b6342f24bf8561d8ee7c6c2a274061072
---

## Assertion

An unpinned evidence path that cannot be read, or that is not UTF-8 text, is reported as a pointer that does not resolve, and does not raise out of the checker.

## Scope

metric: the outcome of resolving an unpinned evidence pointer whose file cannot be decoded or opened
cohort: evidence pointers whose pin names no revision
condition: the path exists and is a file

## Grounds

- code: src/claims_ledger/resolve.py § "resolve_pointer" @ec82c16045421ce5a6cb71befe8ddbe6067489ae

## Warrant

resolve_pointer reads the working-tree file through read_document rather than through read_text. read_document answers a decoding error or an OS error with a problem and no text, instead of letting the exception leave the call, so the unreadable file arrives at the same branch a missing file takes and is reported against the pointer that named it.

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
  note: read against the working tree after the anchor-by-value branch was added: an unpinned path is still read through read_document and reported rather than raised, and a by-value pointer now takes the same branch; the assertion holds as written.

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
