# The freshness checker

A specification, written before the checker existed. Stage 1 is now built; where the
implementation taught the specification something, the specification has been corrected
rather than quietly satisfied, and those corrections are marked **Built:**.

`resolve` asks whether a ground's pointer resolves to the artifact that established the
fact. It asks that of the past: the anchor names a datum — the section as it stood at a
commit, or the section whose text digests to this — and `resolve` reads that text out of
the commit, or out of whatever version of the path the repository still holds. That
question keeps its answer forever. Once an entry resolves it resolves for good, because
the datum its anchor names does not change.

Which means the ledger cannot notice that the world moved. An entry may rest on a test
that has since been deleted, on a module whose behaviour has been inverted, and every
checker stays green — the evidence is still there, at the revision nobody works on any
more. The pin does not merely fail to detect drift; it immunizes the claim against it.

`freshness` asks the other question. Not *did this ground exist* but *is the artifact it
names still the artifact the claim was established on*. It compares the anchor to the
tree this run is reading — the working tree, or the index under `--cached` — and it never
judges whether the difference matters.

## What it refuses to do

The checker does not decide whether a change to an artifact undermines the claim resting
on it. It cannot: that is the warrant's job, and the warrant is prose a person or an
agent reads. A file may be reformatted, a comment may be rewritten, a function may be
renamed, and none of that touches the claim; or one character may invert it. The checker
reports that the ground moved and stops.

This is the same division the rest of the package keeps. `resolve` reports that a quote
is not in the source; it does not report that the quote is misleading. `propagate`
reports that a dependent has not been flagged; it does not decide whether the dependent
survives. Deterministic detection, human judgment.

## Why a fifth checker

`resolve` could carry this. It should not.

The two ask questions about different times, and a checker that answers one clean
question is a checker whose output a reader can act on. `resolve`'s reports all mean *this
entry does not hold together* and all fail. Freshness findings mostly mean *look at this*
and mostly do not fail. Mixing them would make `resolve` a checker whose exit code no
longer means one thing.

The corpus contract also names the checker in every expectation row, and a seed that
distinguishes "the pointer is broken" from "the pointer is stale" is a seed a later
reader can understand.

So: a fifth name in `CHECKERS`, a fifth line under `claims-ledger check`, a
`claims-ledger freshness` subcommand.

## The findings

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/freshness-dark.svg">
  <img alt="A git timeline from the pinned commit to the working tree, with the entry's ground anchored at the pin and the comparison drawn to the tree this run reads; below it the findings: fresh is silent, moved is a flag, withdrawn is a failure, an unstable pin is a flag, and unknown is a failure that no verdict discharges." src="figures/freshness.svg" width="960">
</picture>

### withdrawn — fail

The path does not exist in the tree being checked. The ground is not merely older than
the claim, it is gone. Nothing a person could look at survives to be judged.

    FAIL A0001 Grounds 3: `test: tests/test_legacy_clients.py @ed46323` is not in the
    working tree; the ground it names is gone (1 commit has touched the artifact since
    the pin)

**Built — the count is of commits that touched the artifact, not of withdrawals.**
`rev-list --count` counts the first; this specification's earlier wording claimed the
second, which the same call cannot answer. Under `--cached` the sentence says `is not in
the index`, because that is what was read.

### moved — flag

The path exists and its bytes differ from the bytes at the pin.

    FLAG A0001 Grounds 1: `code: src/serializers/v2.py @ed46323` has moved: 1 commit has
    touched it since the pin

For a `§ "<section>"` pointer the message names the section rather than the file, because
that is what was compared.

### unstable pin — flag

The pin is a symbolic ref — a branch or a tag — rather than a commit. Such a pointer
resolves forever and can never drift, because the name follows the work. It is a hole in
the ledger's own guarantee, and the checker says so once.

    FLAG A0001 Grounds 2: `code: src/api/foo.py @main` is pinned to a name, not a
    commit; a pin that follows the work resolves forever and can never go stale

**Built — a name, not a branch.** An annotated tag is a name that follows the work in
exactly the same way, and this specification's earlier wording named only branches.

`@working` and `@corpus` are not this defect. They are the declared unpinned forms, they
already say in the schema that they are only as reproducible as the tree they were read
in, and freshness skips them in silence.

