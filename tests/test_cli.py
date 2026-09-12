"""The authoring side, end to end: scaffold a ledger, register a source, write an entry
that quotes it, and have all five checkers pass. Then the ways the authoring commands
refuse to do the wrong thing.
"""

import json
import os
import shutil
import subprocess
import sys
import tomllib

import pytest

from claims_ledger import cli
from claims_ledger.authoring import AuthoringError, next_id, register_source, restamp
from claims_ledger.cli import hook_text
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
    _, _, changed, _ = restamp(ledger, path, write=True, force=True)
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


def test_the_configuration_init_writes_is_parseable_toml(tmp_path):
    """The template is filled with `str.format` and then read by a TOML parser, and an
    escape that survives one and not the other is unparseable in a way no other test
    would notice: a backslash-b in a commented-out example became a real backspace, and
    tomllib refuses that character even inside a comment."""
    root = tmp_path / "project"
    root.mkdir()
    assert cli.main(["--root", str(root), "init"]) == 0
    written = (root / "claims-ledger.toml").read_bytes()
    tomllib.loads(written.decode("utf-8"))
    assert not [c for c in written.decode("utf-8") if c < " " and c not in "\n\t"]


def test_the_installed_hook_asks_freshness_about_the_index():
    """Fixed. The defect, as this pass wrote it: MEDIUM-33 gave `freshness` a --cached flag and
    gave `check` the wiring, but HOOK_TEMPLATE still runs bare `freshness`, so the installed
    pre-commit hook — the surface MEDIUM-33's own writeup named as the one that matters —
    reads the working tree while validate reads the index

    A pre-commit hook checks what is being committed. `validate --cached` reads the index; the
    freshness line beside it reads the working tree, so a drift that is staged and then undone
    in the working tree commits through the hook silently.
    """
    text = hook_text(python="/usr/bin/python3")
    # The lines the hook actually runs, and not the comment above them. Selected by
    # `endswith("freshness")`, as this was first written, the test read a comment line
    # instead — the comment says `--cached` because it explains the fix, so the assertion
    # was satisfied by prose while the invocation below it went unexamined. That is
    # HIGH-55's shape exactly: a test green over a mechanism that never fired.
    invocations = [
        ln.strip()
        for ln in text.splitlines()
        if "-m claims_ledger" in ln and not ln.lstrip().startswith("#")
    ]
    assert len(invocations) == 5, invocations
    (line,) = [ln for ln in invocations if " freshness" in ln]
    assert "--cached" in line, f"the hook runs {line!r}"


def test_the_hook_asks_for_the_index_wherever_the_checker_accepts_it(capsys):
    """L0212. The hook's `--cached` lines are exactly the checkers whose own parser takes
    the flag — asked of the parser rather than a list written down here, so a checker that
    gains a cached mode and is not given it in the template fails here instead of quietly
    reading the working tree at the commit boundary.

    The gate's mutant N8 dropped the cached wiring from `cmd_check` and survived the whole
    suite: `check` was the only caller that had it, and the installed hook never runs
    `check`. Nothing asserted what the hook's own lines ask for. (qe ticket 2b90973d753f445c,
    QE19-1.)
    """
    parser = cli.build_parser()
    accepts = set()
    for name in cli.CHECKERS:
        try:
            parser.parse_args([name, "--cached"])
        except SystemExit:
            continue
        accepts.add(name)
    capsys.readouterr()
    assert accepts, "precondition: some checker takes --cached"

    ran = {}
    for line in hook_text(python="/usr/bin/python3").splitlines():
        if "-m claims_ledger" not in line or line.lstrip().startswith("#"):
            continue
        words = line.split()
        ran[words[words.index("claims_ledger") + 1]] = set(
            words[words.index("claims_ledger") + 2 :]
        )
    assert set(ran) == set(cli.CHECKERS), ran
    assert {n for n, flags in ran.items() if "--cached" in flags} == accepts, ran


