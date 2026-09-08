"""The parts of the schema a project can rename, and the parts it cannot.

The evidence pointer's name is the project's (`lab:`, `run:`, `journal:`); the grammar,
the fingerprint, the status derivation and the citation acts are not.
"""

import dataclasses
import os
from datetime import timedelta

import pytest

from claims_ledger.config import from_table
from claims_ledger.schema import (
    Verdict,
    derive_status,
    fingerprint,
    open_ledger,
    parse_pointer,
    parse_quote,
    parse_timestamp,
)
from claims_ledger.validate import is_absence_claim
from claims_ledger.validate import run as validate_run


def test_an_evidence_pointer_carries_whatever_name_it_was_written_with():
    p = parse_pointer('run: runs/2026-09-04.md § "Result" @9fceb02')
    assert (p.type, p.target, p.section, p.pin, p.sectioned) == (
        "run",
        "runs/2026-09-04.md",
        "Result",
        "9fceb02",
        True,
    )
    q = parse_pointer("experiment: experiments/001 @9fceb02")
    assert (q.type, q.sectioned, q.pin) == ("experiment", False, "9fceb02")


def test_the_reserved_pointer_types_keep_their_own_grammar():
    assert parse_pointer("entry: A0001-slug · cites-as-live").act == "cites-as-live"
    assert parse_pointer("source: fx-a · p. 3").locator == "p. 3"
    assert (
        parse_pointer('search: corpus=arxiv; query="refresh"; date=2026-09-04').fields["corpus"]
        == "arxiv"
    )
    assert parse_pointer("defect: Backing quote 1 is not a span").target.startswith("Backing")
    assert parse_pointer("not a pointer at all") is None


def test_a_quote_is_spans_separated_by_elisions():
    q = parse_quote('"the first part" […] "the last part"')
    assert q.spans == ["the first part", "the last part"]
    assert not q.lead_elided and not q.trail_elided
    assert parse_quote('[…] "a tail of a sentence"').lead_elided
    assert parse_quote("no quotation marks") is None


def test_the_fingerprint_ignores_emphasis_whitespace_and_block_order():
    scope = "metric: error\ncohort: all\ncondition: mean aggregation"
    blocks = [("fx-a · p. 1", "Okafor", '"one"'), ("fx-b · p. 2", "Lindqvist", '"two"')]
    a = fingerprint(scope, blocks)
    b = fingerprint(
        "metric:  *error*\n\ncohort: all\ncondition:  mean   aggregation", list(reversed(blocks))
    )
    assert a == b
    assert a != fingerprint(scope, [(s, "Someone else", q) for s, _, q in blocks])


def verdict(status, author="main"):
    return Verdict(index=1, raw="", status=status, author=author, grade="measured")


def test_status_is_the_last_legal_verdict():
    assert derive_status([]) == "open"
    assert derive_status([verdict("corroborated"), verdict("contested")]) == "contested"
    # Terminal stops the walk, except that reinstatement is supersession.
    assert derive_status([verdict("retracted"), verdict("corroborated")]) == "retracted"
    assert derive_status([verdict("refuted"), verdict("superseded")]) == "superseded"
    assert derive_status([verdict("refuted"), verdict("superseded"), verdict("superseded")]) == (
        "superseded"
    )


@pytest.mark.parametrize(
    "text, absent",
    [
        ("Nobody has measured this before.", True),
        ("This is the first report of the effect.", True),
        ("The result is not found in the current scan.", True),
        ("No refresh policy has been measured on this graph.", True),
        ("The no-refresh baseline loses 4 points.", False),
        ("Mean aggregation error grows with the stale fraction.", False),
    ],
)
def test_the_absence_heuristic_is_what_the_corpus_says_it_is(text, absent):
    assert is_absence_claim(text) is absent


ENTRY = """---
id: A0001-a-renamed-evidence-type
kind: claim
stated: 2026-09-04T12:00:00+00:00
author: main
grade: measured
supersedes: none
verbatim_sha: {sha}
---

## Assertion

The measured error is governed by the stale fraction.

## Scope

metric: mean L2 error
cohort: the synthetic graph
condition: mean aggregation

## Grounds

- {ground}

## Warrant

A measurement at a known stale fraction supports the assertion over this cohort.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
"""


def write_entry(root, ground):
    scope = "metric: mean L2 error\ncohort: the synthetic graph\ncondition: mean aggregation"
    entries = root / "ledger" / "entries"
    entries.mkdir(parents=True, exist_ok=True)
    path = entries / "A0001-a-renamed-evidence-type.md"
    path.write_text(ENTRY.format(sha=fingerprint(scope, []), ground=ground), encoding="utf-8")
    return path


def ledger_named(root, **table):
    config = from_table(table, root)
    return open_ledger(config=config)


