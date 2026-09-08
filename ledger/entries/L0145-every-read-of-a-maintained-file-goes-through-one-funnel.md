---
id: L0145-every-read-of-a-maintained-file-goes-through-one-funnel
kind: claim
stated: 2026-09-08T02:46:26-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 4093031c068966035db3204aae3185a1c8f0d964a2a27cf31f7df2b706396412
---

## Assertion

Every read of a file the project maintains goes through one function, so an unreadable entry or registry is reported rather than raised at the reader.

## Scope

metric: the number of paths by which a maintained file is read
cohort: entries, the source registry, and the files they name
condition: a path may be a FIFO, a directory, a dangling link, or undecodable

## Grounds

- code: src/claims_ledger/schema.py § "read_text_or_raise" @4af0acd253eeef1571cd7615ea3a041eda9e945e
- code: src/claims_ledger/schema.py § "file_problem" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

read_text_or_raise asks file_problem what the path is before opening it, and turns a decoding failure or an operating-system error into an error naming the file and what is wrong with it. The type check comes first because a FIFO named like an entry blocks a read forever with nobody on the other end, which inside a commit hook is a wedged commit printing nothing. One funnel means the diagnosis is written once and every reader gets it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
