---
name: choosing-a-citation-act
description: Choose the citation act that matches an entry's real status, and pick the honest outcome when an entry goes contested or falls. Use when `references` fails with "act against <id>, whose status is …", when `freshness` or `propagate` has just contested an entry, when a citing sentence needs writing or repairing, and BEFORE reaching for a supersession — supersession is one of four honest outcomes, not the default.
---

# Choosing a citation act

**`cites-as-live` is not the goal.** The goal is that every citing sentence tells the
truth about the entry it names. An entry that is contested, and is cited as contested, is
a correct ledger. An entry that is contested and cited as live is a false sentence, and
that is the only thing `references` is objecting to.

Agents reliably get this wrong in one direction: they treat a `contested` status as an
emergency and reach for a supersession to make the checker green. That is the expensive
answer and usually the wrong one.

## The four acts, and what each is legal against

    cites-as-live       open, corroborated
    cites-as-contested  contested
    challenges          open, corroborated, contested
    cites-as-fallen     any status at all

There is **no `cites-as-refuted`**. `cites-as-fallen` is the act that covers a refuted,
superseded or retracted target, and it is legal against every status, which makes it the
act you can always fall back to when the prose is deliberately talking about a claim that
did not survive.

The statuses themselves:

    open  corroborated  contested  refuted  superseded  retracted  non-comparable
                        └ not terminal ┘    └────────── terminal ──────────┘
                                            └──── fallen ────┘  (not non-comparable)

`contested` is **not** terminal. An entry can leave it. That single fact is what makes
three of the four outcomes below possible.

## Which checker is objecting

Getting this wrong sends you to repair the wrong thing. The division of labour:

| checker | what it holds | typical message |
| --- | --- | --- |
| `validate` | one entry's shape and wording | frontmatter, sections, verdict lines |
| `resolve` | every pointer actually resolves | `does not resolve`, `has no section` |
| `references` | **an act against the target's current status**, both directions | `cites-as-live against X, whose status is contested` |
| `propagate` | `entry:` edges — fallen grounds, challenges, orphans | `carries no contested verdict by …` |
| `freshness` | a ground's bytes against its pin | `has moved`, `withdrawn`, `unstable pin` |

**`freshness` never objects to a citation, and `references` never objects to drift.** If
the message names an act and a status, it is `references`, and no amount of re-pinning
will answer it — the entry's *status* is what the citing sentence is wrong about.

## When an entry goes contested: four honest outcomes

A `contested` status is a question put to a person. All four of these answers are
legitimate and the checkers accept all four. Pick by what is *true*, never by what is
cheapest to make green.

**1. The prose should say "contested" — flip the act.**
Change the citation to `cites-as-contested` in the document, and the matching row in the
entry's `## References` to `· cites-as-contested`. Both sides, or `references` fails the
other way. The entry stays contested, the sentence now tells the truth, and `check` is
clean. This is a real resting state, not a holding pattern: a ledger whose contested
claims are visibly cited as contested is doing its job.

**2. The claim still holds on the artifact as it now stands — supersede.**
A pin cannot be edited, so re-establishing a claim on new evidence is a new entry. Follow
`docs/OPERATING.md` §"Repairing a drifted pin" step 3. Costs an entry file, a
`superseded` verdict on the predecessor, and every citation moved.

**3. The claim is no longer true — let it fall.**
Append a `refuted` or `retracted` verdict whose evidence points at what shows it false,
then rewrite the prose. Citations go with the sentence, or become `cites-as-fallen` if
the prose is deliberately discussing the claim that failed.

**4. You re-read the artifact and the claim genuinely still holds — corroborate.**
Append a `corroborated` verdict. `contested` is not terminal, so the status moves and
`cites-as-live` becomes legal again.

## The one move that is never legitimate

**Do not append a `corroborated` verdict you did not earn.** A corroborating verdict
asserts that a person read the artifact and found it still supports the Assertion. If
that reading did not happen, the verdict is a false statement, and no checker can catch
it — the checkers hold shapes and statuses, not sincerity.

Measured, on a real ledger: an entry was contested by a drift, then given a hand-written
`corroborated` verdict, while the pinned code had in fact been changed so the entry's
Assertion was **false**. All five checkers reported clean. The verdict was the only thing
that lied, and it was enough.

Reach for outcome 4 only when you can say which artifact you read and when. If you are
choosing it because outcome 1 felt like giving up, you want outcome 1.

## What "fresh" means, and what returning to live costs

`freshness` reports drift **since the pin**, and a drift that has been recorded is no
longer news. Once a contested verdict naming that ground is committed, the finding is
discharged and that ground stops reporting — permanently. That is the intended reading of
the name, and `docs/FRESHNESS.md` §"How a finding is discharged" is the rule.

The consequence is worth stating plainly, because it is the real cost of outcome 4:
**an entry returned to a live status carries a ground that will not flag again.** The
normal flow hides this, because outcomes 2 and 3 retire the entry and `freshness` skips
terminal entries anyway. Choosing outcome 4 is choosing to stop watching that ground, so
choose it only when you have just looked.

## Before you write any citation

1. Read the entry's **current** status — `claims-ledger status`, not what you remember.
2. Pick the act that is true of that status, from the table above.
3. Write it on **both** sides: the citation in the document, and the row in the entry's
   `## References`. `references` checks both directions and will name whichever is
   missing.
4. Run `claims-ledger references` before committing. It prints what it read.
