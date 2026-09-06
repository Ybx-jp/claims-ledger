# The freshness checker

A specification, written before the checker existed. Stage 1 is now built; where the
implementation taught the specification something, the specification has been corrected
rather than quietly satisfied, and those corrections are marked **Built:**.

`resolve` asks whether a ground's pointer resolves to the artifact that established the
fact. It asks that of the past: the pin names a commit, and `git show <pin>:<path>` reads
the artifact as it stood there. That question keeps its answer forever. Once an entry
resolves it resolves for good, because the commit it names does not change.

Which means the ledger cannot notice that the world moved. An entry may rest on a test
that has since been deleted, on a module whose behaviour has been inverted, and every
checker stays green — the evidence is still there, at the revision nobody works on any
more. The pin does not merely fail to detect drift; it immunizes the claim against it.

`freshness` asks the other question. Not *did this ground exist* but *is the artifact it
names still the artifact the claim was established on*. It compares the pin to the tree
this run is reading — the working tree, or the index under `--cached` — and it never
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

For each ground pointer whose type is one of the project's evidence types, whose pin is
not in `UNPINNED`, and whose entry's status is not terminal:

1. `git rev-parse --symbolic-full-name <pin>` — non-empty output means **unstable pin**;
   report and stop for this pointer. The question goes to git for *every* pin and not only
   for the ones that look like a sha: `beef` is a legal branch name, an uppercase object id
   is an object id, and the shape of the text settles neither. A pin git says nothing about
   and cannot verify either — `--symbolic-full-name` exits non-zero and `--verify --quiet`
   exits 1 — is a pointer that does not resolve, which is step 2's case. A pin git *fails*
   on rather than answering about is **unknown**, below.
2. `git rev-parse --verify --quiet <pin>:<path>` — the object at the pin. Exit 1 means the
   pointer never resolved, which is `resolve`'s finding and not repeated here.
3. The artifact as this run reads it: the working tree, or the index under `--cached`,
   matching whatever the rest of the run is reading. Absent means **withdrawn**.
4. `git diff --name-only <pin> -- :(literal)<path>`, with `--cached` when the run is
   reading the index. Empty output means fresh, and the checker says nothing.
5. Any output means **moved** — or, for a `§ "<section>"` pointer, the two texts are read
   and only the named section is compared, so an edit elsewhere in the artifact is not this
   ground's drift. Only now, and only for the message, run
   `git rev-list --count <pin>..HEAD -- :(literal)<path>` for the commit count.

**Built — `git diff`, and not the blob identity this specification first described.** An
earlier draft of this section compared `git hash-object <path>` against
`git rev-parse <pin>:<path>`. That is exact about the wrong thing: it compares the bytes on
disk against the bytes in the object store, while a repository's own line-ending and clean
filter handling sits between them, so a checkout under `core.autocrlf` reports every
grounded file as moved. `git diff` applies whatever the repository does to a file on its
way in and out to *both* sides. The observable difference in the other direction is that a
path removed from the index with `git rm --cached` reads as moved though its bytes have not
changed; that is the cost, and it is the smaller one.

**Built — `:(literal)`.** A path reaches `git diff` and `git rev-list` as a *pathspec*,
where `[`, `*` and `?` are wildcards. A ground on `docs/note[1].md` was reported as moved
when an unrelated `docs/note1.md` was edited. Git's matching tries the literal path too, so
this was noise and never a miss, but a checker whose flags fire over files nobody pinned is
the noise floor this document spends a section arguing about.

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

A `moved` flag is discharged in one of three ways, and the machinery for all three
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
      note: propagated from a moved ground

**Let it fall.** A `refuted` or `retracted` verdict written by a person.

The second is the one the checker can help with, so `freshness --write` appends it, and —
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
**records what this run reads the artifact as** — the ordinary pre-commit case, where the
drift is in the working tree or the index and is in no commit for the history question to
find — **or** when the artifact really was what it says it was between the pin and here.
A verdict that is neither does not silence the finding; that is not an accusation, and the
orphan rule below is where a verdict is called a forgery.

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
path produces exactly that: the hook records the staged blob, the author stages one more
edit before committing — `git add -p`, an amend, a formatter — and the next run appends a
second verdict naming what was finally committed. The first records a blob no commit ever
held, and holding each verdict separately made it an orphan the moment the ground came
back: a failure no legal edit could clear. So a ground is an orphan when **no** propagated
verdict against it states a cause that happened. It costs the rule nothing — a forger who
has genuinely drifted the ground and named the blob has made a record a reader can follow,
and a second, emptier verdict beside it buys nothing the first did not already buy.

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
`artifact:` line — the object id git would store the artifact under at the moment the drift
was seen, or `absent` for a ground that had been withdrawn — and the orphan test asks
whether the artifact really was that between the pin and here: a blob the path has actually
held, or a commit that really deleted it. A blob is the right grain rather than a commit
because the ordinary case is a drift that is in the working tree and not committed at all,
which is what a pre-commit hook is for.

A verdict that records nothing is an orphan, and so is one recording the artifact as the pin
itself has it, which states no drift. This does not make the discharge unforgeable — the
ledger is text a person writes, and a forger who genuinely drifts the artifact in a commit
and names that blob has made a record a reader can follow.

