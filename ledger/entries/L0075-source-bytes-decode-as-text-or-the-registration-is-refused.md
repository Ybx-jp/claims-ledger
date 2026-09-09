---
id: L0075-source-bytes-decode-as-text-or-the-registration-is-refused
kind: claim
stated: 2026-09-08T02:26:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 5f0222688ee85c818414d0287d8af3b58b8bb0e056d94418327699ee773eab07
---

## Assertion

Source bytes that do not decode as UTF-8 are refused at registration.

## Scope

metric: the outcome of registering a source whose bytes are not text
cohort: files offered as the bytes of a source
condition: Backing quotations are matched against normalized text

## Grounds

- code: src/claims_ledger/authoring.py § "register_source" @c9f052af09e01b65a2adde51e941ebf24671dcaa

## Warrant

register_source decodes the bytes and raises when it cannot, saying that quotations resolve in text. A source that cannot be read as text is one against which no Backing block could ever verify, so accepting the row would create a registration whose only possible later outcome is a failure — reported far from the command that caused it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
