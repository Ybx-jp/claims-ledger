"""The immutability checks read the whole ledger's history in a fixed number of git
processes, and read the same history the per-entry walk read.

`check_history` used to ask `git log -- <entry>` once per entry and `git show` once per
revision. Each of those logs walks every commit in the repository, so a ledger of a
thousand entries with a thousand commits behind it cost git a million tree diffs and
`check` took five minutes; one walk of the entries directory and one `cat-file --batch`
answer the same questions in under three seconds. Measured, and recorded in
ARCH-AUDIT.md. What these tests hold is the two properties that let the batch stand in
for the walk: it lists what the walk listed, and its process count does not grow.
"""

import os
import shutil
import subprocess

from claims_ledger import validate
from claims_ledger.schema import git_history, open_ledger


def _git(root, *args):
    r = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=test",
            "-c",
            "user.email=test@example",
            "-c",
            "commit.gpgsign=false",
            *args,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return r.returncode, r.stdout


def _commits_touching(root, rel):
    """The reference: what the per-entry walk asked, verbatim from `check_history` as
    it was — `git log --format=%H -- <path>`, newest first, no --follow."""
    code, out = _git(root, "log", "--format=%H", "--", rel)
    assert code == 0
    return out.split()


def _is_merge(root, commit):
    return len(_git(root, "rev-list", "--parents", "-n", "1", commit)[1].split()) > 2


