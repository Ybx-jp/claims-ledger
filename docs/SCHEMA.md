# The schema

The statement of record for what an entry is. The red-team corpus restates the parts its
seeds depend on (`src/claims_ledger/corpus/README.md`) and proves them; a difference
between the two is a defect in whichever is wrong.

The failure this schema is designed against is structural. In the ledger it was designed
after, a single frozen statement field fused a quotation, an observation, the project's
own reasoning, and the authority behind it into one blob, so a faithful quote could
continue seamlessly into unsourced inference and be sealed there by the freeze. An audit
of that ledger compared every entry whose statement quoted a source against the source
it named and found 23 of 47 quotations faithful and 24 defective, in nine classes. This
schema separates the four roles into Assertion, Grounds, Warrant and Backing, holds
every quotation to its source, and derives status from an append-only verdict list.

The names are Toulmin's, in Verheij's (2005) formalization: assertion, grounds, warrant,
backing; the three-part split into assertion, provenance and publication info is the
nanopublication model (Kuhn et al. 2021); *challenges* is micropublications' relation
(Clark, Ciccarese and Goble 2014).

## Layout

    <project root>/
      claims-ledger.toml    the configuration; see README.md
      ledger/
        entries/            one file per entry, `A####-slug.md`
        sources.jsonl       the source registry — one row per external source an entry
                            cites: id, type, citation, author surnames where the source
                            names authors, retrieval date, sha256 of the text, and the
                            URL and extraction method that regenerate the bytes.
                            Committed; the bytes are not
        cache/              the bytes, keyed by sha256; not committed

## The four checks

Each is `claims-ledger <name>`, each exits non-zero on a failure and zero on a flag (a
report a human judges).

- **validate** — every entry is well-formed: ids, timestamps, the no-quotation-marks
  rule in Assertion, Scope at `measured` and above, grade–grounds consistency, the
  absence-claim rule, the verbatim fingerprint, verdict legality and authorship,
  supersession both ways, and — from git — immutability of the region above the APPEND
  marker and append-only verdicts over the whole history. `--cached` reads staged entries
  from the index, for a pre-commit hook.
- **resolve** — every pointer resolves to the artifact that established the fact, and
  every quotation is a contiguous span of the source it names, elisions marked; a
  consultation-type source's speaker is its expert, and a consultation sentence naming
  another registered author is flagged as relayed. A registry or cache miss is a failure
  that says the check could not run, never a silent pass. On a retracted entry the
  defect the verdict states must reproduce.
- **references** — citation acts are compatible with the target's current status, entry
  to entry and document to entry; document citations and entries' References sections
  agree both ways; no document cites an id in a quarantined series.
- **propagate** — a dependent of a fallen entry, and the target of a `challenges` act,
  carry the `contested` verdict by propagation that records why; `--write` appends the
  missing ones. It is the one place machinery writes into an entry.

They are proven, not trusted: `claims-ledger corpus` runs all four over every seed in
the red-team corpus and holds them to the committed expectations under the contract in
that directory's README. A checker is only as good as the seed that exercises it, and a
defect class found in practice gets a seed before it gets a fix.

## The entry

**One file per entry**, `entries/A####-slug.md`. Ids are a letter and exactly four
digits; the letter rolls over (`B0001`) when a series is exhausted and skips any series
the configuration quarantines. A citation of a quarantined id anywhere in the documents
is a quarantine breach by prefix alone.

**Frontmatter** (publication info): `id`, `kind` (`claim` | `prediction` |
`hypothesis`), `stated` (ISO 8601 to the second with a UTC offset; a bare date is
malformed), `author` (a name the configuration allows), `grade` (`asserted` | `argued` |
`measured` | `controlled` | `preregistered`), `credence` and `resolves_when` (required
for predictions and hypotheses, omitted otherwise, never guessed), `supersedes` (`none`
or an id), `verbatim_sha`, and optionally `verbatim_change` with a reason.

**Sections**, in order: Assertion, Scope, Grounds, Warrant, Backing, then the line
`<!-- APPEND BELOW THIS LINE ONLY -->`, then Verdicts and References.

- *Assertion* is the claim in the project's words. **No quotation mark may appear in
  it.** Every fusion of quote and inference the audit found lived inside quotation marks
  in a statement blob; the seam between source words and project words is structural
  here, not typographic.
- *Scope* is three lines, `metric:`, `cohort:`, `condition:`, required at `measured` and
  above. An assertion claims exactly its scope.
