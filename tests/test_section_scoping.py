"""A `§ "<section>"` pointer finds its section by a pattern the project chooses.

Before this, `§` meant a Markdown heading and nothing else, so a claim could not rest on
a named part of a source file at all, and a whole-file drift comparison called every edit
anywhere in the artifact a moved ground. Both are the same fix: one configurable pattern,
shared by the checker that resolves a pointer and the checker that asks whether it still
names what it named.
"""

import subprocess

import pytest

from claims_ledger import freshness, resolve
from claims_ledger.config import ConfigError, load_config
from claims_ledger.schema import open_ledger, section_text

PY_FILE = '''"""A synthetic module, written for these tests."""


def create_widget(payload):
    # The endpoint the claim is about.
    return LegacySerializer().load(payload)


def delete_widget(widget_id):
    # Nothing rests on this one.
    return None
'''

TWO_SECTIONS = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04.

## Method

Star graphs, one layer, sixteen dimensions.
"""

# A top-level Python definition, anchored at column 0 so that a nested definition does not
# end the section early and leave the rest of it uncompared.
DEF_PATTERN = r"^(?:def|class)[ \t]+{name}\b"


def configure(project, **table):
    """Rewrite the project's configuration, keeping what `init` wrote."""
    path = project.root / "claims-ledger.toml"
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    keep = [ln for ln in lines if not any(ln.startswith(f"{k.replace('_', '-')} =") for k in table)]
    extra = [f"{k.replace('_', '-')} = {v}" for k, v in table.items()]
    path.write_text("\n".join(keep + extra) + "\n", encoding="utf-8")


def head(project):
    out = subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


# --- the pattern itself ----------------------------------------------------------------


def test_the_default_is_the_markdown_heading_that_sections_always_meant(project):
    config = load_config(root=project.root)
    assert section_text(TWO_SECTIONS, config, "lab", "Observation").strip().endswith("was 0.04.")


def test_a_section_ends_where_the_next_one_begins(project):
    """One pattern decides both ends: the section runs to the next header, not to the end
    of the artifact."""
    config = load_config(root=project.root)
    observation = section_text(TWO_SECTIONS, config, "lab", "Observation")
    assert "Star graphs" not in observation
    assert section_text(TWO_SECTIONS, config, "lab", "Method").startswith("## Method")


def test_a_configured_pattern_finds_a_python_definition(project):
    configure(
        project,
        evidence_sectioned='["lab", "code"]',
        section_patterns="{ code = '" + DEF_PATTERN + "' }",
    )
    config = load_config(root=project.root)
    found = section_text(PY_FILE, config, "code", "create_widget")
    assert found.startswith("def create_widget")
    assert "delete_widget" not in found
    assert section_text(PY_FILE, config, "code", "nothing_here") is None


def test_a_section_the_artifact_does_not_have_is_not_found(project):
    config = load_config(root=project.root)
    assert section_text(TWO_SECTIONS, config, "lab", "Conclusion") is None


# --- what the configuration refuses ----------------------------------------------------


@pytest.mark.parametrize(
    ("table", "why"),
    [
        ("{ lab = '^## heading$' }", "does not contain {name}"),
        ("{ lab = '^(#+ {name}$' }", "is not a regex"),
        ("{ experiment = '^{name}$' }", "not in evidence-sectioned"),
        ("{ nowhere = '^{name}$' }", "not in evidence-sectioned"),
        ("{ lab = 3 }", "expected a string"),
    ],
)
def test_a_pattern_that_could_not_do_its_job_is_refused_at_load(project, table, why):
    """Checked once, where the configuration is read. A pattern that never mentions the
    section it is meant to find would otherwise become a checker that silently matched
    the same text for every pointer."""
    configure(project, section_patterns=table)
    with pytest.raises(ConfigError) as exc:
        load_config(root=project.root)
    assert why in str(exc.value)


# --- the seam with resolve and freshness ------------------------------------------------


