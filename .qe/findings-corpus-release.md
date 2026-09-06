# Fifth pass — `corpus + release` dimension

Worktree `/home/ybx/code/claims-ledger/.claude/worktrees/qe-pass5`.
Baseline confirmed before starting: `648 passed` (no xfailed), `.venv/bin/python -m pytest -q`.

Regressions live in `tests/test_corpus_integrity.py`.

Final state: `692 passed, 31 xfailed` (the count includes the other two dimensions'
work in the same tree). Mine: 15 passing controls and 14 strict xfails, all confirmed
xfailing.

| # | Severity | Finding |
|---|---|---|
| 1 | HIGH | An empty corpus reports `0/0 seeds pass` and exits 0 |
| 2 | HIGH | A seed filter matching nothing reports `0/0 seeds pass` and exits 0 |
| 3 | MEDIUM | Ten seeds (all the freshness ones) are absent from the corpus README |
| 4 | LOW | `CHANGELOG.md` `[Unreleased]` holds content already in the 0.1.0 artifacts, again |
| 5 | LOW | Stale seed counts in `CHANGELOG.md` |
| 6 | HIGH | D17 proves nothing: the terminal-verdict rule can be deleted, corpus stays 72/72 |
| 7 | HIGH | D19 the same: the `resolves_when` rule can be deleted, corpus stays 72/72 |
| 8 | HIGH | 60 of 99 report sites across the five checkers can be deleted, corpus stays 72/72 |
| 9 | MEDIUM | `README.md` — the PyPI long description — says 70 seeds; there are 72 |
| 10 | MEDIUM | The sdist is published without ever being installed or run |
| 11 | MEDIUM | Every action is a mutable ref, including the one holding the PyPI identity |
| 12 | LOW | `workflow_dispatch` publishes from a tag ref; the comment reads as if it cannot |
| 13 | LOW | A trailing space on the `---` fence becomes "no YAML frontmatter" + 8 wrong errors |

---

## HIGH-1 — An empty corpus reports "0/0 seeds pass" and exits 0

**Severity: HIGH.** Oracle clause: *a false "0 failures" over content that was never
actually checked* — the clause the brief names as the most severe class in this codebase.

**Repro**

```
$ mkdir -p /tmp/emptycorpus/seeds
$ claims-ledger corpus --corpus /tmp/emptycorpus
0/0 seeds pass
$ echo $?
0
```

**Observed** exit 0 and a line that reads as a pass.
**Required** a non-zero exit and a message saying no seeds were found — a corpus with no
seeds proves nothing, and the package's own README says "Nothing in this package is
trusted to check anything until it passes this corpus".

**Why this is a release finding, not only a corpus one.** Both `ci.yml` (`wheel` job) and
`release.yml` (`The wheel proves itself from elsewhere`) gate publication on
`claims-ledger corpus` run from a clean venv against the *installed wheel*. That command
is the only thing standing between a mis-packaged wheel and PyPI. If a packaging change
ever drops `corpus/seeds/**` from the wheel — a `.gitignore` line, a hatchling
`exclude`, a `force-include` typo — the gate prints `0/0 seeds pass`, exits 0, and the
wheel ships. The gate cannot distinguish "the corpus passed" from "there was no corpus".

`run.py:main` guards `seeds_dir.is_dir()` but nothing guards the seed list being empty:

```python
    seeds = sorted(p for p in seeds_dir.iterdir() if p.is_dir())
    ...
    print(f"\n{passed}/{len(seeds)} seeds pass")
    return 0 if passed == len(seeds) else 1     # 0 == 0
```

**Test:** `tests/test_corpus_integrity.py::test_an_empty_corpus_is_not_a_pass`
**Fix shape:** in `main()`, after filtering, `if not seeds: print(...); return 1`. Separate
the "no seeds at all" message from the "no seed matched your filter" message.

---

## HIGH-2 — A seed-name filter that matches nothing reports "0/0 seeds pass" and exits 0

**Severity: HIGH.** Same oracle clause.

**Repro**

```
$ claims-ledger corpus NOSUCHSEED
0/0 seeds pass
$ echo $?
0
```

