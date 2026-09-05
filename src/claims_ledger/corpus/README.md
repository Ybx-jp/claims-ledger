# The red-team corpus

The proof bar for the checkers. Nothing in this package is trusted to check anything
until it passes this corpus, and the corpus was written before the checkers existed:
the test precedes the thing tested.

Why a corpus and not a sample rebuild. The schema was designed after an audit of a
working ledger built on a single frozen statement field: every entry whose statement
quoted a source was compared against the source it named, and 24 of 47 quotations were
defective, in nine classes. Two of the probes written to run that audit were themselves
wrong — one exhausted a generator before the check ran and reported zero matches,
another would have reported 11 misattributions where 8 were a backtick difference. A
verifier is trusted only after it has passed a known-positive and a known-negative, so
every defect class here has a seed the checkers must catch, and every rule has a
known-good seed the checkers must not catch.

Seeds and their expected outcomes are committed and re-run on every change to a checker.
A checker change that makes a seed's outcome move is a methodology change and is recorded
as such in the commit that makes it.

## Layout

    corpus/
      run.py               the runner: every seed through the four checkers, held to
                           expected.json under the contract below; `claims-ledger corpus`
                           is how it is invoked
      fixtures/            synthetic sources the seeds quote: two papers, one consultation,
                           five lab notes. Every fixture says in its first lines that it
                           is synthetic; the authors named in them are fictional.
      sources.jsonl        the registry rows for the fixtures — id, type, citation,
                           author surnames where the source has named authors, retrieval
                           date, sha256 of the bytes, and (only here) the path of the
                           bytes, because fixtures are committed and real sources are not
      seeds/
        K##-slug/          known-good: every checker must pass
        D##-slug/          defect: the named checker fails or flags at the named place, or
                           the seed is review-only and every checker passes
          expected.json    class, known_good, and the expectation rows
          entries/         the ledger entries of this seed, as they would sit in ledger/entries/
          docs/            any citing documents the seed needs
          commits/01, 02   history seeds only: successive states to apply as commits;
                           a state after 01 may be deliberately tampered

Seeds are independent. Each is checked as if its `entries/` and `docs/` were the whole
ledger, with `sources.jsonl` and `fixtures/` shared from the corpus root. Ids repeat
across seeds (most seeds have an `A0001`) and mean nothing outside their seed.

## What `expected.json` says

    {"class": "unmarked deletion", "known_good": false, "expect": [
      {"checker": "validate", "outcome": "pass", "where": "all", "why": "well-formed"},
      {"checker": "resolve",  "outcome": "fail", "where": "A0001 Backing quote 1",
       "why": "the quote drops the parenthetical (cosine, L2) with no elision mark"}]}

`checker` is one of `validate`, `resolve`, `references`, `propagate` — the four programs
that live beside this directory — or `review`, which is not a program. A checker
row's `outcome` is `pass`, `fail`, or `flag`; a `review` row's outcome is always `judge`.
`where` names an entry and one part of it so a runner can match the checker's report to
the row. `why` describes the outcome for the reader; where it names a mechanism, the
mechanism is illustrative and the outcome is what binds.

The runner's contract, fixed before the runner existed and implemented by `run.py`
(`claims-ledger corpus [-v] [SEED ...]`):

- A seed passes when every `fail` and `flag` row is produced by the named checker at the
  named place, **and every checker not named in a non-pass row exits clean.** The second
  half is the known-negative: a defect seed that trips a checker the row does not name is
  a runner failure, not a bonus catch, because either the seed has a defect its author did
  not see or the checker has a false positive. Both are findings.
- `fail` means exit non-zero and a report naming the place. `flag` means exit zero with a
  report naming the place: the checker has made something visible and a human decides.
  `pass` means neither.
- `review` rows carry no obligation for the machinery. They record what the correct human
  verdict is once the machinery has made the defect visible, and they exist so a later
  reader can tell a seed the checkers are meant to *catch* from one they are meant to
  *surface*, and both from one that is green by design and owes the reader a warning. A
  known-good seed may carry a `review` row; its checker rows are still all `pass`.