### unknown — fail

Git declining to answer a question the checker asked: a required clean filter that exits
non-zero, a pack the reader can no longer open, an object removed from under a revision
that names it, a pin `rev-parse` fails on rather than answers about. `git_problem()` is
asked once before the run and clears a git that cannot work at all; these are the failures
it cannot see, because `rev-parse --git-dir` goes on succeeding through them.

    FAIL A0001 Grounds 1: `lab: docs/note-100.md § "Observation" @HEAD@{99}` was not
    checked: git could not say whether `HEAD@{99}` is a commit or a name: fatal: log for
    'HEAD' only has 1 entries

The comparison did not happen, and a comparison that did not happen is never a fresh
ground. This one is a `fail` and is not discharged by a verdict: a verdict discharges a
drift that was established, and nothing here was established.

## The comparison, exactly

For each ground pointer whose type is one of the project's evidence types, whose anchor
is not in `UNPINNED` and not the `=?` placeholder, and whose entry's status is not
terminal — compared from the pointer of its latest reading where one exists, and from
the Ground itself otherwise:

1. The digest the anchor names. Stated by value, it is the anchor itself, and git is not
   asked. Stated by reference, `git rev-parse --symbolic-full-name <pin>` first —
   non-empty output means **unstable pin**; report and stop for this pointer. The question
   goes to git for *every* pin and not only for the ones that look like a sha: `beef` is
   a legal branch name, an uppercase object id is an object id, and the shape of the text
   settles neither. A pin git says nothing about and cannot verify either —
   `--symbolic-full-name` exits non-zero and `--verify --quiet` exits 1 — is a pointer
   that does not resolve, which is `resolve`'s finding and not repeated here. A pin git
   *fails* on rather than answering about is **unknown**, below. Then the section is read
   out of `<pin>:<path>`, every pinned blob of the run through one `cat-file --batch`,
   and digested exactly as this run's side is about to be.
2. The artifact as this run reads it: the working tree, or the index under `--cached`,
   matching whatever the rest of the run is reading. Absent means **withdrawn**. Bytes
   that cannot be reached at all mean **unknown**: a comparison nobody could make is never
   a finding about the claim. Bytes that are *there* and are not UTF-8 stay **moved**:
   that artifact did change, and it simply cannot be narrowed to a section.
3. For a `§ "<section>"` pointer the named section is found in that text and the section
   alone is digested, so an edit elsewhere in the artifact is not this ground's drift; a
   section no longer in a file that remains is **withdrawn**. A plain pointer digests the
   whole decoded text.
4. Equal digests mean fresh, and the checker says nothing. Different means **moved**
   (L0200-a-ground-is-compared-by-the-digest-of-its-section-on-both-sides, cites-as-live).
   Only now, only for the message, and only for an anchor stated by reference, run
   `git rev-list --count <pin>..HEAD -- :(literal)<path>` for the commit count; an anchor
   stated by value names no commit to count from.

**Built, and rebuilt — the digest of the section on both sides, and neither the blob
identity this specification first described nor the `git diff` that replaced it.** The
first draft compared `git hash-object <path>` against `git rev-parse <pin>:<path>`. That is
exact about the wrong thing: it compares the bytes on disk against the bytes in the object
store, while a repository's own line-ending handling sits between them, so a checkout
under `core.autocrlf` reported every grounded file as moved. `git diff --name-only` was
built in its place, applying whatever the repository does to a file on its way in and out
to *both* sides, at the cost of a file-grained answer a sectioned pointer then had to
narrow by reading both texts anyway. What stands now is the narrowing alone: both sides
are decoded the same way — UTF-8, universal newlines, the section through the type's
pattern, trailing whitespace stripped — and digested, and the digest is what an anchor
stated by value names, so one comparison serves both forms and the `git diff` path is
gone rather than kept beside it. Line endings are handled by the decode. A clean filter
that rewrites more than line endings — `ident`, a large-file pointer — puts different
text on the two sides and such an artifact reads as moved; it is outside what a ground
by value can name, and no ground in this ledger names one.

