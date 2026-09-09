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

## References

- src/claims_ledger/cli.py · standing · cites-as-live
