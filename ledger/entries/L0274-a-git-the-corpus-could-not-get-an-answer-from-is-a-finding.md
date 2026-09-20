---
id: L0274-a-git-the-corpus-could-not-get-an-answer-from-is-a-finding
kind: claim
stated: 2026-09-17T00:34:55-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: b9fe1a2cce9ad9d9514ffd3b45b78c74c57e20d44329dfdf80a5aff3f78eadf4
---

## Assertion

A git command the corpus runner needs an answer from reports a failure or a timeout as a corpus finding naming the seed, and never as an unexpected exception.

## Scope

metric: what the runner reports when a git command it needs a value from does not answer
cohort: the two commands the runner reads a value out of, and the seed being built when one of them fails
condition: a corpus run, including the one `release.yml` makes against a built distribution

## Grounds

- code: src/claims_ledger/corpus/run.py § "git_out" =sha256:887cf3d2813a32a7e5b9b512a01fb2707069f172819a7e35fb99be3c4a9eb395
- code: src/claims_ledger/corpus/run.py § "run_seed" =sha256:e706009e3b790fb43779e4e3a831711bb7d09058b6d3c1f3b8854ea0212bbe2f

## Warrant

`subprocess.run(check=True, timeout=...)` raises `CalledProcessError` or `TimeoutExpired`, and no caller in the runner expects either, so both reach the CLI's catch-all and are printed as `this is a bug. Please report it` — a report about the package over a corpus that was building normally on a loaded machine. `git_out` converts both into a `LedgerError` that says which command did not answer and that nothing was proven, and `run_seed` prefixes the seed's name, because a reader with a hundred seeds is otherwise told everything except where to look.

This entry has no References row, and that is the configuration rather than an omission: `documents` does not reach `src/claims_ledger/corpus/`, because the seeds and the runner's own prose carry citations of ids that live in other ledgers and syntax shown to a reader. So the citation in `git_out` is written for the person editing that span and is read by no checker — the ground holds the claim to the code, and nothing holds the sentence to the ground.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


- 2026-09-17T00:58:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/corpus/run.py § "git_out" =sha256:8de086f0eb11bea88222a1a2fed6be9b14b6305dd503e3602ead080d9e030bbb
  note: re-read after `gc.auto=0` was added to the command line, which is about a different incident — a writer git starts on its own schedule — and changes nothing about what this entry holds: the two exceptions are still converted, still named, and the seed is still put in front of them.

- 2026-09-17T01:12:30-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/corpus/run.py § "git_out" =sha256:f4d0af690196e4d00e553577705f1bf659e758b76c2cde8e5e9a2baffc7097ce
  note: re-read after `maintenance.auto=false` joined `gc.auto=0` on the command line. Both flags are about a different incident and neither touches what this entry holds: the two exceptions are still converted, still named, and the seed is still put in front of them.
- 2026-09-19T14:24:57-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/corpus/run.py § "run_seed" =sha256:e706009e3b790fb43779e4e3a831711bb7d09058b6d3c1f3b8854ea0212bbe2f
  artifact: sha256:065d4488b4b67836bc6e9b9a06915fb3b245ea4cadb538ef74e99785fd4e9b46
  note: propagated from a moved ground

- 2026-09-19T14:25:06-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/corpus/run.py § "run_seed" =sha256:065d4488b4b67836bc6e9b9a06915fb3b245ea4cadb538ef74e99785fd4e9b46
  note: re-read after K35 took the corpus from 106 seeds to 107, which moved a number written into this section's comment about why the seed name is half the report. What the entry claims is that a git command the runner needs an answer from is reported as a finding naming the seed rather than raised as an unexpected exception; the `except LedgerError` arm that does it, and the name it attaches, are byte-for-byte what they were. The reason the count is in the comment at all is the claim itself — a reader with a hundred-odd seeds has to be told which one — so it is a number this section will keep paying for, and correctly.
- 2026-09-20T13:01:48-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/corpus/run.py § "run_seed" =sha256:065d4488b4b67836bc6e9b9a06915fb3b245ea4cadb538ef74e99785fd4e9b46
  artifact: sha256:de397f5ca110c92547690171c1064b22bddc36b3042a081fd63560d841973227
  note: propagated from a moved ground

- 2026-09-20T13:02:11-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/corpus/run.py § "run_seed" =sha256:de397f5ca110c92547690171c1064b22bddc36b3042a081fd63560d841973227
  note: re-read after the commit that adds the four marker-spelling seeds. The only change inside the section is the seed count in the comment explaining why the seed's name is half the report, 107 to 111. What this claim asserts is untouched: a version control failure while a seed is being built is raised as an error naming that seed, rather than counted as a seed that passed.


## References