**Built — `:(literal)`.** A path reaches `git rev-list` as a *pathspec*, where `[`, `*`
and `?` are wildcards. Under the `git diff` comparison a ground on `docs/note[1].md` was
reported as moved when an unrelated `docs/note1.md` was edited. Git's matching tries the
literal path too, so this was noise and never a miss, but a checker whose flags fire over
files nobody pinned is the noise floor this document spends a section arguing about.

Comparing against the working tree rather than `HEAD` is deliberate. The intended home
for this is a pre-commit hook, where `HEAD` is still the commit *before* the change being
made; a HEAD comparison would miss the very edit being committed and surface it one
commit late, against a diff the author has already stopped thinking about.

## Why moved flags and withdrawn fails

A flag that everyone learns to scroll past is the disease this package exists to treat,
so the asymmetry needs a reason.

The reason is measured, not assumed. In the demonstration ledger built for this spec, the
grounded file `src/api/foo.py` drifted between the pin and HEAD because **a comment
inside it changed** — the prose note was replaced by the citation that points at the
claim. That is a true drift by blob identity and a meaningless one by every other
measure. In a repository whose grounded artifacts are the files people edit daily, `moved`
will fire constantly and most firings will be noise. A checker that fails on it makes
every commit that touches a grounded file impossible until someone writes a verdict, and
a checker that does that gets switched off.

`withdrawn` has no such noise floor. A file that is gone is gone.

## How a finding is discharged, and what the schema already forces

This section argues *why* the discharge is shaped as it is. `docs/OPERATING.md` gives the
same ground as a sequence to follow, along with the two findings here that are not drift
and must never be given a verdict.

A `moved` flag is discharged in one of four ways, and the machinery for all four
already exists.

**Re-establish the claim on the new artifact.** Note what this costs: Grounds sit above
the `APPEND BELOW THIS LINE ONLY` marker and the frozen-region check holds them immutable
once git has the entry. **The pin cannot be edited in place.** Re-pinning is therefore
supersession — a new entry, grounded in the artifact as it now stands, with the old one
carrying `superseded`. That is the right answer and the schema arrived at it first: "the
claim was re-established on new evidence" is a different claim from the one established
on the old evidence, and the ledger should be able to tell them apart.

**Contest it.** A `contested` verdict by the propagation author, naming the drifted
pointer, exactly as `propagate` writes one naming a fallen entry:

    - 2026-11-20T09:00:00-08:00 · contested · grade: argued · author: propagation
      evidence: code: src/serializers/v2.py @ed46323
      artifact: sha256:9c2f…(64 hex)
      note: propagated from a moved ground

**Acknowledge that the claim is untouched.** Where the artifact moved and the Assertion
did not — a renumbering, a reformat, a section moved within a file or to another path, a
rename — append a `corroborated` verdict naming the artifact as it now stands, with a note
recording what moved:

    - 2026-11-21T10:15:00-08:00 · corroborated · grade: measured · author: main
      evidence: code: src/serializers/v2.py § "encode" =sha256:3e1c…(64 hex)
      note: the section moved with the module split; the assertion is unaffected

The evidence is written `=?` and `claims-ledger sha --write` fills it with the digest of
the section as the tree has it; it sits below the marker, so the write touches nothing
frozen. A reading stated by value needs no commit to be placed at, and so can be
appended in the same commit as the edit it read
(L0204-a-reading-anchored-by-value-needs-no-place-in-history, cites-as-live); one stated
`@<commit>` is still accepted, and has to sit in this history, after the pin.

`contested` is not terminal, so the status walks past it to the corroborated verdict and
citations reading `cites-as-live` stay legal. The entry keeps its id, its Grounds and its
citations, and no successor is written.

What makes this a record rather than a restatement is a rule `validate` already enforces:
a corroborating verdict may not point at a ground the entry already cites. Its evidence
has to name the artifact as it is now, which is exactly the reading that was done. An
entry discharged this way carries, in order, what the machinery saw and what a person
found when they went and looked.

