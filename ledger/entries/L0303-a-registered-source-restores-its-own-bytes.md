---
id: L0303-a-registered-source-restores-its-own-bytes
kind: claim
stated: 2026-09-20T18:14:21-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 8fb2407c0d36f5ad640cbd5faa60b639d7b118155dfb4dc9c96d1e060afa598c
---

## Assertion

A source whose row is registered and whose cached bytes are gone is restored by offering those bytes again, and bytes that are not the ones the row names are still refused under a taken id.

## Scope

metric: whether the recovery README.md documents can be performed by the command it names
cohort: a registry row whose cache slot is absent, which is every row of a fresh clone
condition: the registry is committed and `ledger/cache/` is not

## Grounds

- code: src/claims_ledger/authoring.py § "register_source" =sha256:4e030e5d464c017078e96f9c2d6c78bb8d17f9181d63d82776584d1ab4a91e6a
- code: tests/test_cli.py § "test_a_registered_source_restores_its_own_bytes" =sha256:aa0bafb584ec047b6982e02d3fb817c042bab695fd1d52ee1b2757da40c41254
- code: tests/test_cli.py § "test_a_restore_cannot_restate_the_row" =sha256:f651851d9993e24ee4f72c797339f505fd37a67e6f6ec7d7e5678277a4cd94d9

## Warrant

The row is committed and the bytes are not — `ledger/cache/.gitignore` is written by `init` — so a fresh clone has every row and none of the bytes, and `check` fails per quotation until they are back. README.md documents the repair as re-running `source add` on the bytes each row's url and extraction name. `register_source` refused before it read anything: `if source_id in rows: raise`, with no `--force`, no `source update`, no `source remove`, and no branch for `row present, bytes absent`. The documented command could not perform the documented repair.

The bytes decide, and that is not a convenience. The registry is content-addressed: a row says which bytes it is about, so bytes hashing to its digest *are* that row's bytes and there is nothing left to decide. It is the same principle `L0076-a-cache-slot-is-verified-rather-than-trusted-by-name` applies one level down, where a slot already holding a file is verified against the digest rather than trusted by its name — asked of the row here instead of the slot. Bytes hashing to anything else are a second source under a taken id, which is what the refusal was always for, and it stands with the two digests named.

Three things the restore refuses rather than guesses, each because the row already says otherwise: a row that names a file in the tree has no cache slot to restore and its bytes are committed with it; `--keep-path` on a restore would move a cached source into the tree, which is a different act; and a `--type` or `--citation` that disagrees with the row is a re-registration, not a restore — if these really are a different paper they need an id of their own. Nothing is appended on the restore path, so `L0064-a-registry-row-and-its-bytes-are-written-together` is untouched in both directions: the row was written with its bytes when it was written, and a restore writes bytes for a row that already exists rather than a row without them.

`--type` and `--citation` stopped being argparse-required so that a restore need not retype what the row holds, and the requirement moved to where it belongs — a new id still cannot be registered without them, and the refusal names the flag rather than writing a row with `type: None` in it. The third test holds that half.

Measured against 0.0.3 from PyPI in a clean venv driving a throwaway project: `source add` after `rm -rf ledger/cache` exited 2 with `source id \`fx-paper\` is already registered`, while `source list` had correctly named the missing path one command earlier. The diagnosis was right and the repair was refused.

Measured again on a wheel built from this change, installed into a clean venv driving a throwaway project: `source add paper.txt --id fx-paper` after `rm -rf ledger/cache` prints `restored the bytes for fx-paper … the row stands` at exit 0, `source list` goes from exit 1 to `bytes present` at exit 0, `ledger/sources.jsonl` still holds one line, and the same command over different bytes exits 2 naming both digests.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- README.md · standing · cites-as-live
- src/claims_ledger/authoring.py · standing · cites-as-live