def _branching_history(root):
    """Four entries across two branches: one edited on both sides and merged clean, one
    merged with a hand resolution, one created on a branch, one renamed away. Every
    shape in which a per-path log and a directory walk could disagree."""
    entries = root / "ledger" / "entries"
    entries.mkdir(parents=True)
    a, b, c = (entries / f"A000{i}-{n}.md" for i, n in ((1, "a"), (2, "b"), (3, "c")))
    assert _git(root, "init", "-q", "-b", "main")[0] == 0
    a.write_text("a\n")
    b.write_text("b\n")
    (root / "README.md").write_text("other\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "c1")
    a.write_text("a\na2\n")
    _git(root, "commit", "-qam", "c2")
    _git(root, "checkout", "-qb", "side")
    b.write_text("b\nb2\n")
    c.write_text("c\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "side1")
    _git(root, "checkout", "-q", "main")
    a.write_text("a\na2\na3\n")
    _git(root, "commit", "-qam", "c3")
    assert _git(root, "merge", "-q", "--no-edit", "side")[0] == 0
    _git(root, "checkout", "-qb", "conflict")
    b.write_text("b\nb2\nconflict-side\n")
    _git(root, "commit", "-qam", "conf1")
    _git(root, "checkout", "-q", "main")
    b.write_text("b\nb2\nmain-side\n")
    _git(root, "commit", "-qam", "c4")
    assert _git(root, "merge", "conflict")[0] != 0, "precondition: the merge conflicts"
    b.write_text("b\nb2\nresolved\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "merge-resolved")
    _git(root, "mv", str(c), str(entries / "A0004-d.md"))
    _git(root, "commit", "-qm", "rename")
    return [os.path.relpath(p, root) for p in (a, b, c, entries / "A0004-d.md")]


def test_one_walk_lists_every_commit_the_per_entry_walk_listed(tmp_path):
    """For every entry, the batch names the same creating commit, every commit the
    per-path log named, in the same order; anything it names beyond those is a merge
    commit, which `-m` lists whenever the file differs from either parent."""
    rels = _branching_history(tmp_path)
    revisions, why = git_history(tmp_path, "ledger/entries")
    assert revisions is not None, why
    for rel in rels:
        reference = _commits_touching(tmp_path, rel)
        assert reference, f"precondition: {rel} has a history to compare"
        batch = revisions[rel]
        assert batch[-1] == reference[-1], f"{rel}: the creating commit"
        assert [h for h in batch if h in reference] == reference, f"{rel}: order and coverage"
        for extra in set(batch) - set(reference):
            assert _is_merge(tmp_path, extra), f"{rel}: {extra[:7]} is not a merge"
    assert set(rels) <= set(revisions), "the renamed-away name is still listed"


def _count_git(monkeypatch):
    counts = []
    real = subprocess.run

    def counting(argv, *args, **kwargs):
        if argv and argv[0] == "git":
            counts.append(argv)
        return real(argv, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", counting)
    return counts


def test_the_history_checks_spawn_the_same_number_of_git_processes_for_five_entries_as_for_one(
    project, monkeypatch
):
    """The property the batch exists for. Before it, `validate` ran two processes plus
    one per revision for every entry; the count below would grow by four per entry."""
    project.cl("new", "first")
    project.write_full_entry(project.entry("A0001-first.md"))
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "one entry")
    counts = _count_git(monkeypatch)
    assert validate.run(open_ledger(root=project.root)) == []
    with_one = len(counts)
    assert validate.run(open_ledger(root=project.root), cached=True) == []
    with_one_cached = len(counts) - with_one

    for i, slug in enumerate(("second", "third", "fourth", "fifth"), start=2):
        project.cl("new", slug)
        project.write_full_entry(project.entry(f"A000{i}-{slug}.md"))
        project.git("add", "-A")
        project.git("commit", "-qm", slug)
    counts.clear()
    assert validate.run(open_ledger(root=project.root)) == []
    assert len(counts) == with_one, [a[3:5] for a in counts]
    counts.clear()
    assert validate.run(open_ledger(root=project.root), cached=True) == []
    assert len(counts) == with_one_cached, [a[3:5] for a in counts]


def _git_that_cannot(tmp_path, subcommand):
    """A real git on PATH that fails one subcommand and delegates the rest — the shape
    `test_git_degradation` uses, because a shim that exits non-zero is a git failing for
    real and not a patched internal."""
    d = tmp_path / "shim-bin"
    d.mkdir(exist_ok=True)
    (d / "git").write_text(
        "#!/bin/sh\n"
        f'for a in "$@"; do [ "$a" = "{subcommand}" ] && exit 128; done\n'
        f'exec {shutil.which("git")} "$@"\n',
        encoding="utf-8",
    )
    (d / "git").chmod(0o755)
    return d


def _committed(project):
    project.cl("new", "first")
    project.write_full_entry(project.entry("A0001-first.md"))
    project.cl("new", "second")
    project.write_full_entry(project.entry("A0002-second.md"))
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "two entries")
    assert validate.run(open_ledger(root=project.root)) == [], "precondition: clean"


def test_a_walk_git_cannot_make_is_reported_for_every_committed_entry(
    project, tmp_path, monkeypatch
):
    """One walk stands in for every entry's history, so a walk that failed is a history
    nobody read for any of them — and each says so, rather than reading as uncommitted."""
    _committed(project)
    monkeypatch.setenv(
        "PATH", f"{_git_that_cannot(tmp_path, 'log')}{os.pathsep}{os.environ['PATH']}"
    )
    reports = validate.run(open_ledger(root=project.root))
    assert sorted(r.entry for r in reports) == ["A0001", "A0002"]
    assert all("cannot read the history" in r.message for r in reports)


def test_blobs_git_cannot_produce_are_reported_for_every_revision(project, tmp_path, monkeypatch):
    """The same for the batch read: a `cat-file` that failed produced no blob for any
    revision, and no entry's frozen region was compared against anything."""
    _committed(project)
    monkeypatch.setenv(
        "PATH", f"{_git_that_cannot(tmp_path, 'cat-file')}{os.pathsep}{os.environ['PATH']}"
    )
    reports = validate.run(open_ledger(root=project.root))
    assert sorted(r.entry for r in reports) == ["A0001", "A0002"]
    assert all(r.message.startswith("cannot read ledger/entries/") for r in reports), reports
