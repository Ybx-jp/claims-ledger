# Operating a ledger that pins claims to code

`docs/SCHEMA.md` says what an entry is. `docs/FRESHNESS.md` says what a pin is and what
the fifth checker does with it. This says what it costs to run one over time: the two
things that break a pinned ledger from the outside, and the order in which a claim is
repaired once it has drifted.

None of it is enforced by a checker. A checker can tell you afterwards that the pins are
broken; nothing here can stop you breaking them, which is why it is written down.

## The history rewrite

A `code:` or `toml:` ground names a section of a file and an anchor, and the anchor
states the datum in one of two ways:

    - code: src/thing.py § "widget" @4023af4006273319aec9ae2512d197e4a99fce8c
    - code: src/thing.py § "widget" =sha256:3e1c…(64 hex)

The first is **by reference**: the section as it stood at that commit, and the commit id
is the whole of the ground's reproducibility. The second is **by value**: the digest of
the section's text, exactly as `freshness` compares it, computed from the working tree
by `claims-ledger sha --write` before the entry is committed — so the ground names what
the claim rests on without naming a commit at all. New grounds and every reading are
written by value; a ledger that has been kept for a while carries both forms.

A rewrite of history costs the two forms different things. Anything that removes a
commit from the branch's history —

- **A squash merge**, which replaces a branch's commits with one new commit.
- **A rebase merge**, which rewrites every commit with a new id.
- **A force-push over rewritten history**, an `amend` of a commit a pin names, a
  `filter-branch` or `filter-repo` pass — the same thing by other means.

— removes the evidence of every ground stated by reference into it. `resolve` fails for
each of them at once, and the failures are not repairable in place: Grounds sit above the
append-only marker and an anchor cannot be edited, so the only route back is a
supersession per entry — a new entry resting on the artifact as it now stands, a
`superseded` verdict on each old one, and every citation moved. Eight entries is an
afternoon. A hundred is a rewrite of the ledger.

A ground stated by value loses nothing it rests on. The datum is in the anchor and
`freshness` compares it exactly as before; what the rewrite costs is the diff a person
would read during repair. When no version of the path this repository holds digests to
the anchor any more, `resolve` flags the ground rather than showing its founding text,
and a reading of the section as it now stands moves the ground past the flag.

**So: merge commits only, on any branch whose commits a ground names by reference.** Turn
the other strategies off at the source rather than relying on habit. On GitHub that is
`allow_squash_merge` and `allow_rebase_merge` set false on the repository, which stops the
merge button as well as the command line:

    gh api -X PATCH repos/<owner>/<repo> \
      -F allow_squash_merge=false -F allow_rebase_merge=false

The merge guard `claims-ledger harness install` writes into a project refuses the local
commands for a coding agent, and is one enforcement of this section rather than a
substitute for it. Both defend the grounds stated by reference. A ledger whose every
ground and reading is by value has nothing left for them to defend, and keeping them is
then a choice for the project rather than a rule of the ledger.

**If it has already happened**, do not paper over it. `resolve` naming a commit that is
not in the repository is a true report of a real loss, and an entry whose evidence is gone
is not an entry whose evidence is fine. Supersede them, and say in the new entries' notes
what happened; a ledger that quietly re-pins is worth less than one that records that its
history was rewritten.

## One branch at a time appends to an entry

Verdicts are lines in one file, so two branches that each append to the same entry conflict
when they meet. Git will offer to keep both, and a resolution that interleaves them is the
one thing this ledger cannot check: the append-only comparison asks that each parent's
verdicts be a prefix of its child's
(L0082-verdicts-append-and-only-append-across-every-edge, cites-as-live), and a weave that
is a prefix of both parents exists only where one parent's list is already a prefix of the
other's — which is to say, only where the branches did not both append. Weakening that comparison so a weave passes has been tried and is not
cheap — every weakening that admits a legal weave also admits a merge that rewrote the
list, because the two are the same shape seen from different sides.

