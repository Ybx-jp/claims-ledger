# Example repository portfolio

This directory contains four repository templates that tell one small product story:

The [concept-grouped feature guide](FEATURES.md) explains every exercised capability
with exact excerpts from these repositories; [FEATURE_MATRIX.md](FEATURE_MATRIX.md) is
the compact index.

- `ui-webapp` renders a claim-risk banner from an API response.
- `backend-service` computes that response.
- `research-repo` records the synthetic study behind the threshold.
- `documentation-repo` publishes the operator-facing explanation.

The application code, measurements, and prose are intentionally plausible fiction. The
claims ledgers are real. `materialize.py` turns the templates into four independent Git
repositories, registers the cross-repository artifacts as content-addressed sources,
pins local evidence to real commits, computes every `verbatim_sha`, installs the real
pre-commit hook, and runs all five checkers.

```console
$ python examples/materialize.py /tmp/claims-ledger-portfolio
ui-webapp: check passed
backend-service: check passed
research-repo: check passed
documentation-repo: check passed
portfolio: 4 repositories and 7 cross-repository snapshots verified
```

The generated repositories are disposable, ordinary repositories: enter any one and run
`python -m claims_ledger check`, `status`, `source list`, or another command normally.
Use an environment where this checkout is installed (`uv run` is sufficient here).

## What is demonstrated where

| Capability | Example |
|---|---|
| claim roles, grades, source quotes, fingerprints | all four repositories |
| custom code-section evidence | UI (`export function`) and backend (`def`) |
| whole-file evidence | research experiment and documentation runbook |
| cross-repository provenance | registered snapshots copied from the other three repositories |
| document citations in both directions | every repository README; research roster |
| prediction, credence, and resolution condition | research `R0002` |
| hypothesis, falsifier, and checked roster | research `R0003` and `ROSTER.md` |
| absence claim with a recorded search | research `R0004` |
| append-only verdicts and derived statuses | research entries |
| supersession chain | research `R0005` → `R0006` |
| challenge propagation | research `R0007` challenged by `R0008` |
| immutable history and commit pins | the two commits made in every generated repository |
| source registry and portable committed bytes | `ledger/sources.jsonl` plus `evidence/` or `sources/` |
| pre-commit enforcement | installed in each generated repository |

## The repository boundary

An `entry:` pointer is intentionally local to one ledger, and configured paths may not
escape a repository root. The examples do not weaken that confinement. A repository
crosses the boundary by exporting an artifact (API contract, UI behavior contract, or
research summary); the consuming repository commits an exact snapshot and registers it
as a source. `portfolio.json` records every origin/snapshot pair, and materialization
fails unless all pairs are byte-identical. This lets claims span repositories while each
clone remains independently and reproducibly checkable.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../docs/figures/portfolio-dark.svg">
  <img alt="Top, one bridge end to end: backend-service owns openapi.yaml; a dashed repository boundary is crossed by an exact copy, evidence/backend-openapi.yaml, committed in ui-webapp; that copy is registered in ui-webapp's ledger/sources.jsonl as backend-contract with its sha256; and entry U0001 cites it as a source ground. Bottom, a matrix of the three exported artifacts against the four repositories, showing the seven origin-snapshot pairs, the source id each is registered under, and which entry cites it; research-repo consumes nothing." src="../docs/figures/portfolio.svg" width="960">
</picture>

The templates contain `@BASE@` commit placeholders and zero fingerprints, so they are
not ledgers by themselves. That is unavoidable for a checked-in template: a real commit
object belongs to the repository being generated. `materialize.py` is the executable
specification and `tests/test_examples.py` exercises it from scratch.

