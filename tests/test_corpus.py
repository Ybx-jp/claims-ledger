"""The red-team corpus is well-formed against its own README, and the checkers pass it.

The shape checks here are checks on the test fixture, not on the checkers the corpus
exists to prove: every seed has expectations a runner can match, known-good seeds expect
only passes, registry hashes match the fixture bytes, and every entry's verbatim_sha
follows the canonicalization the README states. A corpus that drifts from its own
description would prove the wrong thing about the checkers built against it.

The last four tests are the proof bar itself: the checkers reproduce every seed's
expected outcome, and the runner fails when a seed is tampered with in either direction.
"""

import hashlib
import json
import re
import shutil
import unicodedata
from pathlib import Path

import pytest

from claims_ledger.corpus import run as corpus_run

CORPUS = Path(corpus_run.CORPUS)
SEEDS = sorted(p for p in (CORPUS / "seeds").iterdir() if p.is_dir())
CHECKERS = {"validate", "resolve", "references", "propagate", "review"}
OUTCOMES = {"pass", "fail", "flag", "judge"}


def expected(seed):
    return json.loads((seed / "expected.json").read_text(encoding="utf-8"))


def entry_files(seed):
    return sorted(seed.rglob("entries/*.md"))


def test_corpus_has_seeds_of_both_kinds():
    names = [s.name for s in SEEDS]
    assert any(n.startswith("K") for n in names)
    assert any(n.startswith("D") for n in names)


@pytest.mark.parametrize("seed", SEEDS, ids=lambda s: s.name)
def test_expectations_are_matchable(seed):
    exp = expected(seed)
    assert set(exp) >= {"class", "known_good", "expect"}
    assert exp["expect"], "a seed with no expectation rows tests nothing"
    for row in exp["expect"]:
        assert row["checker"] in CHECKERS, row
        assert row["outcome"] in OUTCOMES, row
        assert row["where"] and row["why"], row
        # review is not a program: its rows always judge, and no checker row does.
        assert (row["checker"] == "review") == (row["outcome"] == "judge"), row
    checker_non_pass = [
        r for r in exp["expect"] if r["checker"] != "review" and r["outcome"] != "pass"
    ]
    review_rows = [r for r in exp["expect"] if r["checker"] == "review"]
    if exp["known_good"]:
        assert seed.name.startswith("K") and not checker_non_pass
    else:
        # A defect seed is caught or flagged by a checker, or it is review-only: the
        # machinery passes and the review row is the whole record of what is wrong.
        assert seed.name.startswith("D") and (checker_non_pass or review_rows)
    assert entry_files(seed) or (seed / "commits").is_dir()
    if (seed / "commits").is_dir():
        assert "history" in exp


