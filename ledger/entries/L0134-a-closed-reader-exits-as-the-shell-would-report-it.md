---
id: L0134-a-closed-reader-exits-as-the-shell-would-report-it
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 220fdadd042e6bbcee33284ed25aad929c7f66cdf290fa8329309df087695cad
---

## Assertion

A closed reader ends the run with the status a shell reports for the same signal, and without printing over what the reader already showed.

## Scope

metric: the exit status and output when standard output is closed early
cohort: runs whose output is piped into a program that stops reading
condition: the interpreter flushes again during shutdown

## Grounds

- code: src/claims_ledger/cli.py § "main" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

main points standard output at the null device before returning, so the interpreter's own shutdown flush cannot raise a second time and scribble over the reader's last screen, and returns the conventional status for a broken pipe. Piping the status listing into a pager is an ordinary thing to type, and it is not an error in this tool.

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
  note: re-read after the same edit. The BrokenPipeError path still points stdout at the null device before returning 141, and the docstring clause that moved the section names a different command's dispatch. The assertion is unaffected.

## References

- src/claims_ledger/cli.py · standing · cites-as-live