So the rule is upstream of the merge rather than inside the checker: **only one branch at a
time appends to a given entry.** In practice that means a pass that runs
`claims-ledger freshness --write` finishes and merges before the next branch starts, and
two branches do not both pin the same section. It is a scheduling constraint on the ledger
and not on the code, and it is cheap, because a ledger is written in passes anyway.

**So append a verdict on a branch that is up to date.** Merge `main` into the branch
first, then append; the verdict then sits on top of main's line, main's list is a prefix
of the branch's, and the merge back is a prefix extension of both parents. That is the
whole discipline, and it is the same shape as "rebase before you push" everywhere else —
except done with a merge, because this repository does not rewrite history.

**If both sides have already committed a verdict, there is no resolution that clears it.**
Measured, rather than argued: keeping one side reports the dropped verdict at the merge,
and re-appending the same reading afterwards does not clear that report, because the
comparison is against every revision's own parents and the merge is now one of them.
Keeping both in either order fails against the other parent. What is left is to rebuild
the branch that has not merged yet, off current `main`, and append there — which is a
history rewrite, and permitted here only because those commits are unmerged and nothing
pins them. Check that before doing it: an entry created on that same branch may pin them,
and then the rewrite costs what the section above says it costs.

## Several checkouts, and the ids they mint

A single person running several agent sessions at once has one repository and several
linked worktrees, each on its own branch. That is the ordinary shape of concurrent work
here, and it used to collide by construction: an id was allocated above the entries
directory of whichever checkout was asking, so two sessions that minted on the same
afternoon were handed the same number.

An id is now allocated above everything the repository holds — this checkout's entries,
every entry filename any ref has ever carried, and the entries each sibling worktree holds
including the ones it has not committed
(L0233-an-id-is-allocated-above-the-whole-repository, cites-as-live). Worktrees share
their refs, so none of that costs a fetch. **A mint over a repository git could not read
is refused rather than allocated from the one directory it could see**; `--id` names one
by hand when the repository is broken for other reasons.

**If two entries end up carrying one number anyway, `validate` fails**
(L0242-two-entries-may-not-carry-one-number, cites-as-live). It did not, and that is worth
knowing about ledgers written before this: two branches that each minted a number produce
entry files whose slugs differ, git merges them with no conflict, and every checker read
the result at exit 0. A number names one entry, because a citation may name it without the
slug.

### Reconciling it

**The receiving side keeps its ids**
(L0239-the-receiving-side-keeps-its-ids, cites-as-live). A merge is never symmetric, so
the branch being merged is the one that moves, three open branches are three sequential
merges, and nothing needs an arbiter.

    claims-ledger renumber --onto main            # what would move
    claims-ledger renumber --onto main --write    # move it

It rewrites the branch, not the merge, and every entry it moves is *created* in that
branch's own history under the id it will keep
(L0235-a-renumber-rewrites-the-branch-rather-than-the-merge, cites-as-live). That matters
more than it sounds: `validate` compares a frozen region against the blob at the commit
that created the entry's path, so an entry renamed after a commit holds it is compared
against the rename commit — and whatever else that commit changed rides in unchecked. A
branch rewritten before it merges never renames a committed file.

This *is* a history rewrite, and it is the one the section above permits: the commits are
unmerged and nothing pins them. The command holds you to that. It refuses a branch already
merged, a branch whose own entries pin by reference a commit the rewrite would replace,
commits another ref also holds, a configuration that changes mid-branch, a dirty working
tree, and a branch another checkout has out. Check what it says before reaching for
`--force`.

`--force` covers three of those — the by-reference pin, the shared ref, and the
configuration that changes mid-branch — plus the refusal over a repository that signs its
commits. Those are judgements the command cannot always make correctly, and an operator
who has checked by hand needs a way past. It does not cover a dirty working tree, a branch
another checkout has out, a detached HEAD, or a branch that is already merged: those are
not judgements, they are ways to lose work that was never committed or to land a rewrite
on no ref at all, and no flag reaches them
(L0301-force-covers-the-judgements-and-not-the-ways-to-lose-work, cites-as-live).

