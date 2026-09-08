# The vocabulary, and where to read it

Every list here is exported by the package. Print it rather than trusting a copy — a
project can configure some of it, and this file is a description, not the source.

    python -c "from claims_ledger import STATUSES, ACTS, GRADES, KINDS
    print('statuses', STATUSES); print('acts', ACTS)
    print('grades', GRADES); print('kinds', KINDS)"

For the parts a project configures — which evidence types exist, which authors may write
verdicts, which files are documents — ask the loaded configuration:

    python -c "from claims_ledger import open_ledger
    k = open_ledger().config
    print(k.evidence_types); print(k.verdict_authors); print(k.documents)"

## Statuses

A status is derived from the entry's verdict list; it is never stored. `claims-ledger
status` prints what each entry derives to now.

| status | what it says |
| --- | --- |
| `open` | stated, nothing has been recorded against it |
| `corroborated` | a verdict records independent support |
| `contested` | a verdict records a question against it |
| `refuted` | a verdict records that it does not hold |
| `superseded` | a successor entry replaces it |
| `retracted` | its author withdrew it |
| `non-comparable` | it was measured under conditions that do not compare |

The last four are terminal: they stop the walk, so a verdict appended after one does not
move the status. `contested` and `corroborated` are not terminal, so an entry can pass
through either and come out the other side.

## Acts

An act is how a citation names an entry, and it is legal against a set of statuses.

| act | legal against |
| --- | --- |
| `cites-as-live` | `open`, `corroborated` |
| `cites-as-contested` | `contested` |
| `challenges` | `open`, `corroborated`, `contested` |
| `cites-as-fallen` | every status |

`challenges` is written as an `entry:` ground by an entry disputing another; the other
three appear in documents, written inline as `(A0007-a-slug, cites-as-live)`, and in an
entry's `## References` rows.

`claims-ledger references` states the allowed set in its own findings, which is the
authority when this table and the installed version disagree.

## Grades

A grade says how strong the grounds are, and the checkers hold an entry to it.
`claims-ledger new --help` lists them with what each requires; `asserted` forbids an
evidence ground and never goes stale, while `measured` and above require one and take a
pin that `freshness` watches.

## Kinds

`claim`, `prediction` and `hypothesis`. A prediction carries a credence and the
observation that would settle it; an open hypothesis is expected to appear in a roster
document if the project configures one.

## Pointer types

A ground, and a verdict's evidence, is a typed pointer. Four names are reserved across
every project — `entry`, `source`, `search` and `defect` — and the evidence types are
configured. Print `evidence_types` as above to see what this project accepts.

A sectioned evidence type names a span within an artifact and may carry a revision:

    <type>: <path> § "<section>" @<revision>

What counts as a section is a per-project pattern, so the same syntax addresses a
definition in a module, a table in a settings file, or a heading in a document.
