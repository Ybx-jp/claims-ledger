---
id: L0259-publication-runs-every-gate-ci-runs
kind: claim
stated: 2026-09-15T01:01:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 97c000101f1097e03f91c34f9ae1c19b5528963a8fc5b906f8691def68b1058e
---

## Assertion

The release workflow runs every gate the CI workflow runs before it builds anything, and the two are held in agreement by containment rather than by a list kept in step by hand.

## Scope

metric: whether a gate CI runs can be absent from the release build
cohort: the run commands of ci.yml's test job and release.yml's build job
condition: as the two workflow files stand in the working tree

## Grounds

- code: tests/test_release_record.py § "ci_gate_commands" =sha256:5b19464ef7bbdcbe9f6a2490c802c73bfb465a6ae184aa0a147b085767bd97a6
- code: tests/test_release_record.py § "test_a_tag_runs_the_whole_suite_before_anything_is_built" =sha256:9b60a9485104d90d6d83e35b6f8a7a1fb03485e79b03c1a97b3a8487307bbaf0

## Warrant

A tag matches neither of ci.yml's triggers, so a gate that runs in CI and not in the
release build is one no publication ever applies. The first ground derives the list from
ci.yml's own test job rather than restating it, including commands written as block
scalars; the second asserts that every command on that list appears among release.yml's
build commands, with comment lines dropped first. The enumerated form of this test held
four commands literally while `claims-ledger check` ran in CI and nowhere in the release
workflow, which is the defect a containment cannot reproduce: it cannot name a subset,
because it never writes one down.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- RELEASING.md · standing · cites-as-live
