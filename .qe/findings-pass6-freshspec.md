# Sixth pass — freshness dimension

Verifying the fifth pass's ten freshness findings (HIGH-29 … LOW-38) at `776500b`, then
attacking the fixes. Worktree `/tmp/qe6-fresh`. Probes in `.qe/probe6/probe1_*` …
`probe9_*`.

## The ten, verified

| Finding | Verdict | Evidence |
|---|---|---|
| HIGH-29 (section identity) | FIXED | Two grounds on `§ "Observation"` / `§ "Method"`, both moved; discharging only Observation leaves Method flagged. `probe1::test_high29_section_identity` |
| HIGH-30 (`--write` exit code) | FIXED | `moved` + `--write` → `exit_code() == 1`. Combos (moved+withdrawn, a second no-op write) correct — `probe9` |
| HIGH-31 (`###` inside `##`) | FIXED for the reported case | `probe1::test_high31_nested_subsection` catches the inversion under `### Detail`. See HIGH-58 for the same mechanism's remaining hole |
| MEDIUM-32 (uppercase object id) | FIXED | HEAD's hex uppercased: silent when unedited, flags when edited |
| MEDIUM-33 (`--cached`) | PARTIALLY FIXED | `freshness.run(cached=)`, `cmd_freshness`, `cmd_check` all read the index correctly. The installed hook does not — HIGH-57 |
| MEDIUM-34 (revert wedges ledger) | FIXED for the reported repro | `probe1::test_medium34_revert_no_wedge`. The approximation it introduced is HIGH-53 / HIGH-54 |
| MEDIUM-35 (glob pathspec decoy) | FIXED | Decoy no longer flags; true positive intact. Held under `:`, `?`, `*`, leading `-`, doubled `:(literal)`, `../` traversal — `probe8` |
| LOW-36 (non-hex pin, two names) | FIXED for `v9.9` | Residual for option-shaped pins — LOW-63 |
| LOW-37 (`git diff` not `hash-object`) | SPEC MOVED — legitimate | Step 4 now documents `git diff --name-only`, with the `git rm --cached` divergence disclosed and reasoned: clean-filter parity beats blob-identity purity |
| LOW-38 (verbatim messages) | SPEC MOVED — legitimate | The spec's examples now match the code's actual strings exactly |

## Spec-edit judgement

Both moves are legitimate. In each the code is demonstrably better-reasoned than the old
prose, each is disclosed with its rationale rather than silently rewritten, and neither
launders a defect. The other eight spec edits describe real code changes and match the
code precisely.

The one reservation: MEDIUM-33's and MEDIUM-34's "Built —" paragraphs describe fixes that
are incomplete in the ways recorded as HIGH-57 and HIGH-53/54, and the spec text does not
disclose that residue.

## New defects

Written up in full in `QE-AUDIT.md` as HIGH-53, HIGH-54, HIGH-57, HIGH-58 and LOW-63.
Probes: `probe7_attack_orphan_forgery.py`, `probe6_hook_never_passes_cached.py`,
`probe5_attack_section_span.py`, `probe3_dash_pin_defect.py`, plus
`test_probe_gitfail.py` and `test_probe_launder.py` (this pass's author, reproducing
HIGH-54 and HIGH-53 independently of the agent that found them).

## Explored and held

- **Injection-shaped pins** (`--git-dir=/etc`, `-h`, `--`, empty string, newline): no
  escalation. argv-list `subprocess.run` is not shell-interpreted, and `git_call` discards
  stdout on a non-zero exit, so only the option-echo quirk of LOW-63 leaks through.
- **Ref/object-id collision**: a branch literally named as another commit's full hex is
  correctly resolved as a name, per git's own ref-vs-hash precedence. Matches spec intent.
- **Abbreviated 7-character object ids**: correct in both directions.
- **Performance**: `is_object_name()` costs the two `rev-parse` calls the spec's own "Cost"
  section always claimed. Previously paid only by hex-shaped pins, now paid symmetrically.
  No memoization for repeated identical pins across grounds (61 git calls over 20
  identical-pin grounds, ~3/ground — `probe4`), but that was never promised and is not new.
- **MEDIUM-35 in both directions**, under every metacharacter tried.
- **HIGH-30 combinations**: moved+withdrawn together, a `--write` with nothing to append, a
  second no-op `--write`. All correct.
- **HIGH-29 normalization**: `has_acknowledged()`'s `q.section == pointer.section` and
  `orphans()`'s `p.raw` dict key are both raw, unnormalized comparisons — consistently so.
  No divergence between the two functions is possible; a case/whitespace/Unicode-form
  mismatch fails identically at the section-matching layer before either comparison runs.
