"""A `§ "<section>"` pointer finds its section by a pattern the project chooses.

Before this, `§` meant a Markdown heading and nothing else, so a claim could not rest on
a named part of a source file at all, and a whole-file drift comparison called every edit
anywhere in the artifact a moved ground. Both are the same fix: one configurable pattern,
shared by the checker that resolves a pointer and the checker that asks whether it still
names what it named.
"""

import subprocess
from pathlib import Path

import pytest

from claims_ledger import freshness, resolve
from claims_ledger.config import ConfigError, default_config, load_config
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
    assert "it differs from the pin" in report.message
    assert "section" not in report.message


def test_appending_a_new_section_does_not_move_the_one_before_it(scoped):
    """The last section of an artifact runs to the end of it, so an appended section
    would otherwise lengthen its predecessor by the blank lines between them. Found by
    running the checker against a real repository, not by reading the code."""
    note(scoped, TWO_SECTIONS + "\n## Discussion\n\nThe timings will move.\n")
    assert freshness.run(open_ledger(root=scoped.root)) == []


def test_an_uncommitted_edit_does_not_claim_that_no_commits_touched_it(scoped):
    """`0 commits have touched it` of a file the author is editing right now reads as a
    checker that has lost track of its own subject; it is the ordinary pre-commit case."""
    note(scoped, TWO_SECTIONS.replace("0.04", "0.09"))
    (report,) = freshness.run(open_ledger(root=scoped.root))
    assert "uncommitted" in report.message
    assert "0 commit" not in report.message


# --- what a heading is ------------------------------------------------------------------
#
# Sixth pass, HIGH-58. The `depth` group settled which headings end a section; it did not
# settle what a heading is. A `#`-led line inside a fenced code block is a comment, a shell
# prompt or a preprocessor directive, and a Markdown lab note carrying a code snippet is
# the ordinary shape of the artifact this checker compares.


FENCED = (
    "# note 001\n\n"
    "## Observation\n\n"
    "At a stale fraction of 0.1 the measured error was 0.04.\n\n"
    "```python\n"
    "# a comment, not a heading\n"
    "## nor is this\n"
    "x = 1\n"
    "```\n\n"
    "Conclusion: the result holds.\n\n"
    "## Method\n\n"
    "Star graphs.\n"
)


def _lab(text, section="Observation"):
    from claims_ledger.config import default_config

    return section_text(
        text, default_config(Path(__file__).resolve().parent.parent), "lab", section
    )


def test_a_fenced_hash_line_does_not_end_the_section():
    span = _lab(FENCED)
    assert "Conclusion: the result holds." in span
    assert "## Method" not in span, "and the real next heading still ends it"


def test_a_tilde_fence_hides_a_heading_too():
    """`~~~` is the other fence CommonMark defines, and the one a document uses when its
    code contains backticks."""
    span = _lab(FENCED.replace("```python", "~~~python").replace("```", "~~~"))
    assert "Conclusion: the result holds." in span


def test_a_fence_opened_and_never_closed_swallows_the_rest_of_the_artifact():
    """CommonMark's answer, and the safe one: text whose end nobody can see is text this
    tool should not be finding headings in. The section runs to the end rather than
    stopping at something that is not a heading."""
    span = _lab(FENCED.replace("x = 1\n```\n", "x = 1\n"))
    assert span.endswith("Star graphs.\n")


def test_a_backtick_run_with_an_info_string_containing_a_backtick_is_not_a_fence():
    """CommonMark: a backtick fence's info string may not contain a backtick, so such a
    line is inline code in a paragraph. Read as a fence, it would hide the real headings
    after it."""
    text = (
        "# note 001\n\n"
        "## Observation\n\n"
        "```js `x`\n\n"
        "The measured error was 0.04.\n\n"
        "## Method\n\n"
        "Star graphs.\n"
    )
    span = _lab(text)
    assert "Star graphs." not in span, (
        f"the backtick run was read as an unclosed fence and swallowed the rest: {span!r}"
    )
    assert _lab(text, "Method").startswith("## Method")