- History seeds (`commits/`) are applied as successive commits in a fresh repository, and
  their rows name the commit they apply to. They are the only way to test immutability,
  since immutability is a property of history and not of a file.

## The schema the seeds are written against

The statement of record is `docs/SCHEMA.md`, which carries the schema in full; what
follows is restated here so the corpus is readable on its own, and a difference between
the two is a defect in whichever is wrong. The names are Toulmin's, in Verheij's
(2005) formalization: assertion, grounds, warrant, backing; the three-part split into
assertion, provenance and publication info is the nanopublication model (Kuhn et al.
2021); *challenges* is micropublications' relation (Clark, Ciccarese and Goble 2014).

**One file per entry**, `entries/A####-slug.md`. Ids are a letter and exactly four
digits; the letter rolls over (`B0001`) when a series is exhausted and skips any series
a project has quarantined. This corpus quarantines `C` and `P`, so a citation of a
`C###` or `P###` id anywhere in a seed is a quarantine breach by prefix alone.

**Frontmatter** (publication info): `id`, `kind` (`claim` | `prediction` |
`hypothesis`), `stated` (ISO 8601 to the second with a UTC offset; a bare date is
malformed), `author` (a name the project's configuration allows), `grade` (`asserted` | `argued` |
`measured` | `controlled` | `preregistered`), `credence` and `resolves_when` (required
for predictions and hypotheses, omitted otherwise, never guessed), `supersedes` (`none`
or an id), `verbatim_sha`, and optionally `verbatim_change` with a reason.

**Sections**, in order: Assertion, Scope, Grounds, Warrant, Backing, then the line
`<!-- APPEND BELOW THIS LINE ONLY -->`, then Verdicts and References.

- *Assertion* is the claim in the project's words. **No quotation mark may appear in
  it.** Every fusion of quote and inference the audit found lived inside quotation
  marks in a statement blob; the seam between source words and project words is
  structural here, not typographic.
- *Scope* is three lines, `metric:`, `cohort:`, `condition:`, required at `measured` and
  above. An assertion claims exactly its scope.
