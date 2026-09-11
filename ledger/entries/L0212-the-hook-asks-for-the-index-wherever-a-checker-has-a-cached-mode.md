---
id: L0212-the-hook-asks-for-the-index-wherever-a-checker-has-a-cached-mode
kind: claim
stated: 2026-09-11T13:36:40-07:00
author: main
grade: measured
verbatim_change: condition no longer fixes how many checkers have a cached mode; assertion unchanged; Backing unchanged
supersedes: L0120-the-hook-reads-the-index-wherever-a-checker-can
verbatim_sha: d57095382c7192cacbdf3353aea0ff15a551e0be43c4e8a17a4dc6eb24054e19
---

## Assertion

The installed hook asks each checker for the index wherever that checker has a cached mode of its own, so a drift that is staged and then reverted in the working tree cannot commit unreported.

## Scope

metric: which checkers the hook runs against the index rather than the working tree
cohort: the pre-commit hook this command installs
condition: whichever checkers have a cached mode of their own are asked for it, and how many that is is read off the template rather than fixed here

## Grounds

- code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" =sha256:942ba9cbee29435b9afade468b70c036de4abd07b6e7e016882f1ff9faa7fbf5

## Warrant

The template runs the entry validator, the pointer resolver and the freshness checker with the cached flag, and the remaining two bare. Left bare, the freshness line looked past a staged drift at an already-reverted working tree and found nothing wrong, while the validator saw the stale pointer — so a commit went through carrying a ground nobody had compared; and a bare resolve answered for a by-value anchor against the working tree while the commit carried the index, landing an entry whose anchor no version of the path holds. The rest have no cached mode yet and read the working tree, which the template says in as many words rather than leaving a reader to infer it. The predecessor fixed the count of cached checkers in its condition, so giving a third one the flag cost a supersession for a claim that had not moved; this one names the rule and leaves the counting to the template.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-11T15:06:52-07:00 · superseded · grade: measured · author: main
  evidence: entry: L0216-the-hook-asks-the-index-of-every-checker-that-takes-the-flag · supersedes
  note: the clause inherited from L0120 — that a drift staged and then reverted cannot commit unreported — claims more than the template decides, since two checkers have no cached mode and resolve reads the working tree for a ground pinned at working. The successor claims what the hook asks for and leaves the residual stated beside it

## References
