"""Prose lifted out of an artifact and held on the entry that rests on it.

Four things, and the fourth is the one the mechanism exists for: the section is optional
so a ledger that predates it still validates; a block is well formed or says why; the
list appends and only appends across every revision; and a witness that resolves is not
yet a passage that matches — prose the artifact never held fails even where the digest
it names is perfectly well in history.
"""

import ast

import pytest

from claims_ledger import open_ledger, resolve, validate
from claims_ledger.lift import (
    LiftError,
    add_reference_row,
    citation_act,
    liftable,
    plan,
    refuse_unless_git_holds_it,
)
from claims_ledger.schema import ACT_ALLOWS, digest_of, parse_entry, section_span

MODULE = '''"""A module these tests lift from."""


def install(root, agent):
    """Write the harness into a project.

    They live in the wheel, and the three differences between the agents are
    measured against the shipped CLIs rather than assumed.
    """
    return root, agent
'''


def source_with(body):
    return MODULE.replace("    return root, agent\n", body)


@pytest.fixture
def lifted(project):
    """A project whose entry rests on a code section, committed, ready to lift."""
    root = project.root
    (root / "pkg").mkdir(exist_ok=True)
    (root / "pkg" / "mod.py").write_text(MODULE, encoding="utf-8")
    toml = root / "claims-ledger.toml"
    text = toml.read_text(encoding="utf-8")
    text = text.replace('evidence-sectioned = ["lab"]', 'evidence-sectioned = ["lab", "code"]')
    text += (
        "\n[tool.claims-ledger.section-patterns]\n"
        "code = '^(?![ \\t])(?:(?:def|class)[ \\t]+{name}\\b|{name}[ \\t]*=)'\n"
    )
    toml.write_text(text, encoding="utf-8")
    assert project.cl("new", "first") == 0
    path = project.write_full_entry(project.entry("A0001-first.md"))
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        '- lab: docs/note-001.md § "Observation" @working',
        '- code: pkg/mod.py § "install" =?',
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "seed")
    return project


def entry_of(project, name="A0001-first.md"):
    return parse_entry(project.entry(name))


def pointer_of(entry):
    return next(p for p in entry.ground_pointers if p.type == "code")


# --- the section is optional -------------------------------------------------------


def test_an_entry_with_no_passages_section_still_validates(project):
    """The rule that let a new tail section land on 258 entries that predate it."""
    assert project.cl("new", "first") == 0
    project.write_full_entry(project.entry("A0001-first.md"))
    assert project.cl("validate") == 0
    assert entry_of(project).passages == []


def test_a_passages_section_out_of_place_is_refused(project):
    assert project.cl("new", "first") == 0
    path = project.write_full_entry(project.entry("A0001-first.md"))
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("## Verdicts", "## Passages\n\n## Verdicts"), encoding="utf-8")
    assert project.cl("validate") == 1


# --- a block is well formed, or says why -------------------------------------------


def with_passage(project, block, name="A0001-first.md"):
    path = project.entry(name)
    path.write_text(path.read_text(encoding="utf-8").rstrip("\n") + "\n\n## Passages\n\n" + block)
    return path


def a_block(stamp="2031-01-01T00:00:00+00:00", author="main", lifted_line=None, prose="      body"):
    lifted_line = lifted_line or 'code: pkg/mod.py § "install" =sha256:' + "0" * 64
    return f"- {stamp} · author: {author}\n  lifted: {lifted_line}\n  passage:\n{prose}\n"


