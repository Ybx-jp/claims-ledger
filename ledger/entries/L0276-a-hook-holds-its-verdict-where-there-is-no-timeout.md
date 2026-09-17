---
id: L0276-a-hook-holds-its-verdict-where-there-is-no-timeout
kind: claim
stated: 2026-09-17T02:20:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 4453dcf232d051401bd28badbfe7d6d724046cdf31876a523212a22c9547247a
---

## Assertion

A shipped hook returns the same verdict on both platforms this package tests on, whatever bounds the call it makes to the package.

## Scope

metric: the verdict a hook returns, and whether it returns one at all
cohort: the four shipped hooks that bound a call to the package
condition: a PATH where GNU `timeout` is missing, which is stock macOS

## Grounds

- code: tests/test_harness.py § "test_the_guards_hold_their_verdicts_where_there_is_no_timeout" =sha256:165a45d79b13e05edbb3a14fd6f23a9b5920d5710a51d7bd296c91359f10dd59

## Warrant

`timeout` is GNU coreutils and macOS ships none, so a hook that wrote it bare answered differently on the two platforms this package tests on: `merge-guard.sh` denied an ordinary merge with `line 140: timeout: command not found`, and the three hooks that append `|| true` swallowed the same failure and reported nothing — a drift check silent on a whole platform, which is the worse half. The hooks now bind `bounded` to `timeout 20` where the utility is there and to the command itself where it is not, so the bound is what varies and the verdict is not. The test runs the guard against a PATH built as a farm of symlinks with `timeout` left out, and asserts `bash`, `git` and `jq` survived the farm, because a guard that answered from a broken environment would prove nothing.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- CLAUDE.md · standing · cites-as-live
