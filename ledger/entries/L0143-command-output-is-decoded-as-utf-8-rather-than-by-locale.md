---
id: L0143-command-output-is-decoded-as-utf-8-rather-than-by-locale
kind: claim
stated: 2026-09-08T02:46:26-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 7ed6dcc1911925be553c97b7dec872d187387f9277bda92ad28a0e6716a9dc58
---

## Assertion

Command output is decoded as UTF-8 explicitly rather than with the locale's codec.

## Scope

metric: which codec decodes the output of a version-control call
cohort: every version-control invocation in the package
condition: the schema's own separator character is outside ASCII

## Grounds

- code: src/claims_ledger/schema.py § "git_call" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

git_call names the encoding and the error handler rather than letting the subprocess machinery pick the locale's codec. Under an ASCII locale an entry carrying the separator this schema uses in every verdict line would fail to decode, and the failure would land inside the frozen-region and append-only checks — taking down the two checks that exist to catch an edited history, in exactly the environment where a locale is least likely to be what the author expects.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
