---
id: L0184-a-settings-file-is-written-when-absent-and-printed-when-not
kind: claim
stated: 2026-09-08T21:44:39-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: d4010eec62dc964c25710fcbf1e34d87d8555eceb6018f6ecfc5bec93f6be023
---

## Assertion

The file that has to name the hooks is written when the project has none and is never edited when it has one; the text it needs is printed instead.

## Scope

metric: what an install does to a settings file that already exists
cohort: every agent whose hooks are wired by a file
condition: that file is where people keep their own hooks and permissions

## Grounds

- code: src/claims_ledger/harness.py § "install_wiring" @52859264d2caa6d447021f4cda3c8b26e7d72c1f

## Warrant

A settings file already there is read for the hooks this install would wire and reported as wired or not; it is never rewritten. Merging into it behind its owner would be a change to their harness they did not make. The check is for a script's name rather than the exact path this install would have used, so a project running the copy inside the installed package is recognised as wired rather than told otherwise on every run.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T22:03:38-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/harness.py § "install_wiring" @52859264d2caa6d447021f4cda3c8b26e7d72c1f
  artifact: 4d3633e3f1e5dcb5b1a3cc27880ee7e3d699a61e
  note: propagated from a moved ground

- 2026-09-08T22:03:53-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/harness.py § "install_wiring" @fcacc40a38daaecba8fc1084b6dfe2dd34d8631e
  note: re-read after every agent came to have a settings file, which removed the branch that returned nothing for one that had none. What happens to a file already there — read for the hooks it names, never rewritten — is unchanged.
- 2026-09-11T03:10:01-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/harness.py § "install_wiring" @fcacc40a38daaecba8fc1084b6dfe2dd34d8631e
  artifact: sha256:cb7d0ed28a0cec20b6b8e1cd9622c0a5d56e07a6130f55af495d547a2e57d001
  note: propagated from a moved ground
- 2026-09-11T03:10:01-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/harness.py § "install_wiring" =sha256:cb7d0ed28a0cec20b6b8e1cd9622c0a5d56e07a6130f55af495d547a2e57d001
  note: read against the working tree after install_wiring began, since the reading at fcacc40, taking its text and path from wiring_json and wiring_path and asking containment against the file's own directory for codex: an existing file is still read and reported rather than edited, and the text it needs is still printed; the assertion holds as written.

## References

- src/claims_ledger/harness.py · standing · cites-as-live
