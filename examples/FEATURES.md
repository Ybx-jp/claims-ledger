# Feature guide

The four example repositories tell one synthetic product story while exercising the
actual claims-ledger implementation. This guide groups those features by concept and
uses excerpts copied from the repository templates. The templates show `@BASE@` and a
zero `verbatim_sha`; materialization replaces both with values belonging to each newly
created Git repository.

Start with:

```console
uv run python examples/materialize.py /tmp/claims-ledger-portfolio
cd /tmp/claims-ledger-portfolio/research-repo
uv run claims-ledger check
```

## 1. Claim records

### The five roles

A claim record keeps the project's statement separate from its evidence and reasoning:

- **Assertion** is what the project says.
- **Scope** bounds the metric, cohort, and condition.
- **Grounds** names the evidence used.
- **Warrant** explains why those grounds support the assertion.
- **Backing** preserves exact source language and attribution.

The documentation repository shows the separation particularly clearly.

<!-- snippet: templates/documentation-repo/ledger/entries/D0001-review-boundary-is-inclusive.md -->
```markdown
## Assertion

Nimbus sends risk scores at or above 0.72 to review.

## Scope

metric: documented review decision boundary
cohort: Nimbus API and Console contracts
condition: default example policy

## Grounds

- source: backend-contract · GET /claims/{id}/risk
- source: ui-contract · banner rule

## Warrant

Two independently versioned repository contracts state the same inclusive boundary; the
documentation therefore uses their shared wording without claiming a measurement.
```
<!-- /snippet -->

Assertions contain no quotation marks. Quotes belong in Backing, where the resolver can
hold them to registered bytes and their named speaker.

### Kinds: claims, predictions, and hypotheses

A plain `claim` states what the project currently holds. A `prediction` adds a
credence and the observation that will resolve it.

<!-- snippet: templates/research-repo/ledger/entries/R0002-review-latency-stays-low.md -->
```yaml
id: R0002-review-latency-stays-low
kind: prediction
stated: 2026-09-06T09:05:00-07:00
author: main
grade: argued
credence: 0.7
resolves_when: the preregistered pilot-b run reports median review latency
supersedes: none
verbatim_sha: 0
```
<!-- /snippet -->

A `hypothesis` has the same explicit uncertainty fields, must cite motivating entries,
and must state a falsifier in its Warrant.

<!-- snippet: templates/research-repo/ledger/entries/R0003-threshold-generalizes.md -->
```markdown
## Grounds

- entry: R0001-threshold-balances-review-errors · cites-as-live
- entry: R0002-review-latency-stays-low · cites-as-live

## Warrant

The first pilot leaves margin on both rates and the latency prediction implies adequate
review capacity. Falsified if either preregistered pilot-b error rate exceeds its margin.
```
<!-- /snippet -->

### Evidence grades

The examples exercise the full grade vocabulary:

| Grade | Meaning in the examples | Witness |
|---|---|---|
| `asserted` | source-backed statement without project measurement | research R0004; documentation D0001 |
| `argued` | conclusion derived from other entries | research R0002 and R0003 |
| `measured` | local artifact records an observation | backend B0001; research R0009 |
| `controlled` | controlled implementation condition | UI U0001 |
| `preregistered` | measurement fixed before the demonstration run | research R0001 |

Grades constrain Grounds: measured and stronger entries require a configured evidence
pointer, while asserted entries may use sources or searches but not project measurement.

## 2. Evidence and provenance

### Typed pointers

Grounds use typed pointers rather than prose citations. R0001 combines a whole-file
experiment pinned to Git with a registered external source.

<!-- snippet: templates/research-repo/ledger/entries/R0001-threshold-balances-review-errors.md -->
```markdown
## Grounds

- experiment: experiments/threshold.csv @@BASE@
- source: latency-paper · demonstration cohort
```
<!-- /snippet -->

The portfolio exercises:

- `source:` for registered, hash-checked text;
- `entry:` for local dependencies and challenges;
- `search:` for bounded absence or priority claims;
- `code:` and `lab:` for named sections at a commit;
- `experiment:` and `run:` for whole files at a commit.

The double `@` shown in templates is intentional: replacing the `@BASE@` token leaves
one pointer delimiter followed by the generated commit ID.

### Absence claims carry their search