Note what the reading then becomes. A discharge is against the drift in front of it, and
once the contested verdict is in history that drift is recorded for good — the pin is
frozen, and the range between it and here only grows. So the corroborating verdict is
where the ground is compared from afterwards: its evidence names the section, by value or
at a commit, and `freshness` treats the latest such verdict as the point the ground was
last read from, silent while nothing has changed since and reporting the next change as news since
that reading. Before this, an entry returned to a live status carried a ground that
would never speak again; measured on this package's own ledger, 93 of 270 live grounds
were in that state and 49 of them had moved again unnoticed. Acknowledge when the
reading actually happened; a corroborating verdict is the one place the ledger's accuracy
rests on a person having looked, and no checker can check that — and now it is also the
place the next check starts from. Only a corroboration moves it. An entry left `contested`
after `--write`, with no reading appended, is compared from wherever it was last read and
its recorded drift discharges it there as before; that is the shape the third outcome
below produces, and a ground in it is silent until someone reads it. A reading stated by
reference also has to sit in this history, between the pin and here — a corroboration at
a commit on no branch, or older than the pin, is passed over — and one stated by value
has no such question to answer.

**Let it fall.** A `refuted` or `retracted` verdict written by a person.

The contested verdict is the one the checker can help with, so `freshness --write` appends
it, and —
following `propagate` — the run still exits non-zero afterwards so the appended text is
looked at before it is committed. A pointer whose entry already carries such a verdict
naming it, **including its `§ "<section>"`**, and whose verdict **describes the drift in
front of the run**, is discharged and the checker is silent; a verdict naming one section
of a file does not discharge a drift in another.

**Built — a pointer says which drift a verdict is about, and is not evidence that it is
about this one.** Matching a verdict to a ground by the pointer alone was the whole of the
suppression rule, and it left the `artifact:` line below unreachable in the state a
discharge normally lives in: with the drift live, the orphan rule does not ask, so nothing
read the value at all and a propagated verdict carrying forty zeros, a value the artifact
has never been, or no `artifact:` line at all held a real, committed, ongoing drift at exit
0 with every checker silent. A verdict discharges the drift in front of it when it
**records what this run reads the artifact as** — the digest of the section as this run
sees it, which is the ordinary pre-commit case, where the drift is in the working tree or
the index. A second clause, that the artifact really was what the verdict says between
the pin and here, was built and is deleted (below): a comparison by digest asks history
nothing, and a record that is not what this run sees does not silence the finding. That
is not an accusation, and the orphan rule below is where a verdict is called a forgery.

**Built — the non-zero exit had to be made true.** `propagate` gets it for free, because
every block it queues sits beside a failure. Freshness queues the `moved` case beside a
flag, so the run appended verdicts to entry files and exited 0, and the appended text went
into a commit unlooked-at. The `appended N contested verdict(s)` report is a `fail`: not
because a claim is wrong, but because a file in the ledger was just changed by machinery.

And then the enforcement cascades through machinery that is already built. A contested
entry cannot be cited `cites-as-live`; `references` fails every document and every source
file that still does. In the demonstration ledger this was verified: a `# (A0001-…,
cites-as-live)` comment inside a Python function became a hard failure the moment the
entry stopped being live. Freshness does not need failure semantics of its own. It needs
only to make the status move, and the existing checkers turn a moved status into a broken
build at the citation site.

**Orphans.** As with `propagate`, a propagation-authored contested verdict naming a
pointer that has *not* drifted is an orphan and fails. Otherwise the discharge is
forgeable by writing the verdict pre-emptively.

**Built — the question is asked of the ground, not of each verdict.** An entry may
legitimately carry more than one propagated verdict against one ground, and the pre-commit
path produces exactly that: the hook records the staged section's digest, the author
stages one more edit before committing — `git add -p`, an amend, a formatter — and the
next run appends a second verdict naming what was finally committed. The first records a
digest no commit ever held, and holding each verdict separately made it an orphan the
moment the ground came back: a failure no legal edit could clear. So the question is
asked of the ground, across every propagated verdict it carries, and not of each verdict
alone.

**Built — "has not drifted" is not the same question as "was never drifted".** Asked as
the first, the rule wedged the ledger: undo the edit that caused a discharge and the
checker called its own verdict an orphan, permanently, with no legal way out — verdicts
append and only append, so the verdict cannot be removed, and the pin sits above the APPEND
marker, so it cannot be changed.