- *Grounds* are typed pointers, one per line:
  `lab: <path> § "<section>" @<commit>` · `experiment: <path> @<commit>` ·
  `entry: <id> · <act>` · `source: <registry id> · <locator>` ·
  `search: corpus=…; query="…"; date=…`. The first two are evidence pointers and their
  names are the project's — `lab` and `experiment` are the defaults, a project may
  declare `run`, `journal`, `notebook` instead, sectioned or plain. An absence claim
  carries a `search:` ground instead of a positive pointer. The citation acts are
  `cites-as-live` (target open or corroborated), `cites-as-contested` (target
  contested), `cites-as-fallen` (any status; the only act legal against a fallen
  target), and `challenges` (target open, corroborated or contested; the citing entry's
  Warrant names what it attacks). A ground is a datum the Warrant uses; an artifact the
  entry mentions without resting on it is named in the Warrant's prose, or cited
  `cites-as-fallen` if it is an entry, and is not a ground. A `measured` or higher grade
  requires an evidence ground, and an `asserted` grade forbids one: the grade is the type
  of the evidence.
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
  configured names and nothing else — an expert whose opinion is a source writes none,
  because a consultation is evidence a verdict points at — and a verdict by the
  propagation author must carry `entry:` evidence with `· fallen` or `· challenges`,
  since those are the only two things the machinery writes about. An assertion is a
  proposition made by an agent on an occasion; `author` and `stated` are the agent and
  the occasion, and a verdict under the wrong agent is malformed whatever it says.
- *References* lists the documents (not entries) that cite this entry:
  `- <path> · standing | record · <act>`. Entry-to-entry edges are read from Grounds and
  are not repeated here. A document cites an entry inline as `(A0007-slug, cites-as-live)`,
  and the two views are checked against each other both ways, so a status lives in
  exactly one place: the act a document declares is held to the entry's current status at
  every check, and a copied id cannot go stale silently.

**Hypotheses.** A `kind: hypothesis` entry is a prediction whose `resolves_when` is an
experiment design. It carries at least one `entry:` ground naming the claims motivating
it, and its Warrant states what would falsify it; the falsifier rule is a heuristic on
wording, any word beginning `falsif`, stated so a reader knows what is and is not
caught. Every hypothesis whose status is not terminal has exactly one row in the roster
document the configuration names, a hand-maintained view a preregistration author reads:
the row's first cell cites the entry and its last cell states its status, and the
reference check holds both to the entry. The roster is not generated, so it is checked.

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
a different source or a different speaker changes the fingerprint. A quote is one line.
Grounds are excluded. The value is recomputed at check time and a declared value that
differs is malformed (`claims-ledger sha --write` computes it for a draft). Across a
supersession chain the value must be equal unless the successor declares
`verbatim_change` with a reason; reordering Backing blocks, changing emphasis or
whitespace, or writing an accented word in another normalization form changes nothing.
Resolution applies the same normalization when it matches spans, so the two never
disagree about what a change is. The fingerprint is not an integrity key; the integrity
key over a whole entry is its git blob at the commit that created it, which is what the
immutability check diffs against. Its job is the inverse of the fingerprint in Kuhn et
al. (2017): there, unequal fingerprints trigger a new version; here, equal fingerprints
are what a chain must preserve.

**Immutability.** The region above the APPEND marker never changes after the commit
that created the entry, and a verdict once committed is never edited or removed. Both
are properties of history, not of a file, and are checked against git over the whole
history, so a commit that bypassed the check is caught by the next run anywhere.

**Statuses** are derived from the last verdict, never stored: `open` (no verdicts),
`corroborated`, `contested`, `refuted`, `superseded`, `retracted`, `non-comparable`. The
last four are terminal, with one exception: `refuted` or `non-comparable` may be
followed by exactly one `superseded`, because reinstatement is supersession. A
corroborating verdict must point at a ground the entry does not already cite. A
`refuted` verdict whose evidence grade differs from the entry's is flagged for a
human, since evidence types are not ranked. `non-comparable` is legal only at
`measured` and above. `retracted` here means a defect in the making, not obsolescence
without a successor as in nanopublication usage. On a retracted entry the defective
quote is not re-reported; instead the `defect:` the verdict states must reproduce, and
a retraction whose stated defect does not is flagged — a retraction for a defect that
is not there is itself the defective act. Supersession is a chain, not a tree: an entry
carries one `superseded` verdict, so a second successor is malformed, and a
`superseded` verdict naming a successor that does not declare `supersedes:` is
malformed too.