@pytest.mark.parametrize(
    "block, why",
    [
        ("- not a header\n  passage:\n      body\n", "header"),
        (a_block(stamp="2031-01-01"), "ISO 8601"),
        (a_block(author="nobody-at-all"), "author"),
        (a_block(lifted_line="entry: A0002-x · cites-as-live"), "evidence pointer"),
        (a_block(lifted_line='code: pkg/mod.py § "install" @' + "a" * 40), "by reference"),
        (a_block(lifted_line='code: pkg/mod.py § "install" =?'), "still to be computed"),
        (a_block(lifted_line='code: pkg/mod.py § "install" =sha256:nothex'), "=sha256:"),
        (a_block(lifted_line="code: pkg/mod.py =sha256:" + "0" * 64), "is not written as"),
        (a_block(prose="      "), "holds no prose"),
        (a_block(prose="body-with-no-indent"), "indented by 6 spaces"),
        ("- 2031-01-01T00:00:00+00:00 · author: main\n  passage:\n      body\n", "no `lifted:`"),
        (
            (
                "- 2031-01-01T00:00:00+00:00 · author: main\n  lifted: x\n  lifted: y\n"
                "  passage:\n      body\n"
            ),
            "second `lifted:`",
        ),
        (
            "- 2031-01-01T00:00:00+00:00 · author: main\n  nonsense: x\n  passage:\n      body\n",
            "unrecognized",
        ),
    ],
)
def test_a_malformed_block_is_named(lifted, block, why):
    with_passage(lifted, block)
    ledger = open_ledger(lifted.root)
    reports = validate.check_passages(entry_of(lifted), ledger.config)
    assert reports, "a malformed block passed"
    assert any(why in r.message for r in reports), [r.message for r in reports]


def test_a_passage_before_the_entry_was_stated_is_refused(lifted):
    with_passage(lifted, a_block(stamp="1999-01-01T00:00:00+00:00"))
    ledger = open_ledger(lifted.root)
    reports = validate.check_passages(entry_of(lifted), ledger.config)
    assert any("before the entry was stated" in r.message for r in reports)


def test_passage_timestamps_are_non_decreasing(lifted):
    with_passage(
        lifted,
        a_block(stamp="2031-02-01T00:00:00+00:00")
        + "\n"
        + a_block(stamp="2031-01-01T00:00:00+00:00"),
    )
    ledger = open_ledger(lifted.root)
    reports = validate.check_passages(entry_of(lifted), ledger.config)
    assert any("non-decreasing" in r.message for r in reports)


def test_the_comparison_lines_drop_a_blank_at_either_end():
    """Both ends, and this is the assert that was missing. The strip at the top was added
    without one, and a mutant that disabled it — `while False:` — passed ruff, ty, the
    whole suite, all five checkers and the corpus, and was committed and pushed. The rule
    is documented three lines above the code and nothing held it."""
    from claims_ledger.resolve import lines_rstripped

    assert lines_rstripped("\n\nalpha\nbeta\n\n") == ["alpha", "beta"]
    assert lines_rstripped("alpha  \n\nbeta\t") == ["alpha", "", "beta"]
    assert lines_rstripped("\n \n") == []


def test_a_stored_line_keeps_the_artifacts_own_indentation(lifted):
    with_passage(lifted, a_block(prose="          four-deep\n\n          and again"))
    passage = entry_of(lifted).passages[0]
    assert passage.text == "    four-deep\n\n    and again"


# --- the list appends and only appends ---------------------------------------------


def test_a_held_passage_may_not_be_rewritten(lifted):
    """The rule without which a passage is held by nothing at all: below the marker, so
    the frozen comparison does not reach it, and in a directory no document glob names."""
    path = with_passage(lifted, a_block(prose="      as it was"))
    lifted.git("add", "-A")
    lifted.git("commit", "-qm", "hold a passage")
    path.write_text(path.read_text(encoding="utf-8").replace("as it was", "as it never was"))
    ledger = open_ledger(lifted.root)
    reports = validate.check_history(ledger, [parse_entry(path)])
    assert any("passages append and only append" in r.message for r in reports)


def test_a_held_passage_may_not_be_dropped(lifted):
    path = with_passage(lifted, a_block(prose="      as it was"))
    lifted.git("add", "-A")
    lifted.git("commit", "-qm", "hold a passage")
    text = path.read_text(encoding="utf-8")
    path.write_text(text[: text.index("## Passages")])
    ledger = open_ledger(lifted.root)
    reports = validate.check_history(ledger, [parse_entry(path)])
    assert any("passages append and only append" in r.message for r in reports)


def test_appending_a_second_passage_is_legal(lifted):
    path = with_passage(lifted, a_block(prose="      first"))
    lifted.git("add", "-A")
    lifted.git("commit", "-qm", "hold a passage")
    path.write_text(
        path.read_text(encoding="utf-8").rstrip("\n") + "\n\n" + a_block(prose="      second")
    )
    ledger = open_ledger(lifted.root)
    assert validate.check_history(ledger, [parse_entry(path)]) == []