**Built — and the question the fix first asked was one the forger controls.** The wedge was
closed by also asking whether any commit between the pin and HEAD had touched the artifact
at all, and treating a yes as proof that the verdict was caused. That is not the question
the rule needs answered. *Touched* is not *drifted*: one commit that edits the artifact and
one that puts it back — or a `chmod +x`, or a rename away and back — answers yes while the
artifact stays byte-identical to the blob at the pin, and a discharge written pre-emptively
is then accepted permanently. The rule traded a loud false positive for a silent false
negative, which is the trade this package exists to refuse.

So the verdict states its cause, and is held to what it states. `--write` records an
`artifact:` line — the digest of the section as this run read it at the moment the drift
was seen, or `absent` for a ground that had been withdrawn.

**Built — and then the history question was deleted.** The test that followed asked
whether the artifact really was that between the pin and here — a blob the path had
actually held — and it was the question the forger controlled from the other side: a
commit that drifts the artifact and one that puts it back launders any record into
history. Measured on this package's own ledger before the change, of 114 propagated
verdicts every one was caused and none sat on a fresh current pointer, so the walk was
deciding nothing. What stands asks history nothing. A record that equals the digest its
own pointer's anchor names states no drift at all and is **refuted** — a failure — on any
pointer, whether or not the comparison has since moved past it, so a real drift and a
later reading cannot carry the accusation away. A record on a ground that is fresh where
it is compared from, naming something this run does not see, is **unconfirmable** — a
flag — because that is exactly what an ordinary drift that was never committed or was
undone looks like, and failing it left a permanent red no legal edit could clear
(L0203-a-record-is-refuted-against-its-anchor-and-confirmed-against-the-tree, cites-as-live).
A verdict that records nothing does not parse. None of this makes the discharge
unforgeable — the ledger is text a person writes, and a forger who genuinely drifts the
artifact and names its digest has made a record a reader can follow.

**What it does not reach.** An adversarial review of this rule measured these; they are
stated here rather than left for a reader to discover, because a specification that
overstates its own guarantee is the defect this package exists to refuse.

- ~~**The `artifact:` line is not consulted while the drift is live.**~~ Closed. It is
  consulted twice now: `validate` holds every verdict's `artifact:` to a shape in every
  state, before git is asked anything, and the suppression rule above requires the verdict
  to describe the drift in front of the run. A propagated verdict carrying a value the
  artifact has never been no longer silences a live drift, and one carrying no value at all
  no longer parses as legal.
- ~~**`caused()` has no section awareness.**~~ Closed by deletion: there is no `caused()`,
  and the record is a section's digest, so a commit to another section of the file
  supplies nothing a discharge can name.
- **`absent` is checked against the file, not against the verdict.** A ground deleted and
  restored in two commits satisfies it, which is a touch-and-revert.
- **A verdict that records what the run would have recorded is a discharge, whoever wrote
  it.** The digest of a section is one function call, and a hand-written verdict carrying
  it holds a live drift at exit 0 across all five checkers. This
  is inherent rather than a defect: without signing, no rule can separate "the tool wrote
  this" from "a person wrote what the tool would have written", and *describing the drift*
  is exactly what an honest discharge does. It is stated here because the rule above is
  easy to read as an anti-forgery property, and it is not one — it is a rule about whether
  the record is *true*, not about who made it.

So the accidental forgery is narrowed rather than removed: a record equal to the anchor
is refuted outright, and the two above are not. Both remaining residuals require an
author with commit access deliberately writing a verdict in the machine's name, and both
are stated here rather than left for a reader to find.

**A git that cannot answer is not a git answering no.** Reading the anchor's section out
of the commit a by-reference pointer names can fail — a corrupt pack, the per-call
timeout — and so can reading this run's side of the comparison. When either does, the
run reports that the ground *was not checked*, names why, and exits non-zero. It does not
decide either way: reading the silence as "it drifted" retires the rule without saying
so, and reading it as "it did not" forges an accusation against a correctly discharged
verdict. A comparison that could not be made is never discharged by a verdict, since
nothing was established for the verdict to describe.

## What is exempt, and why

**Terminal entries.** An entry that is refuted, superseded, retracted or non-comparable is
history. Its Grounds record what it was established on, not what anyone should now
believe, and `references` and `propagate` draw the same line at the same place, for the
same reason: no verdict may follow a terminal status, and the Grounds are frozen, so
there is nothing a report against one could ask anybody to repair.

