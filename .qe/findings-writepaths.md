# Fifth pass — `writepaths`: every path that writes, and what it leaves behind

Dimension: every write path (`init`, `new`, `source add`, `sha --write`,
`propagate --write`, `freshness --write`, `hook --install`), what those paths do to a
file they only partly succeed at, and whether a byte that goes in comes back out.

Baseline confirmed before starting: `648 passed` in 17.82s, 0 xfailed.
Regressions: `tests/test_write_paths.py`.

## The write paths, enumerated from the source

| path | code | what it opens | discipline |
| --- | --- | --- | --- |
| `init` | `cli.py:479-486` | `entries/`, `cache/`, `cache/.gitignore`, `sources.jsonl`, `claims-ledger.toml` | truncate-in-place, five separate writes, no rollback |
| `new` | `authoring.py:187-188` | the entry file | `write_text`, exists-check then write |
| `source add` | `authoring.py:339-353` | `cache/<sha256>` then a `+=` line on `sources.jsonl` | `copyfile`, then `open("a")` |
| `sha --write` | `authoring.py:264-274` | the entry file | `read_text` -> regex -> `write_text` |
| `propagate --write` | `propagate.py:83-105` | each entry needing a verdict | `read_text` at load -> `write_text` whole file |
| `freshness --write` | `freshness.py:309-318` | same `append_verdict` | same |
| `hook --install` | `cli.py:508-516` | `.git/hooks/pre-commit` | `write_text` + `chmod` |

No path anywhere in the package writes to a temporary file and renames. Every one of
them truncates the destination first.

---

## HIGH-W1 — every `--write` silently rewrites all of a committed entry's frozen region when the file's line endings are not LF, and `check` cannot see it

**Severity: HIGH.** Oracle: *a false "0 failures" over content that was never actually
checked* — plus the package's own promise that the region above the APPEND marker is
immutable once committed. This is HIGH-26's class (`sha --write` reaching the frozen
region) reached by a different route: `propagate --write` and `freshness --write` have
no `is_committed` guard at all, because they believe they only ever append below the
marker. They do not.

**Repro** (`.qe/probe/p1_crlf.py`):

1. Scaffold a project, `new a-claim`, fill it in, `sha --write`.
2. Convert the entry file on disk to CRLF (`raw.replace(b"\n", b"\r\n")`) — what any
   Windows editor, or `git config core.autocrlf true`, does to it.
3. `git add -A && git commit`. `claims-ledger check` -> 0. The CRLF entry is a valid,
   sealed, committed entry.
4. Add a second entry whose Grounds carry `- entry: A0001-a-claim · challenges`.
5. `claims-ledger propagate --write`.

**Observed.** `git diff --stat` on the *challenged* entry:

```
 ledger/entries/A0001-a-claim.md | 84 +++++++++++++++++++++--------------------
 1 file changed, 44 insertions(+), 40 deletions(-)
```

Every one of the 40 committed lines was rewritten — the frontmatter, Assertion, Scope,
Grounds, Warrant and Backing, all of it above the APPEND marker — because
`append_verdict` reads `entry.text` (produced by `read_text`, universal newlines on, so
CRLF became LF in memory) and writes the whole file back with `write_text` (LF). The
append that was supposed to add three lines below the marker rewrote the file.

And `claims-ledger check` after it: **no immutability failure**. `check_history`
compares `git show`'s output against `e.text`, and `git_call` runs
`subprocess.run(text=True, encoding="utf-8")` — text mode, `newline=None`, universal
newlines — so *both* sides of the "compared as bytes" comparison have already had their
CRLFs translated to LF. The frozen region is not compared as bytes; it is compared as
newline-normalized text.

The second half stands on its own (`.qe/probe/p2_frozen_bytes.py`): commit an LF entry,
rewrite only the region above the APPEND marker to CRLF by hand, `check` -> **0**. Every
byte of the immutable region changed and the checker that exists to notice reported
zero failures.

