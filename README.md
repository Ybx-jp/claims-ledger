# claims-ledger

A checked ledger of claims, in plain Markdown files, for a project that wants its
written record to be verifiable rather than merely earnest.

An entry separates the four roles a sentence in a research note usually fuses — the
claim, the data it rests on, the rule that gets you from one to the other, and the
source's own words — holds every quotation to the bytes of the source it names, and
derives its status from a verdict list that only ever grows. Five checkers enforce that,
and a red-team corpus of 76 seeds with committed expected outcomes proves the checkers.

    pip install claims-ledger

Nothing is installed alongside it: the checkers use the standard library only, so
`python3 -m claims_ledger check` runs from a plain interpreter — which is how the
pre-commit hook invokes them, rather than by console-script name that git's own
environment may not have on PATH. Python 3.11 or newer.

## Why

The schema was designed after an audit of a working ledger whose entries carried a
single frozen statement field. Comparing every entry that quoted a source against the
source it named, 24 of 47 quotations were defective. The failure was structural, not
careless: with quote, observation, inference and authority in one blob, a faithful quote
could continue seamlessly into unsourced inference and be sealed there by the freeze.

So an entry here has an Assertion in the project's words with **no quotation mark
allowed in it**, Grounds that are typed pointers, a Warrant that states the rule, and
Backing that holds the verbatim quotations — each one resolved, at check time, against
the stored bytes of its registered source.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/figures/four-roles-dark.svg">
  <img alt="A single frozen statement, where a faithful quotation runs seamlessly into unsourced inference, against an entry whose Assertion, Grounds, Warrant and Backing each sit on their own line and whose quotation is resolved against the stored source bytes." src="docs/figures/four-roles.svg" width="960">
</picture>

## Quickstart

Every command below is run by `tests/test_readme_quickstart.py` against a fresh project
and its output compared with what is printed here, so this transcript is reproducible
rather than illustrative — including the digests, which is why the source file it starts
from is written out rather than assumed.

```console
$ cat > paper.txt <<'EOF'
Okafor and Lindqvist authored the study. A stale fraction of 0.1 produced an error of 0.04. The full run log is in the appendix.
EOF

$ claims-ledger init
wrote /home/you/project/claims-ledger.toml
created /home/you/project/ledger/entries, /home/you/project/ledger/cache and …

$ claims-ledger source add paper.txt --id fx-paper --type paper \
    --citation "Okafor and Lindqvist (2026)" --authors Okafor Lindqvist
registered fx-paper (f09680d85993…) in ledger/sources.jsonl
bytes at ledger/cache/f09680d85993…

$ claims-ledger new stale-fraction-governs-error
wrote ledger/entries/A0001-stale-fraction-governs-error.md
Fill in Assertion, Scope, Grounds, Warrant and Backing, then `claims-ledger sha --write`…

$ cat > ledger/entries/A0001-stale-fraction-governs-error.md <<'EOF'
---
id: A0001-stale-fraction-governs-error
kind: claim
stated: 2026-09-06T09:00:00-07:00
author: main
grade: asserted
supersedes: none
verbatim_sha: 0
---

## Assertion

A stale fraction of 0.1 produces an embedding error of 0.04.

## Scope

metric: embedding error
cohort: dynamic graph embeddings
condition: stale fraction 0.1

## Grounds

- source: fx-paper · summary

## Warrant

Restates the source's own reported result.

## Backing

- source: fx-paper · summary
  speaker: Okafor and Lindqvist
  quote: "A stale fraction of 0.1 produced an error of 0.04."

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
EOF

$ claims-ledger sha --write ledger/entries/A0001-stale-fraction-governs-error.md
ledger/entries/A0001-stale-fraction-governs-error.md: 0… → 84d9b6514b98…

$ claims-ledger check
validate: 0 failure(s), 0 flag(s)
resolve: 0 failure(s), 0 flag(s)
references: 0 failure(s), 0 flag(s)
propagate: 0 failure(s), 0 flag(s)
freshness: 0 failure(s), 0 flag(s)
```

