---
id: L0178-the-shipped-harness-is-found-beside-the-package
kind: claim
stated: 2026-09-08T21:44:39-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: d3e9cb0eca31baf5c62450400124b4ef2dd4fd92817b0a92ed0e52799195884f
---

## Assertion

The agent hooks and skills the installer writes are read from a directory beside the package's own modules, so any installed copy carries them.

## Scope

metric: where the installable harness is read from
cohort: every installed copy of the package
condition: installed from a wheel, from an sdist, or run out of a checkout

## Grounds

- code: src/claims_ledger/harness.py § "RESOURCES" @52859264d2caa6d447021f4cda3c8b26e7d72c1f

## Warrant

RESOURCES is a path resolved against the module's own file, which is the idiom the corpus runner already uses for its seeds. Both are directory trees inside the package, read from a distribution unpacked onto a filesystem, and a Traversable would buy nothing a zip-imported copy could use: a hook script has to become a real file at a real path before any agent can execute it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/harness.py · standing · cites-as-live
