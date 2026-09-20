"""A citation is read from a document's text, whatever file format the text is in.

Nothing parses a document. `CITATION_RE` runs over the bytes `read_document` returned, so
a marker in a YAML comment, a JavaScript comment, a JSON string or an HTML comment is read
exactly as one in running prose is. That is what lets a project keep the marker out of
what its readers see — a Markdown document rendered on a forge, a rendered reStructuredText
page — while the checkers go on holding it to the entry's status.

What the formats differ in is where a marker may sit, and these say what that costs:
a wrap that puts a comment leader inside the parenthesis stops the citation counting, a
wrap across whitespace alone does not, and a section ends wherever the project's pattern
matches next, which in a format the pattern was not written for is sooner than it looks.
"""

from typing import NamedTuple

import pytest

from claims_ledger import open_ledger, references, renumber

CITE = "(A0001-first, cites-as-live)"


class Fmt(NamedTuple):
    """A document in one file format, and how a marker hides in it.

    `leader` is what begins a continuation line inside that format's comment: `""` where a
    comment runs on with nothing but whitespace, and `None` where the format has no
    comment at all and the marker has to live in a string.
    """

    path: str
    text: str
    leader: str | None

    @property
    def body(self):
        return self.text.replace("{cite}", CITE)


FORMATS = (
    # Markdown, the case this was written for: a forge renders the comment to nothing and
    # the marker is still checked.
    Fmt("README.md", "# readme\n\nRetries stop at three.<!-- {cite} -->\n", ""),
    # The same document with the marker in the prose, which is the ordinary shape and the
    # control the hidden ones are read against.
    Fmt("docs/guide.md", "# guide\n\nRetries stop at three {cite}.\n", ""),
    Fmt("config.yaml", "service:\n  retries: 3  # {cite}\n", "# "),
    Fmt("settings.toml", "[service]\nretries = 3  # {cite}\n", "# "),
    # JSON has no comment syntax at all, so the marker is a string and there is no hiding
    # it from a reader of the file. It is still read.
    Fmt("package.json", '{\n  "retries": 3,\n  "claim": "{cite}"\n}\n', None),
    Fmt("app.js", "export const retries = 3;  // {cite}\n", "// "),
    Fmt("worker.go", "package main\n\nconst Retries = 3 /* {cite} */\n", " * "),
    Fmt("lib.rs", "pub const RETRIES: u32 = 3;  // {cite}\n", "// "),
    Fmt("run.sh", "#!/bin/sh\nretries=3  # {cite}\n", "# "),
    Fmt("index.html", "<p>Retries stop at three.</p>\n<!-- {cite} -->\n", ""),
    Fmt("site.css", ".retry { color: red }  /* {cite} */\n", " * "),
    Fmt("report.sql", "select 3 as retries;  -- {cite}\n", "-- "),
    Fmt("setup.cfg", "[service]\nretries = 3  ; {cite}\n", "; "),
    # A reStructuredText comment is the other format that hides a marker from its reader.
    Fmt("notes.rst", "Retries stop at three.\n\n.. {cite}\n", "   "),
    Fmt("Dockerfile", "FROM scratch\n# {cite}\n", "# "),
)

HIDDEN = tuple(f for f in FORMATS if f.path != "docs/guide.md")
# A wrap is only a wrap where the format has a comment to wrap inside, and what decides
# whether it stops counting is whether the continuation carries anything but whitespace.
LEADERS = tuple(f for f in FORMATS if f.leader and f.leader.strip())
RUNS_ON = tuple(f for f in FORMATS if f.leader is not None and not f.leader.strip())


def ids(formats):
    return [f.path for f in formats]


def set_documents(project, paths):
    path = project.root / "claims-ledger.toml"
    text = path.read_text(encoding="utf-8")
    listed = ", ".join(f'"{p}"' for p in paths)
    swapped = text.replace('documents = ["*.md", "docs/*.md"]', f"documents = [{listed}]")
    assert swapped != text
    path.write_text(swapped, encoding="utf-8")


def write(project, fmt, body=None):
    path = project.root / fmt.path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(fmt.body if body is None else body, encoding="utf-8")
    return path


