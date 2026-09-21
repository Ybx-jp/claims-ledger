---
id: L0304-a-force-included-path-is-one-git-tracks
kind: claim
stated: 2026-09-20T18:21:16-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 52f3fe4dc679db6aec8b99ddecf93ef6edbf142b6df36504911f673390d502d5
---

## Assertion

Every path the wheel force-includes is one git tracks, so a build from a clean checkout finds each of them.

## Scope

metric: whether a force-included source path is present in a checkout
cohort: every entry of `[tool.hatch.build.targets.wheel.force-include]`
condition: the working tree the list was written in may hold files no checkout does

## Grounds

- code: tests/test_release_record.py § "test_every_force_included_path_is_one_git_tracks" =sha256:dcd1ac80ea82a901aba55f0a6d2d1b92d19552e7e948bf8f6110ab1e192596db
- toml: pyproject.toml § "tool.hatch.build.targets.wheel.force-include" =sha256:91441450c81d66f32692f4b0a2951fa366946af7dfd040dea22f5d3c7356fc46

## Warrant

This is a different failure from the one L0302 is about, and worse in a way the cheaper reading misses. A glob that matches nothing is nothing; a *force*-include that names a missing path is a `FileNotFoundError` raised by the build backend, and it is raised while preparing metadata — so it breaks `pip install -e .` and not merely the wheel. A contributor who cloned the repository could not install it at all.

Measured, and measured the expensive way. `docs/design/` is gitignored; naming it in the force-include table took all nine CI jobs down at the install step, before a single test ran, while every local gate had passed — `ruff`, `ty`, 1399 tests, five checkers and 111 corpus seeds — because the working tree it was written in had the directory and no checkout does. That is the whole argument for asking git rather than the filesystem: the filesystem is what agreed with the mistake.

The check is in the suite rather than left to CI because CI is where it was found and that is one round-trip too late for a list that will be edited again. It reads the table out of `pyproject.toml` and asks `git ls-files` about each source path, counting a directory as tracked when git names anything beneath it. Measured both ways: with `docs/design` back in the table it fails naming that path, and it passes over the table as it now stands.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- pyproject.toml · standing · cites-as-live
