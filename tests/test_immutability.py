"""The frozen region, as bytes rather than as parsed sections.

`check_history`'s docstring says "the region above the APPEND marker equals the blob at
the commit that created the file". It does not compare that region. `_frozen_sections`
re-parses both sides and compares `Assertion`, `Scope`, `Grounds`, `Warrant`, `Backing`
and the frontmatter dict — so any byte of the frozen region that no section owns is
outside the comparison, and `_split_sections` gives no section the text before the first
`## ` heading.

The scaffold leaves that region empty, which is what makes it a hiding place: nothing
legitimate is ever written there, so nothing legitimate ever changes there.
"""

from __future__ import annotations

PAYLOAD = """
# Assertion

Degree, not the stale fraction, governs the aggregation error. The section below is
superseded and is kept only for the record; do not cite it.

> Reviewer's note: the grounds were withdrawn on 2026-09-06.
"""


def sealed_entry(project):
    """A full entry, committed, over which `check` is clean."""
    assert project.cl("new", "a-claim") == 0
    path = project.write_full_entry(project.entry("A0001-a-claim.md"))
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the entry, as committed")
    assert project.cl("check") == 0
    return path


def test_prose_added_above_the_first_heading_of_a_committed_entry_is_caught(project):
    """Fixed: the immutability check compared parsed sections, so the frozen region's
    preamble — every byte between the frontmatter and `## Assertion` — went unchecked."""
    path = sealed_entry(project)
    head, rest = path.read_text(encoding="utf-8").split("\n## Assertion", 1)
    path.write_text(head + PAYLOAD + "\n## Assertion" + rest, encoding="utf-8")
    assert project.cl("check") != 0


def test_validate_reports_the_preamble_edit_by_name(project, capsys):
    """Fixed: as above, reached through `validate` directly rather than through `check`."""
    path = sealed_entry(project)
    head, rest = path.read_text(encoding="utf-8").split("\n## Assertion", 1)
    path.write_text(head + PAYLOAD + "\n## Assertion" + rest, encoding="utf-8")
    capsys.readouterr()
    project.cl("validate")
    out = capsys.readouterr().out
    assert "immutable" in out


def test_a_preamble_edit_is_reported_as_outside_any_section(project, capsys):
    """Fixed: the batched history reader dropped the text-level comparison of the frozen
    region, and a preamble edit was caught only by the byte comparison, whose report says
    the text is the same — over a region whose text changed. The named report is back."""
    path = sealed_entry(project)
    head, rest = path.read_text(encoding="utf-8").split("\n## Assertion", 1)
    path.write_text(head + PAYLOAD + "\n## Assertion" + rest, encoding="utf-8")
    capsys.readouterr()
    assert project.cl("validate") != 0
    out = capsys.readouterr().out
    assert "outside any section" in out
    assert "same text" not in out


def test_an_entry_removed_from_the_index_is_not_held_immutable_under_cached(project):
    """The reversal of what this file asserted while the cached entry list was a union, and
    the intent of that assertion survives it.

    This used to stage a preamble edit over an entry taken out of the index with
    `git rm --cached`, and demand that `validate --cached` still catch it — on the reading
    that a union list errs safely. It does not: the commit being built does not carry this
    file, so there is no frozen region in it to hold, and supplying the entry anyway is what
    let a citation of it pass (see
    `test_a_citation_of_an_entry_the_commit_drops_fails_under_cached`).

    The half that matters is kept whole: a bare run, which is about the working tree, still
    catches the edit (L0229-a-cached-run-checks-the-index-alone, cites-as-live).
    """
    path = sealed_entry(project)
    head, rest = path.read_text(encoding="utf-8").split("\n## Assertion", 1)
    path.write_text(head + PAYLOAD + "\n## Assertion" + rest, encoding="utf-8")
    project.git("rm", "-q", "--cached", str(path))
    assert project.cl("validate", "--cached") == 0, "the commit does not carry this entry"
    assert project.cl("validate") != 0, "the working tree does, and the edit is caught there"


def test_an_edit_inside_a_frozen_section_is_still_caught(project):
    """The half that works, kept so a fix for the above cannot regress it."""
    path = sealed_entry(project)
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("governed by the stale fraction", "governed by degree"), "utf-8")
    assert project.cl("check") != 0
