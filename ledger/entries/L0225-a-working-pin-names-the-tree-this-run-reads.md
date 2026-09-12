---
id: L0225-a-working-pin-names-the-tree-this-run-reads
kind: claim
stated: 2026-09-11T21:11:25-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: f391990ba33e94ba07c5ee0cf9341e4d4ad48d3ac1fc20e4c910a0fc07c468e3
---

## Assertion

A ground pinned at working is read from the tree the run reads, which is the index when the run was asked for the index, and from the working tree for a path the index does not hold.

## Scope

metric: which tree a ground with no pin is read from
cohort: every pointer check, with and without the cached flag
condition: what is then asked of the text read is the section rule, claimed elsewhere

## Grounds

- code: src/claims_ledger/resolve.py § "resolve_pointer" =sha256:fc0a18fb75dbff09becb8ca4c1722262b0bde177a4bc084884ee11dcf75a8f5c
- code: src/claims_ledger/schema.py § "staged_blob" =sha256:299ce6121e91353ab74a5988eaa5d5fa8de776597504151c286f7e79efdfa744
- entry: L0033-an-unreadable-evidence-file-is-an-unresolved-pointer · distinguishes
- entry: L0034-a-sections-presence-is-checked-at-the-pin · distinguishes

## Warrant

The pin named the working tree by its own name, and the branch that reads it ran before the flag was consulted, so the installed hook — which runs this checker with the flag — answered about the working tree while the commit carried the index. Measured: a section withdrawn, staged, and restored in the tree gives a bare run 0 and a cached run 1, where before the flag made no difference. Two halves, each with its own killing test, because each fails a different way. A path the index does not hold falls back to the working tree, and that is what the pin is for: it names evidence that is not committed yet, so reading the index and stopping there would fail the case the pin exists to serve. And a path the index does hold is decoded strictly and is not fallen back from. Both of the ordinary readers decode with replacement, so a staged artifact that is not UTF-8 would have come back as text with its section header intact and the pointer resolved, where the working-tree read reports a pointer that does not resolve — one flag and one file answered two ways, and the older of the two entries named above is the claim that would have gone false. Falling back there would be the same error from the other side: the index has the path, so the tree's copy is not what the commit carries. The freshness checker passes such grounds over and still does, which is not a gap: a ground with no pin has nothing to have moved from, and the one thing that can be asked of it is asked here.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-11T22:04:31-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "resolve_pointer" =sha256:19bcb888815f2f87524700a5797837a53eecd7d27c0e9462981a29caee410876
  note: re-read after the commit answering the fix-review gate on this branch (qe ticket e9b7d35601214a1b). An artifact git was asked for and did not answer is reported on the pointer's own line instead of being read from the working tree. The `working` rule, the strict decode and the section rule are unchanged.

- 2026-09-11T22:04:31-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "staged_blob" =sha256:1a1181993646e87847163a92b22b56a92f9fa0fd8f19f555244faed6d964ac85
  note: re-read after the commit answering the fix-review gate on this branch (qe ticket e9b7d35601214a1b). Now (bytes, problem): a batch read git did not answer is no longer folded into 'the index does not hold it'. What the caller does with the bytes is unchanged.

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