**Required.** Either (a) the write paths preserve the file's existing newlines — read
with `newline=""`, write with `newline=""` — so an append is an append and the diff
shows the three lines it added; or (b) if normalization is deliberate, `check_history`
must compare real bytes (`git show` via `git_call` with `text=False`, entry via
`read_bytes`) so that the rewrite is reported rather than passed. Doing neither leaves
a `--write` that mangles a committed immutable region and a checker that says it did
not.

**Tests.**
- `test_propagate_write_preserves_the_committed_frozen_region_bytes` (xfail, strict)
- `test_frozen_region_rewritten_to_crlf_is_caught` (xfail, strict)
- `test_sha_write_preserves_line_endings` (xfail, strict)
- `test_an_edit_inside_the_frozen_region_is_still_caught` (control, passes)

**Fix shape.** In `schema.read_text_or_raise`, read with `newline=""` and keep the
file's own endings; in `authoring.restamp` and `propagate.append_verdict`, write with
`newline=""`. Separately, give `check_history` a bytes comparison of the frozen region.

---

## HIGH-W2 — `source add` glues its row onto the previous one when the registry does not end in a newline, destroying both, and exits 0

**Severity: HIGH.** Oracle: *a wrong exit code* — the run reports
`registered fx-second (…) in ledger/sources.jsonl` and exits 0 having made the registry
unparseable and having destroyed the row that was already in it.

**Repro** (`.qe/probe/p4_registry.py`):

```
claims-ledger init
claims-ledger source add a.txt --id fx-source --type paper --citation "..."
python -c "p=open('ledger/sources.jsonl','rb+'); d=p.read().rstrip(b'\n'); p.seek(0); p.truncate(); p.write(d)"
claims-ledger source add b.txt --id fx-second --type paper --citation "..."
```

**Observed.** stdout: `registered fx-second …`, exit **0**. The file:

```
{"id": "fx-source", …"}{"id": "fx-second", …}
```

one line, invalid JSON. Every later command: `ledger/sources.jsonl:1: not a JSON object
(Extra data)`, `check` exits 2. Both source registrations are gone — the new one and the
one that was there first.

`register_source` (`authoring.py:351-353`) opens the registry `"a"` and writes
`json.dumps(row) + "\n"`. It never checks that what is already there ends in a newline.
A registry can lose its final newline from an editor without "insert final newline",
from a script that appended with `printf '%s'`, or from the interrupted append in
MEDIUM-W3 below — the tool's own failure mode feeds this one.

**Required.** Either append `"\n" + line` when the existing file is non-empty and does
not end in `\n`, or refuse with a message naming the file. Under no circumstances exit 0
after writing a row that cannot be read back.

**Tests.**
- `test_source_add_onto_a_registry_without_a_final_newline` (xfail, strict)
- `test_source_add_appends_cleanly_to_a_well_formed_registry` (control, passes)

**Fix shape.** In `register_source`, before the append: read the last byte
(`ledger.registry.stat().st_size` and a one-byte seek) and prefix `"\n"` when it is not
one. Cheap, and it makes the append idempotent against its own partial writes.

---

## MEDIUM-W3 — no write path uses a temporary file and a rename; a failed write destroys the file it was appending to

**Severity: MEDIUM.** Oracle: not a false pass — the tool exits 2 with a readable
message and the wreckage is loud to `check` — but a ledger whose promise is
append-only leaves a committed entry truncated in place, and the only recovery is
`git checkout`.

**Repro** (`.qe/probe/p3_partial.py`): a real resource limit, no internals patched. In a
child process, `signal.signal(SIGXFSZ, SIG_IGN)` and
`resource.setrlimit(RLIMIT_FSIZE, (entry_size + 40, …))`, then
`claims-ledger propagate --write` over a sealed, committed project where A0001 must
receive one propagated verdict.

**Observed.**

```
child rc 2
claims-ledger: …/A0001-a-claim.md: cannot append the verdict (File too large)
entry bytes: 911 before, 951 after
tail: '…## Verdicts\n\n- 2026-09-06T01:59:24-07:00 · contested · grade: mea'
```

