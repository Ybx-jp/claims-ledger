---
id: L0224-an-existing-hook-is-left-alone-unless-the-install-is-forced
kind: claim
stated: 2026-09-11T19:56:32-07:00
author: main
grade: measured
verbatim_change: the leave-alone rule gains its exception, the forced install; Scope unchanged, since the metric was always what happens when something occupies the hook path
supersedes: L0129-an-existing-hook-is-left-alone-and-the-text-is-printed
verbatim_sha: 2887563e8c3ac713f89152ad9de6cf747a0efa3646338e5ef87f9af314fcd852
---

## Assertion

A pre-commit hook that is already there is left alone and its replacement text is printed instead, unless the install is forced; the refusal says whether what is there is an older copy of this hook.

## Scope

metric: what happens when something already occupies the hook path
cohort: hook installation over an existing file or link
condition: a team may share one hook through a symlink

## Grounds

- code: src/claims_ledger/cli.py § "cmd_hook" =sha256:83e6591b8dc27100bba8c3eb6c269a0823bfa9ae91e9544d9c5a621469dba086
- code: src/claims_ledger/cli.py § "is_our_hook" =sha256:6c64811f8647e3d55a6991f57526be3fc4dab3bc12b1bd5896119a3d80b4e393

## Warrant

cmd_hook asks whether anything exists at the path without following the link, so a symlink to nothing counts as something someone put there; the ordinary existence test said no to it and the install wrote through it. The question is asked before the containment guard, so a deliberate link to a shared hook is met with the text and an explanation rather than with an accusation about leaving the repository. The predecessor left it there unconditionally, and that made this the one installer in the package a project could not update: a checkout that installed once kept that hook however far the shipped one moved on, while init and the harness installer both take a force. The refusal distinguishes the two cases because they ask different things of the reader, one wanting a flag and the other a decision, and it decides between them on a marker line taken from the template rather than on the whole text, which cannot be compared: the interpreter is interpolated at install time, so no two installs need match byte for byte. Anything that cannot be read as that text is not ours, which is the answer that asks rather than offers.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