Citations move with the ids, and an anchor is re-pinned only where undoing the
substitution reproduces the anchor the entry already carries — a proof that the id was the
whole of the change. Where it was not, the anchor stands and `freshness` flags it for
someone to read.

### At merge time

`merge-renumber` says what a merge guard does about a collision it sees
(L0243-the-merge-time-policy-is-configured-and-defaults-to-refusing, cites-as-live):

    merge-renumber = "refuse"   # stop the merge and name the repair (the default)
    merge-renumber = "rewrite"  # renumber the incoming branch, then let it proceed
    merge-renumber = "off"      # say nothing

The guard `claims-ledger harness install` writes asks before `git merge <branch>`, and
before is the only useful moment: measured on git 2.43.0, a conflicted merge fires no hook
at all, its resolution commit fires `pre-commit`, and a clean auto-merge fires
`post-merge`. Every hook a merge has fires once the merge has already happened, by which
point the branch to rewrite is part of the history.

### The hook, in a worktree

git serves one hooks directory to every linked worktree, so `.git/hooks/pre-commit` is a
per-repository file guarding per-checkout trees. It asks git which checkout it is
committing in and prefers that checkout's interpreter, falling back to the one recorded at
install time (L0245-the-hook-runs-the-package-the-checkout-it-guards-resolves,
cites-as-live). For a project that installs this package from outside its own tree the two
are the same; for a project whose tree *is* the package, the recorded path would otherwise
run one checkout's package against another checkout's tree.

## Adding an entry takes one commit

An entry's citation usually lives *inside* the section that entry rests on — the
docstring sits in the function, the README sentence sits in a file that some other entry
pins. A ground stated by reference cannot name the commit that carries its own citation,
because that commit does not exist yet, and landing an entry used to take two commits
with the hook bypassed between them. A ground stated by value is computed before any
commit exists, so the code, the citation and the entry land together:

1. Write the code, and the citation in the prose that states the commitment — README
   sentence, docstring, comment — inside the section the entry will rest on.
2. Write the entry, with each ground's anchor left as `=?`.
3. Run `claims-ledger sha --write <entry>`. It fingerprints the entry and fills each `=?`
   with the digest of the section as the tree has it, and it refuses, naming the
   pointer, when that section is not there.
4. Commit all three. The installed pre-commit hook passes on the first try: `references`
   sees the entry, `resolve` sees the anchor match the tree, `freshness` sees the ground
   fresh.

Two things follow. Never resolve a `references` refusal by deleting the citation: the
citation is the link the ledger exists to keep, and a commit that drops it passes the
check by removing the thing being checked. And a citation written into a section that
other entries already rest on flags their grounds as `moved` in the same run, because it
is an edit to their span; that is the mechanism working, and a reading discharges it, as
below.

## Repairing a drifted pin

`freshness` reports five things, and they do not all mean the same thing. Two of them are
not drift and **must not be given a verdict**:

| finding | | what it needs |
| --- | --- | --- |
| fresh | | nothing; it is silent |
| **moved** | flag | the sequence below |
| **withdrawn** | fail | the sequence below; the artifact reads `absent` |
| **unstable pin** | flag | re-pin at a revision — there is no verdict for this |
| **unknown** | fail | fix the repository; **no verdict discharges it** |

An `unstable pin` names no revision, so there is nothing to compare and nothing to
discharge. An `unknown` is git declining to answer; a verdict written over it records a
judgement that was never made. Both are argued in `docs/FRESHNESS.md`.

For a `moved` or `withdrawn` ground:

**1. Let the machinery write the verdict.**

    claims-ledger freshness --write

This appends a `contested` verdict under the propagation author, carrying the pointer as
evidence and the digest of the section as this run read it as `artifact:`. Exit 1 is
correct — it wrote something. Write this verdict with the tool and never by hand:
`artifact:` is machine provenance and is checked as such, and a hand-written propagation
verdict is a person borrowing the authority of a check that did not run.