def test_a_project_may_name_its_evidence_type_whatever_it_likes(tmp_path):
    write_entry(tmp_path, "run: runs/2026-09-04.md @working")
    ledger = ledger_named(tmp_path, **{"evidence-sectioned": [], "evidence-plain": ["run"]})
    # The pointer is a legal ground, so validate has nothing to say about its type; the
    # path does not exist, which is resolve's business, not validate's.
    assert [r.message for r in validate_run(ledger) if "Grounds" in r.part] == []


def test_an_evidence_type_the_project_did_not_declare_is_not_a_ground(tmp_path):
    write_entry(tmp_path, "lab: notes/001.md @working")
    ledger = ledger_named(tmp_path, **{"evidence-sectioned": [], "evidence-plain": ["run"]})
    messages = [r.message for r in validate_run(ledger)]
    assert any("not a typed pointer" in m for m in messages)


def test_a_sectioned_type_must_be_written_with_its_section(tmp_path):
    write_entry(tmp_path, "lab: notes/001.md @working")
    ledger = ledger_named(tmp_path, **{"evidence-sectioned": ["lab"], "evidence-plain": []})
    messages = [r.message for r in validate_run(ledger)]
    assert any('§ "<section>"' in m for m in messages)


def test_a_kind_outside_the_enum_is_not_well_formed(tmp_path):
    """`corpus/README.md`'s Coverage section says validate's well-formedness guards --
    "the kind, author and grade enums" among them — are held by the unit suite rather
    than by a corpus seed, because a mutation sweep showed the corpus does not need them
    to pass. The sixth pass's sweep found the `kind` enum itself held by neither: `grep
    -rn KINDS tests/` returned nothing before this test existed."""
    path = write_entry(tmp_path, 'lab: notes/001.md § "Observation" @working')
    path.write_text(
        path.read_text(encoding="utf-8").replace("kind: claim", "kind: theory", 1),
        encoding="utf-8",
    )
    ledger = ledger_named(tmp_path)
    messages = [r.message for r in validate_run(ledger)]
    assert any("kind `theory` is not one of" in m for m in messages), messages


def test_a_grade_outside_the_enum_is_not_well_formed(tmp_path):
    """The same sentence names the `grade` enum beside `kind`; held by neither gate
    before this test, same as `kind` above."""
    path = write_entry(tmp_path, 'lab: notes/001.md § "Observation" @working')
    path.write_text(
        path.read_text(encoding="utf-8").replace("grade: measured", "grade: definitive", 1),
        encoding="utf-8",
    )
    ledger = ledger_named(tmp_path)
    messages = [r.message for r in validate_run(ledger)]
    assert any("grade `definitive` is not one of" in m for m in messages), messages


def test_a_frontmatter_author_that_is_not_a_lowercase_name_is_not_well_formed(tmp_path):
    """The same sentence's third named example, `author`: frontmatter `author:` is
    checked against a lowercase-name pattern (validate.py) — a different check from a
    verdict's `author:` being one of `verdict-authors`, which this test does not touch.
    This frontmatter half was held by neither gate before this test."""
    path = write_entry(tmp_path, 'lab: notes/001.md § "Observation" @working')
    path.write_text(
        path.read_text(encoding="utf-8").replace("author: main", "author: Main", 1),
        encoding="utf-8",
    )
    ledger = ledger_named(tmp_path)
    messages = [r.message for r in validate_run(ledger)]
    assert any("author `Main` is not a lowercase author name" in m for m in messages), messages


def test_a_verbatim_sha_that_is_not_64_hex_is_not_well_formed(tmp_path):
    """The same sentence's fourth named example: a `verbatim_sha` that is not 64 hex
    characters is a different defect from one that is 64 hex but wrong (D30 seeds that
    one). The format check itself — `SHA_RE` — was held by neither gate before this
    test: it is not a mismatch the corpus can express without also making the entry
    fail the length/character check first, which is exactly why a seed cannot stand in
    for this test."""
    path = write_entry(tmp_path, 'lab: notes/001.md § "Observation" @working')
    text = path.read_text(encoding="utf-8")
    sha_line = next(ln for ln in text.splitlines() if ln.startswith("verbatim_sha: "))
    path.write_text(
        text.replace(sha_line, "verbatim_sha: not-64-hex-characters", 1), encoding="utf-8"
    )
    ledger = ledger_named(tmp_path)
    messages = [r.message for r in validate_run(ledger)]
    assert any("verbatim_sha is not a 64-hex sha256" in m for m in messages), messages


def test_the_ledger_reads_its_paths_from_the_configuration(tmp_path):
    config = from_table({"ledger": "record", "entries": "claims"}, tmp_path)
    ledger = open_ledger(config=config)
    assert ledger.entries_dir == tmp_path / "record" / "claims"
    assert dataclasses.replace(config, root=tmp_path / "elsewhere").entries_dir == (
        tmp_path / "record" / "claims"
    )