def test_a_section_heading_inside_a_fence_does_not_start_a_section():
    """The other end of the same rule: a fenced `## Observation` before the real one must
    not be found first, or the compared span begins inside a code block."""
    text = "# note\n\n```\n## Observation\n\nnot the section\n```\n\n" + FENCED
    span = _lab(text)
    assert "not the section" not in span
    assert "Conclusion: the result holds." in span


def test_a_fenced_heading_in_an_entry_does_not_replace_the_section_it_names():
    """The entry parser splits on the same kind of line. A fenced `## Verdicts` after the
    real Verdicts section replaced it with an empty one, so an entry carrying a `refuted`
    verdict read as `open` — the direction that matters, because a status that goes
    backwards is a fallen claim readable as a live one."""
    from claims_ledger.schema import parse_entry

    entry = (
        "---\nid: A0001-x\n---\n\n## Assertion\n\nx\n\n## Backing\n\n"
        '- source: s · p\n  speaker: me\n  quote: "a quote"\n\n'
        "<!-- APPEND BELOW THIS LINE ONLY -->\n\n## Verdicts\n\n"
        "- 2026-01-01T00:00:00-08:00 · refuted · grade: measured · author: main\n"
        "  evidence: defect: it did not replicate\n\n## References\n"
    )
    assert parse_entry("x.md", entry).status() == "refuted", "the control"
    forged = entry + "\n```\n## Verdicts\n\n```\n"
    assert parse_entry("x.md", forged).status() == "refuted"


def test_a_fence_in_an_artifact_read_with_its_own_pattern_fails_loudly(tmp_path):
    """The cost of applying Markdown's fence grammar to every artifact, pinned rather than
    left to be discovered. A source file whose sections are `def <name>` and which has a
    line of three backticks at the left margin has that line read as a fence — wrongly. It
    is the loud direction: the section runs past its end, or is not found, and a checker
    says so. Silence is what this package may not produce, and this is not it."""
    from claims_ledger.config import from_table

    config = from_table(
        {"section-patterns": {"code": r"^def {name}\b"}, "evidence-sectioned": ["code"]},
        tmp_path,
    )
    module = 'def alpha():\n    """One."""\n\n```\n\ndef beta():\n    """Two."""\n'
    span = section_text(module, config, "code", "alpha")
    assert span is not None
    # The cost, stated as an assertion so that it is a decision on the record rather than
    # a surprise: `alpha` runs past its end and takes `beta` with it, because the backtick
    # line was read as an unclosed fence. What that produces downstream is an edit to
    # `beta` reported as `alpha` moved — a false positive a reader can see and argue with,
    # and not a ground reported fresh.
    assert "def beta" in span


PROJECT = Path(__file__).resolve().parent.parent


def test_a_hash_inside_a_fenced_code_block_does_not_end_the_section():
    """Fixed. The defect, as this pass wrote it: section_span() has no fence awareness, so a
    `#`-led line inside a ```fenced``` code block is read as a heading and ends the section it
    sits in; everything below it is outside the comparison for both freshness and resolve

    HIGH-31's `depth` group settled which *headings* end a section. It did not settle what a
    heading is. A Markdown lab note carrying a code snippet is the ordinary shape of the
    artifact this checker compares, and `# a comment` is the ordinary content of one.
    """
    doc = (
        "# note 001\n\n"
        "## Observation\n\n"
        "At a stale fraction of 0.1 the measured error was 0.04.\n\n"
        "```python\n"
        "# a comment, not a heading\n"
        "x = 1\n"
        "```\n\n"
        "Conclusion: the result holds.\n\n"
        "## Method\n\n"
        "Star graphs, one layer, sixteen dimensions.\n"
    )
    span = section_text(doc, default_config(PROJECT), "lab", "Observation")
    assert span is not None
    assert "Conclusion: the result holds." in span, (
        f"the section ended at the fence; the compared span was {span!r}"
    )
