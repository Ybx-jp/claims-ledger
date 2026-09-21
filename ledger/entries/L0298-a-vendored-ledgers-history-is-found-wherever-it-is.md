---
id: L0298-a-vendored-ledgers-history-is-found-wherever-it-is
kind: claim
stated: 2026-09-20T17:41:57-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0bf500e1cc8d63e5fb497c88536c84650bb87b1a551449d787f18151b0b88e14
---

## Assertion

The repository whose history holds a vendored ledger is found from any commit that repository can reach, not only from the branch that happens to be checked out, so a ledger committed on another ref is not reported as one no repository holds.

## Scope

metric: whether the repository holding a vendored ledger is found when the commit that vendored it is not on HEAD
cohort: a ledger in a subdirectory of another project, where `<root>/.git` is absent
condition: the entries are on a ref, or on the incoming side of an operation, that is not the branch checked out

## Grounds

- code: src/claims_ledger/schema.py § "enclosing_repository" =sha256:ff1b426b724685b6855288918cfe86ae6345e3fa69961d5fee1cc4423875de3c
- code: tests/test_merge_in_progress.py § "test_sha_write_refuses_a_vendored_entry_committed_on_another_ref" =sha256:41e916cfb081157a36191a0c3fc9c57e0c4eeb9b548a2b4d43e00bc0e38904d5

## Warrant

`enclosing_repository` is what decides, for a ledger that is not its own repository, which repository above it holds its history — and everything downstream reads a `None` from it as a ledger with no history at all. The probe it makes is therefore the whole of the rule, and it now asks `--all` together with the heads of any operation in progress, which is the same reach `committed_paths` asks for and for the same reason: a `no` is the destructive answer, the one that tells `sha --write` to go ahead, so it is only honest once every commit the repository can reach has been looked at.

The test is the second ground because the assertion is about bytes and not about an exit status. Measured on a host repository with a ledger vendored in a subdirectory and committed on `side`, the directory brought onto `main` with `git checkout side -- <dir>`: `sha --write` on a drifted entry exited 0, said nothing, and rewrote the frozen region of an entry that commit already names — which is the whole of what L0007 says must not happen, one ref over. The test asserts the file came back byte-identical, because a fixed `sha --write` refuses by raising and a non-zero exit is also what a dozen unrelated failures look like.

A guard that stood above this probe is gone with it: a `rev-parse --verify HEAD` that separated a repository with no commits from one nobody can read. `--all` over an empty repository walks nothing and exits clean, so that distinction now falls out of the same call, and the guard was wrong on its own terms — an unborn HEAD over refs that do hold the ledger skipped a repository that plainly holds it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
