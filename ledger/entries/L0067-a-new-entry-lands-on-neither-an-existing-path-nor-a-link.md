---
id: L0067-a-new-entry-lands-on-neither-an-existing-path-nor-a-link
kind: claim
stated: 2026-09-08T02:26:24-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 75569448574580fc0d52c9e6b7fd7684533e9de9ab5883121b894812bfb7beaa
---

## Assertion

A new entry is refused when its path already holds a file, and refused again when that path is a link leading outside the project, including a dangling one that does not report as existing.

## Scope

metric: whether an entry is created at a path already occupied or pointed away
cohort: the path a new entry would take in the entries directory
condition: a dangling symlink does not answer to an existence test

## Grounds

- code: src/claims_ledger/authoring.py § "create_entry" @c9f052af09e01b65a2adde51e941ebf24671dcaa
- code: src/claims_ledger/authoring.py § "refuse_to_write_outside_the_root" @c9f052af09e01b65a2adde51e941ebf24671dcaa

## Warrant

create_entry refuses a path that exists, and then asks refuse_to_write_outside_the_root where the path really leads. The second question is the one the first cannot answer: a dangling link fails the existence test, so the refusal steps aside and the write lands wherever the link points. The other two write sites in the package had always asked; this one was clean by accident rather than by a guard, which is not a property to leave resting on an accident.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-14T19:02:18-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/authoring.py § "create_entry" @c9f052af09e01b65a2adde51e941ebf24671dcaa
  artifact: sha256:e43b711ae517deee9e308d1c2e74c575cc6983bf83a0db9ccdf2c88ff194216a
  note: propagated from a moved ground

- 2026-09-14T19:02:42-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/authoring.py § "create_entry" =sha256:9fd1548f22c2ddd0db37c5760efc60c442f2a918faf9fb364f3d118bb35b1bf3
  note: re-read after the commit that allocates above the whole repository. The guards this claim is about are untouched: the write is still funnelled through the same try, `path.exists()` still refuses an entry that is already there, and refuse_to_write_outside_the_root is still asked before the write so a dangling link the exists() check cannot see does not carry the entry out of the root.
- 2026-09-24T21:52:03-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/authoring.py § "create_entry" =sha256:9fd1548f22c2ddd0db37c5760efc60c442f2a918faf9fb364f3d118bb35b1bf3
  artifact: sha256:4ee432b2278cfd856df56c28cadecc4c61abcc2ff92731782ddf4493b74a7ddd
  note: propagated from a moved ground

- 2026-09-24T21:52:23-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/authoring.py § "create_entry" =sha256:4ee432b2278cfd856df56c28cadecc4c61abcc2ff92731782ddf4493b74a7ddd
  note: re-read after #69. The held-number refusal is new and sits before the write; the exists() refusal and the root guard on the write are unchanged, and --force does not reach them, so nothing is written over an existing path or through a link.

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
