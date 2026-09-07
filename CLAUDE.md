# Working in this repository

This package holds a ledger of claims about *itself*. Eight entries under `ledger/`
are pinned to the code that keeps them true, and cited from the README sentence and
the docstring that state the same commitment in prose. `claims-ledger check` runs in
the pre-commit hook and again in CI.

That arrangement is cheap to maintain and easy to destroy by accident. The standing
constraints below are the ones that are *not* enforced by a checker — a checker can
only tell you afterwards that the pins are broken, not stop you breaking them.

## Never squash. Never rebase-merge.

A `code:` ground pins a section of a file **at a commit**: `@4023af40…`. Squashing a
pull request replaces those commits with a new one; a rebase merge rewrites them. Either
way `resolve` can no longer find the commit a ground names, every pinned entry fails at
once, and the only repair is a supersession per entry.

**Merge commits only, for every branch that lands on `main`.** If a merge has already
been squashed, do not paper over it — say so, and expect the repair to be a full round
of supersessions.

`.claude/hooks/merge-guard.sh` refuses the two commands that do it, and
`.claude/hooks/merge-guard.cases` holds its expected verdicts — including the false
positives the anchoring exists to prevent. Run `bash .claude/hooks/merge-guard-test.sh`
after touching either. The hook cannot reach GitHub's own merge button; that needs
`allow_squash_merge` and `allow_rebase_merge` set false on the repository.

## Adding an entry takes two commits

An entry's citation lives inside the section that entry pins — the docstring sits in the
function. So a single commit is unpinnable: the entry would have to name a commit that
does not exist yet, and pinning the commit before it flags as `moved` on the first run.

1. **Commit one:** the citing prose — the README sentence, the docstring, any config.
2. **Commit two:** the entry files, with their grounds pinned to commit one.

Commit one names an entry id that does not exist yet, which is exactly the failure
`references` is built to catch, so the installed pre-commit hook will refuse it. That
collision is real and is not a reason to drop the citation: commit one goes in with
`git commit --no-verify`, and commit two is committed normally, with the hook running
over the finished pair. Run `claims-ledger check` yourself before committing two —
between the two commits the tree is knowingly inconsistent, and the hook is the only
thing that would otherwise tell you when it stopped being.

## Pin sections, never files

`scoped` compares only the named section, so a pin on a function costs a supersession
only when that function changes. A pin on a whole file costs one per commit that touches
it. The section patterns live in `[tool.claims-ledger.section-patterns]` in
`pyproject.toml`; `code` matches a top-level `def`, `class` or assignment and runs to the
next one.

## The grade decides what goes stale

- `measured` — a claim that the code *does* something. Takes a `code:` or `toml:` pin,
  and `freshness` watches it.
- `asserted` — a choice the project *made*. Forbids an evidence ground, so it never
  goes stale.

Choosing `measured` for a claim that is really a preference buys a supersession every
time the file is reformatted, for nothing.

## Sources are for frozen text only

`resolve` hard-fails when a registered source's bytes stop hashing to its row — there is
no flag stage. Registering a living file with `--keep-path` breaks `check` on that file's
next edit. To quote the README or an audit report, snapshot it at a commit with
`git show` into a committed directory and register the snapshot.

## Which files the checkers read

`documents` in `[tool.claims-ledger]` is a list of single-level globs. It deliberately
does not reach `src/claims_ledger/corpus/` or `examples/`: those carry citations of ids
that live in *other* ledgers, and a glob that reached them would turn fixtures into
failures. Widening a glob is a change that must be run before it is committed.

Anything under `.claude/` is not a configured document, which is why the skills there can
show citation syntax literally.

## The pre-commit hook is not tracked

It lives in `.git/hooks/pre-commit` and is written by `claims-ledger hook --install`,
naming the installing interpreter by absolute path. A fresh clone has no hook until
someone runs that command; CI is the only backstop until they do.

## Fixes for a QE pass get a consultation, not another pass

When a quality-engineering audit produces a list of fixes, the fixes are reviewed by a
`qe` consultation before merge — not by a further audit pass over the same ground.

## When a pin has already drifted

Use the `repair-a-drifted-pin` skill. Do not hand-edit an entry's Verdicts section, and
do not delete a `contested` verdict to make `check` pass.
