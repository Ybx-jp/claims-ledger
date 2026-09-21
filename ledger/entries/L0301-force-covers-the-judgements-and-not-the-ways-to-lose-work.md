---
id: L0301-force-covers-the-judgements-and-not-the-ways-to-lose-work
kind: claim
stated: 2026-09-20T18:01:54-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 8aebb2dd673bb23bccd9d7306f4b436cb4b5040b6d75547b60c5ff810bb72617
---

## Assertion

`renumber --force` proceeds past the refusals that are judgements the command cannot always make correctly, and reaches none of the refusals that protect work no commit holds.

## Scope

metric: which refusals a rewrite passed `--force` proceeds past, and which still stop it
cohort: `claims-ledger renumber --write --force`, the only path in the package that rewrites commits and moves a ref
condition: a refusal has been printed and the operator has asked for the rewrite anyway

## Grounds

- code: src/claims_ledger/cli.py § "cmd_renumber" =sha256:ec5f0e891c15fe6919ab2825976b488dc830b60974ef6cf38b6f859435750916
- code: tests/test_renumber.py § "test_force_rewrites_past_a_refusal_and_lands_what_it_said_it_would" =sha256:b31bc7039e2dfb7be10ae7377a2cc4019649a55bcf8204bf2d625a0686acfdea
- code: tests/test_renumber.py § "test_force_does_not_reach_the_refusals_that_protect_uncommitted_work" =sha256:6266d285cd67299b8376bb700b8c32dfab1792f3b9db540b30d4fceb14e24705

## Warrant

`cmd_renumber` is where the line falls, and it falls in one place: `if refused and not args.force` gates the list `refusals()` returned, and the three checks after it — `branch_ref`, `checkout_holding`, `working_tree_changes` — are inside the try that carries the rewrite out and read no flag at all. So the division is structural rather than a list anyone maintains, which is what makes it worth stating as one claim.

What `--force` covers is four judgements: a by-reference pin into a commit the rewrite replaces, commits another ref also holds, a configuration that changes mid-branch, and a repository that signs its commits. Each is a question the command can get wrong — a pin it could not recognise is named in `renumber.py` as a commit the rewrite drops in silence — and an operator who has checked by hand needs a way past. What it does not cover is a dirty working tree, a branch another checkout has out, a detached HEAD, and a branch already merged. Those are not judgements: the rewrite ends by moving a ref and resetting the checkout onto it, so the first two are ways to lose work no commit holds, the third is a rewrite with no ref to land on, and the fourth is a rewrite of history that is already shared.

Both grounds in the tests are here because the claim is a conjunction and one test cannot hold it. The first drives the rewrite past a live refusal and checks what landed against the plan read before it — the ids, the remapped parent, the moved ref, the clean checkout, the citation that moved with the id, and `check` at 0. Its negative control is the same command without the flag, exiting 2 with the ref unmoved. The second passes `--force` with a dirty tree and asserts both that the rewrite did not go ahead and that the uncommitted edit is still there.

Measured before this landed: `--force` was the only branch on this path that no test drove — `grep -c force tests/test_renumber.py` was 0 over 27 tests, every one of them asserting a refusal. And the first test was checked against a mutant of the gate it is about (`if refused` in place of `if refused and not args.force`), which reddens it, so it drives the branch rather than merely reaching the function.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- docs/OPERATING.md · standing · cites-as-live
