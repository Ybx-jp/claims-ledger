"""A throwaway project with a ledger in it, for the tests that write."""

import subprocess

import pytest

from claims_ledger import cli
from claims_ledger.authoring import PLACEHOLDER_GROUNDS

SOURCE_TEXT = """A synthetic source, written for these tests.

The error under mean aggregation scales with the stale fraction and does not grow with
degree. That is the whole of the result.
"""

LAB_NOTE = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04.
"""

ASSERTION = "The mean aggregation error is governed by the stale fraction and not by degree."
QUOTE = (
    "The error under mean aggregation scales with the stale fraction and does not grow with degree."
)


class Project:
    """A project root with a ledger, and the CLI pointed at it."""

    def __init__(self, root):
        self.root = root

    def cl(self, *args):
        return cli.main(["--root", str(self.root), *args])

    @property
    def entries(self):
        return self.root / "ledger" / "entries"

    def entry(self, name):
        return self.entries / name

    def git(self, *args):
        subprocess.run(
            [
                "git",
                "-C",
                str(self.root),
                "-c",
                "user.name=test",
                "-c",
                "user.email=test@example",
                "-c",
                "commit.gpgsign=false",
                *args,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def blob(self, rel):
        """The object id git would store `rel` under, as the working tree has it.

        What `freshness --write` records in a verdict's `artifact:` line, computed the way
        the checker computes it. A hand-written verdict in a fixture needs the real value:
        a discharge is a verdict that describes the drift in front of it, and a fixture
        that names the wrong blob is a fixture whose verdict discharges nothing.
        """
        out = subprocess.run(
            ["git", "-C", str(self.root), "hash-object", "--path", rel, "--", str(self.root / rel)],
            check=True,
            capture_output=True,
            text=True,
        )
        return out.stdout.strip()

    def write_full_entry(self, path):
        """Turn a scaffolded entry into one every checker passes."""
        text = path.read_text(encoding="utf-8")
        for old, new in (
            ("TODO: the claim, in this project's words. No quotation marks.", ASSERTION),
            ("metric: TODO", "metric: mean L2 error of the aggregated representation"),
            ("cohort: TODO", "cohort: the synthetic graph of these tests"),
            ("condition: TODO", "condition: mean aggregation, one layer"),
            (
                PLACEHOLDER_GROUNDS,
                (
                    '- lab: docs/note-001.md § "Observation" @working\n'
                    "- source: fx-source · whole text"
                ),
            ),
            (
                "TODO: the rule by which the grounds support the assertion.",
                (
                    "A measured error at a known stale fraction, with the source stating "
                    "the same rule, supports the assertion over this cohort."
                ),
            ),
            (
                "## Backing\n\nnone",
                (
                    "## Backing\n\n- source: fx-source · whole text\n"
                    "  speaker: Okafor\n"
                    f'  quote: "{QUOTE}"'
                ),
            ),
        ):
            assert old in text, old
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")
        assert self.cl("sha", "--write", str(path)) == 0
        return path


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    p = Project(root)
    assert p.cl("init") == 0
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs" / "note-001.md").write_text(LAB_NOTE, encoding="utf-8")
    source = tmp_path / "source.txt"
    source.write_text(SOURCE_TEXT, encoding="utf-8")
    assert (
        p.cl(
            "source",
            "add",
            str(source),
            "--id",
            "fx-source",
            "--type",
            "paper",
            "--citation",
            "A synthetic source (these tests)",
            "--authors",
            "Okafor",
        )
        == 0
    )
    return p
