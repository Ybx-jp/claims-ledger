---
name: choosing-a-citation-act
description: Match a citation's act to the status of the entry it names, and choose among the repairs available when a status moves. Use when `claims-ledger references` reports "<act> against <id>, whose status is …", when a citing sentence is being written or moved, and when a drift, a challenge or a fallen ground has changed an entry's status.
---

# Choosing a citation act

A citing sentence promises one thing: that the act it names is true of that entry's status
as it stands. `claims-ledger references` checks exactly that, in both directions — the
citation in the document, and the row in the entry's `## References`.

When it objects, the sentence and the status disagree. Several repairs make them agree
again; they differ in what they assert and in what they cost.

**This is the wrong skill if** the finding says `has moved`, `withdrawn`, `unstable pin`
or `unknown` — that is `claims-ledger freshness`, and `repair-a-drifted-pin` covers it.
A finding naming an act and a status is about the entry's status, so re-pinning does not
reach it.

## Read the current state first

    claims-ledger status                 every entry and the status it derives to
    claims-ledger references             every citation, checked both ways

Statuses derive from the verdict list rather than being stored, so the status an entry had
when you last looked is not evidence about now.

## The acts

    claims-ledger references             names the act and the statuses it allows

`reference/vocabulary.md` has the full table and how to read it from the package rather
than from memory. In short: `cites-as-live` speaks of a claim in good standing,
`cites-as-contested` of one under question, `cites-as-fallen` of one that did not survive,
and `challenges` is written by an entry that disputes another.

`cites-as-fallen` is legal against every status, which makes it available whenever the
prose means to discuss a claim as it stands rather than to rely on it.

## When a status moves

The status is a question put to a person, and these answers are all legitimate. Pick the
one that describes what is true.

**Say what is now the case — change the act.**
Update the citation in the document and the matching row in the entry's `## References`.
Both sides, or `references` objects the other way. The entry keeps its status, the
sentence describes it accurately, and the check is clean.

**Re-establish the claim on the artifact as it stands — supersede.**
A ground cannot be edited once the entry is in history, so a claim re-established on new
evidence is a new entry: `claims-ledger new <slug> --supersedes <old-id>`, with the old
one carrying a `superseded` verdict and every citation moved.
`repair-a-drifted-pin/reference/superseding.md` has the sequence.

**Record that it did not survive.**
Append a `refuted` or `retracted` verdict whose evidence points at what settles it, then
rewrite the prose. Citations move with the sentence, or become `cites-as-fallen` where the
prose still means to name the claim.

**Record that it still stands — corroborate.**
Append a `corroborated` verdict. This is a statement that a person went and looked, so it
carries what was read and when. Sincerity is the one thing no checker can check: a
corroborating verdict that records a reading nobody did leaves every checker clean over an
Assertion that is false.

Where the finding is a drift the claim does not depend on — a section that moved, a
renumbering, a rename — `repair-a-drifted-pin` covers acknowledging it without touching
the claim.

## Writing a citation

1. `claims-ledger status` for the entry's status now.
2. Choose the act that is true of it.
3. Write it on both sides: the citation in the document, and the row in the entry's
   `## References`.
4. `claims-ledger references` before committing — it prints what it read.

Removing the citation also clears the finding, by removing the link the ledger exists to
keep.

## Reference

- `reference/vocabulary.md` — statuses, acts, grades and kinds, and the command that
  prints each of them.
- `reference/status-derivation.md` — how a verdict list becomes a status, and which
  verdicts stop the walk.
