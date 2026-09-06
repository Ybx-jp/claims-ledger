"""QE6 — Part 2b: attack HIGH-31's `depth`-group fix in `schema.section_span()`.
Unit-level (no git needed) plus one full-ledger scenario for the fenced-code-block case,
which is the one most likely to be a real, silent miss in practice."""

from claims_ledger.schema import section_span, section_text
from claims_ledger import freshness, resolve
from claims_ledger.schema import open_ledger


class FakeConfig:
    def __init__(self, pattern):
        self._pattern = pattern

    def section_pattern(self, type_name):
        return self._pattern


DEFAULT = r"^(?P<depth>#+)\s*{name}\s*$"


def span_text(text, pattern, section):
    cfg = FakeConfig(pattern)
    return section_text(text, cfg, "lab", section)


def test_a_triple_inside_double():
    text = "## Observation\n\nbody1\n\n### Detail\n\nbody2\n\n## Method\n\nbody3\n"
    got = span_text(text, DEFAULT, "Observation")
    print("### inside ##:", repr(got))
    assert "body1" in got and "body2" in got and "body3" not in got


def test_b_double_inside_triple():
    # A section pinned at a DEEPER heading (###) followed by a SHALLOWER (##) sibling of
    # something else entirely -- the shallower one must still end the deeper section.
    text = "### Detail\n\nbody1\n\n## Observation\n\nbody2\n"
    got = span_text(text, DEFAULT, "Detail")
    print("## after ### (shallower ends deeper):", repr(got))
    assert "body1" in got and "body2" not in got


def test_c_equal_depth_sibling():
    text = "## Observation\n\nbody1\n\n## Method\n\nbody2\n"
    got = span_text(text, DEFAULT, "Observation")
    print("equal depth sibling ends section:", repr(got))
    assert "body1" in got and "body2" not in got


def test_d_same_name_two_depths():
    # `## Observation` ... `### Observation` (nested, same name) ... `## Method`
    text = "## Observation\n\nbody1\n\n### Observation\n\nbody2\n\n## Method\n\nbody3\n"
    got = span_text(text, DEFAULT, "Observation")
    print("same name at two depths:", repr(got))
    assert "body1" in got and "body2" in got and "body3" not in got


def test_e_pattern_without_depth_group():
    # A configured pattern with NO `depth` group must behave exactly as before the fix:
    # ANY match at ANY level ends the section (old, flat behaviour).
    flat = r"^#+\s*{name}\s*$"  # same shape but no (?P<depth>...) group
    text = "## Observation\n\nbody1\n\n### Detail\n\nbody2\n\n## Method\n\nbody3\n"
    got = span_text(text, flat, "Observation")
    print("no-depth-group pattern (should end at ### Detail, old behaviour):", repr(got))
    assert "body1" in got and "body2" not in got


def test_f_malformed_depth_group_empty():
    # A `depth` group that always captures the empty string (misconfigured pattern):
    # len('') == len('') always, so `deeper <= depth` is always True -> every match reads
    # as nested -> the section never terminates before EOF. Not a crash, but a silent
    # "swallows everything to EOF" failure mode worth naming.
    weird = r"^(?P<depth>)#+\s*{name}\s*$"
    text = "## Observation\n\nbody1\n\n## Method\n\nbody2\n"
    got = span_text(text, weird, "Observation")
    print("empty-depth-group pattern (Method should NOT terminate, if this design holds):",
          repr(got))


def test_g_setext_heading_not_matched():
    # Setext-style headings (`Title\n===`) are not ATX (`#`), so the default pattern
    # never finds them at all -- section_span returns None, which resolve already
    # reports (a section absent at the pin) rather than a silent miss.
    text = "Observation\n===========\n\nbody1\n\nMethod\n======\n\nbody2\n"
    got = span_text(text, DEFAULT, "Observation")
    print("setext heading (expect None, not matched by ATX pattern):", got)
    assert got is None


def test_h_hash_inside_fenced_code_block():
    # A `#`-prefixed line inside a ``` fenced code block (a shell comment, a Python
    # comment, a markdown example) is not a heading -- but section_span has no fence
    # awareness and will read it as one, ending the section early.
    text = (
        "## Observation\n\n"
        "At a stale fraction of 0.1 the measured error was 0.04.\n\n"
        "```python\n"
        "# Not a heading -- a comment inside a fenced code block\n"
        "x = 1\n"
        "```\n\n"
        "The rest of the observation, which should still be in-section.\n\n"
        "## Method\n\nbody\n"
    )
    got = span_text(text, DEFAULT, "Observation")
    print("hash inside fenced code block:", repr(got))
    print("  --> 'rest of the observation' present:", "rest of the observation" in (got or ""))


def test_i_section_runs_to_eof():
    text = "## Observation\n\nbody1\n"
    got = span_text(text, DEFAULT, "Observation")
    print("section to EOF:", repr(got))
    assert got.strip() == "## Observation\n\nbody1".strip()


def test_j_fenced_code_block_full_ledger_scenario(project):
    # Real end-to-end: pin a section whose body contains a fenced code block with a
    # `#`-led comment line, then invert the text AFTER that code block, inside the
    # nominally-still-Observation section, and see whether freshness catches it.
    art = project.root / "docs" / "note-001.md"
    art.write_text(
        "# note 001\n\n"
        "## Observation\n\n"
        "At a stale fraction of 0.1 the measured error was 0.04.\n\n"
        "```python\n"
        "# a comment, not a heading\n"
        "x = 1\n"
        "```\n\n"
        "Conclusion: the result holds.\n\n"
        "## Method\n\nmean aggregation, one layer.\n",
        encoding="utf-8",
    )
    import subprocess
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts")
    out = subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    pin = out.stdout.strip()
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    text = path.read_text(encoding="utf-8").replace(
        '- lab: docs/note-001.md § "Observation" @working',
        f'- lab: docs/note-001.md § "Observation" @{pin}',
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")

    # Now edit the sentence AFTER the code fence, still logically under ## Observation.
    art.write_text(
        "# note 001\n\n"
        "## Observation\n\n"
        "At a stale fraction of 0.1 the measured error was 0.04.\n\n"
        "```python\n"
        "# a comment, not a heading\n"
        "x = 1\n"
        "```\n\n"
        "Conclusion: THE RESULT IS INVERTED AND WRONG.\n\n"
        "## Method\n\nmean aggregation, one layer.\n",
        encoding="utf-8",
    )
    out_reports = [
        (r.outcome, r.message) for r in freshness.run(open_ledger(root=project.root))
    ]
    res = [(r.outcome, r.message) for r in resolve.run(open_ledger(root=project.root))]
    print("FENCED-CODE-BLOCK SCENARIO freshness:", out_reports)
    print("FENCED-CODE-BLOCK SCENARIO resolve:", res)
