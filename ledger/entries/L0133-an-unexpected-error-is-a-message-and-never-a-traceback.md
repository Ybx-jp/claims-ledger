---
id: L0133-an-unexpected-error-is-a-message-and-never-a-traceback
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 9565bcfd95787e5172e48c6cb51a111c209492ab88650b506434cef4a944b55a
---

## Assertion

An unexpected error reaches the reader as a message naming its type, saying plainly that it is a bug, and giving both where to report it and how to get the traceback back.

## Scope

metric: what an unhandled exception produces at the terminal
cohort: every subcommand
condition: the person running the command may have written none of it

## Grounds

- code: src/claims_ledger/cli.py § "main" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

main catches everything that is not one of the errors it already turns into a message, prints the type and text, states that it is a bug, gives the issue address, and names the environment variable that re-raises. A traceback at a stranger is an invitation to read a package they did not write in order to find out whether they typed something wrong; the variable keeps the traceback one flag away for whoever is actually debugging it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T21:45:08-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "main" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395
  artifact: 5635a9c60c547010c5878fd5589837af4db0ac77
  note: propagated from a moved ground

- 2026-09-08T21:45:28-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "main" @52859264d2caa6d447021f4cda3c8b26e7d72c1f
  note: re-read after the harness installer was added to the commands dispatched without a ledger, which added a clause to this docstring and nothing else. The unexpected-error path still prints the type, the message, the report address and the traceback variable, and still returns 2. The assertion is unaffected.

## References

- src/claims_ledger/cli.py · standing · cites-as-live
