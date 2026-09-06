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
names still the artifact the claim was established on*. It compares the pin to the
working tree, and it never judges whether the difference matters.

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

## The three findings

### withdrawn — fail

The path does not exist in the tree being checked. The ground is not merely older than
the claim, it is gone. Nothing a person could look at survives to be judged.

    FAIL A0001 Grounds 3: test: tests/test_legacy_clients.py @ed46323 is not in the
    working tree; the ground was withdrawn in 1 commit since the pin

### moved — flag

The path exists and its bytes differ from the bytes at the pin.

    FLAG A0001 Grounds 1: code: src/serializers/v2.py @ed46323 has moved; 1 commit has
    touched it since the pin

### unstable pin — flag

The pin is a symbolic ref — a branch or a tag — rather than a commit. Such a pointer
resolves forever and can never drift, because the name follows the work. It is a hole in
the ledger's own guarantee, and the checker says so once.

    FLAG A0001 Grounds 2: code: src/api/foo.py @main is pinned to a branch, not a
    commit; a pin that moves with the work cannot go stale

`@working` and `@corpus` are not this defect. They are the declared unpinned forms, they
already say in the schema that they are only as reproducible as the tree they were read
in, and freshness skips them in silence.

## The comparison, exactly

For each ground pointer whose type is one of the project's evidence types, whose pin is
not in `UNPINNED`, and whose entry's status is not terminal:

1. `git rev-parse --symbolic-full-name <pin>` — non-empty output means **unstable pin**;
   report and stop for this pointer.
2. `git rev-parse <pin>:<path>` — the blob object id at the pin. Absent means the pointer
   never resolved, which is `resolve`'s finding and not repeated here.
3. The artifact as this run reads it: `git hash-object <path>` on the working tree, or
   the index blob under `--cached`, matching whatever the rest of the run is reading.
   Absent means **withdrawn**.
4. Object ids equal means fresh, and the checker says nothing.
5. Object ids differ means **moved**. Only now, and only for the message, run
   `git rev-list --count <pin>..HEAD -- <path>` for the commit count.

Blob identity, not a diff. It is exact, it is one cheap plumbing call per pointer, and it
has no opinion about what changed.

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
naming it is discharged, and the checker is silent.

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
| `D48-orphan-freshness-verdict` | propagation contested verdict naming a ground that has not moved | `freshness` **fail** at `commit 02, A0001 Verdicts` |

Known-good seeds:

| seed | what it holds | expected |
|---|---|---|
| `K19-unrelated-commit-is-not-drift` | `commits/02` edits a file no entry pins | all checkers pass |
| `K20-drift-acknowledged` | `commits/02` edits the artifact *and* appends the propagation verdict; the citing document is moved to `cites-as-contested` in the same commit | all checkers pass |
| `K21-fallen-entry-may-drift` | the entry is refuted; `commits/02` edits its artifact | all checkers pass |
| `K22-unpinned-is-not-drift` | the pointer is `@working`; `commits/02` edits the artifact | all checkers pass |

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
store; one `git hash-object` per pointer against the working tree; and one
`git rev-list --count` per *drifted* pointer, for the message only. The existing
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
  moved a second time after being contested — the contested verdict names a pointer, and
  the pointer has not changed. It may need to name the blob object id it was written
  against instead.
