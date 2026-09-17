---
id: L0270-a-lift-leaves-the-summary-line
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 1332c88f5378cfe6b298d432b55e27db17c342fd443c34f357796146c7344156
---

## Assertion

A lift takes the body of a docstring and leaves its summary line, so the distributed package still answers with a sentence.

## Scope

metric: which part of a docstring a lift takes
cohort: the docstring of a section a lift is run on
condition: a package whose installed copy is read by help and pydoc

## Grounds

- code: src/claims_ledger/lift.py § "liftable" =sha256:7360a696fa36f08b3acee31551973e2b3d8a12729c63993fed2dcdaa9a10d619

## Warrant

A docstring lifted whole removes __doc__, and with it help, pydoc, Sphinx autodoc and every tooltip that reads them — a change to what the package distributes and not only to what the repository holds. The convention already separates a one-line summary from the body, so the seam the lift needs is one a reader and a tool both already recognise.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/lift.py · standing · cites-as-live
