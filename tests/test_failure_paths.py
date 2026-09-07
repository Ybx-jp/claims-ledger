"""What the tool does when the ledger, or the place it is pointed, is wrong.

The rule these tests hold is the one the whole package rests on: a check that did not
run must never be reported as a check that passed. `0 failure(s)` over a directory with
no ledger in it, or over a checkout where the history checks could not run, is worse
than a crash, because it is indistinguishable from a clean bill of health.

The second rule is that a stranger never gets a traceback. Every file a user maintains
by hand — an entry, the source registry — can be malformed, and malformed input is a
thing to report, not to raise.
"""

import subprocess
import sys

import pytest

from claims_ledger import cli, references
from claims_ledger.schema import LedgerError, load_registry, open_ledger

CHECKING_COMMANDS = ["validate", "resolve", "references", "propagate", "check"]


# --- a check that cannot run does not report success ---------------------------------


@pytest.mark.parametrize("command", CHECKING_COMMANDS)
def test_a_missing_entries_directory_stops_the_command(tmp_path, capsys, command):
    """The wrong --root used to print four `0 failure(s)` lines and exit 0."""
    assert cli.main(["--root", str(tmp_path / "nowhere"), command]) == 2
    err = capsys.readouterr().err
    assert "no entries directory" in err
    assert "nothing was checked" in err


@pytest.mark.parametrize("command", CHECKING_COMMANDS)
def test_an_empty_ledger_warns_but_is_not_an_error(project, capsys, command):
    """An entries directory that exists and is empty is a real ledger with nothing in it
    yet — a fine thing to be, and distinct from being pointed somewhere wrong."""
    assert project.cl(command) == 0
    assert "no entries under" in capsys.readouterr().err


def test_outside_git_the_skipped_history_checks_are_named(project, capsys):
    """validate's frozen-region and append-only checks read git history. Without a
    repository they silently do nothing, so the command has to say so."""
    assert project.cl("validate") == 0
    err = capsys.readouterr().err
    assert "not a git repository" in err
    assert "frozen-region and append-only checks did not run" in err


def test_inside_git_nothing_is_said_about_skipped_history_checks(project, capsys):
    project.git("init", "-q")
    ledger = project.root / "ledger"
    assert ledger.is_dir()
    project.cl("validate")
    assert "did not run" not in capsys.readouterr().err


def test_cached_outside_git_says_it_had_no_effect(project, capsys):
    """`--cached` reads the git index. There isn't one, and silently reading the working
    tree instead is how a hook checks something other than what is being committed."""
    assert project.cl("validate", "--cached") == 0
    assert "--cached had no effect" in capsys.readouterr().err


# --- malformed input a user maintains by hand is reported, not raised ----------------


def test_a_registry_line_that_is_not_json_is_reported(project, capsys):
    registry = project.root / "ledger" / "sources.jsonl"
    registry.write_text("not json at all\n", encoding="utf-8")
    assert project.cl("source", "list") == 2
    err = capsys.readouterr().err
    assert "sources.jsonl:1" in err
    assert "not a JSON object" in err
    assert "Traceback" not in err


def test_a_registry_row_without_an_id_is_reported(project, capsys):
    registry = project.root / "ledger" / "sources.jsonl"
    registry.write_text('{"type": "paper"}\n', encoding="utf-8")
    assert project.cl("check") == 2
    assert "registry row has no `id`" in capsys.readouterr().err


def test_load_registry_names_the_offending_line(tmp_path):
    path = tmp_path / "sources.jsonl"
    path.write_text('{"id": "a"}\n\n{"id": "b"}\nbroken\n', encoding="utf-8")
    with pytest.raises(LedgerError) as exc:
        load_registry(path)
    assert "sources.jsonl:4" in str(exc.value)


