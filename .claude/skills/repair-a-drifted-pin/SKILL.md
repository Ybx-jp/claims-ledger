---
name: repair-a-drifted-pin
description: The procedure for repairing this repository's self-hosted ledger when a pinned ground drifts — reading a freshness finding, writing the contested verdict, re-judging, and superseding an entry with its citations moved. Use when `claims-ledger freshness` or `check` reports a moved, withdrawn or unstable ground, when the pre-commit hook refuses a commit for any of the five checkers, when an edit lands inside a section named by a `code:` or `toml:` ground, and BEFORE hand-editing any file under `ledger/`.
---

# Repair a drifted pin

Eight entries under `ledger/` are pinned to sections of this package's own source. When
you edit a pinned section, `freshness` sees that the artifact no longer matches the pin
and the ledger goes contested until a person re-judges it. This is the procedure. It is
not optional detail: the entry format is append-only and checked against git history
over the whole history, so a wrong repair cannot be tidied away later.

**Never** delete a verdict, edit a committed entry above the `<!-- APPEND BELOW THIS
LINE ONLY -->` marker, or change a ground to make a checker pass. `validate` compares
against history and will catch it on the next run anywhere.

## 1. Read the finding

    .venv/bin/python -m claims_ledger freshness

Five outcomes, and they do not all mean the same thing:

| finding | meaning | what it needs |
| --- | --- | --- |
| fresh | the artifact still matches the pin | nothing; it is silent |
| **moved** | flag — the section changed under the pin | the repair below |
| **withdrawn** | failure — the pinned section is gone entirely | the repair below; `artifact:` will read `absent` |
| **unstable pin** | flag — the pin names no revision, so nothing can be compared | re-pin at a commit; there is no verdict that fixes this |
| **unknown** | failure — git could not answer | fix the repository state; **no verdict discharges it** |

If the finding is `unstable pin` or `unknown`, stop here — those are not drift, and
writing a verdict for them is writing a false record.

## 2. Let the machinery write the verdict

    .venv/bin/python -m claims_ledger freshness --write

This appends a `contested` verdict authored by `propagation`, carrying the pointer as
its evidence and the object id git would store the drifted artifact under as
`artifact:`. Exit code 1 is correct here — it wrote something.

Write this verdict with the tool, never by hand. The `artifact:` field is machine
provenance and is checked as such; a hand-written propagation verdict is a person
borrowing the authority of a check that did not run.

The entry is now `contested`, so `references` fails every site that cites it
`cites-as-live` — by name, which is how you find them.

## 3. Re-judge, as a person

This is the step no tool does. Read the claim's Assertion against the code as it now
stands and decide which of three things happened.

**(a) The claim still holds; the section merely changed.** Supersede it — see §4. A pin
cannot be edited, because Grounds sit above the append marker, and that is deliberate: a
claim re-established on new evidence is a different claim from the one established on the
old.

**(b) The claim is no longer true.** Append a `refuted` verdict authored `main`, whose
evidence points at what shows it false, and rewrite the prose that asserted it. The
citations do not move — they are removed, along with the sentence.

**(c) The flag is cosmetic — a reformat, a comment, a rename with no change of meaning.**
It is still a supersession. There is no "acknowledge without superseding" path, by
design; `docs/FRESHNESS.md` §"Why moved flags and withdrawn fails" is the argument.

## 4. Supersede

Both directions are checked against each other, and supersession is a chain, never a
tree — an entry carries exactly one `superseded` verdict.

1. `.venv/bin/python -m claims_ledger new <slug>` scaffolds the successor.
2. Copy Assertion, Scope, Warrant and Backing across. Re-pin the Grounds to the section
   as it now stands, at the commit that will hold it — see the two-commit shape below.
3. In the successor's frontmatter: `supersedes: L000n-<old-slug>`.
4. Append to the **predecessor** a verdict authored `main`:

       - <timestamp> · superseded · grade: <grade> · author: main
         evidence: entry: L000m-<new-slug> · supersedes

5. Move every citation to the new id. `references` named them in step 2; each is a
   README sentence or a docstring reading `(L000n-<slug>, cites-as-live)`.
6. `.venv/bin/python -m claims_ledger sha --write` on the successor — **before** it is
   committed. `sha --write` refuses an entry that is already in history.

## 5. Commit in two, and expect the hook to refuse the first

The successor's citation lives inside the section the successor pins — the docstring is
in the function — so one commit cannot pin itself.

- **Commit one:** the code change, the README sentence and the docstring, now naming the
  new id. This names an entry that does not exist yet, which is precisely what
  `references` exists to catch, so the pre-commit hook *will* refuse it. Use
  `git commit --no-verify`. Do not resolve the refusal by dropping the citation.
- **Commit two:** the successor entry pinned at commit one, plus the predecessor's
  `superseded` verdict. Commit this one normally and let the hook run.

Between the two commits the tree is knowingly inconsistent and the hook is bypassed, so
run the full check yourself before committing two:

    .venv/bin/python -m claims_ledger check

Five clean checkers, then commit. And when the branch lands: **merge commit, never squash
or rebase** — either one rewrites the commit the new ground names and breaks every pin at
once.

## The interpreter

Commands here name `.venv/bin/python -m claims_ledger` rather than the `claims-ledger`
console script, for the same reason the installed hook does: the console script is not on
PATH unless the virtualenv is active, and `-m` needs nothing on PATH at all.
