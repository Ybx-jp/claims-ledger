---
name: choosing-a-citation-act
description: Match a citation's act to the status of the entry it names, and choose among the repairs available when a status moves. Covers the four acts, the statuses each is legal against, and what each repair asserts and costs. Use when `references` reports "<act> against <id>, whose status is …", when a drift or a challenge has contested an entry, and when writing a citing sentence.
---

# Choosing a citation act

A citing sentence promises one thing: that the act it names is true of the entry's status
as it stands. There is no status a claim is supposed to end up at, and `cites-as-live` is
not a target — an entry that is contested and cited as contested is a correct ledger.

When `references` objects, it is saying the sentence and the status disagree. Four repairs
make them agree again, and they differ in what they cost and in what they assert. Picking
among them is the work; the checker has already done its part.

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

Each checker answers a different question, and the wording of a finding says which one you
are holding:

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

## When an entry goes contested: four outcomes

A `contested` status is a question put to a person. All four answers below are legitimate
and the checkers accept all four; they differ in what they assert, so pick by what is
true.

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

## What a corroborating verdict asserts

Outcome 4 is a statement that a person read the artifact and found it still supports the
Assertion. The checkers hold shapes and statuses, not sincerity, so this is one of the few
places where the ledger's accuracy rests entirely on the verdict being true.

Worth knowing what that costs when it is not: an entry contested by a drift, then given a
`corroborated` verdict while the pinned code had in fact been changed so the Assertion was
false, leaves all five checkers reporting clean. One untrue verdict is enough.

So take outcome 4 when you can say which artifact you read and when. Outcome 1 asserts
much less and is often the more accurate answer.

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