R0004 says that something was not found, so it records the corpus, query, and date rather
than treating silence as positive evidence.

<!-- snippet: templates/research-repo/ledger/entries/R0004-no-calibration-study-found.md -->
```markdown
## Assertion

A real calibration study was not found in the synthetic source scan.

## Scope

metric: presence of a real calibration study
cohort: the two registered synthetic sources
condition: repository scan on 2026-09-06

## Grounds

- search: corpus=registered synthetic sources; query="real calibration study"; date=2026-09-06
```
<!-- /snippet -->

The validator applies the same rule to priority language such as `first`, `novel`,
and `unprecedented`.

### Registered source bytes and exact quotations

Materialization registers every source through the public authoring command with
`--keep-path`. That makes the synthetic source bytes portable and committed while the
registry still records their SHA-256 digest.

<!-- snippet: materialize.py -->
```python
        args = [
            "source",
            "add",
            path,
            "--id",
            source_id,
            "--type",
            source_type,
            "--citation",
            citation,
            "--retrieved",
            "2026-09-06",
            "--keep-path",
        ]
```
<!-- /snippet -->

Backing may contain more than one independently resolved quotation. D0001 uses both the
backend and UI contracts.

<!-- snippet: templates/documentation-repo/ledger/entries/D0001-review-boundary-is-inclusive.md -->
```markdown
## Backing

- source: backend-contract · GET /claims/{id}/risk
  speaker: Nimbus service maintainers
  quote: "description: Scores greater than or equal to 0.72 require review."
- source: ui-contract · banner rule
  speaker: Nimbus Console maintainers
  quote: "The console displays a review banner when the API risk score is at least 0.72."
```
<!-- /snippet -->

The research repository also registers a `consultation` source with its expert as the
speaker. Its deliberately paraphrased quotation is retained only in a correctly
retracted entry, demonstrating that retraction preserves the defective record.

### Verbatim fingerprints

`verbatim_sha` fingerprints Scope and Backing, including attribution. Materialization
runs the real writer before committing the entries.

<!-- snippet: materialize.py -->
```python
        entry_paths = [str(path.relative_to(repo)) for path in sorted(entries_dir.glob("*.md"))]
        ledger(repo, "sha", "--write", *entry_paths)
        run("git", "add", "ledger/entries", cwd=repo)
        run("git", "commit", "-q", "-m", "Add checked claims ledger", cwd=repo)
```
<!-- /snippet -->

Once committed, a changed fingerprint belongs in a successor entry rather than as an edit
to the frozen record.

## 3. Repository boundaries

### Source federation across repositories

Native `entry:` pointers are local to one ledger. The portfolio crosses repository
boundaries by copying producer-owned artifacts into consumers and registering the copies
as sources. The manifest makes each bridge explicit.

<!-- snippet: portfolio.json -->
```json
  "snapshots": [
    ["backend-service/openapi.yaml", "ui-webapp/evidence/backend-openapi.yaml"],
    ["research-repo/reports/summary.txt", "ui-webapp/evidence/research-summary.txt"],
    ["ui-webapp/docs/behavior-contract.txt", "backend-service/evidence/ui-behavior-contract.txt"],
    ["research-repo/reports/summary.txt", "backend-service/evidence/research-summary.txt"],
```
<!-- /snippet -->

Materialization copies those files before initializing the ledgers and later verifies
every origin/snapshot pair byte for byte.

<!-- snippet: materialize.py -->
```python
    for origin, snapshot in SPEC["snapshots"]:
        target = destination / snapshot
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(destination / origin, target)
```
<!-- /snippet -->

This is cross-repository provenance, not automatic cross-ledger propagation. Each
generated clone remains independently checkable and no configuration path escapes its
repository root.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../docs/figures/portfolio-dark.svg">
  <img alt="Top, one bridge end to end: backend-service owns openapi.yaml; a dashed repository boundary is crossed by an exact copy, evidence/backend-openapi.yaml, committed in ui-webapp; that copy is registered in ui-webapp's ledger/sources.jsonl as backend-contract with its sha256; and entry U0001 cites it as a source ground. Bottom, a matrix of the three exported artifacts against the four repositories, showing the seven origin-snapshot pairs, the source id each is registered under, and which entry cites it; research-repo consumes nothing." src="../docs/figures/portfolio.svg" width="960">
