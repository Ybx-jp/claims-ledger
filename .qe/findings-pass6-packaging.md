# Sixth pass — packaging and publication readiness

Not a verification of a fifth-pass finding: a fresh assessment of whether the artifacts and
the release process are fit to publish. Worktree `/tmp/qe6-pkg`.

## Artifacts — clean

- **Wheel** (`claims_ledger-0.1.0-py3-none-any.whl`, 270,087 bytes, 255 files): all 75 seed
  directories, 227 seed files, **byte-identical** to the source tree (`diff -rq` clean),
  including the deliberately non-UTF-8 `D50-document-that-is-not-text/docs/note-102.md`.
  No `tests/`, no `.qe/`, no `.git`, no `__pycache__`, no `.venv`. Grepped for `/home/ybx`,
  the author's e-mail, `ghp_`/`AKIA` patterns and machine names: nothing.
- **Sdist** (197,896 bytes, 273 files): carries `src/`, `tests/`, `docs/`, `pyproject.toml`,
  `README.md`, `CHANGELOG.md`, `LICENSE`, `PKG-INFO`. Unpacked somewhere unrelated to the
  checkout, `pip install ".[dev]"` then `pytest -q` → **725 passed, 12 skipped**; the twelve
  skips are `test_corpus_integrity.py` correctly self-detecting "installed, not a checkout".
- **Reproducible**: built twice into separate directories; wheel and sdist byte-for-byte
  identical across the two (`sha256sum` match, `cmp` clean).
- `RECORD` lists exactly the 255 files present and the hashes check out. `WHEEL` says
  hatchling 1.32.0, `Root-Is-Purelib: true`, `py3-none-any`. `licenses/LICENSE` is identical
  to the repo's. Metadata-Version 2.5 is a real, PyPI-accepted spec version (PEP 639/794).
- `twine check --strict` passes both. README renders under `readme_renderer[md]` (23,316
  bytes of HTML), no relative links to 404 on PyPI, no images or badges.
- **The name is free**: `claims-ledger`, `claims_ledger` and `claimsledger` all 404 on
  pypi.org, checked live.

## Install matrix

| Interpreter | Artifact | `--version` | every `--help` | `corpus` | `python -m` | sdist `pytest` |
|---|---|---|---|---|---|---|
| 3.11.15 | wheel | 0.1.0 | exit 0 | 75/75 | ok | — |
| 3.11.15 | sdist | 0.1.0 | — | 75/75 | — | 725 passed, 12 skipped |
| 3.12.3 | wheel | 0.1.0 | exit 0 | 75/75 | ok | — |
| 3.12.3 | sdist | 0.1.0 | — | 75/75 | — | install + corpus verified |
| 3.14.6 | wheel | 0.1.0 | exit 0 | 75/75 | ok | — |
| 3.14.6 | sdist | 0.1.0 | — | 75/75 | — | install + corpus verified |

All runs from a directory that is not the checkout. Also verified against the installed
wheel: `init` into an empty temp dir; a run in a directory that is **not a git repository**
(`not a git repository, so the frozen-region and append-only checks did not run`, then
`0 failure(s)`, exit 0); a run with `git` off `PATH` entirely (same shape); a bad `--root`
(exit 2, `nothing was checked`). No traceback on any of them, and none reports a false
clean pass.

## Release process

- Publication is tag-gated. `publish` additionally requires `startsWith(github.ref,
  'refs/tags/')`, so a `workflow_dispatch` from a branch stops after `build`. The
  tag-agrees-with-package step would catch a mismatched tag before `publish` runs.
- `id-token: write` is on `publish` alone; top-level `permissions: contents: read` in both
  workflows.
- Every `uses:` in both files is a 40-character SHA with a version comment, and **all five
  were dereferenced against the GitHub API** — including `pypa/gh-action-pypi-publish`,
  whose `v1.14.2` is a GPG-signed annotated tag resolving to the pinned commit.
- The full suite (ruff, ruff format, ty, pytest) gates `build` before `python -m build`, and
  `publish` depends on `build`. Both distributions are installed into clean venvs and made
  to run the corpus from elsewhere.

## Findings

MEDIUM-61 (the Trusted Publishing page a first release cannot use), MEDIUM-62 (README names
three interpreters; CI runs four), MEDIUM-63 (`ci.yml`'s `twine check` is not `--strict`),
LOW-67 (the Quickstart transcript is not reproducible) and LOW-68 (the CHANGELOG's release
link) in `QE-AUDIT.md`.

One more, recorded here rather than numbered because it is an absence rather than a defect:
**there is no RELEASING.md**. The sequence a human must perform — create the PyPI pending
publisher, create the `pypi` GitHub environment, bump `__init__.py`, update the CHANGELOG
heading, commit, tag `vX.Y.Z`, push the tag, then separately create the GitHub Release the
CHANGELOG links to — exists nowhere, and MEDIUM-61 shows the one hint that does exist
(a comment in `release.yml`) is wrong for the only release this project has ever had to do.