**Observed** a green exit for a run that executed no checker at all.
**Required** non-zero, naming the filter that matched nothing. A mistyped seed name
(`claims-ledger corpus D3` when the seed is `D03`) is exactly how someone convinces
themselves a defect class is covered when the run touched nothing. `D3` matches nothing
because the runner uses `startswith`, and `D0` matches ten seeds — both silently.

**Test:** `tests/test_corpus_integrity.py::test_a_filter_that_matches_nothing_is_not_a_pass`
**Fix shape:** as HIGH-1, with the message naming the unmatched arguments.

---

## MEDIUM-3 — Ten of the 72 seeds are absent from the corpus README, the document the corpus is held to

**Severity: MEDIUM.** Oracle clause: the coverage record claims completeness it does not
have. `tests/test_corpus.py`'s own docstring states the standard — *"A corpus that drifts
from its own description would prove the wrong thing about the checkers built against
it"* — and nothing enforces it.

**Repro**

```
$ grep -c "D45\|D46\|D47\|D48\|D49\|K19\|K20\|K21\|K22\|K23" src/claims_ledger/corpus/README.md
0
```

**Observed** `D45`–`D49` and `K19`–`K23` — every seed the `freshness` checker owns —
appear nowhere in `src/claims_ledger/corpus/README.md`. The Coverage table stops at
`K18`; the "Known-good seeds:" paragraph stops at `K18`; the sentence
"K01–K03, K09 and K15–K18 test the schema's own rules" was not extended. The README's
runner-contract paragraph *was* updated to say "five programs", so the file reads as
current while its coverage record is a version behind.

**Required** the README's Coverage table names every seed, or a test fails. The table is
the corpus's claim about what it covers; a freshness rule with no row in it is a rule
whose coverage nobody can audit from the document of record.

**Test:** `tests/test_corpus_integrity.py::test_every_seed_is_named_in_the_corpus_readme` (xfail, strict)
**Fix shape:** add the ten seeds to the Coverage table and the known-good list, and keep
the test as the guard so the eleventh seed cannot land undocumented.

---

## LOW-4 — `CHANGELOG.md` has an `[Unreleased]` section whose contents are in the 0.1.0 artifacts, again

**Severity: LOW** (process), and it is a **repeat of the third pass's own packaging
finding**, which was recorded as fixed.

**Repro**

```
$ grep -n "Unreleased" CHANGELOG.md
14:## [Unreleased]
$ grep __version__ src/claims_ledger/__init__.py
__version__ = "0.1.0"
```

`## [Unreleased]` lists the `freshness` checker, `docs/FRESHNESS.md`, and ten seeds
(`D45`–`D49`, `K19`–`K23`). All of it is in the tree, so all of it is in a wheel built
today, which calls itself `0.1.0` — and `CHANGELOG.md` already carries
`[0.1.0]: .../releases/tag/v0.1.0`, i.e. 0.1.0 is a version that has been named. Pushing
`v0.1.0` today either fails at upload (PyPI refuses a re-used filename) or ships a
`0.1.0` that is not the `0.1.0` the changelog describes. There is no version under which
the freshness work can currently be published.

The third pass fixed this by folding `[Unreleased]` into `[0.1.0]`. It came back because
the fix was applied to the section rather than to the class: nothing checks it.

**Test:** `tests/test_corpus_integrity.py::test_the_changelog_has_no_unreleased_section_at_the_current_version` (xfail, strict)
**Fix shape:** bump `__version__` to `0.2.0` (a new checker is a feature) and retitle the
section, or fold it into `[0.1.0]` before tagging. Keep the test so the release cannot be
cut with the two disagreeing.

---

## LOW-5 — `CHANGELOG.md`'s seed counts are stale in two places

**Severity: LOW.** `[Unreleased]` says the freshness seeds bring "the corpus to 70", then
a later bullet says `D49`/`K23` bring it "to 72" — the 72 is right, and there are 72 seed
directories, so the running total inside one section contradicts itself only in the sense
that the first bullet is a snapshot. Not a defect on its own; recorded because
`test_corpus_integrity.py::test_the_seed_count_the_changelog_claims_is_the_seed_count`
pins the number, so a future seed addition that forgets the changelog is caught.

---

## HIGH-6 — D17 proves nothing: deleting the terminal-status rule from `validate` leaves the corpus 72/72 green

