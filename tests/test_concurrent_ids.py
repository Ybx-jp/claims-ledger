"""Two checkouts of one repository, each minting entries.

A single developer running several agent sessions at once has one repository and several
linked worktrees, each on its own branch. Allocation used to be max+1 over the entries
directory of whichever checkout was asking, so two of those sessions were handed the same
number as a matter of course — and when the slugs differed the two files merged without a
conflict and every checker read the merged tree at exit 0.

The question is asked of the repository here instead: every entry filename any ref has
carried, and every entry file a sibling worktree holds, including the ones it has not
committed. Both halves are answered out of what a repository already shares, so neither
costs a fetch.
"""

import subprocess

from claims_ledger import cli
from claims_ledger.authoring import AuthoringError, create_entry, ids_in_the_repository
from claims_ledger.schema import open_ledger


def committed(project):
    """The project as a repository with its ledger in a commit."""
    project.git("init")
    project.git("add", "-A")
    project.git("commit", "-m", "the ledger")


def worktree(project, name, branch):
    """A linked worktree of the project's repository, and its root."""
    root = project.root.parent / name
    project.git("worktree", "add", "-q", str(root), "-b", branch)
    return root


def mint(root, slug):
    """The id `claims-ledger new` allocates in the checkout at `root`."""
    assert cli.main(["--root", str(root), "new", slug]) == 0
    written = [p.stem for p in (root / "ledger" / "entries").glob(f"*-{slug}.md")]
    assert len(written) == 1, written
    return written[0].split("-", 1)[0]


def test_a_sibling_worktree_does_not_mint_the_number_this_one_holds(project):
    """The case that actually happens: two sessions mint within a minute of each other,
    and neither has committed. No ref can show the first mint, so the second checkout has
    to be looked in rather than asked about."""
    committed(project)
    other = worktree(project, "side", "side")

    here = mint(project.root, "alpha")
    there = mint(other, "beta")

    assert here != there, "a sibling worktree's uncommitted mint was not seen"
    assert (project.root / "ledger" / "entries" / f"{here}-alpha.md").exists()
    assert (other / "ledger" / "entries" / f"{there}-beta.md").exists()


def test_a_number_only_a_branch_holds_is_not_minted_again(project):
    """An entry committed on a branch no checkout has out is still a number that is
    taken. Worktrees share their refs, so the answer needs no fetch and no network."""
    committed(project)
    project.git("checkout", "-q", "-b", "side")
    on_the_branch = mint(project.root, "alpha")
    project.git("add", "-A")
    project.git("commit", "-m", "alpha")
    project.git("checkout", "-q", "-")

    assert not (project.root / "ledger" / "entries" / f"{on_the_branch}-alpha.md").exists()
    assert mint(project.root, "beta") != on_the_branch


def test_a_number_a_deleted_entry_once_held_is_not_minted_again(project):
    """A filename any ref has ever carried, rather than one some ref carries now: a
    number that has been used is not free, however the entry left the tree."""
    committed(project)
    gone = mint(project.root, "alpha")
    project.git("add", "-A")
    project.git("commit", "-m", "alpha")
    (project.root / "ledger" / "entries" / f"{gone}-alpha.md").unlink()
    project.git("commit", "-a", "-m", "and away")

    assert mint(project.root, "beta") != gone


def test_a_mint_over_a_repository_git_cannot_walk_is_refused(project):
    """Produced by configuring git rather than by patching it: a ref naming an object the
    repository does not hold makes the walk exit non-zero, and the repository is otherwise
    a repository. An id allocated over that is the collision the question exists to
    prevent, so nothing is allocated and nothing is written."""
    committed(project)
    ghost = project.root / ".git" / "refs" / "heads" / "ghost"
    ghost.write_text("0000000000000000000000000000000000000001\n", encoding="utf-8")

    ledger = open_ledger(root=project.root)
    _ids, unasked = ids_in_the_repository(ledger)
    assert unasked is not None and "refs of this repository" in unasked

    try:
        create_entry(ledger, "alpha")
    except AuthoringError as exc:
        assert "--id" in str(exc)
    else:  # pragma: no cover - the refusal is the point
        raise AssertionError("a mint over an unwalkable repository was allowed")
    assert not list((project.root / "ledger" / "entries").glob("*-alpha.md"))


def test_an_id_named_by_hand_is_written_when_the_repository_cannot_be_read(project):
    """The refusal is about allocating, not about writing: an id nobody had to choose is
    the way past it, which is what keeps a broken repository from stopping the work."""
    committed(project)
    (project.root / ".git" / "refs" / "heads" / "ghost").write_text(
        "0000000000000000000000000000000000000001\n", encoding="utf-8"
    )

    assert cli.main(["--root", str(project.root), "new", "alpha", "--id", "A0404"]) == 0
    assert (project.root / "ledger" / "entries" / "A0404-alpha.md").exists()


def test_a_ledger_with_no_repository_still_mints(project):
    """Nothing to ask is not a question that failed. A ledger outside version control has
    one directory and that directory is the whole of what there is."""
    assert not (project.root / ".git").exists()
    ledger = open_ledger(root=project.root)
    ids, unasked = ids_in_the_repository(ledger)
    assert (ids, unasked) == (set(), None)
    assert mint(project.root, "alpha")


def test_the_walk_costs_one_git_process_per_question(project, monkeypatch):
    """Two processes for the two questions, whatever the repository holds: the walk is
    one `git log`, and the checkouts are one `git worktree list`. Allocation happens once
    per mint, so the cost is an interactive command's rather than a checker's, but a
    question asked of history is worth counting before it is asked on every commit."""
    committed(project)
    worktree(project, "side", "side")
    ledger = open_ledger(root=project.root)

    calls = []
    real = subprocess.run
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda args, **kw: (calls.append(tuple(args[:4])), real(args, **kw))[1],
    )
    ids_in_the_repository(ledger)
    assert [c for c in calls if c[0] == "git"] == calls
    assert len(calls) == 2, calls


def test_two_entries_carrying_one_number_are_a_failure(project):
    """The state a merge used to produce in silence. Reported once for the number, naming
    both entries, because the repair is one act on the pair."""
    committed(project)
    assert project.cl("new", "alpha", "--id", "A0002") == 0
    assert project.cl("new", "beta", "--id", "A0002") == 0

    from claims_ledger import validate
    from claims_ledger.schema import load_entries

    ledger = open_ledger(root=project.root)
    reports = validate.check_numbers(load_entries(ledger))
    assert len(reports) == 1
    assert reports[0].outcome == "fail" and reports[0].entry == "A0002"
    assert "A0002-alpha" in reports[0].message and "A0002-beta" in reports[0].message
    assert "renumber" in reports[0].message
    assert project.cl("validate") == 1


def test_one_number_for_one_entry_says_nothing(project):
    """The ordinary ledger, which is every ledger that has not had two branches merged
    into it: the check is silent rather than merely quiet."""
    committed(project)
    assert project.cl("new", "alpha") == 0
    assert project.cl("new", "beta") == 0

    from claims_ledger import validate
    from claims_ledger.schema import load_entries

    assert validate.check_numbers(load_entries(open_ledger(root=project.root))) == []
