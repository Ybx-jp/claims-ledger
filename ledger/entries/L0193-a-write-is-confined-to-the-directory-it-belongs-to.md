---
id: L0193-a-write-is-confined-to-the-directory-it-belongs-to
kind: claim
stated: 2026-09-08T22:33:12-07:00
author: main
grade: measured
supersedes: L0183-the-harness-is-not-installed-through-an-escaping-link
verbatim_change: the confinement question is asked against the directory each name belongs to, rather than against the project root alone, because one file the install writes is not in the project
verbatim_sha: 01e0285676f89114c88a2fa52cfc18884bda0d9dbb01d6e8e51b3a891972bff4
---

## Assertion

Every name an install is about to write is asked where it really leads, against the directory that name belongs to, and nothing is written through a link that leaves it.

## Scope

metric: whether a write's destination is confined to the directory it belongs to
cohort: every file an install writes, under every agent
condition: any component of a destination may be a symbolic link the project does not control, and one destination is not under the project at all

## Grounds

- code: src/claims_ledger/harness.py § "install" @922d6cec6ce535b84b13f651c01225b8242d5ca8
- code: src/claims_ledger/harness.py § "install_wiring" @922d6cec6ce535b84b13f651c01225b8242d5ca8

## Warrant

The skills and the scripts are confined to the project root; the wiring file is confined to the directory it lives in, which for codex is its configuration home rather than anything under the project. Both ask the same containment question through the same test rather than through a second one that could drift from it — the question `hook --install` asks of the hooks directory version control names, which is likewise not in the project. A link planted at any of these paths would otherwise take a file elsewhere while the report named the path it was never written to.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/harness.py · standing · cites-as-live
