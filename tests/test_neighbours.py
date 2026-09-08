"""The authoring-time lookup and the act it exists to make writable.

`neighbours` is the one command here that answers a question rather than holding the
ledger to a rule, so what these tests hold are the properties that keep it a question:
it never fails, `check` never runs it, and what it reports is decided by nothing but the
grounds and the Scopes it read.
"""

from claims_ledger import cli, neighbours, open_ledger, validate
from claims_ledger.authoring import PLACEHOLDER_GROUNDS
from claims_ledger.schema import ACT_ALLOWS, ACTS, ENTRY_ACTS, STATUSES, load_entries


def first_entry(project):
    """The entry `write_full_entry` fills in, scaffolded first so it can be filled."""
    assert project.cl("new", "first") == 0
    return project.write_full_entry(project.entry("A0001-first.md"))


def second_entry(project, slug, grounds, cohort="the synthetic graph of these tests"):
    """A second entry beside the one `write_full_entry` writes, with grounds given."""
    assert project.cl("new", slug, "--grade", "argued") == 0
    path = next(p for p in project.entries.iterdir() if p.stem.endswith(slug))
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "TODO: the claim, in this project's words. No quotation marks.",
        "A second claim, written to sit beside the first.",
    )
    text = text.replace("metric: TODO", "metric: whether the two are one claim")
    text = text.replace("cohort: TODO", f"cohort: {cohort}")
    text = text.replace("condition: TODO", "condition: as these tests stand")
    text = text.replace(PLACEHOLDER_GROUNDS, grounds)
    text = text.replace(
        "TODO: the rule by which the grounds support the assertion.",
        "The grounds are what this entry rests on, and they are not the other entry's.",
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    return path


def test_the_act_vocabularies_differ_by_exactly_the_distinction():
    """`distinguishes` is an act between entries and not a citation act. The document
    pattern is built from `ACTS`, so this is the difference that keeps a document from
    performing it."""
    assert set(ENTRY_ACTS) - set(ACTS) == {"distinguishes"}
    assert ACT_ALLOWS["distinguishes"] == set(STATUSES)


def test_a_distinction_is_legal_against_a_target_of_any_status(project):
    """No verdict on the target can make a distinction wrong: it is a claim about two
    Scopes rather than about a truth."""
    first = first_entry(project)
    second_entry(
        project,
        "second",
        f'- lab: docs/note-001.md § "Observation" @working\n- entry: {first.stem} · distinguishes',
    )
    assert project.cl("references") == 0
    first.write_text(
        first.read_text(encoding="utf-8")
        + "\n- 2026-09-08T09:00:00-07:00 · retracted · grade: argued · author: main\n"
        "  evidence: defect: the measurement was run on the wrong graph\n",
        encoding="utf-8",
    )
    # `cites-as-live` against a retracted target would fail here; the distinction does not.
    assert project.cl("references") == 0


def test_a_distinguished_target_that_falls_propagates_nothing(project):
    """Two acts walk in `propagate`, and this is not one of them."""
    first = first_entry(project)
    second_entry(
        project,
        "second",
        f'- lab: docs/note-001.md § "Observation" @working\n- entry: {first.stem} · distinguishes',
    )
    first.write_text(
        first.read_text(encoding="utf-8")
        + "\n- 2026-09-08T09:00:00-07:00 · retracted · grade: argued · author: main\n"
        "  evidence: defect: the measurement was run on the wrong graph\n",
        encoding="utf-8",
    )
    assert project.cl("propagate", "--write") == 0
    second = next(p for p in project.entries.iterdir() if p.stem.endswith("second"))
    assert "propagation" not in second.read_text(encoding="utf-8")


def test_an_entry_resting_only_on_a_distinction_fails(project):
    first = first_entry(project)
    second_entry(project, "second", f"- entry: {first.stem} · distinguishes")
    assert project.cl("validate") == 1


def test_a_distinction_is_not_a_hypothesis_motivation(project):
    """A hypothesis names the entries motivating it. A distinction names one it is not
    built on, and cannot stand in for the motivation."""
    first = first_entry(project)
    assert (
        project.cl(
            "new",
            "bet",
            "--kind",
            "hypothesis",
            "--credence",
            "0.6",
            "--resolves-when",
            "the sweep is rerun at scale",
        )
        == 0
    )
    path = next(p for p in project.entries.iterdir() if p.stem.endswith("bet"))
    text = path.read_text(encoding="utf-8")
    text = text.replace(PLACEHOLDER_GROUNDS, f"- entry: {first.stem} · distinguishes")
    text = text.replace(
        "TODO: the rule by which the grounds support the assertion.",
        "It is falsified if the error stops tracking the stale fraction.",
    )
    path.write_text(text, encoding="utf-8")
    reports = [
        r
        for r in _validate_reports(project)
        if r.part == "Grounds" and "names the entries motivating it" in r.message
    ]
    assert reports, "a hypothesis motivated only by a distinction is not motivated"


def _validate_reports(project):
    ledger = open_ledger(str(project.root))
    return validate.run(ledger)


def test_a_shared_span_is_found_across_different_pins(project):
    """Pins are dropped before spans are compared: two entries about the same section at
    two commits are about the same section."""
    first_entry(project)
    second_entry(project, "second", '- lab: docs/note-001.md § "Observation" @deadbeef')
    ledger = open_ledger(str(project.root))
    lines = neighbours.run(ledger, "A0001-first")
    assert any("shares lab: docs/note-001.md" in line for line in lines)


def test_a_different_section_of_one_file_is_not_a_shared_span(project):
    """The span is the section and not the file. Grounding on a file is what makes a
    claim go stale for edits it does not name; the lookup reads at the same grain."""
    first_entry(project)
    second_entry(
        project,
        "second",
        '- lab: docs/note-001.md § "Method" @working',
        cohort="expander families under sum aggregation",
    )
    ledger = open_ledger(str(project.root))
    lines = neighbours.run(ledger, "A0001-first")
    assert lines == ["no entry shares a ground span or a nesting cohort with A0001-first"]


def test_a_nesting_cohort_is_a_neighbour_without_a_shared_span(project):
    first_entry(project)
    second_entry(
        project,
        "second",
        '- lab: docs/note-001.md § "Method" @working',
        cohort="the synthetic graph of these tests under mean aggregation",
    )
    ledger = open_ledger(str(project.root))
    lines = neighbours.run(ledger, "A0001-first")
    assert any("cohort nests" in line for line in lines)


def test_a_recorded_relation_is_named(project):
    first = first_entry(project)
    second_entry(
        project,
        "second",
        f'- lab: docs/note-001.md § "Observation" @working\n- entry: {first.stem} · distinguishes',
    )
    ledger = open_ledger(str(project.root))
    lines = neighbours.run(ledger, "A0001-first")
    assert any("already related: it cites this entry `distinguishes`" in line for line in lines)


def test_the_question_can_be_asked_of_a_ground_before_the_entry_exists(project):
    first_entry(project)
    ledger = open_ledger(str(project.root))
    lines = neighbours.run(ledger, 'lab: docs/note-001.md § "Observation" @working')
    assert any(line.startswith("A0001-first") for line in lines)


def test_a_target_that_is_neither_an_entry_nor_a_ground_exits_two(project, capsys):
    first_entry(project)
    assert project.cl("neighbours", "nothing-of-the-sort") == 2


def test_the_lookup_exits_zero_whatever_it_finds(project):
    """The exit code of every other command answers `is the ledger sound`. This one has
    no answer to that question and says so by never claiming one."""
    first_entry(project)
    second_entry(project, "second", '- lab: docs/note-001.md § "Observation" @working')
    assert project.cl("neighbours", "A0001-first") == 0
    assert project.cl("neighbours", "--count") == 0


def test_check_does_not_run_the_lookup():
    assert "neighbours" not in cli.CHECKERS


def test_the_count_is_the_lookup_asked_of_every_entry(project):
    first_entry(project)
    second_entry(project, "second", '- lab: docs/note-001.md § "Observation" @working')
    ledger = open_ledger(str(project.root))
    entries = load_entries(ledger)
    counts = neighbours.count(ledger, entries=entries)
    assert set(counts) == {e.id for e in entries}
    assert counts["A0001-first"] == 1