@pytest.fixture
def scoped(project):
    """A claim resting on one section of a two-section note, at a commit that exists."""
    (project.root / "docs" / "note-001.md").write_text(TWO_SECTIONS, encoding="utf-8")
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the note")
    pin = head(project)
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    path.write_text(
        path.read_text(encoding="utf-8").replace("@working", f"@{pin}"), encoding="utf-8"
    )
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")
    return project


def note(project, text):
    (project.root / "docs" / "note-001.md").write_text(text, encoding="utf-8")


def test_an_edit_outside_the_section_is_not_a_moved_ground(scoped):
    """The point of the whole stage. The artifact changed, the claim's section did not,
    and a checker that reported it would be the noise that gets checkers switched off."""
    note(scoped, TWO_SECTIONS.replace("sixteen dimensions", "thirty-two dimensions"))
    assert freshness.run(open_ledger(root=scoped.root)) == []


def test_an_edit_inside_the_section_is_still_a_moved_ground(scoped):
    note(scoped, TWO_SECTIONS.replace("0.04", "0.09"))
    (report,) = freshness.run(open_ledger(root=scoped.root))
    assert report.outcome == "flag"
    assert "section 'Observation'" in report.message


def test_a_section_removed_from_a_file_that_remains_is_withdrawn(scoped):
    """The file is still there, so `resolve` says the pointer's path resolves at the pin.
    The ground it names is gone all the same."""
    note(scoped, "# note 001\n\n## Method\n\nStar graphs, one layer, sixteen dimensions.\n")
    (report,) = freshness.run(open_ledger(root=scoped.root))
    assert report.outcome == "fail"
    assert "section 'Observation' is no longer in `docs/note-001.md`" in report.message


def test_resolve_reads_the_section_through_the_configured_pattern(project):
    """The two checkers must agree about where a section is, or an entry could resolve
    against one span and be compared against another."""
    (project.root / "src").mkdir()
    (project.root / "src" / "foo.py").write_text(PY_FILE, encoding="utf-8")
    configure(
        project,
        evidence_sectioned='["lab", "code"]',
        section_patterns="{ code = '" + DEF_PATTERN + "' }",
    )
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the module")
    pin = head(project)
    assert project.cl("new", "legacy-serializer") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            'lab: docs/note-001.md § "Observation" @working',
            f'code: src/foo.py § "create_widget" @{pin}',
        ),
        encoding="utf-8",
    )
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")

    ledger = open_ledger(root=project.root)
    assert resolve.run(ledger) == []
    assert freshness.run(ledger) == []

    # An edit to the other function is not this claim's business …
    (project.root / "src" / "foo.py").write_text(
        PY_FILE.replace("Nothing rests on this one.", "Still nothing."), encoding="utf-8"
    )
    assert freshness.run(open_ledger(root=project.root)) == []

    # … and an edit inside create_widget is.
    (project.root / "src" / "foo.py").write_text(
        PY_FILE.replace("LegacySerializer", "V2Serializer"), encoding="utf-8"
    )
    (report,) = freshness.run(open_ledger(root=project.root))
    assert report.outcome == "flag"
    assert "section 'create_widget'" in report.message


def test_a_pointer_with_no_section_still_compares_the_whole_artifact(scoped):
    """Narrowing is what a section pointer buys. A plain one gives it up, and must not
    quietly inherit it."""
    configure(scoped, evidence_plain='["experiment", "note"]')
    path = next(scoped.entries.glob("A0001-*.md"))
    text = path.read_text(encoding="utf-8")
    pin = text.split("@")[1].split("\n")[0]
    scoped.git("rm", "-q", "--cached", str(path.relative_to(scoped.root)))
    path.write_text(
        text.replace(
            f'lab: docs/note-001.md § "Observation" @{pin}', f"note: docs/note-001.md @{pin}"
        ),
        encoding="utf-8",
    )
    assert scoped.cl("sha", "--write", str(path)) == 0
    scoped.git("add", "-A")
    scoped.git("commit", "-qm", "the claim, unsectioned")
    note(scoped, TWO_SECTIONS.replace("sixteen dimensions", "thirty-two dimensions"))
    (report,) = freshness.run(open_ledger(root=scoped.root))
    assert report.outcome == "flag"
    assert "touched it since the pin" in report.message
