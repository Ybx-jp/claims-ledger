"""The authoring side, end to end: scaffold a ledger, register a source, write an entry
that quotes it, and have all four checkers pass. Then the ways the authoring commands
refuse to do the wrong thing.
"""

import json
import subprocess
import sys

import pytest

from claims_ledger import cli
from claims_ledger.authoring import AuthoringError, next_id, register_source, restamp
from claims_ledger.schema import load_entries, open_ledger, parse_entry


def test_a_scaffolded_ledger_passes_every_checker_once_the_entry_is_filled_in(project, capsys):
    assert project.cl("new", "stale-fraction-governs-error") == 0
    path = project.entry("A0001-stale-fraction-governs-error.md")
    assert path.is_file()

    # A scaffold is a draft, and the checkers say so: placeholders are not pointers.
    assert project.cl("check") == 1

    project.write_full_entry(path)
    capsys.readouterr()
    assert project.cl("check") == 0
    out = capsys.readouterr().out
    assert "0 failure(s)" in out
    assert "FAIL" not in out


def test_status_derives_from_the_verdicts(project, capsys):
    project.cl("new", "stale-fraction-governs-error")
    path = project.write_full_entry(project.entry("A0001-stale-fraction-governs-error.md"))
    capsys.readouterr()
    assert project.cl("status") == 0
    assert "open" in capsys.readouterr().out

    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "## Verdicts\n",
        "## Verdicts\n\n"
        "- 2026-09-04T12:00:00+00:00 · corroborated · grade: measured · author: main\n"
        '  evidence: lab: docs/note-001.md § "Observation" @working\n'
        "  note: a second reading of the same note\n",
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("status") == 0
    assert "corroborated" in capsys.readouterr().out


def test_the_scaffold_allocates_the_next_id(project):
    assert project.cl("new", "first-claim") == 0
    assert project.cl("new", "second-claim") == 0
    names = sorted(p.name for p in project.entries.glob("*.md"))
    assert names == ["A0001-first-claim.md", "A0002-second-claim.md"]


def test_next_id_rolls_over_and_skips_a_quarantined_series(project):
    ledger = open_ledger(root=project.root)
    assert next_id([], ledger.config.archived_prefixes) == "A0001"

    project.cl("new", "nine-nine-nine-nine", "--id", "A9999")
    entries = load_entries(ledger)
    assert next_id(entries, ("B",)) == "C0001"


def test_a_prediction_carries_a_credence_and_a_resolution_condition(project):
    assert (
        project.cl(
            "new",
            "refresh-beats-no-refresh",
            "--kind",
            "prediction",
            "--credence",
            "0.7",
            "--resolves-when",
            "the preregistered run reports its held-out score",
        )
        == 0
    )
    entry = parse_entry(project.entry("A0001-refresh-beats-no-refresh.md"))
    assert entry.front["credence"] == "0.7"
    assert entry.front["resolves_when"].startswith("the preregistered run")


def test_a_slug_that_is_not_a_slug_is_refused(project, capsys):
    assert cli.main(["--root", str(project.root), "new", "Not A Slug"]) == 2
    assert "is not a lowercase-and-hyphens slug" in capsys.readouterr().err
    assert not list(project.entries.glob("*.md"))


def test_the_fingerprint_is_reported_and_rewritten(project, capsys):
    project.cl("new", "stale-fraction-governs-error")
    path = project.entry("A0001-stale-fraction-governs-error.md")
    before = parse_entry(path).front["verbatim_sha"]

    text = path.read_text(encoding="utf-8").replace("metric: TODO", "metric: mean L2 error")
    path.write_text(text, encoding="utf-8")

    capsys.readouterr()
    assert project.cl("sha", str(path)) == 1  # declared and computed disagree
    assert "not written" in capsys.readouterr().out

    assert project.cl("sha", "--write", str(path)) == 0
    after = parse_entry(path).front["verbatim_sha"]
    assert after != before
    assert after == parse_entry(path).computed_sha()


def test_the_fingerprint_is_not_rewritten_on_a_committed_entry(project):
    project.cl("new", "stale-fraction-governs-error")
    path = project.entry("A0001-stale-fraction-governs-error.md")
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the entry as first written")

    text = path.read_text(encoding="utf-8").replace("metric: TODO", "metric: mean L2 error")
    path.write_text(text, encoding="utf-8")
    ledger = open_ledger(root=project.root)
    with pytest.raises(AuthoringError, match="immutable"):
        restamp(ledger, path, write=True)
    # The frozen region is immutable, so the fix is a successor — or --force, before the
    # commit has left the machine.
    _, _, changed = restamp(ledger, path, write=True, force=True)
    assert changed


def test_registering_a_source_stores_the_bytes_the_quote_is_checked_against(project):
    ledger = open_ledger(root=project.root)
    rows = [json.loads(ln) for ln in ledger.registry.read_text(encoding="utf-8").splitlines()]
    (row,) = rows
    assert row["id"] == "fx-source"
    assert (ledger.cache / row["sha256"]).is_file()
    assert row["authors"] == ["Okafor"]
    assert "bytes" not in row  # a real source's bytes live in the cache, uncommitted


def test_a_duplicate_source_id_is_refused(project, tmp_path):
    ledger = open_ledger(root=project.root)
    other = tmp_path / "other.txt"
    other.write_text("different bytes entirely.\n", encoding="utf-8")
    with pytest.raises(AuthoringError, match="already registered"):
        register_source(ledger, "fx-source", other, "paper", "A second registration")


def test_source_list_reports_bytes_that_are_missing(project, capsys):
    ledger = open_ledger(root=project.root)
    row = json.loads(ledger.registry.read_text(encoding="utf-8").splitlines()[0])
    assert project.cl("source", "list") == 0
    assert "bytes present" in capsys.readouterr().out

    (ledger.cache / row["sha256"]).unlink()
    assert project.cl("source", "list") == 1
    assert "the check cannot run" in capsys.readouterr().out


def test_init_refuses_to_overwrite_a_configuration(project):
    assert project.cl("init") == 1
    assert project.cl("init", "--force") == 0


def test_the_hook_is_printed_and_installed(project, capsys):
    assert project.cl("hook") == 0
    assert "-m claims_ledger validate --cached" in capsys.readouterr().out
    project.git("init", "-q")
    assert project.cl("hook", "--install") == 0
    hook = project.root / ".git" / "hooks" / "pre-commit"
    assert hook.is_file() and hook.stat().st_mode & 0o111
    assert project.cl("hook", "--install") == 1  # an existing hook is left alone


def test_the_hook_does_not_depend_on_the_console_script_being_on_path(project):
    """git runs hooks with its own environment. A hook that said `claims-ledger …` broke
    on every commit for anyone who pip-installed into a virtualenv that was not active,
    so the hook names an interpreter absolutely and reaches the package with -m."""
    project.git("init", "-q")
    assert project.cl("hook", "--install") == 0
    text = (project.root / ".git" / "hooks" / "pre-commit").read_text()
    assert sys.executable in text
    for line in text.splitlines():
        assert not line.startswith("claims-ledger ")
    # The hook is runnable with nothing on PATH but the interpreter it names.
    proc = subprocess.run(
        ["sh", str(project.root / ".git" / "hooks" / "pre-commit")],
        cwd=project.root,
        env={"PATH": "/usr/bin:/bin", "HOME": str(project.root)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert "not found" not in proc.stderr, proc.stderr
