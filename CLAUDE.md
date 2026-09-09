# Working in this repository

This package holds a ledger of the claims about *itself*: entries under `ledger/`
pinned to the code that keeps them true and cited from the README sentence and the
docstring that state the same commitment in prose.
`claims-ledger check` runs in the pre-commit hook and again in CI.

**Read `docs/OPERATING.md` first.** It is the authority on running a ledger that pins
commits — the history-rewrite hazard, the two-commit shape for landing an entry, and the
order in which a drifted claim is repaired. It ships with the package, so it is written
for any project, not just this one. What follows is only what is specific to this
repository.

## Merge commits only

Enforced in two places, neither of which is this file: `allow_squash_merge` and
`allow_rebase_merge` are false on the GitHub repository, and
`src/claims_ledger/resources/agent-harness/merge-guard.sh` refuses the local commands. The
expected verdicts for that guard are committed beside it in `merge-guard.cases`; run
`bash src/claims_ledger/resources/agent-harness/merge-guard-test.sh` after touching either.

The reason is in `docs/OPERATING.md`. The short of it: the entries pin commits, many
of them, and a rewrite that drops one costs a supersession per ground pinned into it.
`claims-ledger status` is the count; it is not repeated here, because a tally in prose
is one more thing that goes stale every time an entry lands.

## What the checkers read here

`documents` in `[tool.claims-ledger]` is a list of single-level globs. It deliberately
does not reach `src/claims_ledger/corpus/`, `src/claims_ledger/resources/` or `examples/`:
they carry citations of ids that live in other ledgers, or show the syntax to a reader,
and a glob that reached them would turn fixtures and examples into failures. Widening
one is a change to run before it is committed.

`CLAUDE.md` is a configured document — it states commitments in the same voice the README
does, so a citation written here is checked. Neither `.claude/` nor `examples/` is, and
`src/claims_ledger/*.py` is single-level so it does not reach the shipped skills either —
which is why they can show citation syntax literally. A skill moved inside the document
globs, or a glob widened to `src/claims_ledger/**`, would have those examples checked as
real citations and fail.

## The agent hooks and skills ship in the package

They live in `src/claims_ledger/resources/`, which is inside the wheel, and
`claims-ledger harness install` writes them into a project that has never seen this
repository — `.claude/`, `.cursor/`, `.codex/` or `.agents/`, one row of `TARGETS` each.

`.claude/settings.json` here points straight at
`src/claims_ledger/resources/agent-harness/`, so the hooks this repository runs are the
shipped files themselves and there is no second copy of them to rot.

`.claude/skills/` cannot be that, and the reason is worth knowing before someone
reinstates the shortcut it replaced. It held symlinks into the package. hatchling follows
a symlink out of `.claude/` into `src/`, counts each file as seen at a path no
distribution includes, and drops the real one — all three skills were missing from the
wheel and the sdist, with no error anywhere, so `harness install` from a released copy
wrote no skills and reported success. So `.claude/skills/` is a local install now,
`.gitignore`d like the pre-commit hook and written the same way:

    claims-ledger harness install --agent claude --no-hooks

after a fresh clone, and again after editing a shipped skill. `tests/test_harness.py`
holds the rule that no symlink in this repository reaches into the package, and builds a
wheel to count what it carries.

Nothing in the hooks or the skills is repository-specific — the interpreter is discovered,
the project root is discovered, the document list is asked of the package, act legality is
read from what `references` said, and counts are asked of `claims-ledger status` rather
than written down — so keep it that way when editing. A path counted in `..` is the one
that would break: the same script runs from `src/claims_ledger/resources/agent-harness/`
here and from `.claude/hooks/` where it is installed.

The hooks name the skills and the skills name each other. `merge-guard.sh` has committed
expected verdicts; the others do not, so a change to one is checked by running it, and
`tests/test_harness.py` holds what the installer promises.

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
