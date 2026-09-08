---
name: tagging-prose-with-claims
description: Turn prose that promises something — a docstring, a README paragraph, a design-document sentence, a comment — into ledger entries, and cite each from the sentence that states it. Use before writing a batch of entries over a file, when prose asserts something no entry holds, and when deciding where a citation will physically sit.
---

# Tagging prose with claims

A tagging pass reads a file's prose, finds the sentences that promise something the
project is answerable for, and gives each one an entry pinned to the artifact that keeps
it true.

Tagging adds a citation and an entry; it removes nothing. What it buys is that the
sentence fails a check when the thing under it moves.

## Decide where the citation will sit, before writing any entry

A pinned ground names a **section** of an artifact, and what counts as a section is a
per-project pattern. Print the patterns this project uses before assuming:

    python -c "from claims_ledger import open_ledger; print(open_ledger().config.section_patterns)"

If a citation is written *inside* a span that entries already pin, adding it moves that
span, and every entry pinned there is flagged. The cost compounds with density: a section
carrying seven grounds has seven entries flagged by the next citation written into it.

Two placements, chosen per file before starting:

- **Inside the section** — the citation sits in the sentence it manages, which is the
  point of the mechanism. Every later citation written there flags the entries pinned
  there.
- **Outside every section** — prose that no pattern matches, such as a file-level preamble
  above the first definition, carries citations without moving any pinned span. The
  grounds still name the individual sections. The trade is distance: the citation no
  longer sits in the sentence it belongs to, and one preamble cannot readably carry
  dozens.

Either way, write all the citations for a file in one commit; the movement is paid once.

## Documents and grounds are different

- **Documents** are the prose scanned for citations. Ask which files those are:

      python -c "from claims_ledger import open_ledger; print(open_ledger().config.documents)"

- **Grounds** are evidence, and the document list does not gate them. A ground names any
  path the project holds.

So a file being outside the document list means only that prose in it cannot carry a
citation — never that a claim about it cannot be grounded.

## Two commits

The citation usually sits inside the span the entry pins, so one commit cannot do it: the
entry would have to name a revision that does not exist yet.

1. **The prose that cites the entry.** The pre-commit hook refuses this, because the
   citation names an entry that is not there — `git commit --no-verify` is the promise
   that the second commit is coming.
2. **The entry files**, with grounds pinned to the first commit.

Run `claims-ledger check` yourself between the two. Resolving the refusal by deleting the
citation passes the check by removing what is being checked.

Batching helps: every citation in the first commit, every entry in the second, one bypass.

## Choosing a ground

A ground should name what makes the claim true and nothing else.
`reference/choosing-a-ground.md` has the cases. The short of it:

- **Name the thing that carries the rule**, not something that merely follows it. A ground
  on a consumer goes stale for every edit to that consumer.
- **Narrower is not always better.** A ground that can never go stale is worse than one
  that goes stale often, because nothing will ever tell you. Check what a narrow pattern
  actually spans before resting a claim on it — `claims-ledger references` prints what it
  read.
- **Grade honestly.** `claims-ledger new --help` lists the grades. A choice the project
  *made* is `asserted`, forbids an evidence ground, and never goes stale. A statement that
  something *does* what it says is `measured` and takes a pin that `freshness` watches.

Several claims resting on one section is a normal shape — it is what enumerating a
section's invariants looks like. The count is also how many entries the next edit inside
it flags.

## What `validate` checks in the wording

`claims-ledger validate` applies rules to the Assertion itself, and reports each by name.
Two worth knowing before drafting:

- **An Assertion that reads as an absence or a priority claim needs a `search:` ground.**
  The test is on words, not sense, so an ordinary sentence can trip it. Rewording is
  usually cheaper than adding a search ground you did not mean.
- **An Assertion carries no quotation marks.** Quoted material belongs in Backing, where
  it is checked against its source.

`reference/entry-anatomy.md` covers what each section of an entry is for.

## Order of operations

1. List the sentences in the file that promise something.
2. Decide citation placement for this file.
3. Draft each Assertion.
4. Choose each ground: the narrowest section that carries the rule.
5. Write every citation. First commit, `--no-verify`.
6. `claims-ledger new <slug>` per entry; fill Assertion, Scope, Grounds, Warrant and
   Backing; pin each ground to the first commit; add the `## References` row naming each
   citing document and the act it uses.
7. `claims-ledger sha --write` on every new entry, before it is committed — it refuses an
   entry version control already has.
8. `claims-ledger check`, then the second commit with the hook running.

If step 8 reports drift on entries that already existed, that is the placement question
arriving late; `repair-a-drifted-pin` covers discharging it.

## Reference

- `reference/entry-anatomy.md` — the sections of an entry and what each is for.
- `reference/choosing-a-ground.md` — ground width, and the two failures that are cheap to
  avoid while writing and expensive afterwards.
