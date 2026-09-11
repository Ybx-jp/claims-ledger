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

## References

- src/claims_ledger/cli.py · standing · cites-as-live