def test_check_cached_holds_the_staged_entry_and_not_the_one_being_edited(project, capsys):
    """`resolve` under `--cached` reads the entries from the index, as `validate` and
    `freshness` do. Handed the working list instead it held the tree's anchor against the
    index's artifact — a pair no commit contains — so an entry staged with an anchor
    nothing digests to and corrected in the working tree alone passed the hook and landed
    unresolved. (qe ticket 2b90973d753f445c, QE19-2.)
    """
    project.git("init", "-q")
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    bogus = "sha256:" + "ab" * 32
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            '- lab: docs/note-001.md § "Observation" @working',
            f'- lab: docs/note-001.md § "Observation" ={bogus}',
        ),
        encoding="utf-8",
    )
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")  # the bogus anchor is what the commit would carry
    good = project.digest("docs/note-001.md", "Observation")
    path.write_text(path.read_text(encoding="utf-8").replace(bogus, good), encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0  # corrected in the tree only
    capsys.readouterr()

    assert project.cl("check") == 0, capsys.readouterr().out
    capsys.readouterr()
    assert project.cl("check", "--cached") == 1, "the staged entry names text nothing holds"
    out = capsys.readouterr().out
    assert "resolve: 1 failure(s)" in out, out
    assert "the index does not hold" in out, out


def _entry_anchored_at_the_tree(project):
    """A scaffolded entry whose one evidence ground names the note's section by value, as
    the working tree has it."""
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    anchor = project.digest("docs/note-001.md", "Observation")
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            '- lab: docs/note-001.md § "Observation" @working',
            f'- lab: docs/note-001.md § "Observation" ={anchor}',
        ),
        encoding="utf-8",
    )
    assert project.cl("sha", "--write", str(path)) == 0
    return path


def test_resolve_cached_holds_the_anchor_to_the_staged_artifact(project, capsys):
    """`resolve --cached` reads the artifact out of the index, which is what the hook runs
    and what the commit will carry. Only `check --cached` drove this path before, and the
    hook does not run `check`, so dropping `cached` from `cmd_resolve`'s `resolve.run` call
    left the whole suite green. (qe ticket 7d0a64cf95214e40, QE20-2 / mutant M3.)
    """
    project.git("init", "-q")
    _entry_anchored_at_the_tree(project)
    note = project.root / "docs" / "note-001.md"
    kept = note.read_text(encoding="utf-8")
    note.write_text(kept.replace("0.04", "0.12"), encoding="utf-8")
    project.git("add", "-A")  # the index holds 0.12; the anchor names 0.04
    note.write_text(kept, encoding="utf-8")  # and the working tree holds 0.04 again
    capsys.readouterr()

    assert project.cl("resolve") == 0, capsys.readouterr().out
    capsys.readouterr()
    assert project.cl("resolve", "--cached") == 1, "the index does not hold the anchor's text"
    assert "the index does not hold" in capsys.readouterr().out