# --- the witness, and the passage it is supposed to prove ---------------------------


def real_witness(project):
    entry = entry_of(project)
    pointer = pointer_of(entry)
    text = (project.root / pointer.target).read_text(encoding="utf-8")
    ledger = open_ledger(project.root)
    span = section_span(text, ledger.config, pointer.type, pointer.section)
    return digest_of(text[span[0] : span[1]])


def test_a_witness_resolves_out_of_history_after_the_prose_is_gone(lifted):
    """The whole point of the shape: the tree cannot hold the pre-lift section, and the
    passage still resolves, in the same commit the lift lands in."""
    witness = real_witness(lifted)
    ledger = open_ledger(lifted.root)
    entry = entry_of(lifted)
    pointer = pointer_of(entry)
    text = (lifted.root / pointer.target).read_text(encoding="utf-8")
    _, proses, after, _ = plan(entry, pointer, text, ledger.config)
    (lifted.root / pointer.target).write_text(after, encoding="utf-8")
    path = with_passage(
        lifted,
        a_block(
            lifted_line=f'code: pkg/mod.py § "install" ={witness}',
            prose="\n".join("      " + ln for ln in proses[0].splitlines()),
        ),
    )
    reports = resolve.resolve_passage(parse_entry(path), parse_entry(path).passages[0], ledger)
    assert reports == [], [r.message for r in reports]


def test_a_witness_no_version_holds_fails(lifted):
    path = with_passage(lifted, a_block())  # a digest of all zeroes
    ledger = open_ledger(lifted.root)
    entry = parse_entry(path)
    reports = resolve.resolve_passage(entry, entry.passages[0], ledger)
    assert any("digests to the witness" in r.message for r in reports)


def test_a_passage_the_artifact_never_held_fails(lifted):
    """A witness that resolves says the section existed, not that the prose came out of
    it. This is the one failure the mechanism exists to make impossible."""
    witness = real_witness(lifted)
    path = with_passage(
        lifted,
        a_block(
            lifted_line=f'code: pkg/mod.py § "install" ={witness}',
            prose="      a sentence this module never contained",
        ),
    )
    ledger = open_ledger(lifted.root)
    entry = parse_entry(path)
    reports = resolve.resolve_passage(entry, entry.passages[0], ledger)
    assert any("contiguous run" in r.message for r in reports), [r.message for r in reports]


def test_a_passage_cut_mid_line_fails(lifted):
    """Lines, not characters. Every character of this prose is in the section, in order,
    and it starts and ends in the middle of a line — which is a quotation of nothing the
    artifact said. A substring comparison passed it."""
    witness = real_witness(lifted)
    ledger = open_ledger(lifted.root)
    entry = entry_of(lifted)
    pointer = pointer_of(entry)
    text = (lifted.root / pointer.target).read_text(encoding="utf-8")
    _, proses, _, _ = plan(entry, pointer, text, ledger.config)
    whole = proses[0]
    cut = whole[8 : len(whole) - 8]
    assert cut in whole and cut.splitlines()[0] not in whole.splitlines()
    path = with_passage(
        lifted,
        a_block(
            lifted_line=f'code: pkg/mod.py § "install" ={witness}',
            prose="\n".join("      " + ln for ln in cut.splitlines()),
        ),
    )
    entry = parse_entry(path)
    reports = resolve.resolve_passage(entry, entry.passages[0], ledger)
    assert any("contiguous run" in r.message for r in reports), [r.message for r in reports]