The entry is now `contested`, so `references` fails every site citing it `cites-as-live`,
by name. That list is how you find the prose to repair.

**2. Re-judge.** This is the step no tool does. Read the Assertion against the artifact as
it now stands:

- **The claim still holds, on different evidence.** Supersede it — step 3. An anchor
  cannot be edited, and that is deliberate: a claim re-established on new evidence is a
  different claim from the one established on the old.
- **The claim is no longer true.** Append a `refuted` verdict whose evidence points at
  what shows it false, and rewrite the prose. The citations are removed with the sentence,
  not moved.
- **The artifact moved and the claim did not** — a reformat, a comment, a renumbering, a
  section moved to another path, a rename. Acknowledge it rather than superseding it:
  append a `corroborated` verdict naming the artifact as it now stands, with a note
  recording what moved. Write its anchor as `=?` and let `sha --write` fill it: a
  reading stated by value needs no commit to be placed at, and filling it touches nothing
  above the marker, so the reading lands in the same commit as the edit it read. The
  entry keeps its id, its Grounds and its citations. Its evidence must name the artifact
  as it is now rather than restate the ground —
  `validate` refuses a corroborating verdict pointing at a ground the entry already
  cites, which is what makes it a record of a reading — and `freshness` compares the
  ground from that reading afterwards, so a later change is reported again.
  `docs/FRESHNESS.md` §"How a finding is discharged" has the shape.

**Before writing the successor, ask what actually moved.** If the pinned section changed
for a reason the claim does not name, the *ground* is wrong, and carrying the same ground
into the successor buys exactly one more supersession on the next unrelated edit. Narrow
it instead: pin the code that carries the rule rather than a caller that follows it, and
configure a `section-pattern` if the claim is about something narrower than a whole table
or function. The tell is mechanical — when `sha --write` on the successor computes a
`verbatim_sha` **byte-identical** to its predecessor's, the Scope and the Backing never
moved and only the ground did. That is the case where narrowing is the whole of the
repair, and often the case where acknowledging is and no successor is needed at all.

Read it as a tell about the Scope and not about the claim, because the fingerprint is
computed from the Scope and the Backing alone: an Assertion that turns out to be false
over a Scope that was right the whole time is superseded with the fingerprint unmoved, and
that is the supersession this tell will tell you not to make.

**3. Supersede.** Both directions are checked against each other, and supersession is a
chain, never a tree — an entry carries exactly one `superseded` verdict.

    claims-ledger new <slug>

Copy Assertion, Scope, Warrant and Backing across; write the Grounds against the artifact
as it now stands, each anchor `=?`; declare `supersedes: <old id>` in the successor's
frontmatter; append to
the predecessor a verdict whose evidence is `entry: <new id> · supersedes`; move every
citation the reference check named; and run `claims-ledger sha --write` on the successor
**before** it is committed, since `sha --write` refuses an entry that is already in
history.

Then commit, and merge without rewriting history.

## What this costs, honestly

Every edit that changes what a claim rests on is a supersession: a new entry file, a
verdict, and moved citations. An edit that moves the artifact without touching the claim
is an acknowledgement instead — one verdict, and the entry keeps its id, its Grounds and
its citations — so the expensive path is paid for real changes of meaning rather than for
every edit. Pins on narrow sections make even the acknowledgements rare: a pin on a
function is flagged only when that function changes, where a pin on a file is flagged by
every commit that touches it. The cost does not go to zero, and it scales with the number
of entries pinned rather than with the number of real changes of meaning.

### Choosing a ground

A ground is evidence, and it should name the code that makes the claim true and nothing
else. Two failures are common and both are avoidable at the moment the entry is written,
which is the only cheap moment there is.