**Severity: HIGH.** Oracle clause: *a false "0 failures" over content that was never
actually checked* — here applied to the corpus itself, which is the package's whole
argument that the checkers work. This is the task's "a seed that passes for the wrong
reason is a false negative dressed as coverage", demonstrated.

**Repro** (copy the tree, delete one rule, run the corpus against the mutant):

```
cp -r src /tmp/mut/src
# in /tmp/mut/src/claims_ledger/validate.py, replace the body of the `else:` at
# line ~349 (the `follows a terminal ... verdict; nothing may follow it` fail) with `pass`
PYTHONPATH=/tmp/mut/src python -c "import sys; from claims_ledger.corpus import run; sys.exit(run.main([]))"
```

**Observed**

```
72/72 seeds pass
EXIT=0
```

**Required** `D17-verdict-after-terminal` fails. It is the only seed for the class
"verdict after a terminal status" (README Coverage table: `D17, K06 | catch`), and the
rule it exists to prove can be removed without the corpus noticing.

**Mechanism.** `run.py:matches()` compares only `(commit, entry, part, outcome)`. It never
compares the report's message. D17's single row is

```json
{"checker":"validate","outcome":"fail","where":"A0001 verdict 2",
 "why":"retracted is terminal; no verdict may follow it"}
```

and `validate` produces **two** fails at `A0001 verdict 2`:

- `a corroborating verdict must point at a ground the entry does not already cite`
- `follows a terminal `retracted` verdict; nothing may follow it`

Either one satisfies the row. The `why` is prose the runner never reads. So the seed is
green whichever of the two rules exists, and the corroborating-ground rule — which the
seed is not about — is what actually holds it up.

The runner's "unexpected trip" half does not save it either: it asks whether each produced
report has *some* matching row, and both reports match the one row. The relation is
many-to-one where it needs to be a bijection.

**Test:** `tests/test_corpus_integrity.py::test_no_expectation_row_is_satisfied_by_more_than_one_report` (xfail, strict)
and `::test_the_terminal_verdict_rule_is_load_bearing_in_the_corpus` (xfail, strict — runs
the mutant and asserts the corpus fails).

**Fix shape.** Two parts, and the second is the class fix:

1. Give D17 a second expectation row for the corroborating-ground fail at
   `A0001 verdict 2`, so each produced report has its own row. (Or rewrite the seed so
   the terminal-following verdict is not also a bare corroboration.)
2. Make `run_seed` require a **one-to-one** match: every produced report is claimed by
   exactly one row and every row is satisfied by exactly one report. That converts
   "some rule fired here" into "this rule fired here" for all 72 seeds at once, and is
   what makes a seed's coverage claim mean something. Optionally add an optional
   `message` substring to a row so the rule is named, not just the place.

---

## HIGH-7 — D19 has the same hole: deleting the `resolves_when` requirement leaves the corpus 72/72 green

**Severity: HIGH.** Same oracle clause, same mechanism, second instance — which is why
HIGH-6's fix belongs in the runner and not only in the seed.

**Repro**

```
# in a copy of validate.py, disable the `kind: … requires resolves_when` fail (line ~115)
PYTHONPATH=/tmp/mut2/src python -c "import sys; from claims_ledger.corpus import run; sys.exit(run.main([]))"
72/72 seeds pass
EXIT=0
```

**Observed** green. **Required** `D19-prediction-without-credence` fails.

**Mechanism.** D19's first row is `where: "A0001 frontmatter"` — a *prefix*. `matches()`
accepts a report whose place merely starts with it (`rp.startswith(qp + " ")`), so the row
is satisfied by `frontmatter credence` **or** by `frontmatter resolves_when`. The README's
Coverage table sells D19 as covering "prediction without credence or resolves_when", i.e.
two rules; the seed binds one, and either will do.

This is also the only place in the corpus where a row's `where` is coarser than the
report's place, so tightening it costs one edit.

**Test:** `tests/test_corpus_integrity.py::test_every_expectation_row_names_the_report_place_exactly` (xfail, strict)
and `::test_the_resolves_when_rule_is_load_bearing_in_the_corpus` (xfail, strict).

