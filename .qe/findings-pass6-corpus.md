# Sixth pass — corpus and release gates

Verifying the fifth pass's eight findings (HIGH-45 … LOW-52) at `776500b`, then re-running
the mutation sweep independently. Worktree `/tmp/qe6-corpus`.

## The eight, verified

| Finding | Verdict | Evidence |
|---|---|---|
| HIGH-45 | FIXED | `--corpus <empty seeds/>` → `no seeds under …; nothing was proven`, exit 1. `corpus NOSUCHSEED` → `no seed under … matches NOSUCHSEED`, exit 1 |
| HIGH-46 | FIXED | `matches()` compares the place exactly, binds one row to one report, and takes an optional message substring. Both original mutants re-run by hand: corpus goes 74/75 each time |
| HIGH-47 | PARTIALLY FIXED | D50/D51/D52 added and each verified load-bearing by its own mutant. The *claim* the fix substituted for coverage is false — HIGH-59 |
| MEDIUM-48 | FIXED (for the sites it named) | `grep -c 70 README.md` → 0; the three counts read 75. A fourth site says 62 — MEDIUM-60 |
| MEDIUM-49 | FIXED | All 75 seed ids appear in `corpus/README.md`'s Coverage table, checked programmatically |
| MEDIUM-50 | FIXED | `release.yml` builds two clean venvs and runs the corpus against wheel and sdist separately |
| MEDIUM-51 | FIXED | All five `uses:` are 40-character SHAs; each checked against GitHub's tags API and each resolves to the tag its comment names (the publish action's is a signed annotated tag dereferencing to the pinned commit) |
| LOW-52 | FIXED | One version heading; re-inserting `## [Unreleased]` into a copy makes the regression fail, confirmed by hand |

## The sweep

Independent of the fifth pass's, and it disagrees with it on the denominator. An **AST**
enumerator (`probe6/enumerate_sites.py`) rather than the text-grep the fifth pass used: the
grep only reached `fail(...)`/`flag(...)` lambda calls and missed direct
`reports.append(Report(...))` sites in `validate.check_history` and throughout `resolve.py`.

**116 report sites at this tip**, not 99 — `validate.py` 72, `resolve.py` 16,
`references.py` 15, `freshness.py` 8, `propagate.py` 5.

Each was neutered in a fresh copy of `src/`, run in a subprocess with `PYTHONPATH` and an
assertion that the mutant really was the module imported, first through the corpus and then
— for corpus survivors — through the full suite (`probe6/mutate_one.py`; raw data in
`sweep_phase1.jsonl` / `sweep_phase2.jsonl`).

| | |
|---|---|
| caught by the corpus | 53 / 116 |
| survived the corpus, caught by the unit suite | 13 |
| **caught by nothing** | **50** |

The seven survivors that are *not* well-formedness guards are listed in `QE-AUDIT.md` under
HIGH-59. Three were hand-confirmed outside the harness — the frontmatter `kind` enum, the
Grounds dead-pointer rule, and `propagate`'s `--write` report — each leaving `75/75 seeds
pass` and the suite green.

## New defects

HIGH-59, MEDIUM-64 and LOW-69 in `QE-AUDIT.md`. Probes: `attack_high45_floor.sh`,
`attack_high46_matches.py`, and the sweep harness above.

## Attacked and held

- **D50's non-UTF-8 seed** is byte-identical across sdist and wheel (sha256 checked), and
  breaks neither `ruff`, `ruff format --check` nor `ty` (all exit 0). Its `is_text()` skip
  in the metamorphic tests excludes only the one file it must — the transforms still run
  over every other seed markdown, verified.
- **HIGH-46's new message rule** is not exploitable today. Emptying D17's own message and
  re-running the terminal-verdict mutant still fails correctly, because the
  one-row-one-report bijection catches the ambiguous-place case regardless of message
  content. LOW-69 is a footgun, not a live hole.
- **`CHANGELOG.md`'s `releases/tag/v0.1.0`** link is intentional per the fifth pass's own
  reasoning and becomes valid when the tag is pushed. Recorded as LOW-68 only because
  nothing in `release.yml` creates the *Release object* that page needs — the tag alone
  does not.