def cited_from(project, formats, *, act="cites-as-live", rows=True):
    """One entry, cited from a document in each format, with a References row for each.

    The rows are what make a clean run mean something: the reverse rule holds every row to
    a document that really cites the entry that way, so a marker the checker could not see
    is a failure rather than a silent pass.
    """
    assert project.cl("new", "first") == 0
    path = project.write_full_entry(project.entry("A0001-first.md"))
    if rows:
        listed = "".join(f"- {f.path} · standing · {act}\n" for f in formats)
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace("## References\n", f"## References\n\n{listed}"), encoding="utf-8"
        )
    set_documents(project, [f.path for f in formats])
    for fmt in formats:
        write(project, fmt, fmt.text.replace("{cite}", f"(A0001-first, {act})"))
    return path


@pytest.mark.parametrize("fmt", FORMATS, ids=ids(FORMATS))
def test_a_citation_is_read_whatever_syntax_surrounds_it(project, fmt):
    cited_from(project, [fmt])
    assert references.run(open_ledger(str(project.root))) == []


def test_every_format_at_once(project):
    """All of them in one ledger, which is the shape a polyglot project actually has."""
    cited_from(project, FORMATS)
    assert references.run(open_ledger(str(project.root))) == []


@pytest.mark.parametrize("fmt", HIDDEN, ids=ids(HIDDEN))
def test_the_act_is_checked_inside_the_comment_too(project, fmt):
    """Hidden from a reader is not hidden from the rule: the act still has to be true of
    the entry's status, and an entry that is open is not one a document may cite as
    contested."""
    cited_from(project, [fmt], act="cites-as-contested")
    messages = [r.message for r in references.run(open_ledger(str(project.root)))]
    assert any("whose status is open" in m for m in messages), messages


@pytest.mark.parametrize("fmt", HIDDEN, ids=ids(HIDDEN))
def test_a_mistyped_act_in_a_comment_is_reported(project, fmt):
    """The rule that reads a citation-shaped parenthesis does not read markup either, so a
    typo hidden in a comment is reported rather than passing as text nobody looks at."""
    cited_from(project, [fmt], rows=False)
    write(project, fmt, fmt.text.replace("{cite}", "(A0001-first, cites-as-liv)"))
    messages = [r.message for r in references.run(open_ledger(str(project.root)))]
    assert any("is not a citation act" in m for m in messages), messages


@pytest.mark.parametrize("fmt", LEADERS, ids=ids(LEADERS))
def test_a_wrap_that_puts_a_comment_leader_inside_the_parenthesis_stops_counting(project, fmt):
    """`CITATION_RE` allows whitespace after the comma and nothing else, so wrapping a
    marker onto a second comment line puts a `#`, a `//` or a `*` where only space may go.

    The citation then is not one, and this is the failure that says so: the entry's
    References row names a document that, as far as the checker can see, does not cite it.
    The message points at the entry rather than at the wrap, which is worth knowing before
    reading one.
    """
    cited_from(project, [fmt])
    wrapped = f"(A0001-first,\n{fmt.leader}cites-as-live)"
    write(project, fmt, fmt.text.replace("{cite}", wrapped))
    messages = [r.message for r in references.run(open_ledger(str(project.root)))]
    assert any("does not cite A0001-first that way" in m for m in messages), messages


@pytest.mark.parametrize("fmt", RUNS_ON, ids=ids(RUNS_ON))
def test_a_wrap_across_whitespace_alone_is_still_read(project, fmt):
    """The other half of the rule, and the reason it is worth stating as the leader rather
    than as the line break: an HTML comment and an indented reStructuredText comment run on
    with nothing but whitespace, and `\\s*` matches a newline."""
    cited_from(project, [fmt])
    write(project, fmt, fmt.text.replace("{cite}", "(A0001-first,\n cites-as-live)"))
    assert references.run(open_ledger(str(project.root))) == []


def test_a_marker_that_is_not_on_one_line_is_caught_only_by_the_row(project):
    """What the References row buys, stated on its own: without it a wrapped marker is a
    clean run over a document that promises something and cites nothing."""
    fmt = Fmt("config.yaml", "service:\n  retries: 3  # {cite}\n", "# ")
    cited_from(project, [fmt], rows=False)
    write(project, fmt, fmt.text.replace("{cite}", "(A0001-first,\n  # cites-as-live)"))
    assert references.run(open_ledger(str(project.root))) == []


def test_an_id_is_renumbered_inside_a_comment(project):
    """`renumber` substitutes over the same text, so a marker hidden in a comment is
    rewritten with the ones in the prose rather than left naming an id that moved."""
    subs = renumber.substitutions({"A0001-first": "A0007-first"})
    for fmt in HIDDEN:
        assert renumber.substitute(fmt.body, subs, True) == fmt.body.replace(
            "A0001-first", "A0007-first"
        )