**Fix shape:** split D19's first row into two rows,
`A0001 frontmatter credence` and `A0001 frontmatter resolves_when`; and make `matches()`
exact, or keep the prefix rule but require the bijection of HIGH-6 so a prefix cannot
absorb two reports.

---

## HIGH-8 — 60 of 99 report sites in the five checkers can be deleted with the corpus still reporting 72/72

**Severity: HIGH.** Oracle clause: *a false "0 failures" over content that was never
actually checked*, applied to the proof bar. The corpus README's claim is explicit:

> Each defect class the audit found has at least one seed, **and so does each rule the
> schema's own structure creates.**

That is false, and it is measurable.

**Repro (mutation sweep).** For every `fail(...)` / `flag(...)` statement in
`validate.py` and `resolve.py`, and every `reports.append(Report(...))` statement in
`references.py`, `propagate.py` and `freshness.py`, replace the statement with `pass` in a
copy of `src/`, then run the corpus against the mutant:

```
PYTHONPATH=<mutant>/src python -c "import sys; from claims_ledger.corpus import run; sys.exit(run.main([]))"
```

Scripts: `sweep.py` / `sweep2.py` in the scratchpad; full log in `sweep.txt`.

**Observed**

| module | mutable sites | survived (corpus still 72/72) |
|---|---|---|
| `validate.py` + `resolve.py` | 73 | **49** |
| `references.py` | 15 | 6 |
| `propagate.py` | 5 | 1 |
| `freshness.py` | 6 | 4 |
| **total** | **99** | **60** |

Two further `Report` sites in `freshness.py` (lines 237 and 247, the `git_problem`
"freshness did not run" returns) are inside `return` statements and were not mutated —
their corpus coverage is therefore unmeasured, not established.

**The survivors that matter most**, because each is a rule about *not silently passing*:

- **`freshness.py:262` — `` `{raw}` was not checked: {detail} ``.** Delete it and the
  corpus is green. This is the package's stated reason to exist — a ground the freshness
  checker could not examine must be a failure, not silence — and **no seed holds it**.
- **`references.py:160` and `:166` — a document that could not be opened, and one that
  failed at the read (`{problem}; its citations were not checked`).** These are the fix
  for the third pass's HIGH-17. They have unit tests; they have **no corpus seed**, so the
  corpus — the artifact the release gate runs — does not prove them.
- `resolve.py:106` — `lab:`/`experiment:` pointer that does not resolve at its pin. The
  README sells `dead pointer | D05 | catch, loudly`; D05 seeds only the **registry** miss
  (`resolve.py:115`, killed). The class is proven on one pointer type of three.
- `resolve.py:188` — *the quote starts inside a sentence with no elision mark*. The
  README sells `mid-sentence cut without […] | D06 | catch`; only the **end**-of-span
  direction (`resolve.py:195`, killed) is seeded. Half a class.
- `resolve.py:108` (`has no section` at the pin), `resolve.py:111` (`entry:` ground names
  a non-existent entry), `references.py:141`, `references.py:187` — dead pointers of
  four more shapes, none seeded.
- Nearly all of `validate`'s well-formedness guards: kind/author/grade enums, a
  non-numeric credence, a `verbatim_sha` that is not 64 hex, a missing or misordered
  section, a missing APPEND marker, an empty Assertion or Warrant, a malformed Backing
  block, a malformed References line, a malformed verdict status/grade/timestamp, a
  `defect:` on a non-retracted verdict.

**Also structurally unreachable, by construction:** `propagate.py:236` and
`freshness.py:313` are the `--write` reports, and `run.py` binds both checkers with
`write=False`. Two rules the corpus can never reach whatever seeds are added. Worth
saying out loud in the README's "What passing this corpus does not show".

**Required.** Either the README stops claiming a seed per rule, or the gaps get seeds.
The three in the first bullet group are the ones that are actually dangerous, because they
are the rules whose absence produces a silent green — the failure mode this package is
built to refuse.

**Test:** `tests/test_corpus_integrity.py::test_the_freshness_not_checked_rule_is_load_bearing_in_the_corpus` (xfail, strict)
and `::test_the_unreadable_document_rule_is_load_bearing_in_the_corpus` (xfail, strict).
Each mutates a copy of the source tree and asserts the corpus notices; both currently
xfail because it does not.

