---
id: L0312-no-shipped-script-tests-its-input-through-a-pipe-into-a-quiet-grep
kind: claim
stated: 2026-10-01T00:54:12-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 97715facfa0637ec77ed426fe6ce53fd089a573a6989ebecda21e98557fb8c7e
---

## Assertion

No shell the package ships tests its input by piping it into a `grep` that exits on a match without reading the rest — `grep`, `egrep` or `fgrep` by name, path or quoted, with no operator between the pipe and it, and with `-q`, `-l`, `-L` or `-m` in any cluster or an abbreviation of `--quiet`, `--silent`, `--max-count` or `--files-with(out)-matches` — and the merge guard's check that hands an ordinary merge to `renumber` holds its refusal however much of the command follows the match.

## Scope

metric: the lines of shipped shell that pipe into `grep -q`, and the merge guard's verdict on a `git merge <branch>` the package refuses
cohort: every `.sh` under the package's resources and the pre-commit hook template; a command whose matching line is followed by more than a pipe buffer
condition: the scripts run under `set -o pipefail`, as every shipped hook does

## Grounds

- code: tests/test_harness.py § "test_no_shipped_script_tests_its_input_through_a_pipe_into_a_quiet_grep" =sha256:55f1473593fb04c31bcdd2ea35509ff594fdc93d9e6fa1aba23bce64f1466f04
- code: tests/test_harness.py § "test_a_merge_the_package_refuses_is_refused_however_much_follows_it" =sha256:81be7c1587aab6155ebe9c8bae5ac8771062ee905bf74df02286e1f553acb7b8

## Warrant

#73 changed four sites from `printf | grep -q` to a here-string. L0309 and L0311 drive three of them with bulk behind the match; the fourth, the merge guard's `git merge <branch>` test that hands the merge to `renumber --on-merge`, had no such test, and the `qe` fix-review round (ticket `1333d78c3857456e`) put it back on the pipe and saw the merge allowed with 200 KB behind it while the suite stayed green. The second ground drives that site with a stand-in interpreter whose `renumber` refuses: green on the here-string, red in 10 runs of 10 against the pipe. The first ground reads every shipped script and the hook template for the shape itself, with the matcher written inside the test so the rule and the pinned span are one text: comments are dropped, then continuations and lines ending in `|` are joined, and a line is refused where a pipe reaches a grep that stops early with nothing but non-operator text between them. It is shown every spelling the rounds found first — 35 that stop early and 5 that read their whole input — so a clean scan cannot come from a matcher that sees nothing. The rounds after the first (tickets `9015d3d4531c480b`, `0c58089cca344063`, `a98256d5d4a04013`) each planted spellings the scan missed, `egrep -q`, an end-of-line pipe, `LC_ALL=C grep -q` and `grep -m1`, then a brace, a subshell, `\grep`, `"grep"`, `env`, `timeout 5`, the hooks' own `bounded`, `--qui`, `grep -l` and a comment ending in `|` or `\` above the line, then `--si`, `--s`, `--m=1`, `--ma=1`, a quoted `"-q"` or `'-qF'`, and `-5q`; each is now a control and each, planted in status-guard.sh, fails the test. Against `main` before the fix it names exactly the four sites, three in the merge guard and one in the pin guard. A lexical scan of shell has a next spelling, which is why the Assertion names the rule it holds: a comment on its own line between the pipe and the grep is not read, and neither is a pipe into `head`, `awk … exit` or `sed q`, which stop early and are not a grep.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- CLAUDE.md · standing · cites-as-live