An entry looks like this:

```markdown
---
id: A0001-stale-fraction-governs-error
kind: claim
stated: 2026-09-04T12:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 3b47609dbcdf…
---

## Assertion

The mean aggregation error is governed by the stale fraction and not by degree.

## Scope

metric: mean L2 error of the aggregated representation
cohort: the synthetic demo graph
condition: mean aggregation, one layer

## Grounds

- lab: notes/001.md § "Observation" @9fceb02
- source: fx-paper · whole text

## Warrant

A measured error at a known stale fraction, with the source stating the same rule,
supports the assertion over this cohort.

## Backing

- source: fx-paper · whole text
  speaker: Okafor
  quote: "The error under mean aggregation scales with the stale fraction and does not grow with degree."

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
```

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/figures/entry-anatomy-dark.svg">
  <img alt="An entry file annotated part by part: frontmatter, then Assertion, Scope, Grounds, Warrant and Backing in a region that is frozen once committed; the APPEND marker as a seam; then Verdicts and References, which only ever grow." src="docs/figures/entry-anatomy.svg" width="960">
</picture>

The schema in full — every field, every rule, and what each heuristic is known to miss —
is in [docs/SCHEMA.md](https://github.com/Ybx-jp/claims-ledger/blob/main/docs/SCHEMA.md).

## The five checks

| command | holds |
|---|---|
| `claims-ledger validate` | entries are well-formed; the frozen region above the APPEND marker never changed after the commit that created it, and verdicts only ever grew (both read from git history) |
| `claims-ledger resolve` | every pointer resolves; every quoted span is a contiguous span of the named source's stored bytes, with elisions marked |
| `claims-ledger references` | citation acts agree with the target's current status, entry to entry and document to entry, both directions |
| `claims-ledger propagate` | when an entry falls or is challenged, its dependents carry the `contested` flag that says why (`--write` appends them) |
| `claims-ledger freshness` | every pinned ground still names the artifact the claim was established on: the path is in the tree and its bytes match the pin, and the pin is a commit rather than a name that moves (`--write` appends the missing `contested` verdicts) |

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/figures/five-checks-dark.svg">
  <img alt="A matrix of the five checkers against what each reads: entries, git history, the source registry and cache, the documents, and the working tree or index; with what each holds, and the two, propagate and freshness, that write a contested verdict under --write." src="docs/figures/five-checks.svg" width="960">
</picture>

`claims-ledger check` runs all five. Each exits non-zero on a failure and zero on a
flag, because a flag is a report a human judges rather than a gate.

A check that could not run never reports that it passed. Pointed at a directory with no
entries directory in it — the wrong `--root`, a configuration file moved away from its
ledger — every checking command stops with exit 2 and says nothing was checked, rather
than printing five clean lines over an empty room. Where a check is genuinely skipped
rather than passed, it is named on stderr: outside a git repository, or with no `git` on
PATH, validate's frozen-region and append-only checks cannot run and say so.

Statuses are never stored. They are derived from the last verdict — `open`,
`corroborated`, `contested`, `refuted`, `superseded`, `retracted`, `non-comparable` —
so the filter a reader would otherwise have to apply by hand is applied at check time,
and a document that still cites a refuted entry as live fails.

## Proving the checkers

A checker nobody has tried to fool is a checker nobody should trust. The package ships
the red-team corpus it was built against: 76 seeds, each a small ledger with committed
expected outcomes, one per defect class the audit found, one per rule about not silently
passing, plus known-good seeds every checker must leave alone. Its README says which
rules the corpus does *not* hold up and which the unit suite holds instead — a coverage
claim nobody has tried to falsify is worth as little as an unfooled checker.

```console
$ claims-ledger corpus
PASS D01-unmarked-deletion
…
76/76 seeds pass
```

The contract is symmetric: a seed passes when every expected failure is produced at the
named place **and** no checker trips where the seed does not say it should. An unlisted
catch is a finding about the seed or the checker, never a bonus, one row is satisfied by
one report and not by two, and a run that checked nothing — an empty corpus, a seed name
that matches none — exits non-zero rather than reporting a clean run over nothing. See
`src/claims_ledger/corpus/README.md` for the coverage table, including the rows where
the machinery only makes a defect visible and a human has to judge it.

## Configuration

`claims-ledger.toml` at the project root, or a `[tool.claims-ledger]` table in
`pyproject.toml`. Everything is optional; the defaults are shown.

```toml
[tool.claims-ledger]
ledger = "ledger"                    # entries/, sources.jsonl and cache/ live here
entries = "entries"
registry = "sources.jsonl"
cache = "cache"                      # empty string: no cache, rows name their bytes

# Documents that may cite an entry, as globs from the project root.
documents = ["*.md", "docs/*.md"]
document-excludes = []

# The named artifacts an entry may rest on. A sectioned type is written
#   lab: <path> § "<section>" @<commit>
# and a plain one
#   experiment: <path> @<commit>
evidence-sectioned = ["lab"]
evidence-plain = ["experiment"]

# How a sectioned type finds its section. `{name}` is the only substitution; the rest is
# an ordinary regex, matched line by line. Omitted, a type gets the Markdown heading that
# `§` always meant. A section runs from its own header to the next one, so anchor the
# pattern at the granularity the section really has — allowing leading whitespace in the
# Python pattern below would end a function at its first nested definition and leave the
# rest of it uncompared.
[tool.claims-ledger.section-patterns]
code = '^(?:def|class)[ \t]+{name}\b'

verdict-authors = ["main", "propagation"]
propagation-author = "propagation"   # the name machinery writes under

roster = "ROSTER.md"                 # the hand-maintained view of open hypotheses
archived-prefixes = []               # id series a previous ledger quarantined
```

The schema itself is not configurable. Grades, kinds, statuses, citation acts, the
fingerprint and the immutability rules are the claims model, not a project's naming, and
a project that changed them would no longer be running the checks the corpus proves.

An unknown key is an error rather than a silent no-op: a misspelled key that quietly
changes nothing is how a project ends up unchecked.

Every path a configuration names — `ledger`, `entries`, `registry`, `cache`, and the
`documents` globs — has to stay under the project root. An absolute path, one that walks
out through `..`, and a `ledger` that is a symlink to somewhere else are all refused by
name rather than honoured: cloning a repository should not hand its `claims-ledger.toml`
the right to say where this tool writes, or point the checkers at a file the project does
not contain.

A checker that cannot read something says so and exits non-zero. An entries directory it
cannot list, a documents directory it cannot enter, a document it cannot open or decode,
and a git that runs but cannot answer, are all reported rather than read as empty —
`0 failure(s)` over a ledger that was never read is the one report this tool must never
produce.

Writing is confined the same way reading is checked. Nothing is written through a link
that leaves the project root, including an entry file inside `entries/` that is a symlink
to somewhere else; reads follow such a link, writes refuse it.

## Authoring

| command | does |
|---|---|
| `claims-ledger new <slug>` | scaffold an entry at the next free id (`--kind`, `--grade`, `--author`, `--supersedes`, `--credence`, `--resolves-when`) |
| `claims-ledger sha <path>` | report the fingerprint recomputed from Scope and Backing; `--write` rewrites the declared value |
| `claims-ledger source add <file>` | register a source and store the bytes its quotations are checked against |
| `claims-ledger source list` | the registered sources, and whether their bytes are present |
| `claims-ledger status` | every entry with its kind, grade and derived status |
| `claims-ledger hook` | print the pre-commit hook; `--install` writes it |
| `claims-ledger --version` | the installed version |

`sha --write` refuses on an entry git already has. The region above the APPEND marker is
immutable once committed, so a new fingerprint there is a new entry: supersede it, or
pass `--force` if the commit has not left the machine.

Registering a source stores its bytes in the same call that writes the row, because a
registry row without its bytes is a check that cannot run. The row is committed and the
bytes are not — `ledger/cache/.gitignore` is written by `init` — so the row carries the
sha256, and the `--url` and `--extraction` that regenerate them.

That means a fresh clone of a project's ledger has rows without bytes, and `check` fails
loudly, per quotation, until they are back: re-run `claims-ledger source add` on the
bytes named by each row's url and extraction, and `claims-ledger source list` will say
`bytes present`. There is no command that fetches them for you, because how a source's
bytes were produced from its url is a decision with a record, not a download.

The hook `--install` writes names the interpreter it was installed by, absolutely, and
reaches the package with `-m`. Git runs hooks with its own environment: a hook that said
`claims-ledger` would fail with `not found` on every commit for anyone who installed
into a virtualenv that was not active.

## As a library

```python
from claims_ledger import open_ledger, load_entries, LedgerError
from claims_ledger import validate, resolve, references, propagate

ledger = open_ledger(root="/path/to/project")
for entry in load_entries(ledger):
    print(entry.id, entry.status(), entry.scope["metric"])

reports = validate.run(ledger)  # [Report(outcome, entry, part, message)]
failed = any(r.outcome == "fail" for r in reports)
```

`open_ledger` finds the configuration; `Ledger` can also be built from a `Config`
directly, which is how the corpus runner points the checkers at a seed.

A file the user maintains that cannot be read or parsed — an entry that is not UTF-8, a
`sources.jsonl` line that is not JSON — raises `LedgerError`, naming the file and the
line. The CLI turns that into a diagnostic and exit 2; nothing reaches a user as a
traceback. `Report` is a finding about a well-formed ledger, `LedgerError` is the ledger
being unreadable in the first place, and the two are not mixed.

## What this does not do

It does not decide whether a claim is true. Resolution shows a span exists in the named
artifact and nothing more. A load-bearing elision, an undercut recorded as a refutation,
a widened scope, a citation chain that never reaches evidence — the machinery can make
each of those visible, and the classification is a human's, recorded as a verdict. An
entry that passes every check is not thereby right.

Both heuristics it does apply (the absence-claim trigger words and the relayed-quotation
flag) are documented with the cases they are known to miss, in `docs/SCHEMA.md`.

## Working on it

```console
$ pip install -e ".[dev]"
$ ruff check . && ruff format --check .
$ ty check
$ pytest -q
$ claims-ledger corpus
```

All five are what CI runs, over Python 3.11, 3.12, 3.13 and 3.14 on Linux and macOS, plus a
job that builds the wheel, installs it into a clean environment and runs the corpus from
a directory that is not the checkout — because the claim that an installed copy can prove
itself is only worth anything if it is tested that way.

`ty` is pointed at the 3.11 floor rather than the newest interpreter, so a construct that
only exists on a newer Python cannot pass here and fail for a user. The ruff rule set is
listed explicitly in `pyproject.toml` rather than inherited from ruff's defaults, which
grow between releases.

A change that moves a corpus seed's expected outcome is a methodology change, not a bug
fix: record it in `CHANGELOG.md` with the seed named.

Cutting a release is `RELEASING.md`'s job to describe, not this one's — it names the
exact PyPI and GitHub setup a first publish needs and the steps every release after it
repeats.

## Provenance

Extracted from the claims ledger built for a research project on dynamic graph embedding
refresh, where the schema, the checkers and the corpus were developed together. The
extraction changed what was project-specific into configuration — where the ledger sits,
which documents may cite it, what an evidence pointer is called, who may write a verdict
— and changed nothing about the schema or the checks. Every one of the sixty-two seeds
the corpus held at extraction still passes unchanged; it has since grown to 76.

MIT licensed.
