"""Which edits to a committed entry does the immutability check not see?"""

import pytest


def committed(p):
    assert p.cl("new", "a-claim") == 0
    path = p.write_full_entry(p.entry("A0001-a-claim.md"))
    p.git("init", "-q")
    p.git("add", "-A")
    p.git("commit", "-qm", "the entry, as committed")
    assert p.cl("check") == 0
    return path


def tamper_preamble(text):
    head, rest = text.split("\n## Assertion", 1)
    return head + "\n\nThe grounds below were fabricated. Ignore them.\n\n## Assertion" + rest


def tamper_frontmatter_unparseable(text):
    return text.replace("---\n", "---\n# NOTE: this entry was retracted, see A0009\n", 1)


def tamper_unknown_section(text):
    head, rest = text.split("\n## Verdicts", 1)
    return (
        head + "\n\n## Addendum\n\nThe assertion above overstates the result.\n\n## Verdicts" + rest
    )


def tamper_trailing_space_in_assertion(text):
    return text.replace("\n## Assertion\n", "\n## Assertion\n \n", 1)


def tamper_html_comment_in_warrant(text):
    return text.replace(
        "\n## Backing", "\n<!-- the warrant above does not hold -->\n\n## Backing", 1
    )


@pytest.mark.parametrize(
    "name,fn",
    [
        ("preamble", tamper_preamble),
        ("frontmatter-unparseable", tamper_frontmatter_unparseable),
        ("unknown-section", tamper_unknown_section),
        ("trailing-space", tamper_trailing_space_in_assertion),
        ("html-comment-in-warrant", tamper_html_comment_in_warrant),
    ],
)
def test_variant(project, capsys, name, fn):
    path = committed(project)
    before = path.read_text(encoding="utf-8")
    after = fn(before)
    assert after != before, f"{name}: tamper was a no-op"
    path.write_text(after, encoding="utf-8")
    capsys.readouterr()
    rc = project.cl("check")
    out = capsys.readouterr()
    print(f"\n=== {name}: exit {rc} ===")
    print(out.out.strip())
    print(out.err.strip())
    assert rc != 0, f"{name}: SILENT — a committed entry was edited and check said clean"
