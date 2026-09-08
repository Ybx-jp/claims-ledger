---
id: L0132-a-report-survives-a-locale-that-cannot-encode-it
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 68179db50def36ca099d076adc6ffceb61773344f91c07dfdcf73a7a8a31ccc5
---

## Assertion

A report survives a locale that cannot encode it: characters the stream cannot represent are printed as escapes rather than taking the message down.

## Scope

metric: what happens when a report holds a character the output encoding lacks
cohort: every message the command prints
condition: the schema's own separator is outside ASCII

## Grounds

- code: src/claims_ledger/cli.py § "soften_output_encoding" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

soften_output_encoding reconfigures both streams to replace unencodable characters with escapes, and does so before any argument is parsed. Under an ASCII locale the separator the schema uses raised on the path that was about to explain why a check had failed, replacing the diagnostic with an apology about a bug. The character stays visible as an escape, which is worse to read and infinitely better than losing the report.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