# --- where a marker may sit, format by format ----------------------------------------

PATTERNS = """
evidence-sectioned = ["lab", "conf", "code", "table"]
citation-placement = "fail"

[tool.claims-ledger.section-patterns]
# Anchored at the left margin, which a YAML pattern has to be: `^{name}:` alone ends the
# section at the block's own first indented key, since that line matches the same shape
# under another name and a section runs only as far as the next match.
conf = '^(?![ \\t]){name}:'
code = '^(?:export )?(?:const|function) {name}\\b'
table = '^\\[{name}\\]'
"""

PLACED = (
    # (pointer type, format, a body citing inside the span, a body citing above it)
    (
        "conf",
        Fmt("config.yaml", "", None),
        "defaults:\n  retries: 1\n\nservice:\n  retries: 3  # {cite}\n",
        "# {cite}\ndefaults:\n  retries: 1\n\nservice:\n  retries: 3\n",
    ),
    (
        "code",
        Fmt("app.js", "", None),
        "export const other = 1;\n\nexport const retries = 3;  // {cite}\n",
        "// {cite}\nexport const other = 1;\n\nexport const retries = 3;\n",
    ),
    (
        "table",
        Fmt("settings.toml", "", None),
        "[other]\nkey = 1\n\n[service]\nretries = 3  # {cite}\n",
        "# {cite}\n[other]\nkey = 1\n\n[service]\nretries = 3\n",
    ),
    (
        "lab",
        Fmt("README.md", "", None),
        "# readme\n\n## Service\n\nRetries stop at three.<!-- {cite} -->\n",
        "# readme\n\n<!-- {cite} -->\n\n## Service\n\nRetries stop at three.\n",
    ),
)
SECTIONS = {"conf": "service", "code": "retries", "table": "service", "lab": "Service"}


def grounded_in(project, type_name, fmt, body):
    """An entry pinned to a section of a document in one of these formats, cited from that
    same document — which is the pair `citation-placement` is about."""
    config = project.root / "claims-ledger.toml"
    config.write_text(
        config.read_text(encoding="utf-8").replace('evidence-sectioned = ["lab"]', "") + PATTERNS,
        encoding="utf-8",
    )
    set_documents(project, [fmt.path])
    write(project, fmt, body.replace("{cite}", CITE))
    assert project.cl("new", "first") == 0
    path = project.entry("A0001-first.md")
    text = project.write_full_entry(path).read_text(encoding="utf-8")
    text = text.replace(
        '- lab: docs/note-001.md § "Observation" @working',
        f'- {type_name}: {fmt.path} § "{SECTIONS[type_name]}" @working',
    )
    text = text.replace(
        "## References\n", f"## References\n\n- {fmt.path} · standing · cites-as-live\n"
    )
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("type_name", "fmt", "inside", "above"), PLACED, ids=[p[1].path for p in PLACED]
)
def test_a_marker_inside_the_span_its_entry_pins_passes_in_every_format(
    project, type_name, fmt, inside, above
):
    """A section is a span of text, so a comment inside one is inside it. Hiding the
    marker from a reader of the rendered page does not move it out of the span — which is
    what separates this from parking a citation somewhere quiet."""
    grounded_in(project, type_name, fmt, inside)
    assert references.misplaced_citations(open_ledger(str(project.root))) == []


@pytest.mark.parametrize(
    ("type_name", "fmt", "inside", "above"), PLACED, ids=[p[1].path for p in PLACED]
)
def test_a_marker_above_the_span_is_reported_in_every_format(
    project, type_name, fmt, inside, above
):
    grounded_in(project, type_name, fmt, above)
    reports = references.misplaced_citations(open_ledger(str(project.root)))
    assert [r.part for r in reports] == [fmt.path]
    assert "from outside" in reports[0].message


def test_a_section_ends_wherever_the_pattern_matches_next(project):
    """The trap a project meets when it points a pattern at a format it was not written
    for. The end of a section is the next line matching the same pattern under any name,
    so in a file where that shape is common the span is shorter than it looks and a marker
    written under the definition can fall outside it.
    """
    fmt = Fmt("app.js", "", None)
    body = (
        "export const retries = 3;\n"
        "export const timeout = 30;\n"
        "// {cite}\n"  # under `retries` to read, inside `timeout` to the checker
    )
    grounded_in(project, "code", fmt, body)
    reports = references.misplaced_citations(open_ledger(str(project.root)))
    assert [r.part for r in reports] == [fmt.path]