def documents_of(tmp_path, excludes, *relatives):
    """The documents a ledger scans, given `document-excludes` and a tree."""
    for rel in relatives:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# fixture\n", encoding="utf-8")
    config = from_table(
        {"documents": ["*.md", "docs/*.md", "docs/**/*.md"], "document-excludes": list(excludes)},
        tmp_path,
    )
    return sorted(rel for rel, _ in open_ledger(config=config).docs)


TREE = ("README.md", "docs/spec.md", "docs/draft-scratch.md", "docs/notes/draft-later.md")


def test_a_document_exclude_is_a_glob_and_not_a_substring(tmp_path):
    """The count of scanned documents has to fall when an exclusion is configured, which
    is the assertion this key never had. It was substring containment, so
    `docs/draft-*.md` — the form both shipped example configurations write, one line under
    `documents`, which is globbed — matched no path at all and excluded nothing. A test
    asserting only `0 failure(s)` passes over an inert exclusion, which is how it shipped.
    (docs/audits/0.1.0.md, QE9-95.)
    """
    assert documents_of(tmp_path, (), *TREE) == sorted(TREE)
    assert documents_of(tmp_path, ["docs/draft-*.md"], *TREE) == sorted(
        ["README.md", "docs/spec.md", "docs/notes/draft-later.md"]
    )
    # And the substring form, which is what this used to take, now excludes nothing.
    assert documents_of(tmp_path, ["docs/draft-"], *TREE) == sorted(TREE)
    # A pattern is normalized before it is split, so an exclusion written in the same
    # hand as the inclusion beside it is not silently inert — which is this defect's
    # exact shape, one level down.
    assert documents_of(tmp_path, ["./docs/draft-*.md"], *TREE) == sorted(
        ["README.md", "docs/spec.md", "docs/notes/draft-later.md"]
    )


def test_an_exclude_matches_segment_by_segment_the_way_documents_does(tmp_path):
    """`*` stops at a separator and `**` spans any number of segments, because the two
    keys sit one line apart in every template this package ships."""
    assert documents_of(tmp_path, ["*.md"], *TREE) == sorted(
        ["docs/spec.md", "docs/draft-scratch.md", "docs/notes/draft-later.md"]
    )
    assert documents_of(tmp_path, ["**/*.md"], *TREE) == []
    assert documents_of(tmp_path, ["docs/**/draft-*.md"], *TREE) == sorted(
        ["README.md", "docs/spec.md"]
    )


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores the permission bits under test")
def test_an_unlistable_directory_is_reported_unless_the_exclusions_take_all_of_it(tmp_path):
    """A directory a `documents` pattern reaches and cannot list is reported, because the
    documents under it were not checked. Now that exclusions work, one can cover such a
    directory — and then there is nothing unchecked to report.

    The suppression is deliberately narrow: only a pattern ending in `*` or `**`, which
    takes everything below the point it matches. A pattern that takes some of what is
    under an unlistable directory leaves the rest both unchecked and unreported, which is
    the one report this package may not lose. (docs/audits/0.1.0.md, QE10-6.)
    """
    (tmp_path / "docs" / "private").mkdir(parents=True)
    (tmp_path / "docs" / "private" / "secret.md").write_text("# secret\n", encoding="utf-8")
    (tmp_path / "docs" / "spec.md").write_text("# spec\n", encoding="utf-8")
    private = tmp_path / "docs" / "private"

    def unlistable(excludes):
        config = from_table(
            {"documents": ["docs/**/*.md"], "document-excludes": list(excludes)}, tmp_path
        )
        os.chmod(private, 0o000)
        try:
            return [rel for rel, _ in open_ledger(config=config).unreadable_docs]
        finally:
            os.chmod(private, 0o755)

    assert unlistable([]) == ["docs/private"]
    assert unlistable(["docs/private/**"]) == []
    assert unlistable(["docs/private/*"]) == []
    assert unlistable(["docs/**"]) == []
    assert unlistable(["docs/private/*.md"]) == ["docs/private"]
    assert unlistable(["docs/other/**"]) == ["docs/private"]


@pytest.mark.parametrize(
    ("value", "offset_hours"),
    [
        ("2026-09-05T12:00:00Z", 0),
        ("2026-09-05T12:00:00+00:00", 0),
        ("2026-09-05T12:00:00-07:00", -7),
    ],
)
def test_timestamps_carry_their_offset_including_a_bare_z(value, offset_hours):
    """`Z` is parsed by fromisoformat itself from 3.11, which is the floor, so the
    checkers no longer rewrite it to `+00:00` first. Nothing covered `Z` when that
    rewrite was removed, so it is covered here."""
    parsed = parse_timestamp(value)
    assert parsed is not None
    assert parsed.utcoffset() == timedelta(hours=offset_hours)


@pytest.mark.parametrize("value", ["", "not a time", "2026-09-05", "2026-09-05T12:00:00"])
def test_a_timestamp_without_an_offset_is_not_a_timestamp(value):
    assert parse_timestamp(value) is None