**Verdict evidence.** A verdict is a dated act — *on this evidence, on this day, I judged
it so*. Its evidence pointer is frozen by construction, and it is not checked for drift
as a ground would be. One kind is read for another purpose: a `corroborated` verdict
naming the same section as a Ground, by value or at a commit, is where that Ground was
last read, and the Ground is compared from there rather than from its anchor.

**`entry:`, `source:`, `search:`, `defect:` pointers.** An `entry:` ground going stale is
`propagate`'s subject. A `source:` ground is registered bytes with a sha, and `resolve`
already fails if those bytes stop hashing to the registry row. `search:` and `defect:`
name no artifact.

**Unpinned pointers.** `@working` and `@corpus`, as above. And a pointer whose anchor is
still `=?`: it names no datum yet, `validate` refuses it, and there is nothing to compare.

## The proof obligation

The corpus contract requires the seeds before the checker, a defect seed for every rule
and a known-good seed for every rule, and every checker not named in a non-pass row to
exit clean on every seed.

Two facts make this tractable. First, **all 82 evidence pins across the 62 existing seeds
are `@corpus`**, which freshness skips — so no existing `expected.json` moves, and adding
the checker is not a methodology change to any seed already committed. Verified: with the
fifth checker in `CHECKERS`, all 62 pass untouched. Second, drift is a property of history
and not of a file, exactly like the immutability the corpus already tests, so its seeds
are `commits/` seeds.

**Built — the runner needed one addition, and this specification was wrong to say it did
not.** A seed cannot write a pin, because the commit it would name does not exist until
the runner makes it. So a history seed writes `@commit01` and the runner substitutes that
state's real short object id before the state is committed. What git records is what the
checkers read, so the entry's frozen region is stable across every later state exactly as
a hand-written pin is. This is documented in `corpus/README.md` alongside the rest of the
seed format.

Defect seeds:

| seed | what it holds | expected |
|---|---|---|
| `D45-ground-moved-unacknowledged` | `commits/02` edits the pinned artifact | `freshness` **flag** at `commit 02, A0001 Grounds 1` |
| `D46-ground-withdrawn` | `commits/02` deletes the pinned artifact | `freshness` **fail** at `commit 02, A0001 Grounds 1` |
| `D47-pin-is-a-name-not-a-commit` | pin written `@HEAD` | `freshness` **flag** at `commit 02, A0001 Grounds 1` |
| `D48-orphan-freshness-verdict` | propagation contested verdict naming a ground that has not moved, recording no artifact it was seen at | `freshness` **fail** at `commit 02, A0001 Verdicts` |
| `D49-section-withdrawn-from-a-file-that-remains` | `commits/02` removes the pinned section; the file stays | `freshness` **fail** at `commit 02, A0001 Grounds 1` |
| `D51-pin-git-cannot-classify` | the pin is `@HEAD@{99}` in a repository with one commit, so `rev-parse` fails rather than answering | `freshness` **fail** at `commit 01, A0001 Grounds 1`, and `resolve` **fail** at `commit 01, A0001 Grounds` |
| `D53-laundered-freshness-discharge` | a propagated verdict recording the digest its own anchor names, on a ground later drifted for real | `freshness` **fail** at `commit 03, A0001 Verdicts` |
| `D62-anchor-left-pending` | a ground written `=?` and never filled | `validate` **fail** at `A0001 Grounds 1` |
| `D63-by-value-anchor-does-not-match-the-tree` | an uncommitted entry whose by-value anchor is not the digest of the section as the tree has it | `resolve` **fail** and `freshness` **flag** at `A0001 Grounds 1` |
| `D64-by-value-anchor-no-version-holds` | a committed entry whose by-value anchor digests to text no version of the path holds — the end state a rewritten history leaves | `resolve` **flag** and `freshness` **flag** at `commit 01, A0001 Grounds 1` |
| `D65-by-value-ground-moved-unacknowledged` | D45 by value: `commits/02` edits the section a by-value ground names | `freshness` **flag** at `commit 02, A0001 Grounds 1` |

Known-good seeds:

