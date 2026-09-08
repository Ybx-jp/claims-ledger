---
id: L0060-the-default-layout-is-confined-too
kind: claim
stated: 2026-09-08T02:13:07-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 1f91bd73381ee896ad20136052fef6b0711c97ec2afd63ea73d24cf622e443b2
---

## Assertion

The default layout is put through the same confinement as a configured one, so a project that never wrote a configuration file still cannot keep its ledger outside the root.

## Scope

metric: whether the default ledger, entries, registry and cache paths are confined
cohort: projects with no configuration file
condition: the working tree may carry a symlink where the default layout expects a directory

## Grounds

- code: src/claims_ledger/config.py § "default_config" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

default_config builds each of its four paths through confined rather than joining them directly. A clone carries a `ledger -> /tmp/outside` symlink as readily as it carries a configuration file, and the containment this package claims is a property of the tool: making it depend on a configuration file existing would leave it off exactly where a project has said the least.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/config.py · standing · cites-as-live
