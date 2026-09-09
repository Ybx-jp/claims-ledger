---
id: L0180-a-skill-is-installed-once-and-reframed-never
kind: claim
stated: 2026-09-08T21:44:39-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: f67f77639441bddd5a069f32ae7c5bad73bb37d905dcab2cff9025f7677cda3a
---

## Assertion

A skill installs as the same body under every agent, and only its frontmatter is rewritten where an agent's own format differs.

## Scope

metric: what changes in a skill between one agent and another
cohort: every skill the package ships, under every agent it installs for
condition: an agent may want frontmatter of its own, as a Cursor rule does

## Grounds

- code: src/claims_ledger/harness.py § "entry_text" @52859264d2caa6d447021f4cda3c8b26e7d72c1f

## Warrant

entry_text returns the source text unchanged for every agent whose entry file is a skill, and rewrites only the two frontmatter fields for one whose format is a rule. A skill rewritten per agent is three skills to keep true instead of one, and the reference links in the body are relative, which is why an agent's rule file goes in a directory of its own rather than beside a reference directory it cannot reach.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T22:03:21-07:00 · superseded · grade: measured · author: main
  evidence: entry: L0191-a-skill-installs-as-the-same-file-under-every-agent · supersedes
  note: the per-agent frontmatter reframing was removed; every agent reads a skill in the same shape, so the installer writes the same file and the section this entry pinned no longer exists. What the successor asserts is what is left of the claim.

## References