def test_registry_hashes_match_fixture_bytes():
    rows = [json.loads(line) for line in (CORPUS / "sources.jsonl").read_text().splitlines()]
    assert rows
    for row in rows:
        data = (CORPUS / row["bytes"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == row["sha256"], row["id"]


def section(text, name):
    m = re.search(rf"^## {name}\n(.*?)(?=^## |^<!-- APPEND|\Z)", text, re.M | re.S)
    assert m, name
    return m.group(1)


def norm(text):
    """The README's normalization: NFC, emphasis markers removed, whitespace collapsed."""
    text = unicodedata.normalize("NFC", text).replace("*", "").replace("`", "")
    return " ".join(text.split())


def canonical_sha(text):
    scope = [norm(ln) for ln in section(text, "Scope").splitlines() if ln.strip()]
    backing = section(text, "Backing")
    blocks = re.findall(r"^- source: (.*)\n\s+speaker: (.*)\n\s+quote: (.*)$", backing, re.M)
    lines = sorted(f"{norm(s)} | {norm(sp)} | {norm(q)}" for s, sp, q in blocks)
    payload = "\n".join(scope) + "\n\n" + "\n".join(lines)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def creation_states(seed):
    """Entries as first written. A history seed's later commit states may be tampered
    on purpose (D23 edits a quote), so only the state a file was created in is held to
    the canonicalization; the one seed whose declared sha is wrong by design is D30."""
    return [p for p in entry_files(seed) if "commits" not in p.parts or p.parents[1].name == "01"]


ENTRIES = [p for s in SEEDS for p in creation_states(s) if not s.name.startswith("D30")]


@pytest.mark.parametrize("path", ENTRIES, ids=lambda p: f"{p.relative_to(CORPUS / 'seeds')}")
def test_verbatim_sha_follows_the_documented_canonicalization(path):
    text = path.read_text(encoding="utf-8")
    declared = re.search(r"^verbatim_sha: ([0-9a-f]{64})$", text, re.M)
    assert declared, "no verbatim_sha"
    assert declared.group(1) == canonical_sha(text)
    assert "<!-- APPEND BELOW THIS LINE ONLY -->" in text


def test_the_mismatch_seed_really_mismatches():
    (path,) = entry_files(CORPUS / "seeds" / "D30-verbatim-sha-mismatch")
    text = path.read_text(encoding="utf-8")
    assert re.search(r"^verbatim_sha: (0{64})$", text, re.M)
    assert canonical_sha(text) != "0" * 64


def run_corpus(capsys, corpus_dir, *args):
    """The runner as the pre-push set invokes it, in process. The corpus directory is an
    argument so the runner can be pointed at a tampered copy."""
    code = corpus_run.main([*args, "--corpus", str(corpus_dir)])
    return code, capsys.readouterr().out


def _copy_corpus(tmp_path):
    dst = tmp_path / "corpus"
    shutil.copytree(CORPUS, dst, ignore=shutil.ignore_patterns("__pycache__"))
    return dst


def test_the_checkers_pass_the_corpus(capsys):
    """The proof bar. Every seed's expected outcomes are reproduced by the checkers and
    no checker trips where a seed does not say it should."""
    code, out = run_corpus(capsys, CORPUS)
    assert code == 0, out
    assert f"{len(SEEDS)}/{len(SEEDS)} seeds pass" in out


def test_the_runner_fails_a_seed_whose_defect_is_not_expected(capsys, tmp_path):
    """The known-negative half of the contract: an unlisted trip is a runner failure."""
    corpus = _copy_corpus(tmp_path)
    path = corpus / "seeds" / "D01-unmarked-deletion" / "expected.json"
    exp = json.loads(path.read_text(encoding="utf-8"))
    exp["expect"] = [r for r in exp["expect"] if r["checker"] != "resolve"]
    path.write_text(json.dumps(exp), encoding="utf-8")
    code, out = run_corpus(capsys, corpus, "D01")
    assert code == 1
    assert "unexpected resolve fail" in out


def test_the_runner_fails_a_known_good_seed_that_is_broken(capsys, tmp_path):
    """The known-positive half: a tampered quote in a known-good seed is caught."""
    corpus = _copy_corpus(tmp_path)
    (entry,) = list((corpus / "seeds" / "K01-measured-claim" / "entries").glob("*.md"))
    text = entry.read_text(encoding="utf-8")
    entry.write_text(
        text.replace("does not grow with degree.", "does not grow.", 1), encoding="utf-8"
    )
    code, out = run_corpus(capsys, corpus, "K01")
    assert code == 1
    assert "unexpected resolve fail" in out
    assert "unexpected validate fail" in out  # the fingerprint moved too


def test_an_expected_row_that_nothing_produces_fails_the_seed(capsys, tmp_path):
    corpus = _copy_corpus(tmp_path)
    path = corpus / "seeds" / "K01-measured-claim" / "expected.json"
    exp = json.loads(path.read_text(encoding="utf-8"))
    exp["expect"].append(
        {
            "checker": "resolve",
            "outcome": "fail",
            "where": "A0001 Backing quote 1",
            "why": "planted",
        }
    )
    path.write_text(json.dumps(exp), encoding="utf-8")
    code, out = run_corpus(capsys, corpus, "K01")
    assert code == 1
    assert "expected resolve fail at A0001 Backing quote 1" in out