**Fix shape:** seeds first for the three "was not checked" rules (a `lab:` ground whose
file the checker cannot read; a `docs/` entry that is a directory or non-UTF-8); then the
dead-pointer shapes; then either seed the well-formedness guards or amend the README's
coverage claim to say the corpus proves the semantic classes and the unit tests prove the
well-formedness guards.

---

## MEDIUM-9 — `README.md` — the file that becomes the PyPI long description — says the corpus is 70 seeds; it is 72

**Severity: MEDIUM.** Oracle clause: the published artifact's own description of its proof
bar is wrong, in the one number a reader would use to check it.

**Repro**

```
$ grep -n "70" README.md
10:… a red-team corpus of 70 seeds with committed expected outcomes proves the checkers.
133:the red-team corpus it was built against: 70 seeds, each a small ledger with committed
141:70/70 seeds pass
$ ls src/claims_ledger/corpus/seeds | wc -l
72
$ claims-ledger corpus | tail -1
72/72 seeds pass
```

Line 141 is a transcript of the command's output, so the README shows a run that cannot
happen. `pyproject.toml` sets `readme = "README.md"`, so this text is the package's PyPI
long description: the published page would advertise 70.

Both `D49`/`K23` (the two seeds beyond 70) and the four freshness seeds landed without the
README's number moving, which is the same drift as MEDIUM-3 one file over.

**Test:** `tests/test_corpus_integrity.py::test_the_readme_seed_count_is_the_seed_count` (xfail, strict)
**Fix shape:** 70 → 72 in all three places, and keep the test; it derives the number from
the directory listing so it cannot go stale again.

---

## MEDIUM-10 — The sdist is published to PyPI without ever being proven

**Severity: MEDIUM.** Oracle clause: an artifact reaches users under a gate that did not
examine it.

**Evidence.** `release.yml`'s two proof steps are wheel-only:

```yaml
      - name: The tag and the package agree on the version
        run: |
          python -m venv /tmp/clean
          /tmp/clean/bin/pip install dist/*.whl        # ← wheel
      - name: The wheel proves itself from elsewhere
        run: |
          test -d /tmp/clean || { python -m venv /tmp/clean; /tmp/clean/bin/pip install dist/*.whl; }
          /tmp/clean/bin/claims-ledger corpus
```

`pypa/gh-action-pypi-publish` then uploads **everything in `dist/`** — the sdist too. The
sdist's only gate is `twine check --strict`, which reads metadata and renders the README;
it never installs, never imports, and never runs a seed. `ci.yml`'s `wheel` job is the
same shape and the same name.

The workflow's own header comment states a stronger claim than the workflow delivers:
*"The wheel that goes to PyPI is the one this job built and then proved from a clean
environment … so a wheel that cannot prove itself never reaches the index."* True of the
wheel; the sdist reaches the index unproven, and an sdist is what `pip install` falls back
to on any platform or policy where wheels are refused (`--no-binary :all:`).

**Verified today, out of band, that the sdist is in fact sound** — which is why this is a
gap in the gate and not a defect in the artifact:

```
$ python -m venv /tmp/sd && /tmp/sd/bin/pip install dist/claims_ledger-0.1.0.tar.gz
$ cd /tmp/elsewhere && /tmp/sd/bin/claims-ledger corpus | tail -1
72/72 seeds pass
```

**Test:** not a test — a workflow finding; recorded here with its evidence, per the brief.
**Fix shape:** in the "proves itself from elsewhere" step, build a second clean venv from
`dist/*.tar.gz` and run `claims-ledger corpus` from it too. Two venvs, four lines.

---

## MEDIUM-11 — Every action is referenced by a mutable tag or branch, including the one that holds the PyPI identity

**Severity: MEDIUM.** Supply chain. Not an oracle violation in the package's own terms;
recorded because the thread `harden-release-publication-gates` is about what can reach
PyPI and under what conditions.

**Evidence.** `.github/workflows/release.yml`:

- `pypa/gh-action-pypi-publish@release/v1` — a **branch**, not a tag, resolved at run
  time, in the one job that carries `id-token: write` and the `pypi` environment. Whoever
  can move that branch can act as this project's publisher: the OIDC token is minted for
  the job, and the action decides what to do with it and what bytes to upload.
