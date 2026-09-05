"""The parts of the schema a project can rename, and the parts it cannot.

The evidence pointer's name is the project's (`lab:`, `run:`, `journal:`); the grammar,
the fingerprint, the status derivation and the citation acts are not.
"""

import dataclasses

import pytest

from claims_ledger.config import from_table
from claims_ledger.schema import (
    Verdict,
    derive_status,
    fingerprint,
    open_ledger,
    parse_pointer,
    parse_quote,
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


def test_the_ledger_reads_its_paths_from_the_configuration(tmp_path):
    config = from_table({"ledger": "record", "entries": "claims"}, tmp_path)
    ledger = open_ledger(config=config)
    assert ledger.entries_dir == tmp_path / "record" / "claims"
    assert dataclasses.replace(config, root=tmp_path / "elsewhere").entries_dir == (
        tmp_path / "record" / "claims"
    )
