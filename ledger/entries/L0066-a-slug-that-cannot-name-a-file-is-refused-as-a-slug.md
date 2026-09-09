---
id: L0066-a-slug-that-cannot-name-a-file-is-refused-as-a-slug
kind: claim
stated: 2026-09-08T02:26:24-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: c0f11420ecf8815df46f793419e78d96c28e25fb7703f9f560a86686e8562f00
---

## Assertion

A slug that is not lowercase-and-hyphens, and one whose filename would overrun what a filename holds, are each refused with a message naming the problem rather than reaching the author as an operating-system error.

## Scope

metric: the error a slug the command cannot use produces
cohort: slugs given to the entry-creating command
condition: the filename is the allocated id and the slug together

## Grounds

- code: src/claims_ledger/authoring.py § "create_entry" @c9f052af09e01b65a2adde51e941ebf24671dcaa
- code: src/claims_ledger/authoring.py § "SLUG_RE" @c9f052af09e01b65a2adde51e941ebf24671dcaa
- code: src/claims_ledger/authoring.py § "NAME_MAX" @c9f052af09e01b65a2adde51e941ebf24671dcaa

## Warrant

create_entry matches the slug against SLUG_RE before anything else and measures the encoded filename against NAME_MAX before it touches the filesystem, reporting the name it would have written and the limit that name passed. Both used to arrive as an OSError out of the write, which asks someone who mistyped a slug to read what looks like a bug in the tool. The remaining length failure — a name that fits NAME_MAX and still overruns PATH_MAX under a deep root — is caught by keeping the existence test inside the same error funnel.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
