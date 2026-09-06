# Releasing

The sequence a human runs to ship a version of `claims-ledger`, in order. Read
`.github/workflows/release.yml` before changing anything here — this file is a
description of what that workflow actually does and needs, not a generic template, and
the two have to be kept in agreement by hand.

## Once, before the first release ever

Trusted Publishing binds three things together: this repository, the workflow file that
is allowed to publish, and a GitHub Actions *environment* name. None of that exists until
someone creates it, and it cannot be created from inside the workflow.

1. **Create the PyPI account-level pending publisher.** `release.yml`'s `publish` job
   uploads via Trusted Publishing rather than a stored API token, and the ordinary way to
   set that up — the project's own `.../settings/publishing/` page — does not exist
   before a project has had a first upload. What a not-yet-published project uses
   instead is the *pending* publisher, configured once at
   https://pypi.org/manage/account/publishing/, with exactly these values:

   | Field | Value |
   |---|---|
   | PyPI project name | `claims-ledger` |
   | Owner | `Ybx-jp` |
   | Repository name | `claims-ledger` |
   | Workflow filename | `release.yml` |
   | Environment name | `pypi` |

   PyPI turns this into the project's ordinary publisher automatically the first time
   `release.yml`'s `publish` job succeeds; nothing further is needed here for the second
   release onward.

2. **Create the `pypi` GitHub environment.** `publish` runs `environment: pypi`; a
   deployment can only target an environment that already exists. In this repository:
   Settings → Environments → New environment → name it `pypi`. No protection rules are
   required for Trusted Publishing to work, though adding a required reviewer here is a
   reasonable place to put a human check before a token is minted, if that is ever
   wanted.

Both of the above are account/repository configuration, not something a commit or a tag
can carry, which is why they are done once and recorded here rather than in the
workflow.

## Every release

3. **Bump the version.** Edit `__version__` in `src/claims_ledger/__init__.py`.
   `pyproject.toml` reads the version from there (`[tool.hatch.version]`), so this is the
   only place it is written.
4. **Update `CHANGELOG.md`.** Give the release its own `## [X.Y.Z] — YYYY-MM-DD` heading
   with the changes since the last one. If the change moves what a corpus seed expects,
   name the seed in the entry — the changelog's own rule, stated at the top of the file.
5. **Commit** both of the above, on `main`.
6. **Tag the commit** `vX.Y.Z` (the `v` is load-bearing: `release.yml` triggers on
   `push: tags: ["v*"]`, and the tag-agrees-with-package step strips exactly one leading
   `v` before comparing against `__version__`).
7. **Push the tag** (`git push origin vX.Y.Z`). This is the only thing that starts a
   real release; pushing commits to `main` does not.

## What the pushed tag then does, unattended

`release.yml`'s `build` job runs the full suite (`ruff check`, `ruff format --check`,
`ty check`, `pytest -q`, `claims-ledger corpus`) again from a clean checkout, builds the
wheel and sdist, runs `twine check --strict` on both, confirms the tag and
`__version__` agree, and installs each distribution into its own clean virtual
environment to run the corpus and `--version` from outside the checkout — proving the
artifact rather than the source tree. If any of that fails, nothing is published.

`publish` then uploads both distributions to PyPI over Trusted Publishing — no token
ever touches this repository. It runs only when the ref is a tag (`workflow_dispatch`
from a branch stops after `build`), which is what keeps a manual dispatch from
publishing whatever `__init__.py` happens to say with no tag to check it against.

`github_release` runs after `publish` succeeds and creates the GitHub Release the
CHANGELOG's version headings link to (`releases/tag/vX.Y.Z`) — otherwise nothing in this
process ever makes that page, and the tag and the PyPI upload both existing does not
mean it exists. It attaches the same wheel and sdist that were uploaded to PyPI as
release assets.

## If something goes wrong mid-release

A failed `build` or a failed `publish` step means nothing reached PyPI — the tag and the
uploaded distributions are the state that matters, and a distribution's metadata cannot
be corrected once published, only superseded by a new version. There is no "retry the
same tag": PyPI refuses a re-upload of a version that has already been released, even a
byte-identical one, so recovering from a bad release means bumping to the next version
and starting again from step 3. Delete the bad tag locally and on the remote only if it
never actually published (`build` failed, or `publish` never ran) — once PyPI has the
version, the tag is the historical record of what was uploaded and should stay.
