---
id: L0231-a-listing-that-fell-back-is-named-by-the-guard
kind: claim
stated: 2026-09-12T14:45:41-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 9f58a9b1e3143c1c6cbc1a5e4240b0d9b13236d4024fb08cd008fb1023dc00a1
---

## Assertion

A cached run whose index listing could not be taken falls back to the working tree and the guard names that fallback before the report, so the run says which tree it actually read.

## Scope

metric: whether a cached run whose listing failed says so before its report
cohort: every checking command given the cached flag, for the entry listing and the document listing alike
condition: the sentence names the listing that failed and the reason git gave

## Grounds

- code: src/claims_ledger/cli.py § "skipped_checks" =sha256:a4106561e8404138ed6bbb1862d8c2cee8a1ba085d236fc0d62ca1afdcb2c069
- code: src/claims_ledger/schema.py § "open_ledger" =sha256:69a9b396207e4ba4ed6f2a4c9f494d0ca338570b2270afb81197d311523e2f2b

## Warrant

`index_problem` asks `ls-files -- .git`, whose output is empty whatever the repository holds; that is deliberate, so a repository with a hundred thousand files still prints nothing. It therefore cannot fail the way a listing of every tracked path can — a timeout, a pack it cannot open — and both listings claimed in their own comments that it reported their fallback for them. Measured with a git failing only the listing call, on a document staged and then removed from the working tree: `references --cached` went from exit 1 naming the staged document to `0 documents` and `0 failure(s)` at exit 0 with nothing said (qe ticket 45909368c43c4379, F2). That is L0227's finding one listing over, and the same answer applies — a question git did not answer is not a no. The fallback itself is kept rather than made a stop, because a run whose index cannot be read should still check something; what was missing was the half that says so.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
- src/claims_ledger/schema.py · standing · cites-as-live
