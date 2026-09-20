---
id: L0083-the-frozen-region-is-compared-against-the-creating-commit
kind: claim
stated: 2026-09-08T02:30:45-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 183b56f4ed3cd68c891c93dabb12584d984495b9e1b7f89001f191a313c246cf
---

## Assertion

An entry's frozen region is compared against the blob at the commit that created the file, and not against its most recent revision.

## Scope

metric: which revision the frozen region is held to
cohort: committed entries
condition: an entry may have many revisions, all of them appends

## Grounds

- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_history takes the oldest revision the walk found for the path and reads the blob there. Comparing against the previous revision instead would make an edit to the frozen region permanent the moment it survived one commit. Comparing against the creating commit holds the region to what it was when the entry entered history, which is what the immutability the ledger promises actually says.

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
  note: read against the working tree after the only edit to check_history since the reading at 2a76453, a comment naming the audit file by its path docs/audits/ARCH-AUDIT.md instead of by its bare name: the frozen region is still read from the blob at the oldest revision the walk found for the path; the assertion holds as written.

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
- 2026-09-20T15:29:16-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_history" =sha256:bdbb8276dcecce0f98f63ef837c77d1fc3ce90f757a0b829d7ce222be0926459
  artifact: sha256:a8dc0b278ba056161297d7bfb4a6899f044b8da899aa83d7a8b9599271e9d6f6
  note: propagated from a moved ground

- 2026-09-20T15:29:43-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_history" =sha256:a8dc0b278ba056161297d7bfb4a6899f044b8da899aa83d7a8b9599271e9d6f6
  note: re-read after the commit that widens the reach of the history walk. The section now passes `prospective_revs` — HEAD and the other side of an operation in progress — where it passed nothing and got HEAD. With no operation under way the walk is the one it was, and the rules this section carries are untouched: the working tree is still the last edge compared.


## References

- src/claims_ledger/validate.py · standing · cites-as-live
