# Fifth pass — `freshspec`: the freshness checker against `docs/FRESHNESS.md`

Oracle: `docs/FRESHNESS.md`. Baseline confirmed before starting: **648 passed, 0 xfailed**.

- Regressions: `tests/test_freshness_spec.py` — **14 passed, 9 strict xfailed**.
- Probes (print-only, not collected): `.qe/probe/probe5_fresh.py`.
- Suite at stop: green, no failures. (`tests/test_write_paths.py` in the same worktree is
  another dimension's file, not mine.)

Every case builds a real repository and makes real commits. Nothing is monkeypatched —
`freshness.py` does `from .schema import git`, so patching would not reach it anyway.

Ten findings: three HIGH, four MEDIUM, three LOW.

---

## F-1 — one discharge verdict silences every ground pointing at the same file and pin

**Severity: HIGH** — *"a false `0 failures` over content that was never actually checked."*

`freshness.has_acknowledged()` compares a propagation verdict's pointer to a ground on
`type`, `target` and `pin` **and not on `section`**. Everywhere else in this checker the
`§ "…"` is part of a pointer's identity: `scoped()` compares only that span, `orphans()`
looks the ground up by `p.raw` (which carries the section), the message names the section.
`has_acknowledged` alone drops it.

**Repro** (`.qe/probe/probe5_fresh.py::test_c_section_blind_discharge`): an entry with
grounds

    - lab: docs/note-001.md § "Observation" @<pin>
    - lab: docs/note-001.md § "Method" @<pin>

Edit both sections — `freshness` reports two flags. Append one propagation `contested`
verdict naming `§ "Observation"` only. Re-run.

**Observed**: `freshness.run(...) == []`, and `validate` is clean too.
**Required**: the verdict discharges `§ "Observation"`; `Grounds 2` still flags.

Grounds 2 has drifted and no checker will ever say so again: a verdict is permanent, so
this is not a one-run miss but a hole for the life of the entry. It is also the forgery
the spec's orphan rule exists to close, arriving by the door the orphan rule does not
watch.

**Tests**: `test_a_verdict_naming_one_section_does_not_discharge_another` (strict xfail);
`test_a_verdict_naming_the_same_section_still_discharges_it` (control — a fix must not
break the real discharge).

**Fix shape**: compare `q.raw == pointer.raw`, which is exactly what `orphans()` already
does, or add `and q.section == pointer.section`.

---

## F-2 — `freshness --write` modifies entry files and exits 0

**Severity: HIGH** — *"a wrong exit code"*, plus an unreviewed write into the ledger.

`docs/FRESHNESS.md`, "How a finding is discharged, and what the schema already forces":

> The second is the one the checker can help with, so `freshness --write` appends it,
> and — **following `propagate` — the run still exits non-zero afterwards so the appended
> text is looked at before it is committed.**

`propagate` gets this for free: every block it queues is queued beside a `fail` report.
`freshness` queues the `moved` case beside a **`flag`**, and the "appended N contested
verdict(s)" report is also a `flag`. `exit_code()` returns 1 only for `fail`.

**Repro** (`::test_d_write_exit_code`, `::test_d2_cli_write_exit`): pin a ground, edit the
artifact, run `claims-ledger freshness --write`.

**Observed**:

    FLAG A0001 Grounds 1: `experiment: docs/note-001.md @2ac86f8` has moved: it differs from the pin in the working tree, uncommitted
    FLAG A0001 Verdicts: appended 1 contested verdict(s) by propagation
    freshness (1 entry): 0 failure(s), 2 flag(s)
    → exit 0

**Required**: exit non-zero — a file on disk was changed.

`withdrawn` masks this in the existing suite: that path *is* a `fail`, so
`test_write_appends_a_verdict_and_still_fails` passes while deleting the file. `moved` is
the case the spec's sentence is actually about, and it is the common one.

**Tests**: `test_write_over_a_moved_ground_still_exits_non_zero` (strict xfail);
`test_write_over_a_withdrawn_ground_exits_non_zero` and
`test_a_second_write_does_not_duplicate_the_verdict` (controls).

**Fix shape**: make the `appended …` report a `fail`. It is a statement that the tree was
modified, not a finding about a claim, and `propagate` should arguably be read the same
way.

---

## F-3 — a `###` subsection ends a `##` section, so an edit under it is not a moved ground

**Severity: HIGH** — *"a false `0 failures` over content that was never actually checked."*

`schema.section_span()` ends a section at "the next match of the same pattern with the
name slot widened to some other name". The **shipped default** is `^#+\s*{name}\s*$`,
whose widened form `^#+\s*[^\n]+?\s*$` matches a heading at *any* depth. So
`## Observation` ends at the first `### …` beneath it and everything under that subheading
is outside the comparison — for `resolve` as well as `freshness`.

`docs/FRESHNESS.md` calls this out only for a *configured* pattern:

> **The anchoring caveat is real and is documented rather than defended.** … The
> configuration comment, `SCHEMA.md` and `section_span`'s own docstring all say to anchor
> at the granularity the section really has.

A project that configures nothing gets the same silent miss and has no anchoring available
to it: `#+` *is* every depth. Nested headings are the ordinary shape of a Markdown lab
note, which is the default type `evidence-sectioned` ships with.

**Repro** (`::test_e_nested_subsection`): a note with `## Observation`, `### Detail` under
it, then `## Method`. Pin at `§ "Observation"`. Rewrite the text under `### Detail`.

**Observed**: `freshness.run(...) == []` and `resolve.run(...) == []`. The claim's evidence
can be inverted under a subheading with every checker green.
**Required**: a `moved` flag on `Grounds 1`.

**Tests**: `test_an_edit_under_a_subheading_of_the_named_section_is_a_moved_ground`
(strict xfail); `test_an_edit_directly_under_the_named_heading_is_still_caught` (control —
holds a fix to *widening* the section rather than moving where it starts).

**Fix shape**: build the terminator from the depth the header actually matched — capture
the `#+` run and end at `^#{1,N}\s` — rather than from a fixed `#+`. The spec anticipates
the general form: "the key can grow a sibling later if a section needs its own
terminator."

---

## F-4 — an uppercase object-id pin is called an unstable pin, and is then never compared

**Severity: MEDIUM** — a false message, and a ground that is never looked at while the
report says it can never go stale.

`OBJECT_NAME_RE = ^[0-9a-f]{4,40}$` rejects uppercase hex **without asking git**. Git
resolves an uppercase object id (`git rev-parse --verify --quiet <UPPER>` exits 0 here)
and prints no refname for it, so by the spec's step 1 it is a commit. `resolve` accepts
it. `freshness` says:

    FLAG A0001 Grounds 1: `experiment: docs/note-001.md @2AC86F84DEDEA36648A8B659C1845FD0685BC0E4`
    is pinned to a name, not a commit; a pin that follows the work resolves forever and can never go stale

Both halves are false. And because `drift()` reports and stops for an unstable pin, the
artifact behind that pin is **never compared at all** — delete it and the run still prints
only this flag, never `withdrawn`. The wrong message buys a permanently uncompared ground.

**Repro** (`::test_g_uppercase_pin`): write the pin as `HEAD`'s object id upper-cased.

**Tests**: `test_an_uppercase_object_id_pin_is_not_a_name` (strict xfail),
`test_a_withdrawn_ground_under_an_uppercase_pin_is_still_reported` (strict xfail — the
severity).

**Fix shape**: `re.IGNORECASE` on `OBJECT_NAME_RE`. `is_object_name()` then puts the
question to git, which is the arbiter it already defers to for `beef`-shaped names.

---

## F-5 — `freshness` ignores `--cached`, and `check --cached` does not say so

**Severity: MEDIUM** — *"a false `0 failures` over content that was never actually
checked"*, on the surface where it matters most.

`docs/FRESHNESS.md`, "The comparison, exactly", step 3:

> The artifact as this run reads it: `git hash-object <path>` on the working tree, **or the
> index blob under `--cached`, matching whatever the rest of the run is reading.**

`freshness.run(ledger, write=False)` takes no `cached` parameter at all. Under
`claims-ledger check --cached`, `validate` reads staged entries out of the index while
`freshness` reads the working tree — for the entries (`load_entries(ledger)`, no `cached`)
*and* for the artifact (`git diff --name-only <pin> -- <path>`, `path.is_file()`).
`skipped_checks()` lists nothing about it, so the run reports on something other than what
is being committed while saying it read what was staged.

**Repro** (`::test_b3_staged_edit_reverted_worktree`): edit the pinned artifact,
`git add` it, then put the working-tree copy back — ordinary partial staging. Then:

    $ git diff --cached --name-only
    docs/note-001.md
    $ claims-ledger check --cached
    …
    freshness: 0 failure(s), 0 flag(s)
    → exit 0

The commit moves the ground and the checker built to notice never looks. The mirror case
is a false alarm rather than a false pass: an *unstaged* edit is flagged under `--cached`
though the commit does not contain it (`::test_b2_cached_unstaged_edit`).

**Tests**: `test_cached_compares_the_index_not_the_working_tree` (strict xfail);
`test_check_without_cached_reads_the_working_tree` (control — the pre-commit argument the
spec makes for comparing against the working tree must survive the fix).

**Fix shape**: `run(ledger, write=False, cached=False)`, threaded from `cmd_check`; the
comparison becomes `git diff --cached --name-only …` and the existence test the index
blob. If that is out of scope for now, correct the spec sentence *and* have
`skipped_checks()` say `--cached does not reach freshness`, because the silent version is
the one the oracle forbids.

---

## F-6 — reverting a drift turns its own discharge into a permanent, unclearable failure

**Severity: MEDIUM** — a wrong exit code that no legal edit can clear.

`orphans()` re-asks `drift()` for every propagation verdict and fails when the ground "has
not drifted". A verdict the checker itself wrote, because the ground *had* drifted, becomes
an orphan the moment the edit is undone.

**Repro** (`::test_p_revert_after_discharge`, `::test_u_cannot_remove_the_orphan_verdict`):
pin, edit the artifact, `freshness --write`, commit, then revert the artifact to its
pinned content.

    FAIL A0001 Verdicts: verdict 1 by propagation names `experiment: docs/note-001.md @ba88ac2`
    as its cause, but that ground has not drifted; a propagated verdict that nothing caused is an orphan
    → check exits 1

And there is no way out. Removing the verdict:

    FAIL A0001 verdict 1: present at 3973ec2 and changed or removed at working tree;
    verdicts append and only append

The pin cannot be edited either — Grounds are above the APPEND marker and frozen. The
entry is red for the rest of its life, which for a checker whose whole argument is about
its noise floor is the failure mode it least affords.

**Required**: the spec justifies the orphan rule as stopping a *pre-emptive* forgery —
"Otherwise the discharge is forgeable by writing the verdict pre-emptively." A verdict
that was caused is not a forgery.

**Tests**: `test_a_reverted_drift_does_not_wedge_the_ledger` (strict xfail);
`test_removing_the_orphaned_verdict_is_itself_a_failure` (control — the append-only
guarantee is correct and must not be relaxed to make room for the fix);
`test_a_fallen_entry_carrying_a_discharge_is_not_an_orphan` (control).

**Fix shape**: the verdict should name the blob object id it was written against — which
is the spec's own open question ("Whether the discharge should expire … It may need to
name the blob object id it was written against instead") pointing the other way. The
orphan test then asks *was this blob ever the artifact's*, not *is it drifted right now*.
A cheaper interim: orphan only a verdict whose ground was never drifted at any commit
between the pin and HEAD.

---

## F-7 — a decoy file matching the path as a glob is reported as this ground's drift

**Severity: MEDIUM** — a false alarm; the oracle's "a correct successful run".

`drift()` passes `pointer.target` to `git diff … -- <path>` and `git rev-list … -- <path>`
as a **pathspec**, where `[…]`, `*` and `?` are wildcards. A ground on `docs/note[1].md`
is therefore reported as moved when an unrelated `docs/note1.md` — which no entry pins —
is edited.

**Repro** (`::test_a3_glob_decoy`): create `docs/note[1].md` and `docs/note1.md`, ground
the entry on the first, edit only the second.

**Observed**: `FLAG A0001 Grounds 1: `experiment: docs/note[1].md @138780a` has moved`.
**Required**: nothing; the ground is byte-identical to its pin.

The good news, checked rather than assumed: the *false-negative* direction does not
happen. Git's pathspec matching also tries the literal path, so editing the real
`docs/note[1].md` (or `docs/a*b.md`) is still reported. This is noise, not a hole — but a
checker whose flags fire over files nobody pinned is precisely what the spec's "Why moved
flags and withdrawn fails" section argues gets checkers switched off.

**Tests**: `test_a_decoy_matching_the_pathspec_glob_is_not_this_grounds_drift` (strict
xfail); `test_a_glob_metacharacter_in_a_path_is_still_compared` (control — a `:(literal)`
fix must keep this working).

**Fix shape**: `-- :(literal)<path>` in both `git diff` and `git rev-list`. Note that
`resolve` is not affected: `git show <pin>:<path>` is a revision, not a pathspec.

---

## F-8 — a non-hex pin that names nothing is reported as an unstable pin

**Severity: LOW** — one defect under two contradictory names.

`docs/FRESHNESS.md` step 1: "`git rev-parse --symbolic-full-name <pin>` — **non-empty
output** means unstable pin". For `@v9.9`, git prints nothing and exits non-zero, so the
pin is not a symbolic ref; it is a pointer that does not resolve, which step 2 hands to
`resolve`. `is_object_name()` never asks, because the text is not hex, and returns
`(False, None)`.

**Repro** (`::test_t_nonexistent_named_pin`):

    freshness: FLAG … `@v9.9` is pinned to a name, not a commit; a pin that follows the work
                      resolves forever and can never go stale
    resolve:   FAIL … experiment: docs/note-001.md @v9.9 does not resolve

Two reports, contradicting each other, for one defect. The equivalent hex pin
`@deadbeef` is correctly silent in `freshness` (`::test_t2_nonexistent_hex_pin`) — that
was settled by the fourth pass's MEDIUM-27 disposition — so the same question is answered
two different ways depending on the shape of the text. `drift()`'s own docstring refuses
this: "reporting it twice under two names would make one defect look like two."

LOW because the run does exit 1 by `resolve` and the reader is not misled about whether
something is wrong, only about what.

**Tests**: `test_a_named_pin_that_names_nothing_is_not_an_unstable_pin` (strict xfail);
`test_a_hex_pin_that_names_nothing_is_left_to_resolve` and
`test_an_annotated_tag_pin_is_an_unstable_pin` (controls — the fix must not make a real
tag silent).

**Fix shape**: ask git for every pin, not only hex-shaped ones: non-zero from
`--symbolic-full-name` plus exit 1 from `--verify --quiet` means "not there", which is
`resolve`'s.

---

## F-9 — the comparison is `git diff`, not `hash-object`, and the spec does not say so

**Severity: LOW** — documentation drift with one observable consequence.

Spec steps 3–5 describe blob identity: `git hash-object <path>` against
`git rev-parse <pin>:<path>`, "Blob identity, not a diff." The code instead runs
`git diff --name-only <pin> -- <path>`, and its comment gives a good reason (the
repository's own clean/smudge and line-ending handling is applied to both sides).

The consequence: `git diff <commit>` reports a path that has left the *index* as deleted
even when the working-tree bytes are identical to the pin. `git rm --cached docs/note-001.md`
therefore produces `has moved` over a file whose blob id has not changed
(`::test_b_cached_ignored`).

No regression written: the code's reason is better than the spec's text, so the spec is
what should move. Recorded so the deviation is a decision rather than something a later
reader has to rediscover.

---

## F-10 — the messages the specification prints verbatim are not the messages printed

**Severity: LOW** — documentation drift.

| `docs/FRESHNESS.md` | the code |
|---|---|
| `… @main is pinned to a branch, not a commit; a pin that moves with the work cannot go stale` | `… is pinned to a name, not a commit; a pin that follows the work resolves forever and can never go stale` |
| `… is not in the working tree; the ground was withdrawn in 1 commit since the pin` | `… is not in the working tree; the ground it names is gone (1 commit has touched the artifact since the pin)` |
| `… has moved; 1 commit has touched it since the pin` | `… has moved: 1 commit has touched it since the pin` |

The code is right in each case — a tag is not a branch, and `rev-list --count` counted
commits that touched the artifact, not withdrawals — so the specification is what should
be corrected. It is otherwise the document a reader checks the output against.

**Test**: `test_the_three_findings_say_what_they_are` (control; pins the current wording so
a later edit to either side is a decision).

---

## What held

Attacks that found nothing. An unexamined surface and a clean one must not look the same
in the record.

- **A section that is not at the pin.** `scoped()` returns `None` on `before is None` and
  the comment claims `resolve` reports it. Checked: it does, once —
  `FAIL A0001 Grounds: docs/note-001.md @<pin> has no section 'Observation'` — and `check`
  exits 1. One defect, one name. (`::test_f_section_absent_at_pin`; kept as
  `test_a_section_absent_at_the_pin_is_resolves_finding`.)
- **A pin naming a blob rather than a commit.** `rev-parse --verify --quiet <blob>:<path>`
  exits 1, so `drift()` returns `(None, None)` and stays quiet; `resolve` fails it once as
  unresolvable. It does *not* arrive as `unknown`, which would have been a second name for
  it. (`::test_q_blob_pin`; kept as
  `test_a_pin_that_is_a_blob_not_a_commit_is_resolves_finding`.)
- **A glob path in the false-negative direction.** `docs/note[1].md` and `docs/a*b.md` are
  still compared correctly when the real artifact is edited: git's pathspec matching tries
  the literal path first. Only the decoy direction fails (F-7). No `:(literal)` is needed
  to keep the true positive. (`::test_a_glob_path`, `::test_a2_star_path`.)
- **An annotated tag pin.** Flagged as unstable, which is what the spec asks — it names "a
  branch or a tag" together. (`::test_s_annotated_tag`; kept as a control.)
- **A `beef`-shaped branch, `HEAD`, `HEAD~2`, `@working`, `@corpus`.** Re-confirmed against
  the existing suite; nothing new.
- **A duplicated heading.** `section_span` takes the first match, so an edit to a second
  `## Observation` is not this ground's drift. `resolve` reads the same span, so the two
  checkers agree about which copy the claim rests on and the entry stays internally
  consistent. Recorded rather than filed as a finding, and the first copy is still
  compared. (`::test_h_duplicate_heading`; kept as
  `test_a_duplicated_heading_compares_only_the_first`.)
- **`Grounds N` numbering counts reserved pointers.** `checked_pointers` enumerates all
  grounds and filters afterwards, so `source:` and `entry:` lines keep their index — which
  is what the spec's `Grounds 3` example shows.
- **A fallen entry with a drifted ground and a discharge verdict.** `run()` exempts the
  Grounds; `orphans()` does not exempt the Verdicts but sees the ground still drifted and
  stays quiet. No double report, and the exemption does not leak into an accusation.
  (`test_a_fallen_entry_carrying_a_discharge_is_not_an_orphan`.)
- **`--write` run twice.** The second run finds the ground acknowledged, queues nothing,
  and writes no duplicate verdict. (`test_a_second_write_does_not_duplicate_the_verdict`.)
- **A `moved` flag over an uncommitted edit.** `since_phrase(0, …)` says "differs from the
  pin in the working tree, uncommitted" as the spec's Stage-2 note requires; re-confirmed.
