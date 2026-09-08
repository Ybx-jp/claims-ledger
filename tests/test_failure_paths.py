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
    repository they silently do nothing, so the command has to say so.

    Exit 0 is correct *here* and only here: there is no repository anywhere under or over
    this ledger, so no entry has a creating commit and nothing was skipped. The case
    below is the one where that reasoning is false.
    """
    assert project.cl("validate") == 0
    err = capsys.readouterr().err
    assert "no git repository of its own" in err
    assert "frozen-region and append-only checks did not run" in err


def nested_in_a_repository(project):
    """`project`, committed in a repository one directory above it — the ordinary shape
    of `--root <subdir>`, or of a ledger vendored inside a larger project."""
    outer = project.root.parent
    # The entry is written before the repository exists, because `sha --write` is one of
    # the commands this case changes and it would refuse afterwards — which is the point.
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    subprocess.run(["git", "-C", str(outer), "init", "-q"], check=True)
    for args in (
        ["add", "-A"],
        ["-c", "user.name=t", "-c", "user.email=t@e", "commit", "-qm", "in"],
    ):
        subprocess.run(["git", "-C", str(outer), *args], check=True, capture_output=True)
    assert not (project.root / ".git").exists(), "the ledger has no repository of its own"
    return path


def test_a_ledger_inside_someone_elses_repository_says_its_history_was_not_read(project, capsys):
    """`open_ledger` calls a project a repository when `<root>/.git` is there, so a ledger
    one directory inside one read as a ledger with no history at all — and "no history"
    is indexed to "nothing to check" everywhere it matters. `validate` answered
    `0 failure(s)` over a frozen region a commit was holding. (ARCH-AUDIT.md, finding 3.)
    """
    nested_in_a_repository(project)
    assert project.cl("validate") == 1
    out = capsys.readouterr().out
    assert "which this ledger is not reading" in out
    assert "unknown, not settled" in out


def test_sha_write_refuses_an_entry_someone_elses_repository_has_committed(project, capsys):
    """The same premise, one command over, and the reason it matters: `is_committed`
    read "no repository" as "nothing is committed", so `sha --write` rewrote the frozen
    region of an entry that repository had already committed and exited 0. That is the
    whole of what L0007 says must not happen.

    Answered rather than refused: an entry path is a path in the tree, so the enclosing
    repository can say whether it holds this file, and `sha --write` reports the thing
    that is true — the entry is committed — instead of reporting that it could not find
    out. Refusing over the whole layout would have left it unusable for a reason that
    does not apply to it.
    """
    path = nested_in_a_repository(project)
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("condition: ", "condition: silently substituted, "), "utf-8")
    capsys.readouterr()
    assert project.cl("sha", "--write", str(path)) == 2
    err = capsys.readouterr().err
    assert "is committed" in err
    assert "immutable" in err
    assert "silently substituted" in path.read_text(encoding="utf-8")


def test_a_ledger_merely_sitting_under_a_work_tree_is_not_a_history_nobody_read(project, capsys):
    """The negative case, and the one whose absence let the first version of this ship:
    the question is not "is there a work tree above me" but "is there a *history* nobody
    read". A ledger materialized under a repository that has never committed it — a
    scratch directory under a `TMPDIR` inside a checkout, a gitignored vendor tree, the
    corpus staging its seeds — has no history, and reporting one took the corpus from
    79/79 to 18/79 and the suite to 146 failures. (ARCH-AUDIT.md finding 3, QE11-1.)
    """
    outer = project.root.parent
    subprocess.run(["git", "-C", str(outer), "init", "-q"], check=True)
    (outer / "seed.txt").write_text("something else entirely\n", encoding="utf-8")
    for args in (
        ["add", "seed.txt"],
        ["-c", "user.name=t", "-c", "user.email=t@e", "commit", "-qm", "unrelated"],
    ):
        subprocess.run(["git", "-C", str(outer), *args], check=True, capture_output=True)
    assert project.cl("new", "fraction-law") == 0
    project.write_full_entry(next(project.entries.glob("A0001-*.md")))
    capsys.readouterr()
    assert project.cl("validate") == 0
    assert "not reading" not in capsys.readouterr().out


def test_the_walk_asks_the_directory_it_names_and_not_what_git_dir_names(
    project, capsys, monkeypatch
):
    """`GIT_DIR` redirects every git call in the process, including the one that asks
    whether the enclosing repository has ever committed these entries — under a `GIT_DIR`
    naming some other repository it answers about *that* one, finds no history for the
    path, and the report disappears. The sibling above proves the report appears, and
    nothing proved it still appeared with the variable set. (QE12-3.)

    The scrub this held used to be an argument at that one call site. It is `git_env()`,
    the default under every git call in the package, since QE12-2; the family of tests for
    what the environment may not answer for is `tests/test_git_environment.py`, and this
    one stays here because its subject is the discovery walk.
    """
    nested_in_a_repository(project)
    elsewhere = project.root.parent.parent / "elsewhere"
    elsewhere.mkdir()
    subprocess.run(["git", "-C", str(elsewhere), "init", "-q"], check=True)
    (elsewhere / "x.txt").write_text("x\n", encoding="utf-8")
    for args in (
        ["add", "-A"],
        ["-c", "user.name=t", "-c", "user.email=t@e", "commit", "-qm", "x"],
    ):
        subprocess.run(["git", "-C", str(elsewhere), *args], check=True, capture_output=True)
    monkeypatch.setenv("GIT_DIR", str(elsewhere / ".git"))
    capsys.readouterr()
    assert project.cl("validate") == 1
    assert "which this ledger is not reading" in capsys.readouterr().out


def test_git_dir_in_the_environment_does_not_invent_a_repository(project, capsys, monkeypatch):
    """`git rev-parse --show-toplevel` with `GIT_DIR` set and no `GIT_WORK_TREE` answers
    with the directory it was run in, so a ledger with no repository anywhere reported
    *itself* as the repository holding it. The walk is the filesystem's now, and asks
    nothing of the environment. (ARCH-AUDIT.md finding 3, QE11-3.)

    This first said that every git hook exports `GIT_DIR` — the reason the case was
    thought to matter — and that is false: measured on git 2.43.0, a hook gets
    `GIT_INDEX_FILE`, and `GIT_DIR` reaches one when git itself was invoked with
    `--git-dir`. Corrected here rather than dropped, since the correction is what the
    comment in `schema.py` already carries.
    """
    elsewhere = project.root.parent / "elsewhere"
    elsewhere.mkdir()
    subprocess.run(["git", "-C", str(elsewhere), "init", "-q"], check=True)
    monkeypatch.setenv("GIT_DIR", str(elsewhere / ".git"))
    capsys.readouterr()
    assert project.cl("validate") == 0
    assert "not reading" not in capsys.readouterr().out


def test_an_enclosing_repository_git_cannot_open_is_not_a_ledger_with_no_history(project, capsys):
    """The false pass this whole branch exists to remove, put back by the first version of
    its own fix: a failed `rev-parse` was read as "there is no repository", so with an
    enclosing repository git refuses to open — `detected dubious ownership` is the
    everyday one — `sha --write` rewrote a committed entry's frozen region and exited 0
    again. A git that cannot answer is not a git answering no. (QE11-2.)
    """
    path = nested_in_a_repository(project)
    subprocess.run(
        ["git", "-C", str(project.root.parent), "config", "core.repositoryformatversion", "99"],
        check=True,
    )
    capsys.readouterr()
    assert project.cl("validate") == 1
    assert "git cannot read the repository at" in capsys.readouterr().out
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("condition: ", "condition: substituted, "), "utf-8")
    capsys.readouterr()
    assert project.cl("sha", "--write", str(path)) == 2
    assert "could not be established" in capsys.readouterr().err


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
