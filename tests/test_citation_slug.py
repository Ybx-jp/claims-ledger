"""The two spellings of a marker, and the configured rule that picks between them.

A marker names its entry in full, `(A0001-first, cites-as-live)`, or by the series and
number alone, `(A0001, cites-as-live)`. Both reach the same entry; a slug that is not
that entry's reaches none. Which spelling a document may use is `citation-slug`, and it
is `either` until a project says otherwise — so the first thing these hold is that a
project which said nothing is asked nothing, and that no rule downstream of a marker can
tell the two spellings apart.
"""

import pytest

from claims_ledger import lift, open_ledger, references
from claims_ledger.config import ConfigError, from_table
from claims_ledger.schema import (
    by_id,
    by_number,
    citation_slug_policy,
    cited_parts,
    load_entries,
)

NOTE = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04. {citation}
"""


def configure(project, text):
    path = project.root / "claims-ledger.toml"
    path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")


def entry_cited_as(project, marker):
    """An entry grounded in `docs/note-001.md`, cited from that note by `marker`."""
    assert project.cl("new", "first") == 0
    path = project.write_full_entry(project.entry("A0001-first.md"))
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "## References\n", "## References\n\n- docs/note-001.md · standing · cites-as-live\n"
    )
    path.write_text(text, encoding="utf-8")
    (project.root / "docs" / "note-001.md").write_text(
        NOTE.format(citation=marker), encoding="utf-8"
    )
    return path


def failures(project):
    ledger = open_ledger(str(project.root))
    return [r.message for r in references.run(ledger) if r.outcome == "fail"]


# --- the two spellings ---------------------------------------------------------------


def test_a_project_that_said_nothing_is_asked_nothing(project):
    entry_cited_as(project, "(A0001, cites-as-live)")
    assert open_ledger(str(project.root)).config.citation_slug == ((None, "either"),)
    assert project.cl("references") == 0


def test_the_short_form_reaches_the_same_entry_as_the_whole_id(project):
    entry_cited_as(project, "(A0001, cites-as-live)")
    assert failures(project) == []
    note = project.root / "docs" / "note-001.md"
    note.write_text(NOTE.format(citation="(A0001-first, cites-as-live)"), encoding="utf-8")
    assert failures(project) == []


def test_a_slug_that_is_not_the_entrys_reaches_nothing(project):
    entry_cited_as(project, "(A0001-renamed-since, cites-as-live)")
    said = failures(project)
    assert any("cites A0001-renamed-since, which does not exist" in m for m in said)
    # and it names what the number does answer to, so the repair is an edit and not a hunt
    assert any("A0001 is A0001-first" in m for m in said)


def test_two_entries_answering_to_one_number_are_not_guessed_between(project):
    entry_cited_as(project, "(A0001, cites-as-live)")
    twin = project.entry("A0001-a-twin.md")
    twin.write_text(
        project.entry("A0001-first.md")
        .read_text(encoding="utf-8")
        .replace("A0001-first", "A0001-a-twin"),
        encoding="utf-8",
    )
    said = failures(project)
    assert any("2 entries answer to that number" in m and "cannot say which" in m for m in said)


def test_cited_parts_reads_a_trailing_hyphen_as_no_slug():
    assert cited_parts("A0001-first") == ("A0001", "first")
    assert cited_parts("A0001") == ("A0001", None)
    assert cited_parts("A0001-") == ("A0001", None)


def test_by_number_keys_a_list_so_a_double_is_visible(project):
    entry_cited_as(project, "(A0001, cites-as-live)")
    entries = load_entries(open_ledger(str(project.root)))
    assert list(by_number(entries)) == ["A0001"]
    assert len(by_number(entries)["A0001"]) == 1
    assert set(by_id(entries)) == {"A0001-first"}


# --- the rule ------------------------------------------------------------------------


def test_require_refuses_the_short_form(project):
    entry_cited_as(project, "(A0001, cites-as-live)")
    configure(project, '\ncitation-slug = "require"\n')
    said = failures(project)
    assert len(said) == 1
    assert "without the entry's slug" in said[0]
    assert "`A0001-first`" in said[0]


def test_require_accepts_the_whole_id(project):
    entry_cited_as(project, "(A0001-first, cites-as-live)")
    configure(project, '\ncitation-slug = "require"\n')
    assert failures(project) == []


def test_forbid_refuses_the_slug(project):
    entry_cited_as(project, "(A0001-first, cites-as-live)")
    configure(project, '\ncitation-slug = "forbid"\n')
    said = failures(project)
    assert len(said) == 1
    assert "with the entry's slug" in said[0]
    assert "`A0001`" in said[0]


def test_forbid_accepts_the_short_form(project):
    entry_cited_as(project, "(A0001, cites-as-live)")
    configure(project, '\ncitation-slug = "forbid"\n')
    assert failures(project) == []


def test_a_marker_that_resolves_to_nothing_is_not_also_reported_for_its_shape(project):
    entry_cited_as(project, "(A0001-renamed-since, cites-as-live)")
    configure(project, '\ncitation-slug = "forbid"\n')
    said = failures(project)
    assert not any("with the entry's slug" in m for m in said)
    assert any("does not exist" in m for m in said)


# --- the rule, per path --------------------------------------------------------------


def test_the_earliest_matching_rule_governs(project):
    entry_cited_as(project, "(A0001-first, cites-as-live)")
    configure(
        project,
        "\ncitation-slug = [\n"
        '  { paths = ["docs/*.md"], slug = "forbid" },\n'
        '  { paths = ["**"], slug = "require" },\n'
        "]\n",
    )
    said = failures(project)
    assert len(said) == 1
    assert "with the entry's slug" in said[0]


def test_a_wider_rule_written_first_wins_which_is_why_order_is_the_projects(project):
    entry_cited_as(project, "(A0001-first, cites-as-live)")
    configure(
        project,
        "\ncitation-slug = [\n"
        '  { paths = ["**"], slug = "require" },\n'
        '  { paths = ["docs/*.md"], slug = "forbid" },\n'
        "]\n",
    )
    assert failures(project) == []


def test_a_document_no_rule_matches_is_asked_nothing(project):
    entry_cited_as(project, "(A0001, cites-as-live)")
    configure(project, '\ncitation-slug = [ { paths = ["README.md"], slug = "require" } ]\n')
    assert failures(project) == []


def test_the_policy_is_asked_of_the_path_and_not_of_the_filesystem(tmp_path):
    config = from_table(
        {
            "citation-slug": [
                {"paths": ["src/**/*.py"], "slug": "forbid"},
                {"paths": ["**"], "slug": "require"},
            ]
        },
        tmp_path,
    )
    assert citation_slug_policy("src/pkg/thing.py", config) == "forbid"
    assert citation_slug_policy("README.md", config) == "require"
    assert citation_slug_policy("docs/guide.md", config) == "require"
    # `*` stops at a separator, as it does for the document globs
    # `**` spans zero segments too, so `src/**/*.py` reaches `src/thing.py`
    assert citation_slug_policy("src/thing.py", config) == "forbid"


def test_a_bare_string_governs_every_document(tmp_path):
    config = from_table({"citation-slug": "forbid"}, tmp_path)
    assert config.citation_slug == ((None, "forbid"),)
    assert citation_slug_policy("anything/at/all.md", config) == "forbid"


# --- what the configuration refuses ---------------------------------------------------


def test_the_setting_takes_one_of_three_values(tmp_path):
    for value in ("either", "require", "forbid"):
        assert from_table({"citation-slug": value}, tmp_path).citation_slug == ((None, value),)


def test_a_value_outside_the_three_is_refused_by_name(tmp_path):
    with pytest.raises(ConfigError, match="citation-slug `requir` is not one of"):
        from_table({"citation-slug": "requir"}, tmp_path)


def test_a_rule_that_is_not_a_table_is_refused(tmp_path):
    with pytest.raises(ConfigError, match=r"citation-slug\[0\] is str"):
        from_table({"citation-slug": ["forbid"]}, tmp_path)


def test_a_rule_with_an_unknown_key_is_refused_by_name(tmp_path):
    with pytest.raises(ConfigError, match="unknown key\\(s\\) path"):
        from_table({"citation-slug": [{"path": ["*.md"], "slug": "forbid"}]}, tmp_path)


def test_a_rule_missing_a_key_is_refused_by_name(tmp_path):
    with pytest.raises(ConfigError, match=r"citation-slug\[0\] has no `slug`"):
        from_table({"citation-slug": [{"paths": ["*.md"]}]}, tmp_path)
    with pytest.raises(ConfigError, match=r"citation-slug\[0\] has no `paths`"):
        from_table({"citation-slug": [{"slug": "forbid"}]}, tmp_path)


def test_a_rule_with_no_paths_is_refused(tmp_path):
    with pytest.raises(ConfigError, match="not a non-empty list of globs"):
        from_table({"citation-slug": [{"paths": [], "slug": "forbid"}]}, tmp_path)
    with pytest.raises(ConfigError, match="not a non-empty list of globs"):
        from_table({"citation-slug": [{"paths": "*.md", "slug": "forbid"}]}, tmp_path)


def test_a_rules_slug_takes_one_of_the_three_values(tmp_path):
    with pytest.raises(ConfigError, match=r"citation-slug\[0\].slug `always` is not one of"):
        from_table({"citation-slug": [{"paths": ["*.md"], "slug": "always"}]}, tmp_path)


def test_a_rule_may_not_address_outside_the_root(tmp_path):
    with pytest.raises(ConfigError, match="outside the project root"):
        from_table({"citation-slug": [{"paths": ["../*.md"], "slug": "forbid"}]}, tmp_path)


def test_the_key_takes_a_string_or_a_list_and_nothing_else(tmp_path):
    with pytest.raises(ConfigError, match="citation-slug is int, expected str or list"):
        from_table({"citation-slug": 1}, tmp_path)


# --- no rule downstream of a marker reads the spelling --------------------------------


def test_the_references_row_and_the_short_form_still_have_to_agree(project):
    path = entry_cited_as(project, "(A0001, cites-as-live)")
    assert failures(project) == []
    # take the row away and the short-form marker is still the one reported
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("- docs/note-001.md · standing · cites-as-live\n", ""), "utf-8")
    said = failures(project)
    assert any("A0001-first's References section does not list this document" in m for m in said)


def test_the_verbatim_assertion_rule_counts_the_short_form_as_a_citation(project):
    path = entry_cited_as(project, "(A0001, cites-as-live)")
    assertion = path.read_text(encoding="utf-8").split("## Assertion\n\n")[1].split("\n")[0]
    note = project.root / "docs" / "note-001.md"
    note.write_text(note.read_text(encoding="utf-8") + f"\n{assertion}\n", encoding="utf-8")
    assert not any("verbatim without citing it" in m for m in failures(project))


def test_the_placement_question_is_asked_of_a_short_form_marker(project):
    """`sha --write` narrows to one entry, and it narrows by the entry rather than by the
    text of the marker — otherwise `citation-placement` would be silently off for exactly
    the markers a project configured `forbid` for."""
    entry_cited_as(project, "(A0001, cites-as-live)")
    # the marker moved out of the Observation section, which is the ground it pins
    (project.root / "docs" / "note-001.md").write_text(
        "# note 001\n\nThe result is (A0001, cites-as-live).\n\n## Observation\n\n"
        "At a stale fraction of 0.1 the measured error was 0.04.\n",
        encoding="utf-8",
    )
    configure(project, '\ncitation-placement = "fail"\n')
    ledger = open_ledger(str(project.root))
    said = references.misplaced_citations(ledger, only="A0001-first")
    assert len(said) == 1 and "from outside" in said[0].message


def test_a_roster_row_may_cite_by_the_short_form(project):
    assert (
        project.cl("new", "first", "--kind", "hypothesis", "--resolves-when", "the run ends") == 0
    )
    path = project.write_full_entry(project.entry("A0001-first.md"))
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "## References\n", "## References\n\n- ROSTER.md · standing · cites-as-live\n"
        ),
        encoding="utf-8",
    )
    (project.root / "ROSTER.md").write_text(
        "| hypothesis | status |\n| --- | --- |\n| (A0001, cites-as-live) | open |\n",
        encoding="utf-8",
    )
    assert failures(project) == []


# --- what a lift writes ---------------------------------------------------------------


def test_a_lift_writes_the_whole_id_where_the_artifact_is_not_a_document(project):
    """L0289. `renumber` rewrites a bare number only in the entries and the configured
    documents, so a bare marker anywhere else would stop following its entry."""
    config = from_table(
        {"citation-slug": "forbid", "documents": ["*.md"], "evidence-sectioned": ["code"]},
        project.root,
    )
    entry = StubEntry("A0001-first", "open")
    section = '"""Summary line.\n\n    Body that will be lifted.\n    """\n'
    parts = lift.liftable(section)
    _, line = lift.marker_for(entry, section, parts, "src/thing.py", config)
    assert line.strip() == "(A0001-first, cites-as-live)"
    _, line = lift.marker_for(entry, section, parts, "README.md", config)
    assert line.strip() == "(A0001, cites-as-live)"


def test_a_lift_sees_a_marker_in_either_spelling(project):
    config = from_table({"documents": ["*.md"]}, project.root)
    entry = StubEntry("A0001-first", "open")
    for marker in ("(A0001-first, cites-as-live)", "(A0001, cites-as-live)"):
        section = f'"""Summary line.\n\n    {marker}\n\n    Body that will be lifted.\n    """\n'
        parts = lift.liftable(section)
        assert lift.marker_for(entry, section, parts, "README.md", config) is None


class StubEntry:
    """The two things `marker_for` asks of an entry."""

    def __init__(self, ident, status):
        self.id = ident
        self._status = status

    def status(self):
        return self._status