def test_an_entry_that_is_not_utf8_is_reported(project, capsys):
    """One stray byte in one entry file used to raise UnicodeDecodeError out of every
    command that loads entries, `status` included."""
    (project.entries / "A0001-bad.md").write_bytes(b"---\nid: A0001-bad\n\xff\xfe raw bytes\n")
    assert project.cl("status") == 2
    err = capsys.readouterr().err
    assert "A0001-bad.md" in err
    assert "not UTF-8 text" in err
    assert "Traceback" not in err


def test_an_unreadable_source_registry_is_reported(project, capsys):
    registry = project.root / "ledger" / "sources.jsonl"
    registry.write_bytes(b"\xff\xfe not text\n")
    assert project.cl("source", "list") == 2
    assert "not UTF-8 text" in capsys.readouterr().err


def test_an_evidence_file_that_is_not_utf8_does_not_resolve(project):
    """An unreadable pointer target is a pointer that does not resolve — a report about
    the ledger, not a crash in the middle of the checker."""
    entry = project.entries / "A0001-quotes-a-source.md"
    assert project.cl("new", "quotes-a-source", "--id", "A0001") == 0
    project.write_full_entry(entry)
    (project.root / "docs" / "note-001.md").write_bytes(b"\xff\xfe not text\n")
    assert project.cl("resolve") == 1


# --- the CLI's own edges --------------------------------------------------------------


def test_version_flag(capsys):
    from claims_ledger import __version__

    with pytest.raises(SystemExit) as exc:
        cli.main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def _explode(monkeypatch, exc):
    """Replace `status` in the dispatch table, undone when the test ends."""

    def boom(_args, _ledger):
        raise exc

    monkeypatch.setitem(cli.COMMANDS, "status", boom)


def test_keyboard_interrupt_is_not_a_traceback(project, monkeypatch, capsys):
    _explode(monkeypatch, KeyboardInterrupt())
    assert project.cl("status") == 130
    assert "interrupted" in capsys.readouterr().err


def test_an_unexpected_error_is_a_diagnostic_not_a_traceback(project, monkeypatch, capsys):
    monkeypatch.delenv("CLAIMS_LEDGER_TRACEBACK", raising=False)
    _explode(monkeypatch, RuntimeError("something gave way"))
    assert project.cl("status") == 2
    err = capsys.readouterr().err
    assert "unexpected RuntimeError: something gave way" in err
    assert "this is a bug" in err


def test_the_traceback_escape_hatch_still_works(project, monkeypatch):
    monkeypatch.setenv("CLAIMS_LEDGER_TRACEBACK", "1")
    _explode(monkeypatch, RuntimeError("boom"))
    with pytest.raises(RuntimeError):
        project.cl("status")


def test_the_package_is_runnable_with_dash_m(project):
    """The installed pre-commit hook invokes the package this way, so it has to work."""
    proc = subprocess.run(
        [sys.executable, "-m", "claims_ledger", "--root", str(project.root), "status"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr


def test_a_document_unreadable_only_after_the_ledger_listed_it_is_not_silent(project):
    """references.py's comment: "A document that could not be opened at all, and one
    that fails at the read: either way its citations were not checked." The first half
    is `ledger.unreadable_docs`, seeded by D50; this is the second half, which fires only
    when a document that passed the ledger's own listing stops being readable before the
    checker gets to it -- the race `tree_documents()`'s one-time filter cannot itself
    prevent."""
    doc = project.root / "docs" / "cites-nothing-special.md"
    doc.write_text("An ordinary document, citing nothing in particular.\n", encoding="utf-8")
    ledger = open_ledger(root=project.root)
    assert any(name == "docs/cites-nothing-special.md" for name, _ in ledger.docs), (
        "the document must be listed as readable for the re-check below to mean anything"
    )
    doc.unlink()  # the race: gone between the listing above and references.run() below
    reports = references.run(ledger)
    assert any(
        r.part == "docs/cites-nothing-special.md" and "its citations were not checked" in r.message
        for r in reports
    ), reports
