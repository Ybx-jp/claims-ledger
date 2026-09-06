# Sixth pass — write paths and crash recovery

Verifying the fifth pass's six write-path findings (HIGH-39 … LOW-44) at `776500b`, then
attacking the atomic-write funnel the fixes introduced. Worktree `/tmp/qe6-write`. Every
repro is a real git repository; every interruption is a real `RLIMIT_FSIZE` in a child
process or a real `SIGKILL`; every newline case is real bytes.

## The six, verified

| Finding | Verdict | Evidence |
|---|---|---|
| HIGH-39 (CRLF frozen region) | FIXED | CRLF-committed entry: `propagate --write` leaves the frozen region byte-identical (`git diff --stat`: 4 insertions, 0 deletions). Hand-rewriting the frozen region to CRLF post-commit is caught — `the frozen region … not the same bytes`. `part1_all.py::high39` |
| HIGH-40 (registry glue) | FIXED | Registry missing its final newline: `source add` prefixes `\n`, both rows parse, `check` exits 0. `part1_all.py::high40` |
| MEDIUM-41 (temp file + rename) | FIXED | Real `RLIMIT_FSIZE` kills `propagate --write` mid-append; entry bytes identical before and after (911/911), no leftover temp, `check` reports the *missing* verdict rather than corruption |
| MEDIUM-42 (retry after interrupted `source add`) | FIXED | The interrupted copy leaves no cache file at all rather than a truncated one; the retry stores the full bytes, digest matches, `check` exits 0 |
| MEDIUM-43 (insertion below the marker) | FIXED | Entry with `## References` above the APPEND marker (a layout `validate` rejects): `propagate --write` leaves the frozen region byte-identical; `check` still fails on the pre-existing layout defect, not on new corruption |
| LOW-44 (`sha --write` over several paths) | FIXED — but its regression is now vacuous | The redesigned repro (a *committed* middle entry, since `chmod 0444` no longer fails — HIGH-55) shows entries one and three restamped, entry two refused by name, exit 2, third path named. `cmd_sha` genuinely catches per path and continues |

## Regression honesty

`git diff 95e292f HEAD -- tests/test_write_paths.py`: only `@pytest.mark.xfail` decorators
removed and docstrings re-tensed. No assertion body changed.

**Except** that one test's own mechanism was defeated by a defect the fix introduced — see
HIGH-55. That is not visible in a diff of the test file, because the test file did not
change.

## New defects

Written up in full in `QE-AUDIT.md` as HIGH-55, HIGH-56 and LOW-64. Probes:
`h1_readonly_file.py`, `h4_symlink_cache.py`.

Both HIGH-55 and HIGH-56 were re-run against a worktree at the pre-fix commit to establish
which is a regression and which is pre-existing. HIGH-55 is a regression (`95e292f`: exit
2, "Permission denied", file unchanged). HIGH-56 is **not** (`95e292f` writes outside the
root identically, via `shutil.copyfile`).

## Hypotheses examined and killed

A surface examined and clean must not look like a surface unexamined.

- **H2 — writable file inside a read-only directory**: clean exit 2, correct
  `Permission denied`, file unchanged, no leftover temp, no traceback. `h2_readonly_dir.py`
- **H3 — leftover temp after `SIGKILL`**: the temp (`.A0001-….md.claims-ledger-<pid>`) is
  left behind and the target is untouched. Nothing collects it — not `check`, not `status`,
  not the `documents` glob (Python's `glob` excludes dotfiles, and the name does not end in
  `.md`), not `list_entry_files` (excludes leading-dot names). Inert; never reaped, which
  is cosmetic. `h3_leftover_temp.py`
- **H5 — directory fsync**: confirmed absent. Recorded as LOW-64 rather than killed.
- **H6 — hard links**: `os.replace` breaks a hard link to an entry, which is inherent to
  any rename-based atomic write. Nothing in the package creates or inspects hard links
  (`grep os.link|hardlink|st_nlink` → empty). Not a project concern. `h6_hardlink.py`
- **H7 — concurrency**: no threading anywhere in the package, so the same-pid temp
  collision does not apply (separate processes get separate pids). Two concurrent
  `sha --write` processes racing on one entry: never corrupted over three runs, atomic
  last-writer-wins, both exit 0 — the same self-announcing behaviour the audit already
  reviewed and declined to flag for propagate/freshness. `h7_concurrency.py`
- **H8 — marker duplication against `append_verdict`'s new assertion**: built an entry
  whose committed Backing section legitimately quotes the literal APPEND marker before the
  real one. `partition` does take the first occurrence for its `head`, but (a)
  `check_history`'s per-section comparison does not depend on the marker boundary and
  caught a hand-edit made between the fake and real marker, and (b) the insertion still
  landed after the true last marker. Two independent layers; no bypass materialized.
  `h8_marker_duplication.py`, `h8_case_c_propagate.py`
- **H9 — `read_text_exact` byte fidelity**: lone-CR, mixed CRLF/LF and no-final-newline all
  round-trip byte-exact through `sha --write` and `propagate --write`. A UTF-8 BOM breaks
  frontmatter parsing (`no YAML frontmatter`) — pre-existing in `FENCE_RE`/
  `split_frontmatter`, identical before and after this pass, and a clean named refusal
  rather than silent corruption. `h9_encoding.py`
- **H10 — registry edge cases**: empty, all-whitespace, CRLF-ending and symlinked
  registries all handled cleanly. A registry truncated mid-JSON is refused by
  `load_registry` before any write is attempted, file untouched. A FIFO registry is refused
  before being opened (`is_file()`), no hang. `h10_registry.py`
- **`create_entry` and the symlink question**: clean, but by accident rather than by a
  guard. A dangling symlink at the target entry path is caught earlier by `load_entries`
  (`entry is a symlink to nothing`); a live symlink to an existing outside file is caught
  by `create_entry`'s own `path.exists()` refusal. Neither is
  `refuse_to_write_outside_the_root`. `h4_symlink_new_entry.py`
