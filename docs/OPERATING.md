# Operating a ledger that pins commits

`docs/SCHEMA.md` says what an entry is. `docs/FRESHNESS.md` says what a pin is and what
the fifth checker does with it. This says what it costs to run one over time: the two
things that break a pinned ledger from the outside, and the order in which a claim is
repaired once it has drifted.

None of it is enforced by a checker. A checker can tell you afterwards that the pins are
broken; nothing here can stop you breaking them, which is why it is written down.

## The history rewrite

A `code:` or `toml:` ground pins a section of a file **at a commit**:

    - code: src/thing.py § "widget" @4023af4006273319aec9ae2512d197e4a99fce8c

That commit id is the whole of the ground's reproducibility. Anything that removes the
commit from the branch's history removes the evidence with it:

- **A squash merge** replaces a branch's commits with one new commit.
- **A rebase merge** rewrites every commit with a new id.
- **A force-push over rewritten history**, an `amend` of a commit a pin names, a
  `filter-branch` or `filter-repo` pass — the same thing by other means.

After any of them `resolve` fails for every ground pinned into the vanished commits, at
once. The failures are not repairable in place: Grounds sit above the append-only marker
and a pin cannot be edited, so the only route back is a supersession per entry — a new
entry pinned at a commit that exists, a `superseded` verdict on each old one, and every
citation moved. Eight entries is an afternoon. A hundred is a rewrite of the ledger.

**So: merge commits only, on any branch whose commits are pinned.** Turn the other
strategies off at the source rather than relying on habit. On GitHub that is
`allow_squash_merge` and `allow_rebase_merge` set false on the repository, which stops the
merge button as well as the command line:

    gh api -X PATCH repos/<owner>/<repo> \
      -F allow_squash_merge=false -F allow_rebase_merge=false

The merge guard `claims-ledger harness install` writes into a project refuses the local
commands for a coding agent, and is one enforcement of this section rather than a
substitute for it.

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

## Adding an entry takes two commits

This bites the first time and then never again, so it is worth stating plainly.

An entry's citation usually lives *inside* the section that entry pins — the docstring
sits in the function, the README sentence sits in a file that some other entry pins. So a
single commit cannot work: the entry would have to name a commit that does not exist yet,
and pinning the commit before it flags the ground as `moved` on the entry's first run.

1. **Commit one:** the code, and the prose that cites the entry — README sentence,
   docstring, comment.
2. **Commit two:** the entry file, with its grounds pinned to commit one.

**The installed pre-commit hook will refuse commit one.** It runs `references`, commit one
carries a citation naming an entry that does not exist yet, and that is exactly the defect
`references` exists to catch.

The checker is not being conservative here; it cannot do better. At commit one a citation
to an entry that is arriving in the next commit and a citation to an entry that never
existed are the same bytes in the same file with the same ledger beside them. Nothing
distinguishes them until the second commit exists, so there is no flag that could be added
to tell them apart — only a promise, from you, that the second commit is coming. `git
commit --no-verify` is that promise. Then let the hook run normally on commit two.

Two things follow. Run `claims-ledger check` yourself before committing the second half:
between the two commits the tree is knowingly inconsistent, and the hook you bypassed is
the only thing that would otherwise tell you when it stopped being. If the promise is not
kept — if commit two never arrives — CI is what catches it, which is why the workflow
checks out the full history and runs `check` on every push; the bypass is local and
one commit deep, and nothing downstream of it is bypassed. And never resolve the refusal
by deleting the citation: the citation is the link the ledger exists to keep, and a commit
that drops it passes the check by removing the thing being checked.

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
evidence and the object id git would store the drifted artifact under as `artifact:`. Exit
1 is correct — it wrote something. Write this verdict with the tool and never by hand:
`artifact:` is machine provenance and is checked as such, and a hand-written propagation
verdict is a person borrowing the authority of a check that did not run.

The entry is now `contested`, so `references` fails every site citing it `cites-as-live`,
by name. That list is how you find the prose to repair.

**2. Re-judge.** This is the step no tool does. Read the Assertion against the artifact as
it now stands:

- **The claim still holds.** Supersede it — step 3. A pin cannot be edited, and that is
  deliberate: a claim re-established on new evidence is a different claim from the one
  established on the old.
- **The claim is no longer true.** Append a `refuted` verdict whose evidence points at
  what shows it false, and rewrite the prose. The citations are removed with the sentence,
  not moved.
- **The artifact moved and the claim did not** — a reformat, a comment, a renumbering, a
  section moved to another path, a rename. Acknowledge it rather than superseding it:
  append a `corroborated` verdict naming the artifact as it now stands, with a note
  recording what moved. The entry keeps its id, its Grounds and its citations. Its
  evidence must name the artifact as it is now rather than restate the ground —
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
`verbatim_sha` **byte-identical** to its predecessor's, the claim never moved and only its
ground did. That is the case where narrowing is the whole of the repair, and often the
case where acknowledging is and no successor is needed at all.

**3. Supersede.** Both directions are checked against each other, and supersession is a
chain, never a tree — an entry carries exactly one `superseded` verdict.

    claims-ledger new <slug>

Copy Assertion, Scope, Warrant and Backing across; re-pin the Grounds to the artifact as
it now stands; declare `supersedes: <old id>` in the successor's frontmatter; append to
the predecessor a verdict whose evidence is `entry: <new id> · supersedes`; move every
citation the reference check named; and run `claims-ledger sha --write` on the successor
**before** it is committed, since `sha --write` refuses an entry that is already in
history.

Then commit the pair as above, and merge without rewriting history.

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

`claims-ledger references` prints what it read; comparing a ground's span against the
claim before committing the entry is the whole of the check, and it takes a minute.

Two more things keep it affordable. Pin sections, never files. And choose the grade
honestly:
`measured` is for a claim that the code *does* something and takes a pin that `freshness`
watches; `asserted` is for a choice the project *made*, forbids an evidence ground, and so
never goes stale. A preference recorded as `measured` buys a supersession every time the
file is reformatted, in exchange for nothing.