def test_a_passage_shorter_than_what_was_removed_is_a_known_miss(lifted):
    """Recorded rather than implied away: every line the entry holds was in the section,
    in that order, and nothing on the entry says how many there should have been. A lift
    that dropped its last line resolves, and only a reader sees it."""
    witness = real_witness(lifted)
    ledger = open_ledger(lifted.root)
    entry = entry_of(lifted)
    pointer = pointer_of(entry)
    text = (lifted.root / pointer.target).read_text(encoding="utf-8")
    _, proses, after, _ = plan(entry, pointer, text, ledger.config)
    (lifted.root / pointer.target).write_text(after, encoding="utf-8")
    kept = proses[0].splitlines()[:-1]
    assert kept, "the fixture's docstring body is one line; there is nothing to drop"
    path = with_passage(
        lifted,
        a_block(
            lifted_line=f'code: pkg/mod.py § "install" ={witness}',
            prose="\n".join("      " + ln for ln in kept),
        ),
    )
    entry = parse_entry(path)
    assert resolve.resolve_passage(entry, entry.passages[0], ledger) == []


def test_a_shallow_clone_says_so_rather_than_that_the_witness_is_unknown(lifted, tmp_path):
    """The two failures a witness can have are not the same failure, and a downstream CI
    is where the difference is felt: `actions/checkout` is depth 1 by default, so the
    commit a witness names is routinely outside the graft boundary. `digest_in_history`
    asks git whether the repository is shallow before concluding anything, so the report
    says the history was truncated rather than that the prose was never there — which is
    the report D69 holds, and it would be a false accusation here."""
    import subprocess

    assert lifted.cl("lift", "A0001-first", "--write") == 0
    lifted.git("add", "-A")
    lifted.git("commit", "-qm", "the lift")
    clone = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{lifted.root}", str(clone)], check=True
    )
    got = [(r.part, r.message) for r in resolve.run(open_ledger(root=clone))]
    passage = [m for part, m in got if part == "Passage 1"]
    assert passage, got
    assert any("shallow clone" in m for m in passage), passage
    assert not any("digests to the witness" in m for m in passage), passage


# --- what the lift takes, and what it refuses ---------------------------------------


def test_the_summary_line_stays():
    section = MODULE[MODULE.index("def install") :]
    runs = liftable(section)
    taken = "\n".join(section[lo:hi] for lo, hi in runs)
    assert "Write the harness into a project." not in taken
    assert "measured against the shipped CLIs" in taken


def test_a_line_carrying_a_citation_is_never_taken():
    section = source_with("    return root, agent\n").replace(
        "    measured against the shipped CLIs rather than assumed.\n",
        "    (A0002-other, cites-as-live)\n"
        "    measured against the shipped CLIs rather than assumed.\n",
    )
    section = section[section.index("def install") :]
    runs = liftable(section)
    taken = "\n".join(section[lo:hi] for lo, hi in runs)
    assert "A0002-other" not in taken
    assert "measured against the shipped CLIs" in taken, "the run after the citation was dropped"


def test_a_docstring_with_no_body_under_its_summary_is_not_liftable():
    assert liftable('def f():\n    """One line."""\n    pass\n') is None


def test_a_section_with_no_docstring_is_not_liftable():
    assert liftable("def f():\n    pass\n") is None


def test_a_lift_refuses_a_file_git_does_not_hold(lifted):
    path = lifted.root / "pkg" / "mod.py"
    path.write_text(MODULE + "\n# edited since HEAD\n", encoding="utf-8")
    ledger = open_ledger(lifted.root)
    with pytest.raises(LiftError, match="differs from HEAD"):
        refuse_unless_git_holds_it(ledger.repo, "pkg/mod.py", path.read_text(encoding="utf-8"))


def test_a_lift_writes_nothing_without_being_asked(lifted):
    before = (lifted.root / "pkg" / "mod.py").read_text(encoding="utf-8")
    held = lifted.entry("A0001-first.md").read_text(encoding="utf-8")
    assert lifted.cl("lift", "A0001-first") == 0
    assert (lifted.root / "pkg" / "mod.py").read_text(encoding="utf-8") == before
    assert lifted.entry("A0001-first.md").read_text(encoding="utf-8") == held


def test_a_lift_writes_both_sides_and_every_checker_passes(lifted):
    assert lifted.cl("lift", "A0001-first", "--write") == 0
    after = (lifted.root / "pkg" / "mod.py").read_text(encoding="utf-8")
    assert "measured against the shipped CLIs" not in after
    assert "Write the harness into a project." in after
    entry = entry_of(lifted)
    assert len(entry.passages) == 1
    assert "measured against the shipped CLIs" in entry.passages[0].text
    for checker in ("validate", "resolve", "references", "propagate"):
        assert lifted.cl(checker) == 0, checker


