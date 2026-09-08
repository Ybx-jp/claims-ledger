---
name: tagging-prose-with-claims
description: Extract claims from existing prose — a docstring, a README paragraph, a comment — into ledger entries, and cite them from the sentence that states them. Use BEFORE writing a batch of new entries over a file, when a source file's prose states commitments nothing holds, and when planning where a citation will physically sit. Covers citation placement, the two-commit shape, ground width, and the wording rules that fail `validate` silently.
---

# Tagging prose with claims

A tagging pass reads a file's prose, finds the sentences that make checkable promises
about the code, and gives each one an entry pinned to the code that keeps it true.

**The prose does not shrink.** Tagging adds a citation and an entry; it deletes nothing.
If the goal was fewer lines of comment, this is the wrong instrument. What it buys is
that the paragraph fails CI when the code under it moves.

## Plan citation placement before you write a single entry

A `code:` ground pins a **section** — under the shipped pattern, a whole top-level
definition, docstring included. So **a citation written inside a function's docstring is
inside the span that function's entries pin.** Adding one drifts every claim already
pinned there.

The cost compounds with density. Adding three citations to one function's docstring drifts
every entry already pinned to that function — two, in one measured pass, each costing a
supersession whose successor computed a `verbatim_sha` byte-identical to its
predecessor's. A function carrying seven grounds pays seven for the next citation added
inside it.

Two placements, and you choose per file before you start:

- **Inside the section** — the citation sits in the sentence it manages, which is the
  whole point of the mechanism. Every later citation added to that section drifts every
  entry pinned to it.
- **In the module docstring** — a module docstring is not inside any section, because the
  pattern matches only a top-level `def`, `class` or assignment. Citations there drift
  nothing, and the grounds still point at the individual functions. The cost is that the
  citation leaves the sentence it belongs to, and one module docstring cannot readably
  carry forty of them.

A workable default: **claims about a specific definition get their citation in the module
docstring when the file will be tagged densely, and in the definition's own docstring
when it will not.** Decide once, per file, and write all the citations in one commit —
the drift is paid once whichever way you go.

## Documents and grounds are different things

- **Documents** are the prose scanned for citations — the `documents` globs in
  configuration. This is the *only* thing that list controls.
- **Grounds** are evidence, and they are **not** gated by `documents`. A `code:` or
  `toml:` ground resolves any path in the repository, whether or not that path is a
  document.

So "this file isn't in `documents`" never means "a claim about it cannot be grounded." It
means only that prose in that file cannot carry a citation.

## Adding an entry takes two commits

The citation usually lives inside the section the entry pins, so a single commit cannot
work — the entry would name a commit that does not exist yet.

1. **Commit one:** the code and the prose that cites the entry. **The pre-commit hook
   will refuse this**, because `references` sees a citation to an entry that does not
   exist. `git commit --no-verify` is the promise that commit two is coming.
2. **Commit two:** the entry files, with grounds pinned to commit one.

Run `claims-ledger check` yourself before committing the second half. Never resolve the
refusal by deleting the citation — that passes the check by removing the thing checked.

Batching helps: N citations in commit one, N entries in commit two, one bypass total.

## Choosing a ground

`docs/OPERATING.md` §"Choosing a ground" is the authority. The three that bite:

- **Do not pin a caller.** Pin the code that carries the rule. A ground on a caller goes
  stale for every edit to that caller forever.
- **Do not pin more than the claim needs** — but know that over-narrowing is the worse
  failure. A ground that can never go stale is worse than one that goes stale too often,
  because nothing will ever tell you. Before resting a claim on a narrow pattern, check
  what the pattern actually spans.
- **A big function is a code-shape problem, not a ledger problem.** If one definition
  accumulates eight claims, the honest fix is usually to split the definition, not to
  invent a narrower pattern.

Several claims resting on one section is a normal shape, not an error — it is what
enumerating a definition's invariants looks like. Just know that the count is also the
supersession cost of the next edit inside it.

## Wording rules that fail after you have written the entry

`validate` applies heuristics to the **Assertion** text. Check yours before writing:

- **Absence and priority claims need a `search:` ground.** Triggered by any of
  `nobody`, `neither`, `first`, `novel`, `unique`, `unprecedented` as standalone words;
  the phrases `no one` and `not found`; or `no` followed later in the same sentence by
  `has`, `have`, `was`, `were`, `report` or `reports`.

  It matches on the word, not the sense, so ordinary uses trip it — "losing the **first**
  to the second write" fires on a claim that says nothing about priority. Rewording is
  cheaper than arguing with the heuristic.

- **No quotation marks in an Assertion.**
- **`measured` requires an evidence ground; `asserted` forbids one.** A preference the
  project *made* is `asserted` and never goes stale. A statement that the code *does*
  something is `measured` and takes a pin. Recording a preference as `measured` buys a
  supersession every time the file is reformatted, in exchange for nothing.

## Do not write counts into prose

A sentence that says how many entries there are, or how many pins sit on which commit, is
false the next time an entry lands, and no checker will tell you. `claims-ledger status`
is the count. This is the one class of prose a tagging pass should *remove* rather than
cite.

## The order of operations

1. Read the file's prose and list the sentences that make checkable promises.
2. Decide citation placement for this file (module docstring vs in-section).
3. Draft each Assertion; check it against the wording rules above.
4. Choose each ground: the narrowest section that carries the rule, never a caller.
5. Write **all** the citations. Commit one, `--no-verify`.
6. `claims-ledger new <slug>` per entry; fill Assertion, Scope, Grounds, Warrant,
   Backing; pin grounds to commit one; add the `## References` row for each citing
   document.
7. `claims-ledger sha --write` on every new entry — it refuses an entry already in
   history, so this happens before commit two.
8. `claims-ledger check`. Commit two, with the hook running normally.

If step 8 reports drift on entries that already existed, that is the placement question
from the top of this file arriving late. `choosing-a-citation-act` has the four repairs
and what each asserts.