def test_resolve_cached_reads_the_staged_entry(project, capsys):
    """The entries come out of the index too, so the anchor held is the one being committed.
    Mutant M2 — `cmd_resolve` loading the working entries — survives every other test.
    (qe ticket 7d0a64cf95214e40, QE20-2.)
    """
    project.git("init", "-q")
    path = _entry_anchored_at_the_tree(project)
    good = project.digest("docs/note-001.md", "Observation")
    bogus = "sha256:" + "cd" * 32
    path.write_text(path.read_text(encoding="utf-8").replace(good, bogus), encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")  # the bogus anchor is what the commit would carry
    path.write_text(path.read_text(encoding="utf-8").replace(bogus, good), encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0  # corrected in the tree alone
    capsys.readouterr()

    assert project.cl("resolve") == 0, capsys.readouterr().out
    capsys.readouterr()
    assert project.cl("resolve", "--cached") == 1, "the staged entry names text nothing holds"
    assert "the index does not hold" in capsys.readouterr().out


def test_resolve_cached_says_so_when_the_index_cannot_be_read(project, capsys):
    """The guard is asked the cached question as well, so a run that fell back to the
    working tree says so rather than answering as though it had read the index
    (L0122-a-cached-run-that-fell-back-to-the-working-tree-says-so). Mutant M1 —
    `guard(ledger)` without the flag — is silent here and nowhere else.
    (qe ticket 7d0a64cf95214e40, QE20-2.)
    """
    project.git("init", "-q")
    _entry_anchored_at_the_tree(project)
    project.git("add", "-A")
    (project.root / ".git" / "index").write_bytes(b"not an index" * 20)
    capsys.readouterr()

    project.cl("resolve", "--cached")
    got = capsys.readouterr()
    said = got.err + got.out
    assert "fell back to the working tree" in said, said
    assert "what is staged was not checked" in said, said

    # The other half of the same rule, and the half no test held: a run that did not ask
    # for the index has not fallen back from it, however broken the index is. Without this
    # arm, `cmd_resolve` guarding with a hard `True` passes the whole suite.
    project.cl("resolve")
    bare = capsys.readouterr()
    assert "--cached" not in bare.err + bare.out, bare


def test_a_healthy_index_is_not_reported_as_a_fallback(project, capsys):
    """The negative control the fallback note never had. Asserting only that the note can
    appear leaves two mutants alive through all 1072 tests: one that makes `index_problem`
    always answer, so every healthy `--cached` run declares that what is staged was not
    checked; and one that hands `cmd_resolve`'s guard a hard `True`, so a bare `resolve`
    announces a fallback for a flag nobody passed. Both are measured to survive without
    this. (qe ticket a55240cd1f6f47e5, QE21-2.)
    """
    project.git("init", "-q")
    _entry_anchored_at_the_tree(project)
    project.git("add", "-A")
    capsys.readouterr()

    # A readable index, asked for: nothing fell back, so nothing says it did.
    assert project.cl("resolve", "--cached") == 0
    healthy = capsys.readouterr()
    assert "fell back" not in healthy.err + healthy.out, healthy
    assert "was not checked" not in healthy.err + healthy.out, healthy

    # And a bare run says nothing about a flag it was not given.
    assert project.cl("resolve") == 0
    bare = capsys.readouterr()
    assert "--cached" not in bare.err + bare.out, bare


def test_check_cached_gives_each_checker_the_tree_it_reads(project, capsys):
    """`check` parses the entries once for all five checkers, and under `--cached` it
    parses twice — `validate`, `resolve` and `freshness` read what is staged, the other two
    read the working tree. Getting that mapping backwards, or collapsing it to one list, is
    invisible to every other test in this suite: both mutants pass 857 tests and 79 seeds.
    Before the entries were hoisted out of the checkers the mapping could not be stated
    wrongly, because each checker asked for its own. (docs/audits/ARCH-AUDIT.md finding 4, QE13-1.)
    """
    project.git("init", "-q")
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")
    capsys.readouterr()

    # Staged: the entry as committed. Working tree: an id that no longer matches the
    # filename, which is `validate`'s finding and nothing else's.
    path.write_text(
        path.read_text(encoding="utf-8").replace("id: A0001-", "id: A0002-", 1), encoding="utf-8"
    )

    project.cl("check")
    assert "filename and id" in capsys.readouterr().out, "precondition: the working tree is bad"
    project.cl("check", "--cached")
    assert "filename and id" not in capsys.readouterr().out, (
        "--cached must give validate the staged entry, which is the one being committed"
    )


def test_the_cached_entry_list_is_the_index_and_not_the_working_tree(project, capsys):
    """Which entries there are is a question about a tree, and under `--cached` that tree
    is the index. `load_entries` globbed the working tree whatever the flag said, so an
    entry staged and then deleted from the tree was in the commit and in no checker's
    list: all five reported `0 failure(s)` at exit 0 over a ledger about to gain a broken
    entry, and with that the only entry, over `0 entries`.

    The staged entry is broken on purpose — its anchor names text nothing holds — so the
    observable is not merely that it was counted but that the failure it carries was
    reported. Both directions are asserted: a bare run sees the tree, which no longer has
    it, and says `0 entries`; the cached run sees the one the index holds.

    Deleting the index list from `load_entries` reddens this and nothing else in the
    suite. (The third 0.1.0 release condition; qe ticket a55240cd1f6f47e5.)
    """
    project.git("init", "-q")
    path = _entry_anchored_at_the_tree(project)
    good = project.digest("docs/note-001.md", "Observation")
    path.write_text(
        path.read_text(encoding="utf-8").replace(good, "sha256:" + "cd" * 32), encoding="utf-8"
    )
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")  # the broken entry is what the commit would carry
    path.unlink()  # and the working tree no longer has it at all
    capsys.readouterr()

    assert project.cl("resolve") == 0
    assert "0 entries" in capsys.readouterr().out

    assert project.cl("resolve", "--cached") == 1, "the staged entry names text nothing holds"
    out = capsys.readouterr().out
    assert "1 entry)" in out, out
    assert "A0001" in out and "does not hold" in out, out


def test_references_cached_reads_the_staged_documents(project, capsys):
    """`references --cached` reads a document out of the index, because the citation the
    commit will carry is the one written there. The checker read the working tree whatever
    it was asked, so a citation staged against one status and corrected in the tree alone
    passed the hook and committed broken — a verdict over prose no commit contains.

    Both directions, because the whole content of the test is that they differ.
    """
    project.git("init", "-q")
    assert project.cl("new", "first") == 0
    path = project.write_full_entry(project.entry("A0001-first.md"))
    text = path.read_text(encoding="utf-8").replace(
        "## References\n", "## References\n\n- docs/note-001.md · standing · cites-as-live\n"
    )
    path.write_text(text, encoding="utf-8")
    note = project.root / "docs" / "note-001.md"
    kept = note.read_text(encoding="utf-8")

    note.write_text(kept + "\nSee (A0404-no-such-entry, cites-as-live).\n", encoding="utf-8")
    project.git("add", "-A")  # the index holds a citation of an id nothing minted
    note.write_text(kept + "\nSee (A0001-first, cites-as-live).\n", encoding="utf-8")
    capsys.readouterr()

    assert project.cl("references") == 0, capsys.readouterr().out
    capsys.readouterr()
    assert project.cl("references", "--cached") == 1, "the staged note cites an id nothing minted"
    assert "A0404-no-such-entry" in capsys.readouterr().out


def test_propagate_cached_reads_the_staged_entries(project, capsys):
    """The same rule for the fifth checker. `propagate` walks entry-to-entry edges, so its
    subject is which entries there are and what they say — and under the flag that is the
    index. Mutant: `cmd_propagate` calling `load_entries(ledger)` without the flag.
    """
    project.git("init", "-q")
    assert project.cl("new", "first") == 0
    assert project.cl("new", "second") == 0
    first = project.write_full_entry(project.entry("A0001-first.md"))
    project.write_full_entry(project.entry("A0002-second.md"))
    kept = first.read_text(encoding="utf-8")
    first.write_text(
        kept.replace(
            '- lab: docs/note-001.md § "Observation" @working',
            '- lab: docs/note-001.md § "Observation" @working\n- entry: A0002-second · challenges',
        ),
        encoding="utf-8",
    )
    project.git("add", "-A")  # the index holds the challenge, which demands a verdict
    first.write_text(kept, encoding="utf-8")  # and the tree does not
    capsys.readouterr()

    assert project.cl("propagate") == 0, capsys.readouterr().out
    capsys.readouterr()
    assert project.cl("propagate", "--cached") == 1, "the staged challenge demands a verdict"
    assert "A0002-second" in capsys.readouterr().out


def test_resolve_cached_reads_the_registry_the_commit_will_carry(project, capsys):
    """The source registry is one file the whole ledger rests on, and `Sources` read it
    from the working tree whatever the run was asked. An emptied registry staged and
    restored in the tree took every checker to a clean run over a commit that lands with
    each `source:` ground unresolvable — the registry the commit carries had no rows at all.

    Found by the qe gate against this branch (ticket 11fd0ed94d86405f) while it was asked
    about something else, and reproduced here before it was fixed. Dropping `cached=cached`
    from the `Sources(...)` call reddens this and nothing else.
    """
    project.git("init", "-q")
    assert project.cl("new", "first") == 0
    project.write_full_entry(project.entry("A0001-first.md"))
    registry = project.root / "ledger" / "sources.jsonl"
    kept = registry.read_text(encoding="utf-8")
    assert "fx-source" in kept, "the fixture registers a source this entry points at"
    registry.write_text("", encoding="utf-8")
    project.git("add", "-A")  # the commit would carry a registry with no rows in it
    registry.write_text(kept, encoding="utf-8")  # and the tree has it back
    capsys.readouterr()

    assert project.cl("resolve") == 0, capsys.readouterr().out
    capsys.readouterr()
    assert project.cl("resolve", "--cached") == 1, "the staged registry has no row for it"
    assert "has no registry row" in capsys.readouterr().out


def test_hook_install_force_replaces_an_older_copy_of_this_hook(project, capsys):
    """The only installer here a project could not update: a checkout that ran `--install`
    once kept that hook forever, however far the shipped one moved on. `init` and
    `harness install` both have a `--force`; this now does too.

    The refusal without one says which case it is, because the two want different things
    of the reader. A marker line decides that, not a comparison of the whole text, which
    cannot be made: the interpreter is interpolated into the template, so no two installs
    need match byte for byte.
    """
    project.git("init", "-q")
    hook = project.root / ".git" / "hooks" / "pre-commit"
    assert project.cl("hook", "--install") == 0
    stale = hook.read_text(encoding="utf-8").replace("freshness --cached", "freshness")
    hook.write_text(stale, encoding="utf-8")
    capsys.readouterr()

    assert project.cl("hook", "--install") == 1
    assert "older copy of this hook" in capsys.readouterr().err
    assert hook.read_text(encoding="utf-8") == stale, "unforced, it is still left alone"

    assert project.cl("hook", "--install", "--force") == 0
    assert "freshness --cached" in hook.read_text(encoding="utf-8")


def test_a_hook_that_is_not_ours_is_named_as_a_decision_to_make(project, capsys):
    """The other half of the same message. Anything that cannot be read as our own text —
    somebody's own hook here, and a dangling link or a directory by the same route — is
    not offered a `--force` in the reply, because replacing it is not this command's call.
    """
    project.git("init", "-q")
    hook = project.root / ".git" / "hooks" / "pre-commit"
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text("#!/bin/sh\necho mine\n", encoding="utf-8")
    capsys.readouterr()

    assert project.cl("hook", "--install") == 1
    said = capsys.readouterr().err
    assert "not a copy of this hook" in said
    assert "--force" not in said
    assert hook.read_text(encoding="utf-8") == "#!/bin/sh\necho mine\n"


def test_a_forced_install_does_not_rewrite_a_shared_hook_through_a_link(project, capsys):
    """`--force` replaces this repository's hook, and a link that leaves the hooks
    directory is not this repository's hook. The write resolves a symlink before it
    replaces, so forcing over `pre-commit -> ../../shared/pre-commit` would rewrite the
    team's file; the containment guard is asked under `--force` too, and refuses.
    """
    project.git("init", "-q")
    shared = project.root / "shared"
    shared.mkdir()
    team = shared / "pre-commit"
    team.write_text("#!/bin/sh\necho team\n", encoding="utf-8")
    hooks = project.root / ".git" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    (hooks / "pre-commit").symlink_to("../../shared/pre-commit")
    capsys.readouterr()

    assert project.cl("hook", "--install", "--force") == 2
    assert "outside the hooks directory" in capsys.readouterr().err
    assert team.read_text(encoding="utf-8") == "#!/bin/sh\necho team\n"


def test_a_working_pin_is_read_from_the_index_under_cached(project, capsys):
    """The fifth and last of the 0.1.0 release conditions, and the one left open longest
    because it was a design question rather than a defect: what `working` means when the
    run was asked for the index.

    It means the tree this run reads. `resolve_pointer` took the unpinned branch and read
    `ledger.tree` before the flag was consulted, so a `working` section withdrawn, staged
    and restored in the working tree committed unreported — through the installed hook,
    which runs `resolve --cached`. Both directions are asserted: the bare run reads the
    tree, which still has the section, and says so.
    """
    project.git("init", "-q")
    assert project.cl("new", "first") == 0
    path = project.write_full_entry(project.entry("A0001-first.md"))
    assert '§ "Observation" @working' in path.read_text(encoding="utf-8")
    project.git("add", "-A")
    project.git("commit", "-qm", "the entry and the note it rests on")

    note = project.root / "docs" / "note-001.md"
    kept = note.read_text(encoding="utf-8")
    note.write_text(kept.replace("## Observation", "## Method"), encoding="utf-8")
    project.git("add", "--", str(note))  # the index has no Observation section
    note.write_text(kept, encoding="utf-8")  # and the working tree has it back
    capsys.readouterr()

    assert project.cl("resolve") == 0, capsys.readouterr().out
    capsys.readouterr()
    assert project.cl("resolve", "--cached") == 1, "the staged note withdrew the section"
    assert "has no section 'Observation'" in capsys.readouterr().out


def test_a_working_pin_over_an_untracked_file_still_resolves_under_cached(project, capsys):
    """The fallback, and why it is the point rather than a concession: `working` is the pin
    for evidence that is not committed yet, so reading the index and stopping there would
    fail exactly the case the pin exists for. A path the index does not hold is read from
    the working tree, as it always was.
    """
    project.git("init", "-q")
    assert project.cl("new", "first") == 0
    project.write_full_entry(project.entry("A0001-first.md"))
    assert (project.root / "docs" / "note-001.md").is_file()
    capsys.readouterr()

    assert project.cl("resolve", "--cached") == 0, capsys.readouterr().out


def test_a_staged_working_artifact_that_is_not_utf8_does_not_resolve(project, capsys):
    """The asymmetry a naive read of the index would have introduced, and the reason the
    staged blob is decoded strictly and never fallen back from.

    `git_call` and `blob_text` both decode with replacement, so an artifact staged as
    bytes that are not UTF-8 would have come back as text with replacement characters —
    section header intact, pointer resolved — where the working-tree read reports it as a
    pointer that does not resolve (L0033). One flag, one file, two answers. Falling back
    to the tree would be just as wrong: the index HAS this path, so the tree's copy is not
    what the commit carries.
    """
    project.git("init", "-q")
    assert project.cl("new", "first") == 0
    project.write_full_entry(project.entry("A0001-first.md"))
    note = project.root / "docs" / "note-001.md"
    kept = note.read_bytes()
    note.write_bytes(b"# note 001\n\n## Observation\n\n\xff\xfe not utf-8\n")
    project.git("add", "--", str(note))
    note.write_bytes(kept)  # the working tree is fine; the index is not
    capsys.readouterr()

    assert project.cl("resolve") == 0, capsys.readouterr().out
    capsys.readouterr()
    assert project.cl("resolve", "--cached") == 1, "the staged artifact is not UTF-8 text"
    assert "does not resolve" in capsys.readouterr().out


def _git_whose_cat_file_fails(tmp_path, only_for=None):
    """A real git that fails `cat-file` — for every batch, or only for one whose input
    names `only_for`. The batch's specs arrive on stdin, so the discriminating shim reads
    them there and passes them on when it delegates."""
    d = tmp_path / "shim-bin"
    d.mkdir(exist_ok=True)
    real = shutil.which("git")
    if only_for is None:
        body = f'for a in "$@"; do [ "$a" = cat-file ] && exit 128; done\nexec {real} "$@"\n'
    else:
        body = (
            'for a in "$@"; do\n'
            '  if [ "$a" = cat-file ]; then\n'
            "    input=$(cat)\n"
            f'    case "$input" in *{only_for}*) exit 128;; esac\n'
            f'    printf \'%s\\n\' "$input" | {real} "$@"\n'
            "    exit $?\n"
            "  fi\n"
            "done\n"
            f'exec {real} "$@"\n'
        )
    (d / "git").write_text("#!/bin/sh\n" + body, encoding="utf-8")
    (d / "git").chmod(0o755)
    return d


def _staged_withdrawal(project):
    """A project whose `@working` ground the index no longer satisfies and the tree does:
    the shape a cached run must report, so that a run which fails to read the index cannot
    be mistaken for a run that read it and found nothing wrong."""
    project.git("init", "-q")
    assert project.cl("new", "first") == 0
    project.write_full_entry(project.entry("A0001-first.md"))
    note = project.root / "docs" / "note-001.md"
    kept = note.read_text(encoding="utf-8")
    note.write_text(kept.replace("## Observation", "## Method"), encoding="utf-8")
    project.git("add", "-A")
    note.write_text(kept, encoding="utf-8")
    return project


def test_an_entry_the_index_could_not_be_read_for_stops_the_run(
    project, tmp_path, monkeypatch, capsys
):
    """A `cat-file` that could not answer is not the index saying it does not have the
    path. Every staged read folded the two together, so a git broken only in `cat-file` —
    a timeout, a pack it cannot open, a kill — took the whole ledger back to the working
    tree and reported a clean run: measured, `resolve --cached` went from exit 1 naming a
    staged withdrawal to `0 failure(s)` with nothing said.

    It stops the run the way an unlistable entries directory does, because the entry has
    not been parsed and there is no per-entry line to say it on.

    The message is asserted and not only the exit code, and that is what makes this hold
    the site: the registry read raises the same error at the same exit code a moment later,
    so a test that asked for 2 alone passed with this stop deleted.
    """
    _staged_withdrawal(project)
    assert project.cl("resolve", "--cached") == 1, "the fixture's withdrawal must be reported"
    monkeypatch.setenv(
        "PATH", f"{_git_whose_cat_file_fails(tmp_path)}{os.pathsep}{os.environ['PATH']}"
    )
    assert project.cl("resolve", "--cached") == 2
    said = capsys.readouterr().err
    assert "A0001-first.md" in said, said
    assert "could not be read from the index" in said


def test_an_artifact_the_index_could_not_be_read_for_is_a_pointer_that_fails(
    project, tmp_path, monkeypatch, capsys
):
    """The same rule one layer in, at the pointer rather than at the entry list. Here the
    entries load and only the artifact's blob is unreadable, so the run has a line to say
    it on and says it there rather than reading the working tree's copy of the artifact.
    """
    _staged_withdrawal(project)
    shim = _git_whose_cat_file_fails(tmp_path, only_for="docs/note-001.md")
    monkeypatch.setenv("PATH", f"{shim}{os.pathsep}{os.environ['PATH']}")
    capsys.readouterr()
    assert project.cl("resolve", "--cached") == 1
    assert "could not be read from the index" in capsys.readouterr().out


def test_a_staged_document_that_is_not_utf8_is_reported_as_it_is_in_the_tree(project, capsys):
    """`document_bodies` decoded staged documents with `blob_text`, which replaces what it
    cannot decode — so a document the index holds as bytes nobody can read came back as
    text with the real thing's shape, and `references --cached` reported a clean run where
    the landed commit fails. L0047's rule is that an unreadable document is a failure and
    not a clean run; the flag was deciding whether it applied.
    """
    project.git("init", "-q")
    assert project.cl("new", "first") == 0
    project.write_full_entry(project.entry("A0001-first.md"))
    note = project.root / "docs" / "note-001.md"
    kept = note.read_bytes()
    note.write_bytes(kept + b"\n\xff\xfe tail\n")
    project.git("add", "-A")
    note.write_bytes(kept)
    capsys.readouterr()

    assert project.cl("references") == 0, capsys.readouterr().out
    capsys.readouterr()
    assert project.cl("references", "--cached") == 1
    assert "is not UTF-8 text" in capsys.readouterr().out


def test_a_registry_the_index_could_not_be_read_for_stops_the_run(
    project, tmp_path, monkeypatch, capsys
):
    """Every `source:` ground in a ledger rests on the registry, so a registry git could
    not hand over is not an empty registry and is not the working tree's either. The shim
    fails only the batch naming the registry, so the entries load and this is the one read
    under test.
    """
    _staged_withdrawal(project)
    shim = _git_whose_cat_file_fails(tmp_path, only_for="sources.jsonl")
    monkeypatch.setenv("PATH", f"{shim}{os.pathsep}{os.environ['PATH']}")
    capsys.readouterr()
    assert project.cl("resolve", "--cached") == 2
    said = capsys.readouterr().err
    assert "sources.jsonl" in said, said
    assert "could not be read from the index" in said


def test_a_document_the_index_could_not_be_read_for_is_a_failure_not_a_clean_run(
    project, tmp_path, monkeypatch, capsys
):
    """The same rule for the documents a citation is read out of. Reading the working
    tree's copy because git would not answer for the index's is a verdict about prose no
    commit contains, reported as a clean run — which is what L0047 refuses for a document
    that cannot be opened, arrived at through the flag instead of through the filesystem.
    """
    project.git("init", "-q")
    assert project.cl("new", "first") == 0
    project.write_full_entry(project.entry("A0001-first.md"))
    project.git("add", "-A")
    shim = _git_whose_cat_file_fails(tmp_path, only_for="note-001.md")
    monkeypatch.setenv("PATH", f"{shim}{os.pathsep}{os.environ['PATH']}")
    capsys.readouterr()

    assert project.cl("references", "--cached") == 1
    out = capsys.readouterr().out
    assert "could not be read from the index" in out, out
