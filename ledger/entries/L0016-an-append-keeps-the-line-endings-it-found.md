---
id: L0016-an-append-keeps-the-line-endings-it-found
kind: claim
stated: 2026-09-07T22:47:42-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 24ad4a511584a983f39ea0fb858eac37b51d37632c316c3010e72e88df566ab3
---

## Assertion

An entry stored with CRLF line endings keeps them through an append: the file is re-read from disk rather than written back from the text the parser normalized, and the appended block takes the newline the file already uses.

## Scope

metric: the line endings of an entry file after a verdict is appended to it
cohort: entry files stored with CRLF endings
condition: an append by the propagation machinery, over a file the parser has already read

## Grounds

- code: src/claims_ledger/propagate.py § "append_verdict" @e80ad36e50c2c2a2afab6603592ff5fb1818f89e
- code: src/claims_ledger/schema.py § "read_text_exact" @e80ad36e50c2c2a2afab6603592ff5fb1818f89e

## Warrant

read_text_exact opens the file with newline="" so no ending is translated on the way in, and append_verdict reads the file through it rather than reusing the parsed text. It then takes the file's own newline from what it read and rewrites the block's newlines to match before inserting it, so the only bytes that differ from the file on disk are the ones the block adds.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