| seed | what it holds | expected |
|---|---|---|
| `K19-unrelated-commit-is-not-drift` | `commits/02` edits a file no entry pins | all checkers pass |
| `K20-drift-acknowledged` | `commits/02` edits the artifact *and* appends the propagation verdict; the citing document is moved to `cites-as-contested` in the same commit | all checkers pass |
| `K21-fallen-entry-may-drift` | the entry is refuted; `commits/02` edits its artifact | all checkers pass |
| `K22-unpinned-is-not-drift` | the pointer is `@working`; `commits/02` edits the artifact | all checkers pass |
| `K23-edit-outside-the-section-is-not-drift` | `commits/02` edits a section the pointer does not name | all checkers pass |
| `K30-ground-anchored-by-value` | the anchor is the digest of the section as the note holds it | all checkers pass |

`K19` is the load-bearing known-negative: without it, a checker that reported every entry
on every commit would pass every defect seed above.

`K22` is the seed that documents why the other 62 stay green, so that a later reader who
changes `UNPINNED` finds out what it costs.

`K30` is the first drift seed that can be read without running the runner: its anchor is
the digest of the section text itself, so no `@commitNN` substitution stands between what
the seed says and what git records. `D64` is written as the end state a rewrite leaves,
directly, because a seed can only build linear, append-only history and cannot make a
commit unreachable.

**Built — each seed was falsified rather than assumed.** Every rule was removed from the
checker in turn and the corpus re-run: dropping the fallen-entry exemption fails `K21`
alone; reporting every pinned ground fails `K19` and `D48`; dropping the orphan check
fails `D48`; dropping the acknowledgement fails `K20`; dropping the unstable-pin rule
fails `D47`; and dropping the `UNPINNED` skip fails 43 seeds, `K22` among them. A seed
that survives its own rule being deleted is not proving anything, and none of these do.

## Cost

No history walk. For an anchor stated by reference, one `git rev-parse
--symbolic-full-name` per checked pointer and one `cat-file --batch` for the run, reading
every pinned blob once; for an anchor stated by value, nothing from git at all — a
working-tree run over 271 grounds measured at 0.134 s before the by-reference reads were
counted. Under `--cached` this run's side is read out of the index through git, one
`show :<path>` per distinct path. One `git rev-list --count` per drifted by-reference
pointer, for the message only. The existing
`GIT_TIMEOUT` and the `git_problem()` reporting apply unchanged — a checker that cannot
run must say it did not run, rather than passing quietly, which is the failure mode
`git_problem()` was written for.

## Staging

**Stage 1 is everything above**, and it needs no configuration key. Evidence types are
already project-declared, `code:`/`test:` already parse, and the comparison is pure git.

**Built — it did need one schema change, which this specification did not foresee.**
`validate` held a propagation-authored verdict to `entry:` evidence with `· fallen` or
`· challenges`, since those were the only things the machinery wrote. Freshness writes a
third: a `contested` verdict naming a pinned evidence ground. The rule is widened to admit
exactly that shape and no more, so a person still cannot write under the machine's name.

**Built — three smaller things the implementation turned up.** `UNPINNED` moved from
`resolve` to `schema`, because `validate` now needs it too. `resolve`'s `git show
<pin>:<path>` and freshness's working-tree read both go to `ledger.repo` rather than
`ledger.tree`: `git show` resolves a path from the repository root, and the two are the
same directory in a real project but not in a corpus history seed. And `propagate` had a
latent bug that freshness would have inherited — two verdicts destined for one entry were
two writes from the same in-memory text, so the second silently overwrote the first. Both
now group by entry and write once.

**Stage 2 is section scoping**, and it is the answer to the noise floor. Before it,
`§ "<section>"` matched a Markdown heading and nothing else — `resolve` looked for
`^#+\s*<name>\s*$` — so a pointer at a Python function could not be written at all, and
the drift comparison called every edit anywhere in an artifact a moved ground.

**Built.** A sectioned evidence type may carry a pattern:

    evidence-sectioned = ["lab", "code"]

    [tool.claims-ledger.section-patterns]
    code = '^(?:def|class) +{name}'

`resolve` and `freshness` read a section through the same pattern, so an entry cannot
resolve against one span and be compared against another. Omitted, a type gets the
Markdown heading `§` has always meant, which is why no existing ledger changes.