**Do not pin a caller.** A claim about what a command does is grounded in the code that
does it, not in every command that calls it. A ground on a caller goes stale for every
edit to that caller for the rest of its life, none of which the claim cares about. If the
claim's cohort really is "all six commands", say that in the Scope and let the Warrant
name the pattern; a Scope clause is prose the reader checks, and it does not go stale.

**Do not pin more than the claim needs.** A section is the unit, and a section as the
patterns ship it is a whole table or a whole top-level definition. A claim about one
setting resting on the table holding it goes stale when an unrelated key beside it
changes. `section-patterns` is the instrument: a pattern can name something narrower
than the type's default. A `toml` ground on a table is the whole table; a type configured
as `'^{name} = '` is one key of it, and a claim about two settings then rests on four
lines rather than on the thirty around them.

**Check what the narrower pattern actually spans before you rest a claim on it.** One
pattern decides both ends of a section — the same pattern with the name widened is what
finds the end — so a key pattern's section runs to the next line that pattern matches,
whatever that line is. Two consequences, and the first is the dangerous one:

- **Over a value written across several lines it spans the key's own first line and
  nothing else.** `authors = [` followed by three lines of names is `authors = [` before
  and after any of those names change: a ground that can never go stale, which is worse
  than one that goes stale too often, because nothing will ever tell you.
- **A key name is matched wherever it first appears**, in whichever table. `toml-key`
  cannot say *which* table, so a Scope that says "the project table" is asserting
  something its ground cannot check. Say it in the Warrant if you rely on it.

**A declaration's prefix belongs to the declaration.** Where a language writes something
in front of the line that names a thing — a Python decorator, an attribute, an annotation
— a pattern anchored on the naming line alone leaves that prefix in the *previous*
section, or in none at all. `@dataclass` above a class sits inside the section of whatever
was defined before it, so an edit to it flags a claim it has nothing to do with;
`@dataclass(frozen=True)` *ends* the previous section instead, because the same pattern
with the name slot widened matches `@dataclass(frozen` before its `=`, and the decorator
is then in no section and an edit to it flags nothing. One keyword argument decides which.

The repair is to take the prefix into the pattern, which a pattern may do because it is
matched over the whole artifact rather than line by line
(L0280-a-section-pattern-is-matched-over-the-whole-artifact, cites-as-live):

    [tool.claims-ledger.section-patterns]
    code = '^(?:@[^\n]*\n)*(?![ \t])(?:(?:async[ \t]+)?(?:def|class)[ \t]+{name}\b|{name}[ \t]*(?::[^=\n]+)?=)'

Measured over this repository's own ledger — 391 `code:` grounds, 382 of them resolvable
in the working tree — that recipe resolves all 382, leaves 376 spans byte-identical and
moves 6 onto the declaration the prefix belongs to
(L0281-the-documented-recipe-starts-a-section-at-the-prefix, cites-as-live).

**Adopting it here cost three of those six, and which three is the useful part.** A
pattern change is invisible to a ground whose most recent reading is stated *by reference*:
both sides of the comparison are re-derived under the new pattern, so the commit and the
tree still agree and nothing is reported
(L0195-the-latest-corroboration-is-where-a-ground-was-last-read, cites-as-live). A ground
last read *by value* is the opposite. Its anchor froze the digest of a span the old pattern
produced, and no version of the file digests to that under the new one — so `freshness`
says the ground moved and `resolve` says the text the claim was established on can no
longer be shown at all. One re-read verdict discharges both, and the flag says so. Change a
pattern in a commit that does nothing else, and read the by-value grounds it moves in that
same commit.

`claims-ledger references` prints what it read; comparing a ground's span against the
claim before committing the entry is the whole of the check, and it takes a minute.

Two more things keep it affordable. Pin sections, never files. And choose the grade
honestly:
`measured` is for a claim that the code *does* something and takes a pin that `freshness`
watches; `asserted` is for a choice the project *made*, forbids an evidence ground, and so
never goes stale. A preference recorded as `measured` buys a supersession every time the
file is reformatted, in exchange for nothing.