**Three things it does not yet reach, and the first is the largest.** An adversarial review
of this rule measured them; they are stated here rather than left for a reader to discover,
because a specification that overstates its own guarantee is the defect this package exists
to refuse.

- ~~**The `artifact:` line is not consulted while the drift is live.**~~ Closed. It is
  consulted twice now: `validate` holds every verdict's `artifact:` to a shape in every
  state, before git is asked anything, and the suppression rule above requires the verdict
  to describe the drift in front of the run. A propagated verdict carrying a value the
  artifact has never been no longer silences a live drift, and one carrying no value at all
  no longer parses as legal.
- **`caused()` has no section awareness.** For a `§ "<section>"` ground it asks whether the
  *file* ever held the recorded blob, so one ordinary commit editing a different section of
  the same file supplies a blob a discharge can name, with the pinned section untouched.
- **`absent` is checked against the file, not against the verdict.** A ground deleted and
  restored in two commits satisfies it, which is a touch-and-revert.
- **A verdict that records what the run would have recorded is a discharge, whoever wrote
  it.** `git hash-object --path <file> -- <file>` is one command, and a hand-written
  verdict carrying its output holds a live drift at exit 0 across all five checkers. This
  is inherent rather than a defect: without signing, no rule can separate "the tool wrote
  this" from "a person wrote what the tool would have written", and *describing the drift*
  is exactly what an honest discharge does. It is stated here because the rule above is
  easy to read as an anti-forgery property, and it is not one — it is a rule about whether
  the record is *true*, not about who made it.

So the accidental forgery is narrowed rather than removed: the object-id case needs a
deliberate `git rev-parse`, and the two above do not. Both remaining residuals require an
author with commit access deliberately writing a verdict in the machine's name, and both
are stated here rather than left for a reader to find.

**A git that cannot answer is not a git answering no.** The history question can fail — a
corrupt pack, a clean filter that exits non-zero, the per-call timeout. When it does, the
run reports that whether the drift happened *could not be established* and exits non-zero.
It does not decide either way: reading the silence as "it drifted" retires the rule without
saying so, and reading it as "it did not" forges an accusation against a correctly
discharged verdict.

## What is exempt, and why

**Fallen entries.** An entry that is refuted, superseded, retracted or non-comparable is
history. Its Grounds record what it was established on, not what anyone should now
believe, and `references` already exempts fallen entries for the same reason.

**Verdict evidence.** A verdict is a dated act — *on this evidence, on this day, I judged
it so*. Its evidence pointer is frozen by construction. Only Grounds are checked.

**`entry:`, `source:`, `search:`, `defect:` pointers.** An `entry:` ground going stale is
`propagate`'s subject. A `source:` ground is registered bytes with a sha, and `resolve`
already fails if those bytes stop hashing to the registry row. `search:` and `defect:`
name no artifact.

**Unpinned pointers.** `@working` and `@corpus`, as above.

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

Known-good seeds:

| seed | what it holds | expected |
|---|---|---|
| `K19-unrelated-commit-is-not-drift` | `commits/02` edits a file no entry pins | all checkers pass |
| `K20-drift-acknowledged` | `commits/02` edits the artifact *and* appends the propagation verdict; the citing document is moved to `cites-as-contested` in the same commit | all checkers pass |
| `K21-fallen-entry-may-drift` | the entry is refuted; `commits/02` edits its artifact | all checkers pass |
| `K22-unpinned-is-not-drift` | the pointer is `@working`; `commits/02` edits the artifact | all checkers pass |
| `K23-edit-outside-the-section-is-not-drift` | `commits/02` edits a section the pointer does not name | all checkers pass |

`K19` is the load-bearing known-negative: without it, a checker that reported every entry
on every commit would pass every defect seed above.

`K22` is the seed that documents why the other 62 stay green, so that a later reader who
changes `UNPINNED` finds out what it costs.

**Built — each seed was falsified rather than assumed.** Every rule was removed from the
checker in turn and the corpus re-run: dropping the fallen-entry exemption fails `K21`
alone; reporting every pinned ground fails `K19` and `D48`; dropping the orphan check
fails `D48`; dropping the acknowledgement fails `K20`; dropping the unstable-pin rule
fails `D47`; and dropping the `UNPINNED` skip fails 43 seeds, `K22` among them. A seed
that survives its own rule being deleted is not proving anything, and none of these do.

## Cost

Two `git rev-parse` calls per checked pointer, both plumbing, both O(1) against the object
store; one `git diff --name-only` per pointer, limited to one pathspec; one `git show` per
*sectioned* pointer that has drifted, to read the two texts; and one `git rev-list --count`
per drifted pointer, for the message only. The existing
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
- **Whether the discharge should expire.** Nothing here re-flags a claim whose ground
  moved a *second* time after being contested. The suppression rule does now read the
  `artifact:` line — but it accepts a verdict whose record the artifact really held
  between the pin and here, and a first drift that was committed satisfies that forever.
  So the discharge covers every later version of the ground as well as the one it judged.
  The question can be asked — is the artifact still the version this discharge judged? —
  and asking it would mean deciding what a project does about a discharge that has aged
  out, which is a policy this has no experience to choose from.
