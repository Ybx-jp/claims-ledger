---
id: L0029-an-append-keeps-the-line-endings-it-found
kind: claim
stated: 2026-09-07T23:20:23-07:00
author: main
grade: measured
supersedes: L0016-an-append-keeps-the-line-endings-it-found
verbatim_sha: 24ad4a511584a983f39ea0fb858eac37b51d37632c316c3010e72e88df566ab3
---

## Assertion

An entry stored with CRLF line endings keeps them through an append: the file is re-read from disk rather than written back from the text the parser normalized, and the appended block takes the newline the file already uses.

## Scope

metric: the line endings of an entry file after a verdict is appended to it
cohort: entry files stored with CRLF endings
condition: an append by the propagation machinery, over a file the parser has already read

## Grounds

- code: src/claims_ledger/propagate.py § "append_verdict" @0af113005f955a4e120d71338993a94cc6efeb7b
- code: src/claims_ledger/schema.py § "read_text_exact" @0af113005f955a4e120d71338993a94cc6efeb7b

## Warrant

read_text_exact opens the file with newline="" so no ending is translated on the way in, and append_verdict reads the file through it rather than reusing the parsed text. It then takes the file's own newline from what it read and rewrites the block's newlines to match before inserting it, so the only bytes that differ from the file on disk are the ones the block adds.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