**Sources.** Every `source:` pointer names a row in `sources.jsonl`, and the row's
sha256 names the bytes a quotation is checked against. A registry row without its
bytes, or a pointer without its row, is a failure that says the check could not run —
never a silent pass. A consultation-type source's speaker is its expert; a sentence in
such a source that names another registered author is flagged as relayed.

**Propagation** is the one place machinery writes into an entry. When an entry cited
`cites-as-live` falls, or an entry is named by a `challenges` act, a `contested` verdict
under the propagation author is appended to the dependent or challenged entry, and the
flag is reported until a human re-verdicts. A `challenges` act whose target lacks that
verdict, or whose target is fallen, is a failure, and so is a propagated verdict whose
named cause does not exist. A dependent flagged because its live-cited ground fell
cannot return to `corroborated`: its Grounds are immutable and still cite the fallen
entry, so the reference check keeps failing until it is superseded; once it has fallen
itself, its Grounds are history, exempt from the act check, and it needs no further
flag, since a verdict after a terminal status is illegal. A document that cites an entry
`cites-as-live` after the entry is superseded or refuted fails the same way; the filter
a reader must apply every time is applied for them at check time.

**Two rules are heuristics**, stated so a reader knows what is and is not caught:

- An Assertion is read as an absence claim, and must carry a `search:` ground, when it
  contains one of the standalone words `nobody`, `no one`, `neither`, `first`, `novel`,
  `unique`, `unprecedented`, the phrase `not found`, or the standalone word `no` followed
  within the sentence by `has`, `have`, `was`, `were`, `report` or `reports`. Words are
  whitespace-delimited: `no-refresh` is a baseline's name and contains no `no`. A
  priority word is an absence claim about everyone else, which is why a search is on
  record before one is written. A false positive costs a `search:` line; a false negative
  is the defect the audit found. Known miss: an absence stated without any of these
  tokens (`lacks`, `remains open`, `unreported`).
- A quote from a consultation-type source is flagged as relayed third-party material when
  the source sentence containing the span also contains a surname from another registry
  row's `authors` or the token `et al.`. Title words are not used: a consultation about
  mean aggregation would name every paper about mean aggregation. This is a flag for
  review, not a failure; the failure case is a consultation source whose `speaker:` is
  not its expert. Known miss: a relay by pronoun in a sentence that names nobody.

## What a mechanical check does not show

- That a quotation is *true*, or that its source is the right one. Resolution shows a
  span exists in the named artifact and nothing more.
- That a load-bearing elision, an undercut recorded as a refutation, an attack on a
  datum recorded as a refutation, a distortion by reversal, a widened scope, or a chain
  with no empirical base is classified correctly. The machinery can make each of those
  visible; the classification is a human's, recorded as a verdict, and an entry the
  checks pass is not thereby right.
- That a defect class not seeded is caught. The seeded classes are the ones the audited
  ledger actually exhibited plus the ones this schema's own rules create; a class found
  in practice is added to the corpus before it is fixed in a checker.

## Naming, disclosed

`retracted` here means a defect in the making of an entry, not obsolescence without a
successor as in nanopublication usage; a refuted claim nobody replaced is `refuted`, not
`retracted`. `Assertion` is used in the nanopublication sense (the claim); SEPIO uses
the same word for the whole of proposition, agent and occasion. `Scope` is the domain
the claim holds over and is not Toulmin's qualifier, which is `credence`.

## Sources this schema was designed from

Named by author and year only, which is how the corpus's own coverage table names them;
the corpus README says which seed encodes which claim.

- Toulmin (1958) and Verheij (2005) — assertion, grounds, warrant, backing, and the
  evaluation of an argument under attack.
- Kuhn et al. (2021) — the split into assertion, provenance and publication info, and
  versioning by supersession. Kuhn et al. (2017) — the content fingerprint this one
  inverts.
- Clark, Ciccarese and Goble (2014) — micropublications, the *challenges* relation, and
  the citation-distortion classes relayed there from Greenberg.
- Brush, Shefchek and Haendel (2016) — an assertion as proposition, agent and occasion.
- Giglio et al. (2019) and Guyatt et al. (2008) — evidence grading, and the reason a
  grade here is an evidence type carrying no quality ranking.
