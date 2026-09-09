"""The configured rule that a citation sits inside the span its entry pins.

Off by default, so the first thing these hold is that a project which said nothing is
asked nothing. The rest is the rule itself and the two places it is asked: `references`,
which is what refuses a commit, and `sha --write`, which is the first moment it can be
asked at all.
"""

import pytest

from claims_ledger import open_ledger, references
from claims_ledger.config import ConfigError, from_table

NOTE = """# note 001

{preamble}

## Observation

At a stale fraction of 0.1 the measured error was 0.04.{inside}
"""


def set_placement(project, value):
    path = project.root / "claims-ledger.toml"
    text = path.read_text(encoding="utf-8")
    path.write_text(f'{text}\ncitation-placement = "{value}"\n', encoding="utf-8")


def entry_citing_its_own_ground(project, *, inside):
    """An entry grounded in `docs/note-001.md`, cited from that same note — inside the
    section the ground names, or above it."""
    assert project.cl("new", "first") == 0
    path = project.write_full_entry(project.entry("A0001-first.md"))
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "## References\n", "## References\n\n- docs/note-001.md · standing · cites-as-live\n"
    )
    path.write_text(text, encoding="utf-8")
    citation = "(A0001-first, cites-as-live)"
    (project.root / "docs" / "note-001.md").write_text(
        NOTE.format(
            preamble=f"The result this note establishes is {citation}." if not inside else "",
            inside=f" That is {citation}." if inside else "",
        ),
        encoding="utf-8",
    )
    return path


def test_a_project_that_said_nothing_is_asked_nothing(project):
    entry_citing_its_own_ground(project, inside=False)
    ledger = open_ledger(str(project.root))
    assert ledger.config.citation_placement == "off"
    assert project.cl("references") == 0


def test_the_setting_takes_one_of_three_values():
    for value in ("off", "flag", "fail"):
        assert from_table({"citation-placement": value}, ".").citation_placement == value
    with pytest.raises(ConfigError, match="citation-placement"):
        from_table({"citation-placement": "sometimes"}, ".")


def test_a_citation_outside_the_span_is_reported(project):
    entry_citing_its_own_ground(project, inside=False)
    set_placement(project, "flag")
    reports = references.misplaced_citations(open_ledger(str(project.root)))
    assert [r.part for r in reports] == ["docs/note-001.md"]
    assert "from outside" in reports[0].message
    # A flag prints and exits 0; the run is not a failure.
    assert project.cl("references") == 0


def test_a_citation_inside_the_span_is_not(project):
    entry_citing_its_own_ground(project, inside=True)
    set_placement(project, "flag")
    assert references.misplaced_citations(open_ledger(str(project.root))) == []
    assert project.cl("references") == 0


def test_fail_is_what_refuses_the_commit(project):
    entry_citing_its_own_ground(project, inside=False)
    set_placement(project, "fail")
    assert project.cl("references") == 1


def test_a_citation_of_an_entry_grounded_elsewhere_is_asked_nothing(project):
    """The rule needs a span in this very file to be outside of. A document that cites an
    entry resting on something else is the ordinary case and must stay silent."""
    assert project.cl("new", "first") == 0
    path = project.write_full_entry(project.entry("A0001-first.md"))
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "## References\n", "## References\n\n- docs/other.md · standing · cites-as-live\n"
    )
    path.write_text(text, encoding="utf-8")
    (project.root / "docs" / "other.md").write_text(
        "# other\n\nInherits (A0001-first, cites-as-live).\n", encoding="utf-8"
    )
    set_placement(project, "fail")
    assert references.misplaced_citations(open_ledger(str(project.root))) == []


def test_sha_write_says_so_at_the_moment_the_entry_is_written(project, capsys):
    """The write-time half. In the two-commit shape the citation is written first and the
    entry second, so `sha --write` is the first moment both exist."""
    path = entry_citing_its_own_ground(project, inside=False)
    set_placement(project, "flag")
    capsys.readouterr()
    assert project.cl("sha", "--write", "--force", str(path)) == 0
    out = capsys.readouterr().out
    assert "from outside" in out


def test_sha_write_stays_quiet_when_the_project_did_not_ask(project, capsys):
    path = entry_citing_its_own_ground(project, inside=False)
    capsys.readouterr()
    assert project.cl("sha", "--write", "--force", str(path)) == 0
    assert "from outside" not in capsys.readouterr().out
