"""A throwaway project with a ledger in it, for the tests that write."""

import re
import subprocess
from pathlib import Path

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

    def digest(self, rel, section=None, type_name="lab"):
        """The digest of `rel` as the working tree has it — of the named section, or of
        the whole text — which is what `freshness --write` records in a verdict's
        `artifact:` line and what an anchor stated by value names. A hand-written verdict
        in a fixture needs the real value: a discharge is a verdict that describes the
        drift in front of it, and a fixture that names the wrong digest discharges nothing.
        """
        from claims_ledger.schema import digest_of, open_ledger, section_digest

        text = (self.root / rel).read_text(encoding="utf-8")
        if section is None:
            return digest_of(text)
        found = section_digest(text, open_ledger(root=self.root).config, type_name, section)
        assert found is not None, (rel, section)
        return found

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


@pytest.fixture
def repository():
    """This checkout, for the tests that are about how it is packaged and wired."""
    return Path(__file__).resolve().parent.parent


# A by-value anchor is the digest of a section's text, and a seed writes it as a literal
# so it can be read without running the runner. A transformation of a seed's text that
# is meant to say nothing new — trailing whitespace on every line — therefore has to do
# for the digest what the runner does for `@commitNN`: name the section as the transformed
# seed holds it. A digest that named nothing in the untransformed seed (D63, D64) is left
# as written, since it is the seed's point that it matches nothing.
_POINTER_LINE = re.compile(
    r'^(?:- |\s+evidence: )(\w+): (\S+?)(?: § "([^"]+)")? [=@]', re.MULTILINE
)


def redigest(before, after):
    """Rewrite every by-value digest in the transformed seed `after` that named a section
    of an artifact as `before` held it, to the digest of that section as `after` holds
    it. `before` and `after` are seed directories of the same shape."""
    from claims_ledger.corpus.run import CORPUS, corpus_config
    from claims_ledger.schema import digest_of, section_digest

    if (before / "commits").is_dir():
        states = [
            (before / "commits" / s.name, after / "commits" / s.name)
            for s in sorted((before / "commits").iterdir())
            if s.is_dir()
        ]
    else:
        states = [(before, after)]
    mapping = {}
    for old_state, new_state in states:
        config = corpus_config(Path(CORPUS), new_state / "entries")
        for entry in sorted((new_state / "entries").glob("*.md")):
            for type_name, rel, section in _POINTER_LINE.findall(entry.read_text("utf-8")):
                if not (old_state / rel).is_file() or not (new_state / rel).is_file():
                    continue
                was = (old_state / rel).read_text(encoding="utf-8")
                now = (new_state / rel).read_text(encoding="utf-8")
                if section:
                    old = section_digest(was, config, type_name, section)
                    new = section_digest(now, config, type_name, section)
                else:
                    old, new = digest_of(was), digest_of(now)
                if old and new and old != new:
                    mapping[old] = new
    for path in after.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # D50's document is not text, and a digest is not in it
        swapped = text
        for old, new in mapping.items():
            swapped = swapped.replace(old, new)
        if swapped != text:
            path.write_text(swapped, encoding="utf-8")
