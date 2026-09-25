---
id: L0168-the-scaffold-names-the-neighbour-lookup
kind: claim
stated: 2026-09-08T12:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 585e2dbabbfea9d49f32439e1b0b612d53b77a4706035aac37a983a9e50e741c
---

## Assertion

Scaffolding an entry prints the neighbours command for that entry by name, so the lookup is offered at the moment its grounds are about to be chosen.

## Scope

metric: whether the neighbours lookup is named to the author, and where
cohort: the new command
condition: an entry was scaffolded

## Grounds

- code: src/claims_ledger/cli.py § "cmd_new" @aadceb0aba82a85fe71b15394896c43977751709

## Warrant

cmd_new prints the command with the new entry's id in it, after the two lines that say what to fill in and what a ground too wide costs. Nothing downstream asks the question: the lookup is not a checker, the hook does not run it, and check does not either, which is deliberate and is what keeps it from being a gate. That leaves exactly one moment at which it can be offered, and this is it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-11T02:58:18-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "cmd_new" @aadceb0aba82a85fe71b15394896c43977751709
  artifact: sha256:4505141153fe847a2c68432ae71e1cd075e326561bd9a7f35bd71be3d022e563
  note: propagated from a moved ground
- 2026-09-11T02:58:18-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "cmd_new" =sha256:4505141153fe847a2c68432ae71e1cd075e326561bd9a7f35bd71be3d022e563
  note: read against the working tree after the scaffold's next-step sentence began saying a ground's anchor may be left as `=?` and that sha --write fills it: the neighbours command is still printed for the entry by name, in the same place; the assertion holds as written.
- 2026-09-20T18:08:45-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "cmd_new" =sha256:4505141153fe847a2c68432ae71e1cd075e326561bd9a7f35bd71be3d022e563
  artifact: sha256:bc6681eec4301fd3e1269fa799c2450a2da90722cafe73ba5ece500ca57626e7
  note: propagated from a moved ground

- 2026-09-20T18:08:58-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "cmd_new" =sha256:bc6681eec4301fd3e1269fa799c2450a2da90722cafe73ba5ece500ca57626e7
  note: The scaffold still names the neighbour lookup, on the same line and in the same words — `claims-ledger neighbours <id>` is printed after the grounds advice as before. The lines above it changed: the ground-width warning binds the document's path first so it can name the installed copy.
- 2026-09-24T21:52:04-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "cmd_new" =sha256:bc6681eec4301fd3e1269fa799c2450a2da90722cafe73ba5ece500ca57626e7
  artifact: sha256:6950899fc527b69fffa7d8343ea0aab0fc297acf5bbee801b3eee5cb39f15d9d
  note: propagated from a moved ground

- 2026-09-24T21:52:23-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "cmd_new" =sha256:6950899fc527b69fffa7d8343ea0aab0fc297acf5bbee801b3eee5cb39f15d9d
  note: re-read after #69. cmd_new passes --force and a notes list through and prints the notes to stderr; the neighbours line printed after the write is unchanged.

## References

- src/claims_ledger/cli.py · standing · cites-as-live