</picture>

## 4. Git history and freshness

### Real commit pins

Every generated repository gets two commits. The first contains the application,
research, or documentation artifacts and registered sources. Its object ID replaces
`@BASE@` in the entries, which are fingerprinted and committed second.

<!-- snippet: materialize.py -->
```python
        run("git", "add", ".", cwd=repo)
        run("git", "commit", "-q", "-m", "Add example artifacts and registered sources", cwd=repo)
        base = run("git", "rev-parse", "HEAD", cwd=repo).strip()

        entries_dir = repo / "ledger" / "entries"
        entries_dir.mkdir(parents=True)
        for filename, text in held_entries[name].items():
            (entries_dir / filename).write_text(text.replace("@BASE@", base), encoding="utf-8")
```
<!-- /snippet -->

That history lets `validate` prove the frozen region and existing verdicts were not
rewritten, and lets `freshness` compare present artifacts with the exact pinned commit.

### Section-scoped evidence

The UI and backend configure evidence sections using their languages' definition syntax.

<!-- snippet: templates/ui-webapp/claims-ledger.toml -->
```toml
evidence-sectioned = ["code"]
evidence-plain = ["run"]
verdict-authors = ["main", "propagation"]
propagation-author = "propagation"
roster = "ROSTER.md"

[tool.claims-ledger.section-patterns]
code = '^export function[ \t]+{name}\b'
```
<!-- /snippet -->

U0001 then pins only one function.

<!-- snippet: templates/ui-webapp/ledger/entries/U0001-ui-banner-uses-service-threshold.md -->
```markdown
## Grounds

- code: src/dashboard.ts § "renderRiskBanner" @@BASE@
- source: backend-contract · GET /claims/{id}/risk
```
<!-- /snippet -->

The regression test changes `renderFooter` and observes no drift, then changes
`renderRiskBanner`, receives a freshness flag, runs `freshness --write`, and verifies
that the machine-authored contested verdict discharges that exact drift.

### Explicitly unpinned working evidence

A low-risk illustrative claim can opt out of historical freshness with `@working`.

<!-- snippet: templates/ui-webapp/ledger/entries/U0002-footer-build-is-visible.md -->
```markdown
## Grounds

- code: src/dashboard.ts § "renderFooter" @working
```
<!-- /snippet -->

The pointer still resolves against the current file, but freshness does not claim that it
is anchored to history.

## 5. References and maintained views

### Bidirectional document citations

Documents cite entries inline with an explicit act.

<!-- snippet: templates/documentation-repo/docs/operator-guide.md -->
```markdown
Scores at or above 0.72 enter review
(D0001-review-boundary-is-inclusive, cites-as-live). The example response procedure is
recorded separately (D0002-review-response-is-documented, cites-as-live).
```
<!-- /snippet -->

Each entry lists the document in the other direction.

<!-- snippet: templates/documentation-repo/ledger/entries/D0001-review-boundary-is-inclusive.md -->
```markdown
## References

- README.md · standing · cites-as-live
- docs/operator-guide.md · standing · cites-as-live
```
<!-- /snippet -->

`references` checks existence, status compatibility, and both directions. The research
findings document also demonstrates `cites-as-contested` and `cites-as-fallen`;
entry-to-entry challenges provide the fourth act.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../docs/figures/references-dark.svg">
  <img alt="Left, a document, docs/operator-guide.md, citing an entry inline as D0001-review-boundary-is-inclusive with the act cites-as-live. Right, the entry, whose References section lists that document as standing, cites-as-live, and whose status is open because it has no verdicts. An arrow runs each way: the document declares the act, the entry lists the document. Below, a matrix of the four citation acts against the target statuses each is legal for: cites-as-live for open and corroborated; cites-as-contested for contested; cites-as-fallen for any; challenges for open, corroborated and contested, and only from an entry." src="../docs/figures/references.svg" width="960">
</picture>

### Standing versus record references

A `standing` reference is part of the current maintained view. A `record` reference
retains history without presenting the target as current.

<!-- snippet: templates/research-repo/ledger/entries/R0011-single-cohort-generalization-refuted.md -->
```markdown
## References

- reports/findings.md · record · cites-as-fallen
```
<!-- /snippet -->

