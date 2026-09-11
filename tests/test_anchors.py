"""An anchor stated by value: `=sha256:<digest>` where a pointer used to say `@<commit>`.

The datum a ground rests on is the text of a section; naming it by its digest names it
without naming a commit, which is what lets an entry land in the same commit as the code
and the citation. This file holds the grammar, the digest, and what `validate` and
`resolve` make of the form. What `freshness` compares is held beside the rest of that
checker's tests.
"""

import hashlib

from claims_ledger import resolve, validate
from claims_ledger.schema import (
    digest_of,
    open_ledger,
    parse_pointer,
    read_artifact,
    section_digest,
)

NOTE = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04.
"""


def _digest(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_a_sectioned_pointer_may_state_its_anchor_by_value():
    d = "sha256:" + "ab" * 32
    p = parse_pointer(f'lab: docs/note-001.md § "Observation" ={d}')
    assert (p.type, p.target, p.section, p.sectioned) == (
        "lab",
        "docs/note-001.md",
        "Observation",
        True,
    )
    assert (p.pin, p.digest, p.by_value, p.anchor) == ("", d, True, f"={d}")


def test_a_plain_pointer_may_state_its_anchor_by_value():
    d = "sha256:" + "cd" * 32
    p = parse_pointer(f"experiment: experiments/001 ={d}")
    assert (p.sectioned, p.pin, p.digest, p.by_value) == (False, "", d, True)


def test_a_pointer_by_reference_carries_no_digest():
    p = parse_pointer('lab: docs/note-001.md § "Observation" @9fceb02')
    assert (p.pin, p.digest, p.by_value, p.anchor) == ("9fceb02", "", False, "@9fceb02")


def test_the_placeholder_parses_as_a_pending_anchor():
    p = parse_pointer('lab: docs/note-001.md § "Observation" =?')
    assert p is not None and p.by_value and p.digest == "?"


def test_the_digest_is_over_the_section_with_its_trailing_whitespace_stripped(project):
    ledger = open_ledger(root=project.root)
    section = "## Observation\n\nAt a stale fraction of 0.1 the measured error was 0.04."
    assert section_digest(NOTE, ledger.config, "lab", "Observation") == _digest(section)
    assert digest_of(section + "\n\n\n") == _digest(section)
    assert section_digest(NOTE, ledger.config, "lab", "Method") is None


def test_line_endings_are_not_part_of_the_datum(project):
    """Read through universal newlines, as every artifact is: a CRLF checkout and an LF
    one name the same datum."""
    ledger = open_ledger(root=project.root)
    crlf = project.root / "docs" / "note-crlf.md"
    crlf.write_bytes(NOTE.replace("\n", "\r\n").encode("utf-8"))
    text, unreachable = read_artifact(crlf)
    assert unreachable is None
    assert section_digest(text, ledger.config, "lab", "Observation") == section_digest(
        NOTE, ledger.config, "lab", "Observation"
    )


def _entry_with(project, ground):
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    text = path.read_text(encoding="utf-8").replace(
        '- lab: docs/note-001.md § "Observation" @working', ground
    )
    path.write_text(text, encoding="utf-8")
    return path


def _reports(project, checker):
    return [(r.outcome, r.part, r.message) for r in checker.run(open_ledger(root=project.root))]


def test_a_pending_anchor_is_refused_by_validate(project):
    _entry_with(project, '- lab: docs/note-001.md § "Observation" =?')
    found = [r for r in _reports(project, validate) if r[0] == "fail"]
    message = (
        '`lab: docs/note-001.md § "Observation" =?` has an anchor still to be computed; '
        "`claims-ledger sha --write` fills `=?` with the digest of the section as the "
        "tree has it"
    )
    assert found == [("fail", "Grounds 1", message)]


def test_an_anchor_that_is_not_a_digest_is_refused_by_validate(project):
    _entry_with(project, '- lab: docs/note-001.md § "Observation" =sha256:beef')
    messages = [r[2] for r in _reports(project, validate) if r[0] == "fail"]
    message = (
        '`lab: docs/note-001.md § "Observation" =sha256:beef`: an anchor stated by value '
        "is `=sha256:<64 hex>`, or `=?`"
    )
    assert messages == [message]


def test_a_pending_anchor_in_a_verdicts_evidence_is_refused_too(project):
    path = _entry_with(project, '- lab: docs/note-001.md § "Observation" @working')
    text = path.read_text(encoding="utf-8")
    head, marker, tail = text.partition("\n## References")
    block = (
        "- 2026-11-21T10:15:00-08:00 · corroborated · grade: measured · author: main\n"
        '  evidence: lab: docs/note-001.md § "Observation" =?\n'
        "  note: read again\n"
    )
    path.write_text(head.rstrip("\n") + "\n\n" + block + marker + tail, encoding="utf-8")
    parts = [r[1] for r in _reports(project, validate) if r[0] == "fail"]
    assert parts == ["verdict 1"]


def test_a_by_value_ground_is_read_from_the_tree_by_resolve(project):
    ledger = open_ledger(root=project.root)
    text = (project.root / "docs" / "note-001.md").read_text(encoding="utf-8")
    d = section_digest(text, ledger.config, "lab", "Observation")
    _entry_with(project, f'- lab: docs/note-001.md § "Observation" {"=" + d}')
    assert [r for r in _reports(project, resolve) if r[0] == "fail"] == []
    assert [r for r in _reports(project, validate) if r[0] == "fail"] == []


def test_a_by_value_ground_whose_section_is_not_in_the_tree_does_not_resolve(project):
    d = "sha256:" + "ab" * 32
    _entry_with(project, f'- lab: docs/note-001.md § "Method" ={d}')
    messages = [r[2] for r in _reports(project, resolve) if r[0] == "fail"]
    assert len(messages) == 1
    assert "docs/note-001.md has no section 'Method' in the working tree" in messages[0]
    assert "the entry is not committed" in messages[0]


def test_a_by_value_ground_whose_file_is_not_in_the_tree_does_not_resolve(project):
    d = "sha256:" + "ab" * 32
    _entry_with(project, f'- lab: docs/note-999.md § "Observation" ={d}')
    messages = [r[2] for r in _reports(project, resolve) if r[0] == "fail"]
    assert len(messages) == 1
    assert "docs/note-999.md is not a readable file in the working tree" in messages[0]
