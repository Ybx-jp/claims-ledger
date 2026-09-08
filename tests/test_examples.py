"""The example portfolio is executable documentation, not a collection of snippets."""

from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent
MATERIALIZER = PROJECT / "examples" / "materialize.py"


def load_materializer():
    spec = importlib.util.spec_from_file_location("example_materializer", MATERIALIZER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ("git", *args), cwd=repo, check=True, text=True, capture_output=True
    ).stdout


def test_materialized_portfolio_is_four_independent_checked_repositories(tmp_path):
    materializer = load_materializer()
    destination = tmp_path / "portfolio"
    repos = materializer.materialize(destination)

    assert [repo.name for repo in repos] == materializer.SPEC["repositories"]
    for repo in repos:
        assert (repo / ".git").is_dir()
        assert len(git(repo, "rev-list", "--all").splitlines()) == 2
        hook = repo / ".git" / "hooks" / "pre-commit"
        assert hook.is_file() and "claims_ledger" in hook.read_text(encoding="utf-8")
        assert "0 failure(s), 0 flag(s)" in materializer.ledger(repo, "check")
        assert "bytes present" in materializer.ledger(repo, "source", "list")

    for origin, snapshot in materializer.SPEC["snapshots"]:
        assert (destination / origin).read_bytes() == (destination / snapshot).read_bytes()


def test_code_section_pin_ignores_an_unrelated_function_but_flags_its_own(tmp_path):
    materializer = load_materializer()
    destination = tmp_path / "portfolio"
    repos = materializer.materialize(destination)
    ui = next(repo for repo in repos if repo.name == "ui-webapp")
    source = ui / "src" / "dashboard.ts"

    original = source.read_text(encoding="utf-8")
    source.write_text(original.replace("Example build", "Demo build"), encoding="utf-8")
    assert "0 failure(s), 0 flag(s)" in materializer.ledger(ui, "freshness")

    source.write_text(original.replace("Evidence risk", "Claim risk"), encoding="utf-8")
    output = materializer.ledger(ui, "freshness")
    assert "0 failure(s), 1 flag(s)" in output
    assert "section 'renderRiskBanner'" in output
    with pytest.raises(subprocess.CalledProcessError) as written:
        materializer.ledger(ui, "freshness", "--write")
    assert "appended 1 contested verdict" in written.value.stdout
    assert "0 failure(s), 0 flag(s)" in materializer.ledger(ui, "freshness")


def test_research_statuses_show_prediction_hypothesis_supersession_and_challenge(tmp_path):
    materializer = load_materializer()
    repos = materializer.materialize(tmp_path / "portfolio")
    research = next(repo for repo in repos if repo.name == "research-repo")
    status = materializer.ledger(research, "status")
    rows = {}
    for line in status.splitlines():
        if line.startswith(("R", "U", "B", "D")):
            ident, kind, grade, state = line.split()
            rows[ident] = (kind, grade, state)

    assert rows["R0002-review-latency-stays-low"] == ("prediction", "argued", "open")
    assert rows["R0003-threshold-generalizes"] == ("hypothesis", "argued", "open")
    assert rows["R0005-threshold-rounds-to-seven-tenths"] == ("claim", "measured", "superseded")
    assert rows["R0007-threshold-is-cohort-invariant"] == ("claim", "measured", "contested")
    assert rows["R0009-threshold-direction-replicates"] == ("claim", "measured", "corroborated")
    assert rows["R0010-consultation-wording-retracted"] == ("claim", "asserted", "retracted")
    assert rows["R0011-single-cohort-generalization-refuted"] == ("claim", "measured", "refuted")
    assert rows["R0012-latency-and-error-rates-non-comparable"] == (
        "claim",
        "measured",
        "non-comparable",
    )


def scanned_documents(materializer, repo: Path) -> int:
    """The document count `references` prints for `repo`."""
    heading = materializer.ledger(repo, "references").splitlines()[0]
    match = re.search(r"(\d+) document", heading)
    assert match, heading
    return int(match.group(1))


@pytest.mark.parametrize(
    ("repo_name", "excluded"),
    [
        ("documentation-repo", "docs/draft-scratch.md"),
        ("ui-webapp", "docs/internal-notes.md"),
    ],
)
def test_a_configured_exclusion_removes_a_document_that_is_there(tmp_path, repo_name, excluded):
    """Both example configurations write `document-excludes` as a glob, and
    `draft-scratch.md` states in its own text that it is excluded from citation scanning.
    Under substring containment none of that was true: the file was scanned, and the
    sentence was false in a repository whose subject is checked claims. The count is
    compared against the same repository with the key emptied rather than against a
    literal, so a template that gains a document does not redden this.
    (docs/audits/0.1.0.md, QE9-95.)
    """
    materializer = load_materializer()
    repos = materializer.materialize(tmp_path / "portfolio")
    repo = next(r for r in repos if r.name == repo_name)
    assert (repo / excluded).is_file()

    with_exclusion = scanned_documents(materializer, repo)
    config = repo / "claims-ledger.toml"
    text = config.read_text(encoding="utf-8")
    emptied = re.sub(
        r"^document-excludes = .*$", "document-excludes = []", text, flags=re.MULTILINE
    )
    assert emptied != text, text
    config.write_text(emptied, encoding="utf-8")

    assert scanned_documents(materializer, repo) == with_exclusion + 1


def test_feature_guide_snippets_are_exact_repository_excerpts():
    guide = (PROJECT / "examples" / "FEATURES.md").read_text(encoding="utf-8")
    pattern = re.compile(
        r"<!-- snippet: ([^\n]+) -->\n"
        r"```[^\n]*\n"
        r"(.*?)"
        r"```\n<!-- /snippet -->",
        re.DOTALL,
    )
    snippets = pattern.findall(guide)

    assert len(snippets) >= 15
    for relative, snippet in snippets:
        source_path = PROJECT / "examples" / relative
        assert source_path.is_file(), relative
        source = source_path.read_text(encoding="utf-8")
        assert snippet.rstrip("\n") in source, f"documented snippet is no longer exact: {relative}"
