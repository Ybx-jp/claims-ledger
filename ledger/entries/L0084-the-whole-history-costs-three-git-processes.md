---
id: L0084-the-whole-history-costs-three-git-processes
kind: claim
stated: 2026-09-08T02:30:49-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 893c84b73b5944d9c6dcfb6b8be225579186311e4021da89caa3f64f2ce5b1f1
---

## Assertion

The whole ledger's history is read with three git processes: one asking whether anything is committed, one walk of the entries directory, and one batch reading every blob the walk named.

## Scope

metric: the number of git processes a history check starts
cohort: a validate run over a ledger of any size
condition: the count is expected to stay flat as entries and revisions grow

## Grounds

- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/schema.py § "git_history" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/schema.py § "git_blobs" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_history asks rev-parse once, calls git_history once over the entries directory rather than once per entry, and hands every wanted blob specification to git_blobs, which reads them in a single cat-file batch. The walk was the part that scaled worst: git log against one path visits every commit however few touched it, so a per-entry loop cost the product of entries and commits. Three is a constant, and it is the constant that keeps a pre-commit hook usable as the ledger grows.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:43-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d
  artifact: 3ebabaa4d367b5f9fa08dd065da0555734c20f01
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_history" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed
- 2026-09-11T03:10:33-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_history" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  artifact: sha256:a0f5460dc7e6805f42f37f08c07a994eaac5dd9d160914c883daecf28f17db9b
  note: propagated from a moved ground
- 2026-09-11T03:10:33-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_history" =sha256:a0f5460dc7e6805f42f37f08c07a994eaac5dd9d160914c883daecf28f17db9b
  note: read against the working tree after the only edit to check_history since the reading at 2a76453, a comment naming the audit file by its path docs/audits/ARCH-AUDIT.md instead of by its bare name: re-counted against the code rather than the diff, since this claim once went false unnoticed — on a ledger with its own repository the section runs rev-parse --verify HEAD once, git_history once over the entries directory and git_blobs once over every wanted blob, and enclosing_repository is asked only when no repository is recorded, which is outside this claim's cohort; three processes, and the assertion holds as written.

- 2026-09-12T15:32:58-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_history" =sha256:2936b88e568080efefbb408f73a1b80f72321109bdf1d06ab1ad5dee9130b4e5
  note: acknowledged: the frozen-region comparison now asks for the staged blob through `index_spec`, so that under a symlinked entries directory it names the path the index holds rather than the address the listing invented. The comparison, and this claim about it, are unchanged (L0232).
- 2026-09-15T17:25:45-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_history" =sha256:2936b88e568080efefbb408f73a1b80f72321109bdf1d06ab1ad5dee9130b4e5
  artifact: sha256:bdbb8276dcecce0f98f63ef837c77d1fc3ce90f757a0b829d7ce222be0926459
  note: propagated from a moved ground

- 2026-09-15T17:26:29-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_history" =sha256:bdbb8276dcecce0f98f63ef837c77d1fc3ce90f757a0b829d7ce222be0926459
  note: re-read after the revision-edge loop was generalised to compare `## Passages` blocks beside the verdict blocks, so that prose held below the APPEND marker appends and only appends the way a verdict does. The frozen-region half of this function is untouched, the walk still costs three git processes for the whole ledger, and what each edge compares is the same comparison applied to a second list.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