The committed entry is truncated mid-verdict; `## References` is gone. `check` afterwards
reports `A0001 References: section missing` and a malformed verdict 1 — so it does *not*
read as valid, which is the one thing that keeps this out of HIGH. But `write_text`
truncated a good file before it knew it could write the new one, and every write path in
the package does the same: `authoring.create_entry`, `authoring.restamp`,
`propagate.append_verdict`, `cli.cmd_init`, `cli.cmd_hook`. There is no
temp-file-and-rename discipline anywhere; it is not "used in some places", it is used in
none.

The same limit against `source add` truncates a JSON line in the registry, which then
feeds HIGH-W2 exactly.

**Required.** A `--write` that fails leaves the file as it found it.

**Tests.**
- `test_a_failed_append_does_not_truncate_the_entry` (xfail, strict)
- `test_a_failed_append_still_exits_cleanly_with_a_message` (control, passes — the
  diagnostic half is already right)

**Fix shape.** One helper in `schema.py` — write to `path.with_suffix(path.suffix +
".tmp")` in the same directory, `os.replace` onto the target — and route
`restamp`, `append_verdict` and `create_entry` through it. `os.replace` is atomic within
a filesystem, which is where every one of these writes lands.

---

## MEDIUM-W4 — retrying an interrupted `source add` exits 0 over cache bytes it never wrote, and no re-run can repair it

**Severity: MEDIUM.** Oracle: *a wrong exit code* — exit 0 for a run that registered a
row whose `sha256` does not describe the bytes it says it stored. Not the most severe
class, because the mismatch is loud the moment something cites the source; but the
accusation it produces points at the wrong culprit and the command that made the mess
cannot clean it up.

**Repro** (`.qe/probe/p8_srcretry.py`), a real `RLIMIT_FSIZE` in a child process, nothing
patched:

1. `source add big.txt --id fx-2 …` under `RLIMIT_FSIZE = 500` with `SIGXFSZ` ignored.
   Exit 2, message `cannot store the bytes at ledger/cache/926514… (File too large)` —
   the diagnostic half is right. It leaves `ledger/cache/926514…` at 500 bytes of a
   2560-byte file, and no registry row (the copy precedes the append, deliberately).
2. Re-run the identical command with no limit — the retry after the interruption.

**Observed.**

```
registered fx-2 (926514c84261…) in ledger/sources.jsonl
bytes at ledger/cache/926514c84261ccb35c856eda08d6a10a57022b39dab75e7dd9d425bc6f76dc83
retry rc: 0     cache size now: 500
```

`register_source` (`authoring.py:344-346`) copies only `if not stored.exists()`. The
truncated file exists, so it is kept; the row is appended claiming the digest of the
*real* file; and the command prints `bytes at …` about bytes it did not write. The next
`check`:

```
FAIL A0001 Grounds: bytes for fx-2 hash to f410c6a78b1d…, registry says 926514c84261…;
  re-verify everything citing it
```

— an accusation aimed at a source that was never tampered with. And `source add fx-2`
again answers `source id `fx-2` is already registered`, so the documented command has no
way back; the user has to know to delete a cache file by hand.

**Required.** The retry either stores the right bytes or refuses. `stored.exists()` is
a cheap-path optimisation over a content-addressed store, and it is only sound if what is
there hashes to its own name.

**Test.** `test_retrying_an_interrupted_source_add_stores_the_right_bytes` (xfail, strict)

**Fix shape.** Replace `if not stored.exists()` with a digest check of the existing file
(or just always copy — it is content-addressed, so a re-copy is a no-op in content), and
copy through a temp name in the same directory plus `os.replace`, which removes the
truncated-file state entirely.

---

## MEDIUM-W5 — `propagate --write` / `freshness --write` choose their insertion point by `## References` alone, with no check that it is below the APPEND marker

**Severity: MEDIUM.** Oracle: the immutability promise. `append_verdict`
(`propagate.py:88-95`) splits on the first `"\n## References"` and inserts there. Nothing
in that function knows the APPEND marker exists. It is safe only because `validate`
happens to enforce the section order — and `propagate --write` does not require
`validate` to be clean before it writes.

