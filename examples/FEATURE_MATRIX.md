# Checked feature matrix

This matrix names a concrete witness for each public feature. The
[feature guide](FEATURES.md) explains the same coverage by concept and includes
repository excerpts. Generated repositories
replace `@BASE@` with real commit IDs and compute the zero fingerprints.

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
| `validate` and immutable Git history | two-commit materialization |
| `resolve` | registered sources and pinned artifacts in every repository |
| `references` | every README; research roster |
| `propagate` | research R0007/R0008 |
| `freshness` and section-local comparison | UI drift regression test |
| `sha --write`, `source add/list`, `status`, `hook --install` | materializer and tests |
| all five checks together | materializer calls `check` in every repository |
| red-team corpus | the package-level `claims-ledger corpus` command |

Cross-repository source federation is described in `examples/README.md` and verified
against the seven origin/snapshot pairs in `portfolio.json`. Native cross-ledger
`entry:` dependencies and automatic cross-ledger propagation are not current features.
