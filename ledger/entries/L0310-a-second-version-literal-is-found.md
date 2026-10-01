---
id: L0310-a-second-version-literal-is-found
kind: claim
stated: 2026-10-01T00:46:54-07:00
author: main
grade: measured
supersedes: L0152-the-version-is-written-in-one-place
verbatim_sha: 4b3c69bd35092ad28506de8f5de2599f2c4dd79c4b485f73e8145d51e94537fa
---

## Assertion

The package version is written in one place, and the packaging metadata reads it from there, so the runtime attribute, the installed metadata and the published release cannot disagree; a second copy written under the package's source directory, apart from the corpus's seeds and fixtures — a string or bytes constant in a module, or a line in any other file, that is a version, names one beside the package's name, `%(prog)s` or the word version, or holds this one — is found before it ships.

## Scope

metric: the number of places the version is written
cohort: the runtime attribute, the packaging metadata and the release
condition: the build backend can read a version out of a source file

## Grounds

- toml: pyproject.toml § "tool.hatch.version" =sha256:873edf9aed529e5ff94b1164c7733ed452aea5b1eacc76c2dc9509dba6205c48
- code: tests/test_release_record.py § "test_the_version_is_written_once_in_what_ships" =sha256:c286dfd07d43dfc547b132fe1dca8b30f22831081dd40280a80628fa3a9c4f42

## Warrant

The claim is L0152's, and what changes is what witnesses it. L0152 rested on `__init__.py § "__version__"`, the one place the version is written, and a ground naming the single site cannot see a second: `version="claims-ledger 0.0.1"` written into `cli.py` in place of the f-string left all five checkers at 0/0 and the suite green (#36). The same ground carried the version's value, so every release drifted it and cost a re-read that said only that the literal had moved. The test asserts `pyproject.toml` declares the version dynamic and reads it from `__init__.py`, which `[tool.hatch.version]` is the other half of, and then reads every file under the package directory. In a module it refuses a string or bytes constant that is a version of any value, names one beside the package, `%(prog)s` or the word version, or holds this one's as a whole number; docstrings and the `__version__` assignment itself are exempt. In any other file it refuses a line that is a version, names one the same way or holds this one's. A `>=`, `<` or `~=` bound states a range and is not a copy, and a copy of any value is refused because a stale copy of the version just released matches nothing after the next bump. The corpus's seeds and fixtures are skipped as other projects' ledgers and third-party text. The test reads the source tree and not the imported package, because an installed copy also holds the documents the wheel force-includes from `docs/`, whose audits name versions as history; release.yml runs the suite against the installed sdist, and a walk from `claims_ledger.__file__` failed there on `docs/audits/0.1.0.md` while every PR job stayed green. What the rule does not see is a limit and not a gap: a tuple such as `__version_info__ = (0, 0, 4)`, a comment, a docstring, the name spelled with a space, such as `Claims Ledger 0.0.3` (case is not the limit: `CLAIMS-LEDGER 0.0.3` is refused), a bare `v0.0.3` inside a sentence, and a file that is not UTF-8 text. Each red and green below was found or confirmed by the `qe` fix-review rounds (tickets `1333d78c3857456e`, `9015d3d4531c480b`, `0c58089cca344063`, `a98256d5d4a04013`), the green on `10.0.0.5` measured by the author after the whole-number fix and confirmed in the third round: red against `claims-ledger 0.0.1`, `claims-ledger 0.0.4`, `0.0.9`, `%(prog)s 0.0.3`, `claims-ledger version 0.0.3` and a bytes constant in `cli.py`, a user-agent string holding the current version in `harness.py`, a stale `%(prog)s 0.0.4` after a bump to 0.0.5, and the version written into a shipped shell script and a shipped skill; green on the tree, after bumps to 0.0.5, 0.1.0 and 1.0.0 with nothing else changed, on a `>=0.0.2` bound, and on `10.0.0.5` after a bump to 0.0.5.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- pyproject.toml · standing · cites-as-live
- src/claims_ledger/__init__.py · standing · cites-as-live