**Repro** (`.qe/probe/p6_layout.py`, case 2): a committed entry whose `## References`
heading sits above the APPEND marker (an entry `validate` already fails for
`sections out of order` — the state a project is in while someone is fixing it). Run
`propagate --write` because a second entry challenges it.

**Observed.** The bytes above the APPEND marker change; the appended verdict lands at the
end of `Backing`; the subsequent `check` reports

```
FAIL A0001 Backing: differs from the blob at the creating commit 96b4e6e;
  the region above the APPEND marker is immutable
```

The tool wrote into the frozen region of a committed entry — HIGH-26's class, reached by
a route that has no `is_committed` guard at all. The `--write` also exits 1 in a way that
reads as "the propagation failed", not as "I have just corrupted an immutable region".

**Required.** `append_verdict` inserts below the APPEND marker or refuses; and no write
path touches the frozen region of a committed entry without `--force`, which is the rule
`restamp` already follows and these two do not.

**Test.** `test_propagate_write_never_writes_above_the_append_marker` (xfail, strict)

**Fix shape.** In `append_verdict`, split on `APPEND` first and search for
`"\n## References"` only in the tail; if there is no marker, append at EOF. Give
`propagate.run` and `freshness.run` the `is_committed` guard `restamp` has.

---

## LOW-W6 — `sha --write a b c` stops at the first file it cannot write and never mentions the third

**Severity: LOW.** Oracle: clean non-zero exit with a readable message — which it is. But
the run half-happened, and the output does not say so.

**Repro** (`.qe/probe/p10.py`): three scaffolded entries whose Scope was edited, the
middle one `chmod 0444`, then

```
claims-ledger sha --write A0001-one.md A0002-two.md A0003-three.md
```

**Observed.**

```
claims-ledger: cannot write …/A0002-two.md (Permission denied)
…/A0001-one.md: 986b8f35faa4… → 8d1b7f49fd50…
rc: 2
declared shas after: ['8d1b7f49', '986b8f35', '986b8f35']
```

A0001 was restamped, A0002 refused, **A0003 never attempted and never named**.
`cmd_sha` (`cli.py:396-419`) loops over `args.path` and the `AuthoringError` from the
second escapes the loop entirely. A user reading that output has no way to tell that the
third file is unprocessed rather than already correct. Re-running the whole command after
fixing the permission does the right thing, which is what keeps this at LOW.

**Test.** `test_sha_write_over_several_paths_does_not_silently_skip_the_rest`
(xfail, strict) — asserts only that A0003 is either restamped or named in the output.

**Fix shape.** Catch `AuthoringError` per path in `cmd_sha`, print it, set `worst = 2`,
and carry on — the same shape `corpus` already uses for per-seed failures.

---

## What held

Attacks that found nothing. An unexamined surface and a clean one must not look the same
in the record.

- **`init` is idempotent and refuses without `--force`.** A second `init` exits 1 with
  `already exists; pass --force`; `init --force` over a populated project rewrites a
  byte-identical tree (the registry is only created `if not registry.exists()`, so an
  existing `sources.jsonl` survives `--force`).
  `test_init_twice_leaves_the_same_tree`.
- **Read-only directories are ordinary conditions everywhere.** `init` into a read-only
  root, `new` into a read-only `entries/`, `hook --install` into a `.git/hooks` that is a
  regular file: exit 2, a message naming the path and the errno, no traceback, nothing
  half-made left in `entries/`.
  `test_init_into_a_read_only_root_is_a_clean_refusal`,
  `test_new_into_a_read_only_entries_directory_is_a_clean_refusal`,
  `test_hook_install_when_the_hooks_path_is_a_file`.
- **A directory occupying the entry path.** `new` where `entries/A0001-x.md` is a
  directory: `entry is not a regular file`, exit 2. The `exists()` call being inside the
  try funnel (a fix from an earlier pass) is what keeps this clean.
  `test_new_where_a_directory_occupies_the_entry_path`.
- **The write-outside-the-root guard holds on both paths that have it.** An entry file
  replaced by a symlink to a file outside the project: `sha --write` exits 2 naming the
  target, and the outside file is byte-identical afterwards. `propagate --write` has the
  same guard in `append_verdict(root=…)`.
  `test_no_write_path_follows_a_symlink_out_of_the_project`.
