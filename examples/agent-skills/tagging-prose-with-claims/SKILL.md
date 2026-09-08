---
name: tagging-prose-with-claims
description: Turn prose that promises something — a docstring, a README paragraph, a design-document sentence, a comment — into ledger entries, and cite each from the sentence that states it. Use before writing a batch of entries over a file, when prose asserts something no entry holds, when deciding where a citation will physically sit, and to ask with `claims-ledger neighbours` which entries are already about the ground being chosen.
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

## Ask who is already there

    claims-ledger neighbours 'code: path/to/file.py § "the_section" @HEAD'
    claims-ledger neighbours <entry id>

Once a ground is chosen and before the entry is written, this answers with the entries
already resting on that span, or whose Scope `cohort` nests inside the one being drafted.
The pointer form is the one that works before the entry exists — the question is asked of
the ground being considered.

It is advisory. It exits 0 whatever it finds, `check` does not run it, and it decides
nothing. What it is for is the pair no checker can see: two entries about the same
function that name nothing of each other are out of range of every rule by construction,
and the moment the grounds are being chosen is the only moment anything asks.

Each answer says whether the ledger already relates the two. For one it does not:

- **The same claim, said twice** — write one entry, or supersede the older.
- **Different claims about the same artifact** — record it once, as a `distinguishes`
  ground in the entry being written, with the Warrant saying how they differ. It sits
  *beside* the grounds the entry rests on: a distinction is not support, and `validate`
  reports an entry whose every ground is one. `choosing-a-citation-act` has the act in
  full.
- **Neither** — near is not inconsistent, and most neighbours are neither. Leave them.

`claims-ledger neighbours --count` prints the distribution over a whole ledger — median,
mean, most, and how many entries have none — which is what says whether the lookup is
worth running on a given project.

## What `validate` checks in the wording

`claims-ledger validate` applies rules to the wording itself, and reports each by name.
Three worth knowing before drafting. Two read the Assertion:

- **An Assertion that reads as an absence or a priority claim needs a `search:` ground.**
  The test is on words, not sense, so an ordinary sentence can trip it. Rewording is
  usually cheaper than adding a search ground you did not mean.
- **An Assertion carries no quotation marks.** Quoted material belongs in Backing, where
  it is checked against its source.

And one reads the Scope against the Warrant:

- **A Scope and a Warrant name one set of statuses, not two nested ones.** Where a Scope
  names each of the ways an entry falls and never says `terminal`, while the Assertion or
  Warrant does, `validate` **flags** it. Those are two populations — a status can be
  terminal without being a fall — and it is the Warrant a person implements, so an entry
  written that way states one rule and gets another. A flag, not a failure: widening the
  Scope and narrowing the Warrant are both legal repairs, and only the author knows which
  claim was meant. The finding names the status that separates the two sets, and
  `choosing-a-citation-act/reference/vocabulary.md` has the statuses with which are
  terminal.

`reference/entry-anatomy.md` covers what each section of an entry is for.

## Order of operations

1. List the sentences in the file that promise something.
2. Decide citation placement for this file.
3. Draft each Assertion.
4. Choose each ground: the narrowest section that carries the rule.
5. `claims-ledger neighbours` on each ground, before writing the entry, and decide what to
   do with anything it surfaces.
6. Write every citation. First commit, `--no-verify`.
7. `claims-ledger new <slug>` per entry; fill Assertion, Scope, Grounds, Warrant and
   Backing; pin each ground to the first commit; add the `## References` row naming each
   citing document and the act it uses.
8. `claims-ledger sha --write` on every new entry, before it is committed — it refuses an
   entry version control already has.
9. `claims-ledger check`, then the second commit with the hook running.

If step 9 reports drift on entries that already existed, that is the placement question
arriving late; `repair-a-drifted-pin` covers discharging it.

## Reference

- `reference/entry-anatomy.md` — the sections of an entry and what each is for.
- `reference/choosing-a-ground.md` — ground width, and the two failures that are cheap to
  avoid while writing and expensive afterwards.
