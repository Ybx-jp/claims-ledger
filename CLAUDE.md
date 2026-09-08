# Working in this repository

This package holds a ledger of the claims about *itself*. Eleven entries under `ledger/`
— eight live and three superseded — pinned to the code that keeps them true and cited from the
README sentence and the docstring that state the same commitment in prose.
`claims-ledger check` runs in the pre-commit hook and again in CI.

**Read `docs/OPERATING.md` first.** It is the authority on running a ledger that pins
commits — the history-rewrite hazard, the two-commit shape for landing an entry, and the
order in which a drifted claim is repaired. It ships with the package, so it is written
for any project, not just this one. What follows is only what is specific to this
repository.

## Merge commits only

Enforced in two places, neither of which is this file: `allow_squash_merge` and
`allow_rebase_merge` are false on the GitHub repository, and
`examples/agent-harness/merge-guard.sh` refuses the local commands. The expected verdicts
for that guard are committed beside it in `merge-guard.cases`; run
`bash examples/agent-harness/merge-guard-test.sh` after touching either.

The reason is in `docs/OPERATING.md`. The short of it: the entries pin commit
`4023af40` — L0009 and L0010 pin later commits — and a rewrite that drops one costs a
supersession per entry pinned into it.

## What the checkers read here

`documents` in `[tool.claims-ledger]` is a list of single-level globs. It deliberately
does not reach `src/claims_ledger/corpus/` or `examples/`: both carry citations of ids
that live in other ledgers, and a glob that reached them would turn fixtures into
failures. Widening one is a change to run before it is committed.

`CLAUDE.md` is a configured document — it states commitments in the same voice the README
does, so a citation written here is checked. `.claude/` is not, which is why the skill
there can show citation syntax literally.

## The agent hooks live in `examples/`

`.claude/settings.json` points at `examples/agent-harness/`, not at a private copy. The
hooks are an example that ships to readers and the thing this repository actually runs;
keeping one copy is what stops the example rotting. Nothing in them is
repository-specific — the interpreter is discovered and the document list is asked of the
package — so keep it that way when editing.

## The pre-commit hook is not tracked

It lives in `.git/hooks/pre-commit`, written by `claims-ledger hook --install`, naming the
installing interpreter absolutely. A fresh clone has no hook until someone runs that
command; CI is the only backstop until they do.

## Adding a corpus seed

Four places must agree, and the tests enforce three of them: the seed directory under
`src/claims_ledger/corpus/seeds/`, a row naming it in `src/claims_ledger/corpus/README.md`,
the count in `tests/test_corpus_integrity.py`, and the counts in `README.md` and
`QUALITY.md`. A seed can only build linear, append-only history — there is no way to make
a commit unreachable — so a defect that depends on a rewrite is seeded by writing the
end state the rewrite would produce.

## Fixes for a QE pass get a consultation, not another pass

When a quality-engineering audit produces a list of fixes, the fixes are reviewed by a
`qe` consultation before merge — not by a further audit pass over the same ground.