- *Grounds* are typed pointers, one per line:
  `lab: <path> § "<section>" @<commit>` · `experiment: <path> @<commit>` (the evidence
  type names are the project's; these two are the defaults) ·
  `entry: <id> · <act>` · `source: <registry id> · <locator>` ·
  `search: corpus=…; query="…"; date=…`. In this corpus the pin is `@corpus`, because
  fixtures are not at a commit. An absence claim carries a `search:` ground instead of a
  positive pointer. The citation acts are `cites-as-live` (target open or corroborated),
  `cites-as-contested` (target contested), `cites-as-fallen` (any status; the only act
  legal against a fallen target), and `challenges` (target open, corroborated or
  contested; the citing entry's Warrant names what it attacks). A ground is a datum the
  Warrant uses; an artifact the entry mentions without resting on it is named in the
  Warrant's prose, or cited `cites-as-fallen` if it is an entry, and is not a ground.
- *Warrant* states the rule by which the grounds support the assertion. Conditions on the
  rule are Scope lines, not Warrant sentences.
- *Backing* holds every verbatim quotation, one block per quote: `source:` (a registry
  id and locator), `speaker:` (the text's author), `quote:`. A consultation-type source
  may back only the expert's own judgment; a result the expert attributes onward resolves
  to the primary source or not at all.
- *Verdicts* append and only append. One row each:

      - <timestamp> · <status> · grade: <grade of the evidence> · author: <an allowed author>
        evidence: <typed pointer, held to the same resolution bar as Grounds>
        note: <optional>

  Verdict evidence adds two pointer forms Grounds do not have: `entry: <id> · fallen`,
  `· challenges` or `· supersedes` names the entry whose fall, challenge or succession
  moved this one; `defect: <description>` is legal only on a `retracted` verdict and
  names the making-defect. Timestamps are non-decreasing down the file and none is
  earlier than `stated`. **Who may write a verdict is checked:** `author:` is one of the
  names the configuration allows and nothing else — an expert whose opinion is a source
  writes none, because a consultation is evidence a verdict points at — and a verdict by
  the propagation author must carry `entry:` evidence
  with `· fallen` or `· challenges`, since those are the only two things the machinery
  writes about. An assertion is a proposition made by an agent on an occasion; `author`
  and `stated` are the agent and the occasion, and a verdict under the wrong agent is
  malformed whatever it says.
- *References* lists the documents (not entries) that cite this entry:
  `- <path> · standing | record · <act>`. Entry-to-entry edges are read from Grounds and
  are not repeated here.

**Hypotheses.** A `kind: hypothesis` entry carries at least one `entry:` ground naming the
claims motivating it, and its Warrant states what would falsify it (heuristic: any word
beginning `falsif`). Every hypothesis whose status is not terminal has exactly one row in
the roster document the configuration names (`docs/ROSTER.md` in a seed): the row's
first cell cites the entry and its last cell states its status, and the reference check
holds both to the entry.

**The quote grammar.** A `quote:` value is one or more quoted spans separated by `[…]`,
optionally beginning or ending with `[…]`. Each span must be a contiguous substring of
the named source, spans appear in source order, and a span that starts or ends inside a
sentence must have the elision mark on that side. Comparison is made after the same
normalization the fingerprint uses (below); anything that survives it must match.

**`verbatim_sha`** is a fingerprint over the verbatim record: sha256 over the Scope
lines, then a blank line, then one line per Backing block, with the blocks sorted. A
Scope line or a Backing block is normalized before hashing: Unicode NFC, the markdown
emphasis markers `*` and backtick removed, whitespace collapsed to single spaces, blank
Scope lines dropped. A Backing block's line is its `source:`, `speaker:` and `quote:`
values joined by ` | ` — attribution is part of the verbatim record, so a quote moved to
a different source or a different speaker changes the fingerprint. Grounds are excluded.
The validate check recomputes the value and a declared value that differs is malformed. Across
a supersession chain the value must be equal unless the successor declares
`verbatim_change` with a reason; reordering Backing blocks, changing emphasis or
whitespace, or writing an accented word in another normalization form changes nothing.
The resolver applies the same normalization when it matches spans, so the two never
disagree about what a change is. The fingerprint is not an integrity key; the integrity
key over a whole entry is its git blob at the commit that created it, which is what the
immutability check diffs against. Its job is the inverse of the fingerprint in Kuhn et
al. (2017): there, unequal fingerprints trigger a new version; here, equal fingerprints
are what a chain must preserve.

**Statuses** are derived from the last verdict, never stored: `open` (no verdicts),
`corroborated`, `contested`, `refuted`, `superseded`, `retracted`, `non-comparable`. The
last four are terminal, with one exception: `refuted` or `non-comparable` may be
followed by exactly one `superseded`, because reinstatement is supersession. A
corroborating verdict must point at a ground the entry does not already cite.
`non-comparable` is legal only at `measured` and above. `retracted` here means a defect
in the making, not obsolescence without a successor as in nanopublication usage. On a
retracted entry the resolve check does not re-report the defective quote; it checks that the
`defect:` the verdict states reproduces, and flags a retraction whose stated defect does
not — a retraction for a defect that is not there is itself the defective act.
Supersession is a chain, not a tree: an entry carries one `superseded` verdict, so a
second successor is malformed, and a `superseded` verdict naming a successor that does
not declare `supersedes:` is malformed too.

**Propagation** is the one place machinery writes into an entry. When an entry cited
`cites-as-live` falls, or an entry is named by a `challenges` act, the propagate check
appends a `contested` verdict under the propagation author to the dependent or challenged entry and
exits non-zero so the flag is seen. A `challenges` act whose target lacks that verdict,
or whose target is fallen, is a failure, and so is a `propagation` verdict whose named
cause does not exist. A dependent flagged because its live-cited ground fell cannot
return to `corroborated`: its Grounds are immutable and still cite the fallen entry, so
the reference check keeps failing until it is superseded. A document that cites an entry
`cites-as-live` after the entry is superseded or refuted fails the same way; the filter
a reader must apply every time is applied for them at check time.

**Two rules the seeds assume are heuristics**, and they are stated here so a checker
author implements what the seeds test rather than something stronger:

- An Assertion is read as an absence claim, and must carry a `search:` ground, when it
  contains one of the standalone words `nobody`, `no one`, `neither`, `first`, `novel`,
  `unique`, `unprecedented`, the phrase `not found`, or the standalone word `no` followed
  within the sentence by `has`, `have`, `was`, `were`, `report` or `reports`. Words are
  whitespace-delimited: `no-refresh` is a baseline's name and contains no `no`. A
  priority word is an absence claim about everyone else, which is why a search is on
  record before one is written. A false positive costs a `search:` line; a false
  negative is the defect the audit found. Known miss: an absence stated without any
  of these tokens (`lacks`, `remains open`, `unreported`).
- A quote from a consultation-type source is flagged as relayed third-party material when
  the source sentence containing the span also contains a surname from another registry
  row's `authors` or the token `et al.`. Title words are not used: a consultation about
  mean aggregation would name every paper about mean aggregation. This is a flag for
  review, not a failure; the failure case is a consultation source whose `speaker:` is
  not its expert. Known miss: a relay by pronoun in a sentence that names nobody.

## Coverage

Each defect class the audit found has at least one seed, and so does each rule the
schema's own structure creates. The right column is the honest limit: `catch` means the checker
fails; `flag` means it reports and a human judges; `review` means the machinery passes
and only the human record says what is wrong.

| class | seeds | machinery owes |
|---|---|---|
| unmarked deletion | D01 | catch (span not contiguous) |
| paraphrase inside quotation marks | D02 | catch |
| text no source contains | D03 A0001 | catch |
| distortion by reversal | D03 A0002 | catch as unresolvable; the class is review |
| right quote, wrong source | D04 | catch |
| dead pointer | D05 | catch, loudly — a cache or registry miss never passes silently |
| mid-sentence cut without `[…]` | D06 | catch |
| fusion of quote and inference | D07 | catch (no quotation marks in Assertion) |
| grade inversion | D08 | catch the pointer-kind mismatch, both directions; a fixture note that calls its own numbers typed is not seen |
| absence-scope widening | D09, D38, K04 | catch the missing `search:`, including on a priority word; the widening itself is review |
| speaker misidentified | D10, K13, D40 | catch the structural case; flag the relayed case; the name-free relay is a known miss |
| load-bearing elision | D11 | review — the elision is marked and visible; the machinery passes |
| refuted on weaker evidence | D12 | flag |
| undercut recorded as refuted | D13 | review |
| datum attack recorded as refuted | D33 | review |
| challenge without its flag | D14, K07 | catch |
| act incompatible with target status | D15, D16 | catch |
| document cites a superseded entry as live | D32 | catch |
| verdict after a terminal status | D17, K06 | catch |
| malformed or non-monotonic timestamps | D18 | catch |
| prediction without credence or resolves_when; credence out of range | D19, K02, K03 | catch |
| id width, archived prefix, archived-id citation | D20 | catch |
| verbatim drift across a chain | D21, K05 | catch |
| attribution changed across a chain | D39, K10 | catch without a declaration; pass with one |
| normalization-only differences across a chain | K11 | pass |
| supersession without the predecessor's final verdict | D22 | catch |
| predecessor names an undeclared successor | D35 | catch |
| supersession fork | D34 | catch |
| frozen region edited after creation | D23, K09 | catch (history) |
| verdict line modified | D24 | catch (history) |
| corroborated by its own grounds | D25 | catch |
| non-comparable below measured | D26 | catch |
| references not two-way consistent | D27 | catch |
| challenge against a fallen target | D28 | catch |
| measured claim with an incomplete Scope | D29 | catch |
| declared `verbatim_sha` does not match the content | D30 | catch |
| verdict author not who could have written it | D31 | catch |
| orphan propagation | D36 | catch |
| false retraction | D37 | flag |
| chain with no empirical base | K14 | review — every checker passes by design |
| amplification across a citation | D41 | review |
| hypothesis without a falsifier, or without a motivating entry | D42, K03 | catch |
| open hypothesis without a roster row | D43, K15 | catch |
| roster status cell stale | D44 | catch |
| fallen citer held to its immutable acts, or flagged after a terminal status | K16, K17 | pass — a fallen entry's Grounds are history |
| creating commit misread by rename detection when a successor copies a kept predecessor | K18 | pass — the creating commit is the one that added the file |

Known-good seeds: K01 (a measured claim), K02 (a prediction), K03 (a hypothesis with a
falsifier), K04 (an absence claim with its search), K05 (a supersession chain), K06
(reinstatement by supersession), K07 (a challenge with its propagated flag), K08 (an
asserted claim on backing alone), K09 (a verdict appended in history), K10 (an
attribution change declared), K11 (normalization-only differences across a chain), K12
(a baseline named `no-refresh` in an Assertion), K13 (a consultation quote sharing title
words with the papers), K14 (a chain with no empirical base), K15 (a roster consistent
with its hypothesis), K16 and K17 (a dependent superseded after its live-cited ground
fell, with and without the propagated flag), K18 (a successor written as a near-copy of
a predecessor that stays in the tree, committed together with the predecessor's
`superseded` verdict). K01–K03, K09 and K15–K18 test the schema's own rules and encode
no claim from the canon; the others each stand for one.

## What the corpus encodes from the canon

The seeds were checked against the sources the schema was designed from. The claims the
corpus is meant to encode, and where each lives:

- A warrant that does not adequately represent, distorts, or fabricates its backing calls
  the claim into question (Clark, Ciccarese and Goble 2014, relaying Greenberg): D01, D06
  and D11 are the first, D02 and D03 A0002 the second, D03 A0001 the third; D04 and D05
  are the cited reference that resolves to the wrong document or to none.
- An attack on the connection between data and claim leaves the claim neither justified
  nor defeated (Verheij 2005, following Pollock): D13. An attack on a datum does the
  same: D33. An attack on the applicability of the warrant is an attack on Scope: K07 is
  one, recorded as a challenge.
- Evaluation is nonmonotonic and a defeated claim can be reinstated (Verheij 2005): K06.
- A challenge is recorded in the challenger's object (Clark et al. 2014): K07, D14, D28.
- A new version declares what it supersedes and the previous version stays untouched
  (Kuhn et al. 2021): K05, D21, D22, D23, D24, D34, D35.
- A grade is an evidence type and carries no quality; expert opinion is not an evidence
  category (Giglio et al. 2019; Guyatt et al. 2008): D08, D12, K08.
- An assertion is identified by its proposition, its agent and its occasion (Brush,
  Shefchek and Haendel 2016): D18, D31.
- A reader must filter superseded and retracted records every time (Kuhn et al. 2021):
  D15, D16, D27, D32.
- A citation lineage may not resolve to empirical evidence, and a qualifier can be
  dropped across a citation (Clark et al. 2014, relaying Greenberg): K14, D41.

Not encoded, by decision and disclosed: retraction as a separate object (here it is a
verdict), and challenge discoverability as a service function (here it is a propagated
verdict on the challenged entry). Not found in the sources held (scan of 2026-09-02):
Greenberg's own taxonomy of citation distortion, which is relayed by Clark only in
outline; a test-oracle literature on corpora of this shape.

## What passing this corpus does not show

- That the checkers catch a defect class not seeded here. The classes are the ones the
  audited ledger actually exhibited plus the ones the schema's own rules create; a new
  class found in practice gets a seed before it gets a fix.
- That a quotation is *true*, or that its source is the right one. Resolution shows a
  span exists in the named artifact and nothing more.
- That the load-bearing elision, the undercut, the datum attack, the reversal, the
  widened scope, or the chain with no empirical base are classified correctly. Those rows
  say `review` because the machinery can only make them visible, and a row claiming
  otherwise would be a fifth thing that says it is checked and is not.
- That the fixtures are safe to cite. They are synthetic, their authors are fictional,
  and each says so in its first lines; a reader who quotes a fixture as a source has done
  the thing the corpus exists to catch.