Three things this differs from the sketch above, each for a reason:

- **One `section-patterns` table, not a restructuring of `evidence` into an array of
  tables.** The sketch was prettier and would have rewritten how every evidence type is
  declared. This is additive: a project that writes no patterns is unaffected, and the
  key can grow a sibling later if a section needs its own terminator.
- **`{name}` is replaced, not formatted.** `str.format` would choke on `^#{1,3}` — regex
  quantifiers are braces too — so the slot is a literal substring replacement and every
  other brace in the pattern is left alone.
- **The pattern decides both ends.** A section runs from its own header to the next match
  of the same pattern with the name slot widened to some other name, or to the end of the
  artifact. That needs no second configuration value, and it works for both the Markdown
  default and a column-anchored code pattern.

**The anchoring caveat is real and is documented rather than defended.** A pattern
written as `^\s*(?:def|class)\s+{name}` — allowing leading whitespace, which is the
obvious thing to write — ends a function at its first *nested* definition and leaves the
rest of it uncompared. That is a silent miss, the worst kind for this package. The
configuration comment, `SCHEMA.md` and `section_span`'s own docstring all say to anchor
at the granularity the section really has. A checker cannot detect the mistake, because
a pattern that matches less is indistinguishable from a section that is genuinely shorter.

**Built — and the shipped default could not take that advice.** `^#+\s*{name}\s*$`
matches a heading at *every* depth, so `## Observation` ended at the first `### …` beneath
it and everything under that subheading was outside the comparison — for `resolve` as well
as for `freshness`. A claim's own evidence could be inverted under a subheading with every
checker green, and no anchoring was available to a project that had configured nothing,
because `#+` *is* every depth. So a pattern that can nest now says so, with a group named
`depth`:

    DEFAULT_SECTION_PATTERN = r"^(?P<depth>#+)\s*{name}\s*$"

A match whose `depth` is longer than the header's is a subsection of it rather than the
start of the next section. A pattern without the group behaves exactly as before — every
match ends the section — which is what a flat pattern wants. This is the sibling key the
paragraph above anticipated, arriving as a group in the pattern rather than as a second
value.

**Two things found by running it, not by reading it.** Pointed at the demonstration
repository with a pattern for Python definitions, appending a *new* function to a file
reported the function before it as moved: the last section of an artifact runs to the end
of it, so an appended section lengthened its predecessor by the blank lines between them.
Trailing whitespace is the gap between sections and not part of either, and is stripped
before the comparison. And a drifted ground in an uncommitted working tree said `0
commits have touched it`, which of a file the author is editing right now reads as a
checker that has lost track of its own subject; the zero case now says so plainly. Both
have regressions.

**What the corpus cannot prove here.** A seed is checked under `corpus_config()`, which
is one fixed configuration for every seed; a seed cannot declare a pattern of its own. So
the corpus proves section scoping under the default Markdown pattern — `D49` (a section
gone from a file that remains) and `K23` (an edit outside the section) — and the custom
pattern, the Python-definition case, is proven in `tests/test_section_scoping.py` against
a real project and a real repository. Making seeds configurable is the honest fix and is
not worth its cost yet; this paragraph exists so that the gap is a recorded decision
rather than something a later reader has to notice.

## What this spec is not sure about

- **Whether `moved` should be able to fail.** A `freshness-outcome` configuration key, or
  a `--strict` flag, would let a project that wants the harder guarantee take it. Left out
  of Stage 1 deliberately: a knob added before anyone has lived with the default is a
  guess about which default is wrong.
- **Whether an unstable pin should fail rather than flag.** It defeats the mechanism
  entirely, which argues for failing. But it may be the only workable pin for a project
  whose evidence lives on a moving branch, and failing would make that project's ledger
  uncheckable rather than merely weaker.
- ~~**Whether the discharge should expire.**~~ Answered, twice over. A ground is compared
  from its latest reading rather than from its anchor, so a second move after an
  acknowledgement is news; and a discharge holds only against what this run sees, so a
  first drift that was committed no longer satisfies it forever. What is not answered is
  what a project does with a ground nobody has re-read for a long time while it stayed
  fresh — nothing here ages a reading, and there is no experience yet to say whether
  anything should.
