---
id: L0302-a-document-a-shipped-string-names-is-in-the-wheel
kind: claim
stated: 2026-09-20T18:08:11-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 9c039853d3c55c574d3bf6b5b56cec1d6a7c11d9b521ad9dcdfc8d5296bac32f
---

## Assertion

Every document a shipped module tells a reader to go and read is carried by the wheel, and the message names the copy that reader actually has.

## Scope

metric: whether a `docs/` path named by a module in the package is present in a built wheel
cohort: every `docs/*.md` path `src/claims_ledger/*.py` names that is a real file
condition: the reader installed the package and has no checkout to read it from

## Grounds

- code: src/claims_ledger/schema.py § "DOCS" =sha256:ff83ff020c0b5d693e234eb51f1d4cbb3007c7e9560397dd52af92b61e28a086
- toml: pyproject.toml § "tool.hatch.build.targets.wheel.force-include" =sha256:84d22de0d0a69a39123c31eb00364c4e8aec7910efda817fdaa37096eae2ca21
- code: tests/test_release_record.py § "test_the_wheel_carries_every_document_a_shipped_string_names" =sha256:a9ab0080e3868893c3da3f00421b5074fe00b2c8d9c2eb073cf837291f1a73da

## Warrant

`packages = ["src/claims_ledger"]` is what puts the corpus and the agent harness in the wheel: they live under the package, so the build takes them. `docs/` cannot live there — the README links to it, CI reads it, and the tests read it from the repository root — and a symlink into `src/` is the one shortcut this project has already measured as silently emptying both distributions. The force-include table is therefore the mechanism, and it is a ground because it is also the thing that was missing: measured against `claims-ledger 0.0.3` installed from PyPI into a clean venv, the installed package had no `docs` directory anywhere, while `claims-ledger new` — the first command a project runs after `init` — told the reader to see `docs/OPERATING.md`, and a `resolve` failure named it again.

`DOCS` and `doc_path` are where the message gets its path, and `None` is the load-bearing part of that answer. The two readers want different things: in a checkout `docs/OPERATING.md` is exactly right and is what the reader already has, and in an installed copy the relative path means nothing while the absolute one can be opened. A resolver that returned a path regardless would name a file that is not there in one of the two cases, which is the failure this is about rather than a fix for it.

The test builds the wheel rather than reading the configuration, because the configuration is what was wrong and a second reading of it would agree with the first. It also measures the trap found while writing it: an `exclude` beside the force-include looks like it keeps the 11 MB of rendered videos out and does not — force-included files are not subject to it, and `"docs" = "claims_ledger/docs"` with both heavy subtrees named in `exclude` built an 11 MB wheel with both of them in it. Naming the subtrees one at a time is what keeps the wheel at 721 KiB, and the test's last assertion is what says a widened list did not quietly undo that.

Measured end to end rather than at the build: the 724 KiB wheel installed into a clean venv, `claims-ledger init` in an empty directory, and `claims-ledger new` there prints an absolute path under `site-packages/claims_ledger/docs/OPERATING.md` which is a file of 22,942 bytes. That is the whole of what the claim says, asked of the artifact rather than of the source tree.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-20T18:22:12-07:00 · contested · grade: measured · author: propagation
  evidence: toml: pyproject.toml § "tool.hatch.build.targets.wheel.force-include" =sha256:84d22de0d0a69a39123c31eb00364c4e8aec7910efda817fdaa37096eae2ca21
  artifact: sha256:91441450c81d66f32692f4b0a2951fa366946af7dfd040dea22f5d3c7356fc46
  note: propagated from a moved ground

- 2026-09-20T18:22:13-07:00 · corroborated · grade: measured · author: main
  evidence: toml: pyproject.toml § "tool.hatch.build.targets.wheel.force-include" =sha256:91441450c81d66f32692f4b0a2951fa366946af7dfd040dea22f5d3c7356fc46
  note: `docs/design` came off the list and a comment went on it. The removal is not a narrowing of this claim: `docs/design/` is gitignored, so no shipped string could name a file in it and this entry's own test — every real `docs/` path a module names — passes over the list without it. The path had to go for a different reason, which L0304 now states: force-including a path the checkout does not have is a `FileNotFoundError` from the build backend at `pip install -e .` time. The three documents a shipped string names are on the list as before.

## References

- src/claims_ledger/schema.py · standing · cites-as-live
- CLAUDE.md · standing · cites-as-live