- **`--write` is idempotent under repetition.** `propagate --write` twice appends one
  verdict; the second run exits 0 with nothing to do. `has_propagated` matches on author,
  status, pointer target and act, and the timestamp it does not compare is the only thing
  that differs between runs.
  `test_propagate_write_twice_appends_one_verdict`.
- **Ordering is fixed, not filesystem-dependent.** `load_entries` iterates
  `sorted(list_entry_files(...))`, so nothing depends on directory iteration order.
  `test_entry_files_are_visited_in_filename_order`.
- **The ordinary append really is an append.** In the scaffolded layout with LF endings,
  `propagate --write` leaves the bytes above the APPEND marker identical and adds exactly
  one verdict below it. This is what makes HIGH-W1 and MEDIUM-W5 bugs rather than the
  design. `test_propagate_write_appends_below_the_marker_in_the_ordinary_layout`.
- **Non-ASCII round-trips exactly.** An entry carrying `é`, `μ`, `中文`, an emoji and the
  schema's own `·` separator goes through `sha --write` with every byte but the
  `verbatim_sha` line unchanged. The defect in HIGH-W1 is newlines specifically, not
  encoding. `test_sha_write_leaves_every_byte_but_the_sha_line_alone`.
- **Two entry files claiming one id are reported.** Nothing locks `entries/` between
  `next_id()` and the write, so two concurrent `new` runs can pick the same number — but
  the consequence is loud: `id \`A0001-a-claim\` does not match filename \`A0001-clash\``,
  and `check` exits non-zero. Observed directly: two `new` processes started together
  produced A0002 and A0003 rather than colliding, and the collision was reproduced by
  hand to check that it is caught.
  `test_two_entries_claiming_one_id_are_reported`.
- **A cache file cannot be aliased into a lie by a symlink in `entries/`.** A second
  filename in `entries/` symlinked to an existing entry gives two `Entry` objects over
  one inode; `propagate --write` appended once (the id index collapses them) and the
  filename/id mismatch is reported.
- **`check` never writes.** `cmd_check` calls `propagate.run(ledger, write=False)` and
  `freshness.run(ledger, write=False)` unconditionally; there is no `check --write`, so
  the read-only command is genuinely read-only.
- **The diagnostics on every interrupted write are already right.** Under a real
  `RLIMIT_FSIZE`, `propagate --write` says `cannot append the verdict (File too large)`
  and `source add` says `cannot store the bytes at … (File too large)`; both exit 2 with
  no traceback. It is the *state left behind*, not the message, that is the defect
  (MEDIUM-W3, MEDIUM-W4).
  `test_a_failed_append_exits_cleanly_with_a_message`,
  `test_a_failed_source_add_exits_cleanly_with_a_message`.

### Examined and judged not a finding

- **Concurrent writers lose an update, but the next run repairs it.** `propagate --write`
  and `freshness --write` both read every entry at `load_entries` and write the whole file
  at the end; there is no lock and no re-read. Two of them running at once on the same
  entry means the second write wins and one verdict is lost while both runs report
  "appended". It is not carried as a finding because the loss is self-announcing: the next
  `check` reports the missing verdict again, and re-running the command appends it. No
  deterministic regression could be written for it that was not a race dressed up as a
  test.
- **`## References` cannot be moved above the APPEND marker on an entry `validate`
  accepts** — the section-order check refuses it, and the marker cannot legally sit
  anywhere else either (inside `Verdicts` it parses as a malformed verdict, inside
  `References` as a malformed reference). That is why MEDIUM-W5 is MEDIUM: it is reachable
  only on a project that is already failing `validate`, which `propagate --write` does not
  require.
- **`source add` orders its two writes correctly.** The cache copy precedes the registry
  append, so an interruption between them leaves bytes with no row (harmless) rather than
  a row with no bytes (a check that cannot run). The docstring claims this and the code
  does it. The defect is what happens on the *retry* (MEDIUM-W4), not the ordering.