### Checked hypothesis roster

Every non-terminal hypothesis appears exactly once in the configured roster, whose final
cell must equal the entry's derived status.

<!-- snippet: templates/research-repo/ROSTER.md -->
```markdown
| hypothesis | statement | motivating claims | falsifier | status |
|---|---|---|---|---|
| (R0003-threshold-generalizes, cites-as-live) | The threshold transfers to pilot-b | (R0001-threshold-balances-review-errors, cites-as-live); (R0002-review-latency-stays-low, cites-as-live) | either preregistered error rate exceeds its margin | open |
```
<!-- /snippet -->

This is deliberately hand-maintained and mechanically checked rather than generated.

### Included, excluded, and quarantined references

Document globs select prose that participates in checking, while exclusions remove
drafts or generated files. Archived ID prefixes can never be cited.

<!-- snippet: templates/documentation-repo/claims-ledger.toml -->
```toml
documents = ["README.md", "docs/*.md"]
document-excludes = ["docs/draft-*.md"]
evidence-sectioned = ["note"]
evidence-plain = ["run"]
verdict-authors = ["main", "propagation"]
propagation-author = "propagation"
roster = "ROSTER.md"
archived-prefixes = ["Z"]
```
<!-- /snippet -->

The research repository separately quarantines the `Q` series.

## 6. Verdicts, statuses, and revision

### Status is derived

Entries do not store a status field. With no verdict they are `open`; otherwise the
last legal verdict derives one of `corroborated`, `contested`, `refuted`,
`superseded`, `retracted`, or `non-comparable`.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../docs/figures/status-derivation-dark.svg">
  <img alt="Left, an append-only verdict list whose last legal row derives the status. Right, the state diagram: open with no verdicts; corroborated and contested, which can re-verdict each other; and the four terminal statuses, refuted, superseded, retracted and non-comparable, after which a verdict is malformed, except that refuted or non-comparable may be followed by exactly one superseded." src="../docs/figures/status-derivation.svg" width="960">
</picture>

The research repository contains a green, checked witness for every status:

| Status | Witness |
|---|---|
| open | R0001, R0002, R0003, R0004, R0006, R0008 |
| corroborated | R0009 |
| contested | R0007 |
| refuted | R0011 |
| superseded | R0005 |
| retracted | R0010 |
| non-comparable | R0012 |

A corroborating verdict must introduce independent evidence not already present in
Grounds.

<!-- snippet: templates/research-repo/ledger/entries/R0009-threshold-direction-replicates.md -->
```markdown
## Verdicts

- 2026-09-06T09:45:00-07:00 · corroborated · grade: measured · author: main
  evidence: lab: lab/notes.md § "Replication sweep" @@BASE@
```
<!-- /snippet -->

### Append-only verdict history

Verdicts are appended below the marker and cannot later be edited or removed. Human
verdict authors must be configured; machine verdicts use the configured propagation
author and a constrained evidence shape.

A retraction records a defect in how the entry was made.

<!-- snippet: templates/research-repo/ledger/entries/R0010-consultation-wording-retracted.md -->
```markdown
## Verdicts

- 2026-09-06T09:55:00-07:00 · retracted · grade: asserted · author: main
  evidence: defect: Backing quote 1 is a paraphrase and does not verify against review-consult
  note: the defective making remains visible rather than being silently edited
```
<!-- /snippet -->

A non-comparable verdict records that evidence does not support the attempted comparison
without rewriting the original assertion.

### Supersession is two-sided

The predecessor carries a terminal verdict naming its successor.

<!-- snippet: templates/research-repo/ledger/entries/R0005-threshold-rounds-to-seven-tenths.md -->
```markdown
## Verdicts

- 2026-09-06T09:25:00-07:00 · superseded · grade: measured · author: main
  evidence: entry: R0006-threshold-displays-as-seventy-two-percent · supersedes
  note: replaced by the exact display value
```
<!-- /snippet -->

The successor points back in frontmatter.

<!-- snippet: templates/research-repo/ledger/entries/R0006-threshold-displays-as-seventy-two-percent.md -->
```yaml
id: R0006-threshold-displays-as-seventy-two-percent
kind: claim
stated: 2026-09-06T09:25:00-07:00
author: main
grade: measured
supersedes: R0005-threshold-rounds-to-seven-tenths
verbatim_sha: 0
```
<!-- /snippet -->