def test_a_lift_leaves_the_module_parseable(lifted):
    """The artifact a lift writes back is still Python, and still has its docstring.

    Nothing in `liftable` looks outside a docstring body, so this cannot fail by taking a
    statement — but it can fail by taking the wrong end of the body and carrying a
    closing quote with it, which is a `SyntaxError` in a file the command has already
    written. The section here has two runs of body with a citation line between them, so
    both ends of both runs are exercised.
    """
    path = lifted.root / "pkg" / "mod.py"
    path.write_text(
        '"""A module these tests lift from."""\n'
        "\n"
        "\n"
        "def install(root, agent):\n"
        '    """Write the harness into a project.\n'
        "\n"
        "    They live in the wheel, and the three differences are measured.\n"
        "\n"
        "    (A0001-first, cites-as-live) is what keeps them honest.\n"
        "\n"
        "    The installer writes one row of TARGETS per agent.\n"
        '    """\n'
        "    return root, agent\n",
        encoding="utf-8",
    )
    lifted.git("add", "-A")
    lifted.git("commit", "-qm", "two runs")
    assert lifted.cl("lift", "A0001-first", "--write") == 0
    after = path.read_text(encoding="utf-8")
    ast.parse(after)
    summary = ast.get_docstring(ast.parse(after).body[-1]) or ""
    assert summary.startswith("Write the harness")
    assert "(A0001-first, cites-as-live)" in after
    assert "three differences are measured" not in after
    assert "one row of TARGETS per agent" not in after
    assert len(entry_of(lifted).passages) == 2


def test_a_lift_can_hand_back_a_reverse_patch(lifted, tmp_path):
    patch = tmp_path / "back.patch"
    assert lifted.cl("lift", "A0001-first", "--write", "--patch", str(patch)) == 0
    text = patch.read_text(encoding="utf-8")
    assert "measured against the shipped CLIs" in text
    assert text.startswith("---")


def test_show_prints_what_the_entry_holds(lifted, capsys):
    assert lifted.cl("lift", "A0001-first", "--write") == 0
    capsys.readouterr()
    assert lifted.cl("show", "A0001-first") == 0
    assert "measured against the shipped CLIs" in capsys.readouterr().out


def test_show_says_so_when_there_is_nothing_held(lifted, capsys):
    assert lifted.cl("show", "A0001-first") == 0
    assert "holds no lifted prose" in capsys.readouterr().out


def test_lift_names_the_grounds_when_there_is_more_than_one(lifted, capsys):
    path = lifted.entry("A0001-first.md")
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "- source: fx-source · whole text",
            '- code: pkg/mod.py § "install" =?\n- source: fx-source · whole text',
        ),
        encoding="utf-8",
    )
    assert lifted.cl("sha", "--write", "--force", str(path)) == 0
    assert lifted.cl("lift", "A0001-first") == 2
    assert "--ground" in capsys.readouterr().err


def test_a_witness_git_cannot_be_asked_about_says_so(project):
    """The branch between `no version holds it` and `nobody looked`: a ledger with no
    repository has no history to search, and that is a check that could not run rather
    than prose that was never there."""
    assert project.cl("new", "first") == 0
    project.write_full_entry(project.entry("A0001-first.md"))
    witness = 'lab: docs/note-001.md § "Observation" =sha256:' + "0" * 64
    path = with_passage(project, a_block(lifted_line=witness))
    ledger = open_ledger(project.root)
    assert ledger.repo is None, "this fixture is meant to have no repository"
    entry = parse_entry(path)
    reports = resolve.resolve_passage(entry, entry.passages[0], ledger)
    assert any("no repository whose history" in r.message for r in reports), [
        r.message for r in reports
    ]


# --- and what it leaves behind ------------------------------------------------------


