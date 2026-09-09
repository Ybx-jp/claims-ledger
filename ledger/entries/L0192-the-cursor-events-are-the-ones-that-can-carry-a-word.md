---
id: L0192-the-cursor-events-are-the-ones-that-can-carry-a-word
kind: claim
stated: 2026-09-08T22:33:12-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0702524ebcaa82e2f32728a036308c14be541c58a6ab4c57942acf9e8c870b53
---

## Assertion

Each hook is wired to an event that can carry what it has to say on the harness it is installed for.

## Scope

metric: whether the event a hook is wired to can deliver that hook's output to the agent
cohort: every hook the installer wires, on every agent it writes for
condition: the harnesses differ in which events accept context back from a hook

## Grounds

- code: src/claims_ledger/harness.py § "WIRING" @922d6cec6ce535b84b13f651c01225b8242d5ca8

## Warrant

One table names what runs when in both vocabularies, and the edit-time guards take Cursor's postToolUse rather than its afterFileEdit. Measured in cursor-agent 2026.08.11: an afterFileEdit hook's return value is read only for file contents, and the events whose additional_context reaches the agent are exactly sessionStart, beforeSubmitPrompt, preToolUse and postToolUse. A guard wired to the event that best describes what happened, but whose answer nothing reads, is a guard that does not exist — installed, reported, and silent.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/harness.py · standing · cites-as-live
