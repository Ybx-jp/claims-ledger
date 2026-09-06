# The revert experiment, run against the sixth pass's fixes

The sixth pass asked for this before the next pass calls these fixes done, and the fifth
pass's run is why: it found that one of the thirty-one regressions counted as evidence was
green over its own deleted fix. A count of passing regressions is not a claim until each
one has been shown to detect the loss of the thing it holds.

Method as before, with one addition. The fix commit is split into one patch per hunk and
one per file (`split.sh`); each is reverse-applied alone to a clean `git archive` of the
tree; the **43 regressions this pass added or flipped** (`regressions.txt`) are run against
it, with the test files held at HEAD throughout. Two controls: the import is asserted to
resolve inside the copy rather than in the editable install, and a no-revert run gives
`43 passed`, `76/76 seeds pass`.

**The addition: the corpus runs too.** The fifth pass's harness ran pytest only, so a seed
that detects nothing would have been reported as a hunk nothing detects. Running it changed
the answer for real hunks — `corpus/run.py`'s staging fix among them.

## Results

| | |
|---|---|
| hunks, across 25 files | 57 |
| reverted individually | 56 |
| not independently revertible | 1 — `import re` in `freshness.py`, which breaks its own module; reached by the whole-file revert (8 regressions red, corpus 75/76) |
| hunks whose removal turned something red | 40 |
| hunks whose removal changed nothing | 16 |
| **regressions red under at least one revert** | **39 of 43** |

`results-by-hunk.jsonl` and `results-by-file.jsonl` are the raw records, and together they
are a fix→regression map: for every hunk, which regressions its removal breaks.

## The sixteen hunks that changed nothing

Fifteen are prose — `CHANGELOG.md`, `RELEASING.md`, `docs/FRESHNESS.md`, `docs/SCHEMA.md`,
`corpus/README.md` — plus two data hunks, and the reason each is inert is worth stating
rather than assuming:

- `D05-dead-pointer/expected.json` **hunk 31** of two: the second hunk of the same file
  carries the rows, and the whole-file revert takes the seed to `75/76`.
- `D53-…/commits/03/docs/note-100.md`: reverting it deletes the note at commit 03 rather
  than editing it, and a deletion is a touch too — the seed's subject is that *any* touch
  followed by a restoration launders nothing, so its verdict does not move. The
  whole-file reverts of the other four D53 states each take the corpus to `75/76`.

The sixteenth is code, and it is inert on purpose: **hunk 49**, which drops
`if root is not None and` from `append_verdict`'s guard. With `root` now a required
keyword-only parameter (hunk 48, which *is* caught), the `is not None` test can never be
false, so removing it is a no-op. Hunk 48 is what carries the change.

## The four regressions no revert turns red

None is a second HIGH-55, and each is a different reason:

- `test_a_broken_git_is_not_a_freshness_check_that_ran`,
  `test_a_broken_git_is_not_settled_as_pointers_that_do_not_resolve`,
  `test_a_document_unreadable_only_after_the_ledger_listed_it_is_not_silent` — the three
  HIGH-59 gap closures over report sites that **already existed**. This pass added the
  coverage, not the code, so there is no hunk of this commit whose removal could break
  them. They were verified the way that class has to be: by neutering the report site each
  one exists for (`.qe/probe6/mutate_one.py`) and watching the test go red.
- `test_new_does_not_scaffold_an_entry_through_a_link_that_leaves_the_root` — held by
  `load_entries`' refusal of a symlink to nothing, which fires before the new guard does.
  Its docstring says so, and `test_every_write_asks_where_the_link_leads` is what holds the
  guard itself.

## Re-running it

    .qe/probe7/revert-experiment/list_regressions.sh <base>     # regressions.txt
    .qe/probe7/revert-experiment/split.sh <fix-commit> <outdir>
    ls <outdir>/hunks | sed 's/\.patch$//' | sort -n \
      | xargs -P 6 -I{} .qe/probe7/revert-experiment/run_one.sh <outdir>/hunks/{}.patch hunk-{}

About four minutes at `-P 6`. Run it against the next pass's fixes before calling them done.
