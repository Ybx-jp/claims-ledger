---
id: L0123-check-parses-the-entries-once-into-two-lists
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 6a566e46f84fcac9603ba940db4f3a1590b5e8fae425656b1dc8e67e743c64ba
---

## Assertion

A combined run parses the entries once into two lists rather than once per checker: what is staged for the two checkers that read the index, and the working tree for the other three.

## Scope

metric: the number of times the entries are parsed in a combined run
cohort: a run of all five checkers
condition: the cached flag makes the two lists differ

## Grounds

- code: src/claims_ledger/cli.py § "cmd_check" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

cmd_check loads the working tree once and, under the cached flag, the index once, then hands each checker the list it should be reading. One list would erase the distinction the cached flag exists to make; five loads would parse every entry five times for no answer that differs. Two is what the difference actually costs.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T19:39:25-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "cmd_check" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395
  artifact: 676dcd35eb188588bb7ee218eeba3438f3c789d6
  note: propagated from a moved ground

- 2026-09-08T19:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "cmd_check" @225f5867b2591ffc5b3020dfe20ca407d81ee06f
  note: read against commit 225f586, which moved `ARCH-AUDIT.md` into `docs/audits/` and rewrote the mentions of it in this section; the section was parsed at the pin and at that commit and compared with comments and docstrings set aside, and the two are identical, so nothing the claim rests on changed
- 2026-09-11T03:57:56-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "cmd_check" @225f5867b2591ffc5b3020dfe20ca407d81ee06f
  artifact: sha256:18d89c978b00ae1f8eccf9cb6f8bad2851495302fc68b9a114c5a10720d46215
  note: propagated from a moved ground
- 2026-09-11T03:58:17-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "cmd_check" =sha256:18d89c978b00ae1f8eccf9cb6f8bad2851495302fc68b9a114c5a10720d46215
  note: read against the working tree after cmd_check began handing --cached to resolve as well, for the index's artifacts under a by-value anchor: the entries are still parsed once into the two lists as stated, and resolve still takes the working list; that a third checker now reads the index's artifacts is a fact about artifacts and not about the lists this claim counts; the assertion holds as written.
- 2026-09-11T13:35:32-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "cmd_check" =sha256:18d89c978b00ae1f8eccf9cb6f8bad2851495302fc68b9a114c5a10720d46215
  artifact: sha256:72f612821c626b793c67ffe9327a7c747a3181fd1089e7d488b2c0e7dabc95a0
  note: propagated from a moved ground

- 2026-09-11T13:37:26-07:00 · superseded · grade: measured · author: main
  evidence: entry: L0213-a-combined-run-parses-the-entries-once-into-two-lists · supersedes
  note: two lists parsed once is unchanged; the assertion said which checkers took which by counting them, and resolve gaining a cached mode inverted the counts, so the successor names the lists by what decides membership

## References

