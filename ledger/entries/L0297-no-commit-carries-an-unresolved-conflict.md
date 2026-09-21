---
id: L0297-no-commit-carries-an-unresolved-conflict
kind: claim
stated: 2026-09-20T17:31:38-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: e725db9949d8005e7c5ec294728fafe69f1452cb94be8b197df8f2e7de924085
---

## Assertion

No file this repository tracks carries an unresolved merge conflict marker, and the suite says so by reading what git tracks rather than by trusting the hook that was bypassed.

## Scope

metric: whether a committed file carries a `<<<<<<<`, `=======` or `>>>>>>>` marker at column zero
cohort: every file `git ls-files` names in this repository
condition: the five checkers read citations and grounds, and none of them reads a document for the marks of a merge that was never finished

## Grounds

- code: tests/test_release_record.py § "test_no_tracked_file_carries_an_unresolved_conflict_marker" =sha256:d0600c4f162fa764cd4101e2850cd37f1b0291dbbcfb734fbeddc79d7ff36ba8
- code: tests/test_release_record.py § "CONFLICT_MARKERS" =sha256:9123a4e71829c1a115980280a3bdfe36fe0e39cd32455a907a278e4f53828e28
- search: corpus=tracked-files; query="^(<{7}|={7}|>{7})([ \t]|$)"; date=2026-09-20

## Warrant

The test lists what git tracks and reads each file for a marker anchored at column zero, so the assertion is checked over the same set of files a commit records rather than over whatever the working tree happens to hold. `CONFLICT_MARKERS` is the second ground because the whole of the claim's precision is in that pattern: unanchored, or without the width and the trailing-space requirement, a Markdown setext underline and a rule of arrows in prose both read as conflicts, and a check that cries wolf over ordinary documents is one a person turns off.

The `search:` ground is the absence itself: the pattern above, run over every path `git ls-files` names on 2026-09-20, found nothing once `CLAUDE.md` was settled. It is stated as a search rather than as a pointer because there is no section that holds an absence — what can be shown is the sweep that looked for it and the set it swept.

What makes this worth a claim rather than a habit is that every other gate missed it. `3151bbc` committed `CLAUDE.md` with all three markers and both sides of the conflict in place; `claims-ledger check` reported 0 failures and 0 flags across five checkers, one of which reads `CLAUDE.md` as a configured document, and the suite was green. The markers fell between two citations and broke neither, which is precisely why nothing downstream of a citation could see them. Measured both ways before this landed: the test fails on that tree naming `CLAUDE.md:39`, and passes once the conflict is settled.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- CLAUDE.md · standing · cites-as-live
