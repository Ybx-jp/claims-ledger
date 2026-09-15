# Checked feature matrix

This matrix names a concrete witness for each public feature the examples cover. Two
commands are deliberately outside them: `neighbours`, which is advisory and decides
nothing, and `harness`, which installs the agent hooks into a project rather than acting on
a ledger.

The [feature guide](FEATURES.md) explains the same coverage by concept and includes
repository excerpts. Generated repositories replace `@BASE@` with real commit IDs and
compute the zero fingerprints. The last seven rows are built by `concurrent-ids`, which is
not part of the four-repository portfolio: it needs two lines of work, and each of the four
has one.

| Feature | Witness |
|---|---|
| Assertion, Scope, Grounds, Warrant, Backing | every entry |
| claim, prediction, hypothesis | research R0001, R0002, R0003 |
| asserted, argued, measured, controlled, preregistered | research R0004/R0002/R0009, UI U0001, research R0001 |
| source, entry, search, sectioned and plain evidence pointers | research ledger |
| custom section regex | UI `renderRiskBanner`; backend `classify_risk` |
| `@working` freshness opt-out | UI U0002 |
| checked quotes and source registry | every repository |
| multiple backing blocks | documentation D0001 |
| document references and document exclusions | UI and documentation configs |
| hypothesis roster | research R0003 and `ROSTER.md` |
| credence and `resolves_when` | research R0002 and R0003 |
| open, corroborated, contested | research R0002, R0009, R0007 |
| refuted, superseded, retracted, non-comparable | research R0011, R0005, R0010, R0012 |
| challenge propagation | research R0008 → R0007 |
| supersession in both directions | research R0005 → R0006 |
| absence-search rule | research R0004 |
| archived-prefix quarantine | research `Q`; documentation `Z` |
| `validate` and immutable Git history | two-commit materialization; the rewritten branch in `concurrent-ids` |
| `resolve` | registered sources and pinned artifacts in every repository |
| `references` | every README; research roster |
| `propagate` | research R0007/R0008 |
| `freshness` and section-local comparison | UI drift regression test |
| `sha --write`, `source add/list`, `status`, `hook --install` | materializer and tests |
| all five checks together | materializer calls `check` in every repository |
| red-team corpus | the package-level `claims-ledger corpus` command |
| repository-wide id allocation | `concurrent-ids`: `new` with no id steps past the number a branch holds |
| two entries carrying one number | `concurrent-ids`, and corpus seed `D66-two-entries-carrying-one-number` |
| `merge-renumber` policy | `concurrent-ids` configures `refuse` before either branch is cut |
| `renumber --on-merge` | `concurrent-ids`: the merge is denied and the denial names the repair |
| `renumber` dry run and `--write` | `concurrent-ids`: the plan writes nothing; the rewrite moves the branch |
| a ground by value surviving a rewrite | `concurrent-ids`: the pinned digest is re-anchored with proof |
| `init` and `new` | `concurrent-ids` starts from `init`, the way a new project does |

Cross-repository source federation is described in `examples/README.md` and verified
against the seven origin/snapshot pairs in `portfolio.json`. Native cross-ledger
`entry:` dependencies and automatic cross-ledger propagation are not current features.
