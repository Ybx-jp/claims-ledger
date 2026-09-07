"""What the package publishes about itself, held to what it actually does.

`README.md` states a seed count and names the interpreters CI runs; `ci.yml` and
`release.yml` state what is checked before an upload. Every one of those is a promise to
a stranger, and none of them is checked by running the package — a number in prose stays
green forever after it stops being true.

These read the checkout. A wheel-only install has none, which is why the tests that need
one are in `tests/` rather than in the corpus.
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent


def project_file(*parts):
    return PROJECT.joinpath(*parts)


def test_the_readme_states_the_seed_count_correctly_wherever_it_states_it():
    """Fixed. The defect, as this pass wrote it: README.md says `All 62 corpus seeds pass
    unchanged`; the corpus is 75. MEDIUM-48's regression only matches a count directly
    adjacent to the word, so the one site with a word in between stayed stale underneath a
    green test.

    README.md is the PyPI long description. MEDIUM-48 was this defect at three sites; the
    regression written for it guards exactly the phrasings that were already wrong. A
    regression narrower than its finding is how a defect comes back.
    """
    from claims_ledger.corpus.run import CORPUS

    n = len([p for p in (Path(CORPUS) / "seeds").iterdir() if p.is_dir()])
    readme = project_file("README.md").read_text(encoding="utf-8")
    wrong = sorted(
        {m.group(1) for m in re.finditer(r"\b(\d+)(?:[ /]\d*)?(?:\s+\w+){0,2}\s+seeds?\b", readme)}
        - {str(n)}
    )
    assert not wrong, f"README claims {wrong} seeds; there are {n}"


def test_the_readme_names_every_interpreter_ci_runs():
    """Fixed. The defect, as this pass wrote it: README.md says CI runs `Python 3.11, 3.12 and
    3.13`; ci.yml's matrix is 3.11, 3.12, 3.13 and 3.14, and 3.14 is in the package's own
    classifiers

    The PyPI long description is where a user reads which interpreters this is held to.
    Claiming fewer than are run is the harmless direction and still wrong.
    """
    ci = project_file(".github", "workflows", "ci.yml").read_text(encoding="utf-8")
    matrix = re.search(r"python:\s*\[([^\]]*)\]", ci)
    assert matrix is not None, "ci.yml has no interpreter matrix to compare against"
    readme = project_file("README.md").read_text(encoding="utf-8")
    missing = [v for v in re.findall(r"3\.\d+", matrix.group(1)) if v not in readme]
    assert not missing, f"README does not name {missing}, which CI runs"


def test_the_release_workflow_names_the_page_a_first_publish_actually_needs():
    """Fixed. The defect, as this pass wrote it: release.yml sends the operator to
    pypi.org/manage/project/claims- ledger/settings/publishing/ to configure Trusted
    Publishing. That page cannot exist before the first upload; a never-published project
    needs the account-level pending publisher. Followed literally, the first tag push fails at
    the publish step.

    The workflow's comment is the only written record of how to publish this package. A first
    release has no project page to configure a publisher on.
    """
    text = project_file(".github", "workflows", "release.yml").read_text(encoding="utf-8")
    assert "manage/account/publishing" in text, (
        "the only publishing instructions point at a project-settings page that does not "
        "exist until after the first upload"
    )


def test_ci_checks_the_metadata_the_way_the_release_does():
    """Fixed. The defect, as this pass wrote it: release.yml runs `twine check --strict`, ci.yml
    runs plain `twine check`, so a metadata regression that only --strict catches passes every
    PR and first fails at the tag, which is the run with no cheap way back

    The value of a pre-merge gate is that it fails before the irreversible step. A gate weaker
    than the one it stands in front of is not one.
    """
    ci = project_file(".github", "workflows", "ci.yml").read_text(encoding="utf-8")
    assert "twine check --strict" in ci
