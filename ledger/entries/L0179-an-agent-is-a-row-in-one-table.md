---
id: L0179-an-agent-is-a-row-in-one-table
kind: claim
stated: 2026-09-08T21:44:39-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: b58aa2e3254fac0275240412bf1917b201e3b91e10e5b334b8e4c8118d41783c
---

## Assertion

Every difference between the coding agents the installer writes for is one row of a single table.

## Scope

metric: where an agent's install layout is decided
cohort: every agent the installer supports
condition: agents differ in their skill directory, their entry file name, their hook directory and what wires the hooks

## Grounds

- code: src/claims_ledger/harness.py § "TARGETS" @52859264d2caa6d447021f4cda3c8b26e7d72c1f

## Warrant

TARGETS names, per agent, the skill directory, the name the entry file takes there, the hook directory and the file that has to name the hooks. Nothing in the hooks or the skills is agent-specific, so a second place deciding any of that would be a branch that could disagree with the row beside it. An agent whose hook protocol this package cannot write says so in its row rather than being left out, because the scripts are still worth installing for somebody adapting them.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T22:03:38-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/harness.py § "TARGETS" @52859264d2caa6d447021f4cda3c8b26e7d72c1f
  artifact: 4d3633e3f1e5dcb5b1a3cc27880ee7e3d699a61e
  note: propagated from a moved ground

- 2026-09-08T22:03:53-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/harness.py § "TARGETS" @fcacc40a38daaecba8fc1084b6dfe2dd34d8631e
  note: re-read after the rows lost the fields that made the agents differ. A row is now the agent's name and its directory, and the layout under it is the same for all of them, which is the assertion holding more plainly rather than less.
- 2026-09-11T03:10:01-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/harness.py § "TARGETS" @fcacc40a38daaecba8fc1084b6dfe2dd34d8631e
  artifact: sha256:93648bfcb8e144434217a8fd0f08ca1bc371415d307b2e3e5f9f14e6141fc625
  note: propagated from a moved ground
- 2026-09-11T03:10:01-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/harness.py § "TARGETS" =sha256:93648bfcb8e144434217a8fd0f08ca1bc371415d307b2e3e5f9f14e6141fc625
  note: read against the working tree after each row gained, since the reading at fcacc40, the file that arms the hooks, which schema it takes and, for codex, the home it is read from: every difference between the agents is still one row of this one table, and the scripts and skills still do not vary; the assertion holds as written.

## References

- src/claims_ledger/harness.py · standing · cites-as-live
