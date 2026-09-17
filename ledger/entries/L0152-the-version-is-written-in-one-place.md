---
id: L0152-the-version-is-written-in-one-place
kind: claim
stated: 2026-09-08T02:49:37-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 4b3c69bd35092ad28506de8f5de2599f2c4dd79c4b485f73e8145d51e94537fa
---

## Assertion

The package version is written in one place, and the packaging metadata reads it from there, so the runtime attribute, the installed metadata and the published release cannot disagree.

## Scope

metric: the number of places the version is written
cohort: the runtime attribute, the packaging metadata and the release
condition: the build backend can read a version out of a source file

## Grounds

- code: src/claims_ledger/__init__.py § "__version__" @94e61e9404b22bd766f6cd97126c73413d0c7e2e
- toml: pyproject.toml § "tool.hatch.version" @94e61e9404b22bd766f6cd97126c73413d0c7e2e

## Warrant

The version is declared once in the package root, and the build backend is told to read it from that file rather than from a literal of its own. A second copy is the ordinary way a release goes out describing itself as one version while reporting another at runtime — a disagreement nothing in a test suite notices, because both halves are individually correct.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:17:13-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/__init__.py § "__version__" @94e61e9404b22bd766f6cd97126c73413d0c7e2e
  artifact: 263bfd4931fa02984416181466f88f64e7c03355
  note: propagated from a moved ground

- 2026-09-08T14:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/__init__.py § "__version__" @ee234ed85969dcc0c8400721f9a16162d6cee9f5
  note: read against commit ee234ed: the citing comment moved into this section from outside it, so the section now carries the sentence it always managed; the value and the single place it is written are unchanged

- 2026-09-11T20:00:14-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/__init__.py § "__version__" =sha256:c5e6333c3c95aec5c7511db44651c1c8fa1a0b9c0d2ee0b93e931c4fda05930f
  note: re-read after the commit that moves the first release's number from 0.1.0 down to 0.0.1, which this package has never published either of. The claim is about the number being written in one place and read from there by the build backend, not about which number it is; the one place is unchanged and still the only one.
- 2026-09-16T21:20:08-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/__init__.py § "__version__" =sha256:c5e6333c3c95aec5c7511db44651c1c8fa1a0b9c0d2ee0b93e931c4fda05930f
  artifact: sha256:8bcda8fc6a9d0d4425aff86bf8a811de5a280a33be5a7763f1ba5ad95412455c
  note: propagated from a moved ground

- 2026-09-16T21:20:33-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/__init__.py § "__version__" =sha256:8bcda8fc6a9d0d4425aff86bf8a811de5a280a33be5a7763f1ba5ad95412455c
  note: re-read after the commit that bumps the version from 0.0.1 to 0.0.2. The claim is about the number being written in one place and read from there by the build backend, not about which number it is; `pyproject.toml` still reads `[tool.hatch.version]` out of this file and no second copy was added, so the only thing that moved is the literal a release is supposed to move.

## References

- src/claims_ledger/__init__.py · standing · cites-as-live