- `actions/checkout@v7`, `actions/setup-python@v7`, `actions/upload-artifact@v7`,
  `actions/download-artifact@v7` — mutable major tags. (All four majors do exist upstream;
  checked. `download-artifact` is at v8, so v7 is a version behind, not broken.)
- `ci.yml` is the same.

Nothing here is presently exploited; the point is that the release path's integrity rests
on refs that a third party can move, in a repository whose entire argument is that a check
must be provably the check it claims to be.

**Test:** not a test — a workflow finding.
**Fix shape:** pin each `uses:` to a full 40-character commit SHA with the human-readable
version in a trailing comment, and let Dependabot bump them. Start with
`pypa/gh-action-pypi-publish`, which is the one that matters.

---

## LOW-12 — `workflow_dispatch` is a publish path for any tag, and the workflow comment reads as though it is not

**Severity: LOW.** Verifying and narrowing the standing thread
`harden-release-publication-gates`.

**What the thread asked** — "prevent manual workflow dispatch from publishing an arbitrary
**branch**" — **is done and holds.** `publish` carries
`if: startsWith(github.ref, 'refs/tags/')`, `github.ref` for a branch dispatch is
`refs/heads/…`, so a dispatch from a branch builds and stops. The second half of the
thread — "ensure tag-triggered publication runs the full test suite before upload" — is
also done: `build` runs `ruff check`, `ruff format --check`, `ty check` and `pytest -q`
before `python -m build`, unconditionally, and `publish` has `needs: build`.

