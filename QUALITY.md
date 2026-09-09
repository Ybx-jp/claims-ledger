# How this package is tested

The product is a promise that four invariants hold over somebody else's files. A checker
that says "fine" over something it did not check is worse than no checker, because the
person now believes something. So the implementation is small — a dozen modules, no
runtime dependencies — and almost everything else in the repository exists to try to
make it lie.

That ratio is deliberate. It is the appropriate one for a checker and would be absurd for
most other packages.

## The four things that hold the checkers

**The red-team corpus** — 90 seeds under `src/claims_ledger/corpus/seeds`, each a small
ledger with its expected outcome committed beside it: one per defect class an audit
found, one per rule about not silently passing, plus known-good seeds every checker must
leave alone. It ships inside the wheel, so `claims-ledger corpus` is how an installed
copy proves itself on a machine nobody here has seen. The contract is symmetric — a seed
passes when every expected failure is produced *at the named place* and no checker trips
where the seed does not say it should. `src/claims_ledger/corpus/README.md` names the
rules the corpus does **not** hold up, and which tests hold them instead.

**The behavioural suite** — `tests/`, run by `pytest`. Organised by the property under
attack rather than by module: hostile and malformed input, immutability of the frozen
region, freshness semantics, the discharge protocol, git degradation, section scoping, the
write funnel, config boundaries, corpus integrity, the README's own quickstart, and the
record the package publishes about itself.

Not organised by *when* a defect was found. Filing a test under the audit pass that
produced it puts the only copy of a rule under a label that means nothing a release later,
and this suite carried three such files until the measurement showed fifteen of the rules
in them had no second holder. The finding ID is the key that survives instead: it is
unique across every pass, a test cites it, and `docs/audits/0.1.0.md` is where it is
written up.

**The invariant and metamorphic tests** — `tests/test_invariants.py`, which assert
properties that must hold across the whole surface rather than at one call site: every
write path idempotent, independence from orders the schema does not fix, normalization
invariance, append-only monotonicity, cross-checker consistency, and the corpus itself
used as a metamorphic base. Each property is grounded in a promise quoted from
`README.md` or `docs/SCHEMA.md`, cited in the test.

**The packaging checks** — CI builds the wheel, installs it into a clean environment, and
runs the corpus from a directory that is not the checkout, on Python 3.11 through 3.14
across Linux and macOS. The claim that an installed copy can prove itself is only worth
something if it is tested that way.

## What happens to a defect

Every defect that was real becomes a permanent case, and the case is checked to fail
against the unfixed code before the fix lands — a regression test nobody has watched go
red is a regression test nobody should trust. While a defect is open it is a **strict
xfail** naming the sentence it holds the code to, so it flips to a loud failure the
moment the fix arrives and cannot rot quietly. A suspected defect that turns out not to
be one is written down as such, with the reasoning, rather than deleted.

A change that moves a corpus seed's expected outcome is a methodology change, not a bug
fix; it goes in `CHANGELOG.md` with the seed named.

## The audit trail

`docs/audits/` holds the adversarial passes, one file per released version. For 0.1.0
that is six passes plus a fix-review gate that runs between the fixer and the merge —
findings, repro commands, the interpreter matrix, the packaging and filesystem edge
cases, and the disposition of each finding including the ones that were not defects.

It is long and it is a historical record, not documentation. Nothing in it needs to be
read to use or change this package. It exists because a fix whose defect nobody wrote
down gets reintroduced, and because "we tested it" is not a claim anyone should accept
without the list.

## Running all of it

See **Working on it** in `README.md` — the same five commands CI runs.