def test_a_lift_leaves_a_citation_where_the_prose_was(lifted):
    """The marker half of the feature, which the file used to be left without.

    Before this, a lift out of a section carrying no citation of the lifting entry was a
    pure deletion: the prose was on the entry and nothing at the site said so, and the
    only signal was a freshness flag that any edit produces and that names no id.
    """
    assert lifted.cl("lift", "A0001-first", "--write") == 0
    after = (lifted.root / "pkg" / "mod.py").read_text(encoding="utf-8")
    assert "    (A0001-first, cites-as-live)\n" in after, after
    ast.parse(after)
    assert ast.get_docstring(ast.parse(after).body[-1]).startswith("Write the harness")


def test_a_section_that_already_cites_the_entry_gets_no_second_marker(lifted):
    """The citation the author wrote is the marker, and is left where they put it."""
    path = lifted.root / "pkg" / "mod.py"
    path.write_text(
        source_with("    return root, agent\n").replace(
            "    They live in the wheel,",
            "    (A0001-first, cites-as-live)\n    They live in the wheel,",
        ),
        encoding="utf-8",
    )
    lifted.git("add", "-A")
    lifted.git("commit", "-qm", "cited")
    assert lifted.cl("lift", "A0001-first", "--write") == 0
    after = path.read_text(encoding="utf-8")
    assert after.count("(A0001-first, cites-as-live)") == 1, after


def test_the_dry_run_names_the_marker_it_would_write(lifted, capsys):
    before = (lifted.root / "pkg" / "mod.py").read_text(encoding="utf-8")
    assert lifted.cl("lift", "A0001-first") == 0
    assert "marker (A0001-first, cites-as-live)" in capsys.readouterr().out
    assert (lifted.root / "pkg" / "mod.py").read_text(encoding="utf-8") == before


def test_a_marker_outside_the_documents_gets_no_references_row(lifted):
    """`pkg/mod.py` is not a configured document here, so nothing reads the marker.

    A References row naming it would be the failure — `references` reports a row naming a
    file the checker cannot see — so the inert marker gets none.
    """
    assert lifted.cl("lift", "A0001-first", "--write") == 0
    assert entry_of(lifted).references == []
    assert lifted.cl("references") == 0


def test_a_marker_in_a_document_gets_its_references_row(lifted):
    """Where a checker does read the marker, the row it demands is written with it."""
    toml = lifted.root / "claims-ledger.toml"
    toml.write_text(
        toml.read_text(encoding="utf-8").replace(
            'documents = ["*.md", "docs/*.md"]',
            'documents = ["*.md", "docs/*.md", "pkg/*.py"]',
        ),
        encoding="utf-8",
    )
    assert lifted.cl("lift", "A0001-first", "--write") == 0
    rows = [r for _, r in entry_of(lifted).references if r]
    assert [(r.path, r.genre, r.act) for r in rows] == [("pkg/mod.py", "standing", "cites-as-live")]
    assert lifted.cl("references") == 0, "the marker and its row disagree"


def test_a_references_row_is_added_above_the_passages_section(lifted):
    """The row goes in References, which is not the end of the file once a lift has run.

    `## Passages` is the last section, so a row appended to the end of the text is a row
    in another section — and `references` would then report a document citing an entry
    that does not list it, on an entry that visibly holds the citation.
    """
    text = (
        "## Verdicts\n\n## References\n\n- a.md · standing · cites-as-live\n"
        "\n## Passages\n\n- a block\n"
    )
    out = add_reference_row(text, "- b.md · standing · cites-as-live")
    assert out.index("- b.md") < out.index("## Passages")
    assert out.index("- a.md") < out.index("- b.md")
    assert out.endswith("## Passages\n\n- a block\n")


@pytest.mark.parametrize(
    "status, act",
    [
        ("open", "cites-as-live"),
        ("corroborated", "cites-as-live"),
        ("contested", "cites-as-contested"),
        ("refuted", "cites-as-fallen"),
        ("superseded", "cites-as-fallen"),
        ("retracted", "cites-as-fallen"),
        ("non-comparable", "cites-as-fallen"),
    ],
)
def test_the_marker_is_written_with_an_act_the_status_allows(status, act):
    """A marker is an ordinary citation, so it is legal at the moment it is written."""
    assert citation_act(status) == act
    assert status in ACT_ALLOWS[citation_act(status)]