**What is left.** `workflow_dispatch` accepts a **tag** as its ref (the UI's ref picker
lists tags; the REST API's `ref` field takes either). A manual dispatch on `refs/tags/vX`
therefore satisfies the publish gate and publishes — with the version-agreement check
running, since `GITHUB_REF_NAME` is the tag. That is defensible behaviour (re-running a
failed tag release), but the comment above the gate describes it as ref-independent:

> Only a tag publishes. Trusted Publishing binds the repository, the workflow file and the
> environment — never the ref — so without this a manual dispatch from any branch would
> publish whatever `__init__.py` said …

"from any branch" is precise; "Only a tag publishes" invites the reader to conclude
`workflow_dispatch` cannot publish at all. It can, from a tag.

Two smaller things on the same surface:

- **No `concurrency` group.** Two tag pushes close together run two `publish` jobs that
  race on the same PyPI project. `concurrency: { group: release, cancel-in-progress: false }`.
- **Nothing ties the tag to `CHANGELOG.md`.** With LOW-4 open, `v0.2.0` can be tagged
  while the changelog still calls that content `[Unreleased]`. A one-line grep for
  `## [${GITHUB_REF_NAME#v}]` in the build job closes it.

**Test:** not a test — a workflow finding.
**Fix shape:** reword the comment to say a dispatch publishes only from a tag ref, and
add the concurrency group and the changelog grep.

---

## LOW-13 — A trailing space on the `---` fence turns an entry with frontmatter into "no YAML frontmatter", plus eight cascading errors

**Severity: LOW.** Not an oracle violation — the exit is non-zero and the messages are
human-readable — but the message is a wrong diagnosis of a real file, which is the class
of thing that sends an author looking in the wrong place.

**Repro**

```
$ sed -i 's/^---$/--- /' entries/A0001-*.md
$ claims-ledger validate
A0001 frontmatter: no YAML frontmatter
A0001 filename and id: no id
A0001 frontmatter kind: kind `None` is not one of ['claim', 'prediction', 'hypothesis']
A0001 frontmatter stated: `None` is not ISO 8601 to the second with a UTC offset
A0001 frontmatter author: author `` is not a lowercase author name
A0001 frontmatter grade: grade `None` is not one of [...]
A0001 frontmatter supersedes: no supersedes: line (`none` or an id)
A0001 frontmatter verbatim_sha: verbatim_sha is not a 64-hex sha256
```

Applied to the whole corpus it is `0/72 seeds pass`, 576 reports, none of them naming the
actual cause.

**Mechanism.** `schema.py:653` — `head, body = text[4:].split("\n---\n", 1)`. Both fences
must be exactly `---` with no trailing whitespace. YAML permits whitespace (and a comment)
after a document marker, editors add trailing whitespace, and two trailing spaces is
Markdown's own hard-line-break syntax — which is why the *body* case matters and,
happily, does not break anything (verified: trailing whitespace on every non-fence line
leaves the corpus at 72/72; that is the control in
`test_a_transformation_that_says_nothing_new_moves_no_verdict[trailing whitespace on body lines]`).

**Observed** eight reports, all of them wrong about what is wrong.
**Required** either accept `---\s*$` as the fence, or one report that says the fence
carries trailing whitespace.

**Test:** `tests/test_corpus_integrity.py::test_a_frontmatter_fence_with_trailing_whitespace_is_still_frontmatter` (xfail, strict)
**Fix shape:** in `parse_entry`, match the fences with `re.match(r"---[ \t]*\n", …)` and
`re.search(r"\n---[ \t]*\n", …)` rather than a literal split. One line each, and the
cascade goes away with them.

---

# What held

Attacks that found nothing. An unexamined surface and a clean one must not look the same
in the record.

## The corpus

- **Line endings.** Every seed file converted to CRLF: **72/72**. `read_text` universal
  newlines carries it; the frozen-region byte comparison in `check_history` is against
  git's own blob, which is CRLF too after the conversion, so nothing drifts.
- **Unicode normalization form.** Every seed file NFD-normalized: **72/72**. The
  fingerprint normalizes to NFC before hashing and the resolver applies the same
  normalization when matching spans, exactly as the README says they must.
- **Frontmatter key order.** Every entry's frontmatter keys reversed: **72/72**.
  Frontmatter parses into a dict; nothing depends on the order the schema lists.
- **Backing block order.** Every multi-block Backing section reversed: **72/72**. The
  fingerprint sorts the block lines before hashing, which is the documented behaviour, and
  the resolver checks each block independently.
- **Trailing whitespace on body lines** (Markdown's hard line break): **72/72**. Only the
  `---` fences are brittle — LOW-13.
- **A consistent entry-id rename** (every well-formed `[A-Z]dddd` shifted by 500, in the
  entry bodies, the filenames, the citing documents and the expectation rows):
  **71/72**, and the one exception is correct behaviour, not a defect.
  `D28-challenge-against-fallen-target`'s A0004 has the Scope line
  `condition: as in A0003`, so its `verbatim_sha` genuinely covers another entry's id and
  a rename genuinely moves it. It is the **only** seed in the corpus whose frozen region
  names an id — checked, and kept as
  `test_only_one_seed_couples_its_fingerprint_to_another_entrys_id`.
- **No two seeds are the same case.** Content-hashed with ids normalized away across all
  72: no collisions.
- **No seed silently no-ops undeclared.** Five defect seeds produce no checker report at
  all — D11, D13, D33, D40, D41 — and all five are documented as review-only or as a
  known miss in the corpus README's Coverage table. The set matches exactly; kept as
  `test_only_the_documented_seeds_produce_no_report_at_all`.
- **The fixtures and the registry agree.** Every `sources.jsonl` row's `bytes` path exists,
  every sha256 matches (already covered by `test_corpus.py`), every registry id is cited by
  at least one seed, and the five `fixtures/lab-00[5-9].md` files that are *not* in the
  registry are correct — they are `lab:` grounds resolved from the filesystem, not
  `source:` grounds resolved from the registry, and the README says "five lab notes".
- **Every seed has an `expected.json` and every expectation row is matchable** — already
  held by `test_corpus.py`; re-checked and unchanged.
- The nine seeds whose defect is about ids themselves (`D20`'s `A10000` and `C0001`) are
  untouched by the rename pattern, as intended, so the archived-prefix and id-width
  classes still bind.

## Packaging

- **Both artifacts carry all 72 seeds.** `claims_ledger-0.1.0-py3-none-any.whl`: 72 seed
  directories, 219 seed files. `claims_ledger-0.1.0.tar.gz`: 72. Nothing was dropped by
  hatchling's default VCS-ignore filtering.
- **`twine check --strict` passes on both**, exit 0.
- **No host paths, absolute paths or e-mail addresses leak.** Extracted both artifacts and
  grepped for `/home/`, the build host's name, the scratch directory, and any
  `local@domain.tld` pattern: **zero hits in either.** The only e-mail-shaped string in the
  source, `corpus@example` in `run.py`'s `git -c user.email`, does not survive as a match
  and is a reserved example domain in any case.
- **The wheel proves itself from a clean venv, from elsewhere.**
  `python -m venv /tmp/clean; /tmp/clean/bin/pip install dist/*.whl; cd /tmp/elsewhere;
  claims-ledger corpus` → **72/72 seeds pass**, exit 0. `claims-ledger --version` →
  `claims-ledger 0.1.0`, and `awk '{print $2}'` on it gives `0.1.0`, which is what
  `release.yml`'s tag-agreement step parses.
- **The sdist also proves itself**, though nothing in CI asks it to — see MEDIUM-10.
  `pip install dist/*.tar.gz` into a fresh venv, `claims-ledger corpus` from elsewhere →
  **72/72**.
- **Version agreement.** `src/claims_ledger/__init__.py` (`0.1.0`) is the only place a
  version is written; `pyproject.toml` reads it via `[tool.hatch.version] path`;
  `importlib.metadata.version("claims-ledger")`, `claims-ledger --version`,
  `python -m claims_ledger --version` and the built wheel/sdist filenames all agree, and
  `CHANGELOG.md` has both a `## [0.1.0]` heading and a resolving `[0.1.0]:` link. Held as
  `test_the_version_is_the_same_in_every_place_it_is_written`. (What does *not* agree is
  which changes belong to it — LOW-4.)
- **The wheel deliberately omits `docs/` and `CHANGELOG.md`**, and every in-code pointer at
  `docs/SCHEMA.md` / `docs/FRESHNESS.md` carries the absolute GitHub URL beside the path —
  the third pass's fix, still in place in `__init__.py`, `schema.py`, `freshness.py` and
  `cli.py`'s epilog.
- **The wheel declares no runtime dependencies**, which `ci.yml`'s `wheel` job asserts
  directly.

## The workflows

- **The `harden-release-publication-gates` thread's two items are done.** `publish` is
  gated on `startsWith(github.ref, 'refs/tags/')`, carries `id-token: write` and
  `environment: pypi`, and `needs: build`; `build` runs `ruff check`, `ruff format
  --check`, `ty check` and `pytest -q` *unconditionally* — not under the tag guard —
  before `python -m build`. A `workflow_dispatch` from a branch therefore builds and
  stops. Held as `test_only_a_tag_reaches_the_publish_job` and
  `test_a_tag_runs_the_whole_suite_before_anything_is_built`. The residue is LOW-12
  (a dispatch on a *tag* ref does publish, which the comment does not say).
- **The tag-vs-package version check and the publish gate use the same condition**, so
  there is no ref for which the gate opens and the check is skipped — the third pass's
  reported hole. Checked explicitly.
- **The workflow-level `permissions:` is `contents: read`** in both files, with
  `id-token: write` scoped to the one job that needs it. No `pull_request_target`, no
  `pull_request` write permissions, no secrets in `ci.yml`.
- **`fetch-depth: 0`** on both checkouts, which the history-dependent checks need.
- **All four `actions/*@v7` majors exist upstream** (checked against the GitHub tags API:
  checkout, setup-python, upload-artifact and download-artifact all publish a `v7`), so
  the workflows are runnable as written. They are still mutable refs — MEDIUM-11.
- **`release.yml`'s multi-line `run:` blocks are safe against a silently-passing step**:
  GitHub's default shell is `bash -e {0}`, so `ruff`/`ty`/`pytest` failures abort the step.
- **The artifact handoff is sound**: `build` uploads `dist/`, `publish` downloads it to
  `dist/` in the same run; no cross-workflow artifact name reuse can reach it.

## Notes for whoever picks this up

- `.venv` in this worktree now also has `build` and `twine` installed (needed to build and
  check the artifacts). Nothing was removed, and the suite is unaffected.
- Scratch scripts for the mutation sweep and the metamorphic transforms are in the session
  scratchpad (`sweep.py`, `sweep2.py`, `sweep.txt`, `meta.py`, `rename.py`, `loose.py`).
  The four mutations worth keeping are reproduced as tests in
  `tests/test_corpus_integrity.py`; the sweep itself is not a test because it takes ~3
  minutes.
