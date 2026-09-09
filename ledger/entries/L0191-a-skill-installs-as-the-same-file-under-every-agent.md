---
id: L0191-a-skill-installs-as-the-same-file-under-every-agent
kind: claim
stated: 2026-09-08T22:03:21-07:00
author: main
grade: measured
supersedes: L0180-a-skill-is-installed-once-and-reframed-never
verbatim_change: the assertion narrows to what the installer now does — the file is the same under every agent rather than the body being the same and the frontmatter reframed
verbatim_sha: ee03f4e6f25ef4d1e9256159fd822e0867223f3259730681941e879400a81605
---

## Assertion

A skill installs as the same file under every agent, and only the directory it lands in differs.

## Scope

metric: what changes in an installed skill between one agent and another
cohort: every skill the package ships, under every agent it installs for
condition: the agents keep skills in the same shape, each under a directory of its own

## Grounds

- code: src/claims_ledger/harness.py § "plan" @fcacc40a38daaecba8fc1084b6dfe2dd34d8631e

## Warrant

The plan reads each shipped SKILL.md and writes those bytes to the skill directory of the agent being installed for, with the reference directory beside it. Nothing rewrites the file per agent: a skill reframed for each one is a skill per agent to keep true, and the reference links in the body are relative, so the directory it sits in is part of what makes it readable.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/harness.py · standing · cites-as-live