The checker rejects a fork, a missing reverse declaration, or a document that continues
to cite the predecessor as live.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../docs/figures/supersession-dark.svg">
  <img alt="Two entries side by side. The predecessor, R0005, carries a superseded verdict whose evidence names R0006 with the supersedes act; the successor, R0006, declares supersedes: R0005 in its frontmatter. One arrow runs forward from the verdict, one back from the frontmatter, and each side is checked against the other. Below, a chain of entries with a second successor branching off it, marked malformed: supersession is a chain, not a tree. The checker rejects three shapes: a fork, since an entry carries one superseded verdict; a missing reverse, a superseded verdict naming a successor that does not declare supersedes; and a stale citation, a document still citing the predecessor as live. Neither status is stored, and reinstatement is supersession: refuted or non-comparable may be followed by exactly one superseded verdict and nothing else." src="../docs/figures/supersession.svg" width="960">
</picture>

### Challenges and propagation

R0008 attacks R0007 with a typed `challenges` ground.

<!-- snippet: templates/research-repo/ledger/entries/R0008-one-cohort-cannot-establish-invariance.md -->
```markdown
## Grounds

- lab: lab/notes.md § "Threshold sweep" @@BASE@
- entry: R0007-threshold-is-cohort-invariant · challenges
```
<!-- /snippet -->

The challenged target carries the machine-authored contested verdict.

<!-- snippet: templates/research-repo/ledger/entries/R0007-threshold-is-cohort-invariant.md -->
```markdown
## Verdicts

- 2026-09-06T09:35:00-07:00 · contested · grade: measured · author: propagation
  evidence: entry: R0008-one-cohort-cannot-establish-invariance · challenges
  note: propagated from a challenges act
```
<!-- /snippet -->

`propagate --write` writes the same verdict shape when it finds a missing challenge or
a live dependency whose target has fallen. `freshness --write` also writes a contested
verdict, but names the changed pinned artifact and records the observed blob ID.

## 7. Checking and automation

### The five checks

| Command | Property exercised by the portfolio |
|---|---|
| `validate` | schema, grades, verdict legality, frozen entry regions, append-only verdicts |
| `resolve` | typed pointers, Git objects, source registry, exact quotes and speakers |
| `references` | entry acts, document back-references, roster, exclusions and quarantine |
| `propagate` | challenge and fallen-dependency contested verdicts |
| `freshness` | stable commit pins, scoped drift, withdrawal, and `@working` |
| `check` | all five in sequence |

Materialization refuses to report success unless the combined check passes in every
repository.

<!-- snippet: materialize.py -->
```python
        ledger(repo, "hook", "--install")
        ledger(repo, "check")
```
<!-- /snippet -->

Flags are review findings and normally exit zero. Failures gate. A write command reports
what it appended and exits nonzero for that run, requiring a clean rerun before commit.

### Authoring and inspection commands

The workflow itself exercises:

- `source add --keep-path` while registering producer snapshots;
- `sha --write` while finalizing draft entries;
- `hook --install` in every generated repository;
- `check` after each repository is built;
- `source list` and `status` in the regression tests;
- `freshness --write` in the scoped-drift regression.

The package also provides `init`, `new`, individual checker commands, and
`claims-ledger corpus`. The templates are richer than an `init` or `new` scaffold,
while the package-level test run proves all 76 adversarial corpus seeds.

### Pre-commit enforcement

The installed hook runs the staged forms of validation and freshness and the working-tree
forms of the other three checkers. It uses the absolute Python interpreter that installed
it, so Git does not depend on an activated virtual environment.

## 8. What a passing example means

A clean run establishes that the records are structurally valid, their pointers and
quotes resolve, citations agree with current statuses, required propagation is present,
and pinned evidence has not moved unnoticed. It does **not** establish that the synthetic
Nimbus claims are true. The research summary says so directly, and D0002 carries that
disclaimer as Backing.

Likewise, source federation proves that a consumer checked the exact exported bytes
listed in `portfolio.json`. It does not provide native cross-ledger dependency edges,
remote status lookup, or automatic propagation between repositories. Those would be new
product features rather than behaviors demonstrated here.

