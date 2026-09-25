"""Reconciling two branches that minted one number, by rewriting the one that has not
merged.

The scenario each test builds is the one that actually happens: two branches cut from one
base, each minting the same number for a different claim, each clean on its own. Merged as
they stand they produce two entries carrying one number — and with different slugs git
merges them without a conflict and every checker reads the result at exit 0.
"""

import re
from pathlib import Path

import pytest

from claims_ledger import renumber
from claims_ledger.schema import open_ledger

NOTE = """# note 001

## Observation Base

At a stale fraction of 0.1 the measured error was 0.04.

## Observation Alpha

At a stale fraction of 0.2 the measured error was 0.08.

## Observation Beta

At a stale fraction of 0.3 the measured error was 0.12.
"""

SECTIONS = {
    "Observation Alpha": "At a stale fraction of 0.2 the measured error was 0.08.",
    "Observation Beta": "At a stale fraction of 0.3 the measured error was 0.12.",
}


def entry(project, ident, slug, section, pin="=?", cite=True):
    """An entry resting on one section of the note, cited from inside that section.

    Inside it, because that is where this project's own citations sit and because it is
    what makes a renumber move the digest the entry is anchored to — the case the
    re-pinning has to get right. `--force`, because a collision is what these tests build
    on purpose, and `new` refuses a number the repository already holds.
    """
    assert project.cl("new", slug, "--id", ident, "--force") == 0
    path = project.entry(f"{ident}-{slug}.md")
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "TODO: the claim, in this project's words. No quotation marks.",
        f"The {section} reading is recorded.",
    )
    text = re.sub(
        r"- TODO: one typed pointer[^\n]*\n",
        f'- lab: docs/note-001.md § "{section}" {pin}\n',
        text,
    )
    text = text.replace(
        "TODO: the rule by which the grounds support the assertion.",
        "The section states the reading.",
    )
    text = text.replace("metric: TODO", "metric: the recorded reading")
    text = text.replace("cohort: TODO", f"cohort: {section.lower()}")
    text = text.replace("condition: TODO", "condition: as written")
    text = text.rstrip("\n") + "\n\n- docs/note-001.md · standing · cites-as-live\n"
    path.write_text(text, encoding="utf-8")

    if cite:
        note = project.root / "docs" / "note-001.md"
        body = note.read_text(encoding="utf-8")
        line = SECTIONS[section]
        note.write_text(
            body.replace(line, f"{line}\nStated as a claim here ({ident}-{slug}, cites-as-live)."),
            encoding="utf-8",
        )
    assert project.cl("sha", "--write", str(path)) == 0
    return path


def make_collision(project, merge_renumber=None):
    """Two branches off one base, each holding A0002 for a different claim.

    The policy is written before the branches are cut, because a configuration that
    changes *on* the branch is one of the things a rewrite refuses — the rewrite reads
    one configuration for every commit it replaces.
    """
    (project.root / "docs" / "note-001.md").write_text(NOTE, encoding="utf-8")
    if merge_renumber is not None:
        config = project.root / "claims-ledger.toml"
        config.write_text(
            config.read_text(encoding="utf-8") + f'\nmerge-renumber = "{merge_renumber}"\n',
            encoding="utf-8",
        )
    project.git("init")
    project.git("add", "-A")
    project.git("commit", "-m", "base")
    project.git("branch", "-M", "main")

    project.git("checkout", "-q", "-b", "side")
    entry(project, "A0002", "beta-claim", "Observation Beta")
    project.git("add", "-A")
    project.git("commit", "-m", "the beta claim")

    project.git("checkout", "-q", "main")
    entry(project, "A0002", "alpha-claim", "Observation Alpha")
    project.git("add", "-A")
    project.git("commit", "-m", "the alpha claim")
    project.git("checkout", "-q", "side")
    return project


@pytest.fixture
def collision(project):
    return make_collision(project)


def head(project, *args):
    import subprocess

    return subprocess.run(
        ["git", "-C", str(project.root), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def test_each_branch_is_clean_and_the_collision_is_across_them(collision):
    """The premise: neither branch has anything wrong with it. The number is only held
    twice once the two are put together, which is why nothing on either side reports it."""
    assert collision.cl("check") == 0


def test_the_branch_is_rewritten_and_the_entry_is_born_with_its_new_id(collision):
    """The whole point of rewriting the branch rather than the merge: the commit that
    creates the entry's path is the commit that carries its final id, so what `validate`
    compares the frozen region against is the entry as it will stand."""
    assert collision.cl("renumber", "--onto", "main", "--write") == 0

    moved = collision.entries / "A0003-beta-claim.md"
    assert moved.exists() and not (collision.entries / "A0002-beta-claim.md").exists()
    created = head(
        collision,
        "log",
        "--diff-filter=A",
        "--format=%H",
        "--",
        "ledger/entries/A0003-beta-claim.md",
    )
    assert created == head(collision, "rev-parse", "HEAD")
    assert collision.cl("check") == 0


def test_the_receiving_side_keeps_its_ids(collision):
    """Which side moves is decided by which one is being merged, not by any ordering."""
    assert collision.cl("renumber", "--onto", "main", "--write") == 0
    collision.git("checkout", "-q", "main")
    assert (collision.entries / "A0002-alpha-claim.md").exists()


def test_the_citation_moves_with_the_id(collision):
    """A renumber that left the prose naming the old id would be repaired by deleting the
    citation, which is the one repair this ledger never wants."""
    assert collision.cl("renumber", "--onto", "main", "--write") == 0
    note = (collision.root / "docs" / "note-001.md").read_text(encoding="utf-8")
    assert "(A0003-beta-claim, cites-as-live)" in note
    assert "A0002-beta-claim" not in note


def test_an_anchor_moved_by_the_id_alone_is_re_pinned(collision):
    """The citation sits inside the span the entry pins, so rewriting it moves that span's
    digest. Undoing the substitution reproduces the anchor, which is the proof that the id
    was the whole of the change."""
    before = (collision.entries / "A0002-beta-claim.md").read_text(encoding="utf-8")
    assert collision.cl("renumber", "--onto", "main", "--write") == 0
    after = (collision.entries / "A0003-beta-claim.md").read_text(encoding="utf-8")

    anchors = lambda text: re.findall(r"=sha256:[0-9a-f]{64}", text)  # noqa: E731
    assert anchors(before) != anchors(after), "the anchor did not move with the span"
    assert collision.cl("freshness") == 0


def test_an_anchor_whose_span_changed_otherwise_is_left_for_freshness(collision):
    """The other half of the same rule. When the span moved for a reason the renumber
    cannot account for, the anchor stands as written and the drift is reported — a
    checker that absorbed it would be answering for a reading nobody made."""
    note = collision.root / "docs" / "note-001.md"
    note.write_text(
        note.read_text(encoding="utf-8").replace(
            "At a stale fraction of 0.3 the measured error was 0.12.",
            "At a stale fraction of 0.3 the measured error was 0.99.",
        ),
        encoding="utf-8",
    )
    collision.git("commit", "-a", "-m", "the beta reading is corrected")
    assert collision.cl("freshness") == 0  # flags, and a flag exits zero

    assert collision.cl("renumber", "--onto", "main", "--write") == 0

    moved = (collision.entries / "A0003-beta-claim.md").read_text(encoding="utf-8")
    assert "0.99" not in moved, "the anchor was re-pinned over a change the id cannot account for"
    adrift = [
        r for r in _freshness_reports(collision) if r.entry == "A0003" and "has moved" in r.message
    ]
    assert adrift, "a span that changed for another reason was silently re-pinned"


def _freshness_reports(project):
    from claims_ledger import freshness

    return freshness.run(open_ledger(root=project.root))


def test_nothing_is_written_without_the_flag(collision):
    """A dry run says what would move and leaves the branch alone."""
    at = head(collision, "rev-parse", "HEAD")
    assert collision.cl("renumber", "--onto", "main") == 1
    assert head(collision, "rev-parse", "HEAD") == at
    assert (collision.entries / "A0002-beta-claim.md").exists()


def test_a_branch_with_nothing_to_move_says_so(collision):
    """Asked of a branch whose numbers nobody else holds, the answer is that there is
    nothing to do — not an error, and not a rewrite of the history anyway."""
    assert collision.cl("renumber", "--onto", "main", "--write") == 0
    at = head(collision, "rev-parse", "HEAD")
    assert collision.cl("renumber", "--onto", "main", "--write") == 0
    assert head(collision, "rev-parse", "HEAD") == at


def test_a_merged_branch_is_refused(collision):
    """Rewriting merged history is the thing this repository forbids, and the command
    refuses it rather than leaving the rule to the operator."""
    collision.git("checkout", "-q", "main")
    collision.git("merge", "--no-ff", "--no-edit", "side")
    collision.git("checkout", "-q", "side")
    assert collision.cl("renumber", "--onto", "main", "--write") == 2


def test_a_ground_pinning_a_branch_commit_by_reference_is_refused(collision):
    """`docs/OPERATING.md` permits the rewrite because nothing pins the commits it
    replaces. Where something does, the rewrite would remove the evidence a ground rests
    on — a supersession rather than a re-read — so it is refused with the commit named."""
    pinned = head(collision, "rev-parse", "HEAD")
    path = collision.entries / "A0002-beta-claim.md"
    path.write_text(
        re.sub(
            r'(lab: docs/note-001\.md § "Observation Beta" )=sha256:[0-9a-f]{64}',
            rf"\1@{pinned}",
            path.read_text(encoding="utf-8"),
            count=1,
        ),
        encoding="utf-8",
    )
    collision.git("commit", "-a", "-m", "a ground stated by reference into this branch")

    ledger = open_ledger(root=collision.root)
    plan = renumber.plan(ledger, "main", "HEAD")
    refused = renumber.refusals(ledger, plan)
    assert any("by reference" in r for r in refused), refused
    assert collision.cl("renumber", "--onto", "main", "--write") == 2


def test_a_dirty_working_tree_refuses_the_write(collision):
    """The rewrite ends by resetting this checkout onto the commits it wrote, so anything
    uncommitted would go with it."""
    (collision.root / "docs" / "note-001.md").write_text("scribbled over\n", encoding="utf-8")
    assert collision.cl("renumber", "--onto", "main", "--write") == 2
    assert (collision.entries / "A0002-beta-claim.md").exists()


def test_a_branch_another_checkout_holds_refuses_the_write(collision, tmp_path):
    """A worktree sitting on the commits the rewrite replaces is a checkout on history no
    ref names, which is the state this exists to avoid producing."""
    collision.git("checkout", "-q", "main")
    other = tmp_path / "side-checkout"
    collision.git("worktree", "add", "-q", str(other), "side")
    assert collision.cl("renumber", "--onto", "main", "--branch", "side", "--write") == 2


def test_on_merge_refuses_by_default(collision):
    """What a merge guard gets when the branch would land a number the other side holds:
    a non-zero exit and the command that repairs it."""
    at = head(collision, "rev-parse", "HEAD")
    assert collision.cl("renumber", "--onto", "main", "--on-merge") == 1
    assert head(collision, "rev-parse", "HEAD") == at


def test_on_merge_rewrites_when_that_is_what_the_project_configured(project):
    """Opt-in, because rewriting a branch is a thing to have asked for."""
    collision = make_collision(project, merge_renumber="rewrite")
    assert collision.cl("renumber", "--onto", "main", "--on-merge") == 0
    assert (collision.entries / "A0003-beta-claim.md").exists()
    assert collision.cl("check") == 0


def test_on_merge_says_nothing_when_it_is_off(project):
    """A project that does not want the question asked at merge time is not asked it."""
    collision = make_collision(project, merge_renumber="off")
    at = head(collision, "rev-parse", "HEAD")
    assert collision.cl("renumber", "--onto", "main", "--on-merge") == 0
    assert head(collision, "rev-parse", "HEAD") == at
    assert (collision.entries / "A0002-beta-claim.md").exists()


def test_on_merge_is_silent_about_a_branch_it_cannot_plan(collision):
    """A guard asks about every merge, including merges of branches that have nothing to
    do with this ledger; one it cannot plan is not its business to refuse."""
    assert collision.cl("renumber", "--onto", "no-such-branch", "--on-merge") == 0


# --- what the pre-merge gate on this branch found, as regressions -------------------


def test_a_detached_head_is_refused(collision):
    """`--branch` defaults to HEAD, and on a detached HEAD `rev-parse
    --symbolic-full-name` answers `HEAD`. Moving that moves the detached head: the
    rewritten commits end up reachable from nothing a branch names, the branch still
    holds the originals, and the working tree keeps the old content with the rewrite
    staged against it — reported, before this, as a rewrite that had succeeded.

    The branch is deleted after detaching, so no other ref contains these commits and the
    shared-ref refusal cannot stand in for the one being tested. Without that, this passes
    against a `branch_ref` that has been removed entirely.
    """
    collision.git("checkout", "-q", "--detach")
    collision.git("branch", "-q", "-D", "side")
    at = head(collision, "rev-parse", "HEAD")

    assert collision.cl("renumber", "--onto", "main", "--write") == 2
    assert head(collision, "rev-parse", "HEAD") == at
    assert (collision.entries / "A0002-beta-claim.md").exists()


def test_a_merge_is_not_allowed_over_a_repository_that_could_not_be_read(collision):
    """The guard's one state of ignorance. A branch it cannot plan is not its business
    and the merge proceeds; a repository it could not read is different in kind, and
    allowing a merge out of ignorance is the false pass this package exists to refuse."""
    ghost = Path(collision.root) / ".git" / "refs" / "heads" / "ghost"
    ghost.write_text("0000000000000000000000000000000000000001\n", encoding="utf-8")

    assert collision.cl("renumber", "--onto", "main", "--on-merge") == 1
    assert collision.cl("renumber", "--onto", "no-such-branch", "--on-merge") == 0


def test_a_number_the_branch_holds_twice_is_moved_and_a_prefix_id_is_not_touched(project):
    """Two sessions that both minted into one branch. `check_numbers` names this command
    for that too, so it answers for it — and the pair is the shape that catches a
    substitution written with `\\b` on the right: `A0009-beta` is a prefix of
    `A0009-beta-claim`, and a boundary that accepts the following hyphen renumbers the
    wrong entry.

    The doubled number is one the receiving side does NOT hold, so the collision can only
    be found by looking at the branch against itself. With a number `main` also holds,
    this passes against a `plan()` that never learned to.
    """
    (project.root / "docs" / "note-001.md").write_text(NOTE, encoding="utf-8")
    project.git("init")
    project.git("add", "-A")
    project.git("commit", "-m", "base")
    project.git("branch", "-M", "main")
    project.git("checkout", "-q", "-b", "side")
    entry(project, "A0009", "beta-claim", "Observation Beta")
    entry(project, "A0009", "beta", "Observation Alpha")
    project.git("add", "-A")
    project.git("commit", "-m", "two sessions minted into one branch")

    assert project.cl("validate") == 1  # two entries carry A0009, and main holds neither
    before = len([r for r in _freshness_reports(project) if "has moved" in r.message])

    assert project.cl("renumber", "--onto", "main", "--write") == 0
    assert project.cl("validate") == 0
    after = len([r for r in _freshness_reports(project) if "has moved" in r.message])
    assert after == before, "the renumber flagged a ground the collision had not"

    ids = sorted(p.stem for p in project.entries.glob("*.md"))
    assert len(ids) == len({i.split("-", 1)[0] for i in ids}), ids
    assert sorted(i.split("-", 1)[1] for i in ids) == ["beta", "beta-claim"]
    for path in project.entries.glob("*.md"):
        assert f"id: {path.stem}\n" in path.read_text(encoding="utf-8")


def test_the_anchor_freshness_compares_from_is_re_pinned(collision):
    """A ground is compared from the latest corroborating verdict that names its section
    once one exists, and from the ground's own pin only until then. Re-pinning the
    Grounds alone leaves the pointer the checker actually uses naming text the rewrite
    replaced, and the entry comes out of its own renumber flagged."""
    path = collision.entries / "A0002-beta-claim.md"
    digest = collision.digest("docs/note-001.md", "Observation Beta")
    path.write_text(
        path.read_text(encoding="utf-8")
        .rstrip("\n")
        .replace(
            "## References",
            "- 2026-09-14T12:00:00-07:00 · corroborated · grade: measured · author: main\n"
            '  evidence: lab: docs/note-001.md § "Observation Beta" '
            f"={digest}\n"
            "  note: read again against the note as it stands.\n\n## References",
        )
        + "\n",
        encoding="utf-8",
    )
    collision.git("commit", "-a", "-m", "a reading of the beta section")
    assert collision.cl("freshness") == 0

    assert collision.cl("renumber", "--onto", "main", "--write") == 0
    moved = (collision.entries / "A0003-beta-claim.md").read_text(encoding="utf-8")
    assert moved.count(digest) == 0, "the verdict's anchor was left naming the old text"
    assert not [r for r in _freshness_reports(collision) if "has moved" in r.message]


def test_a_detached_sibling_worktree_on_the_commits_is_refused(collision, tmp_path):
    """`git worktree list --porcelain` reports a detached checkout with no `branch` line
    at all, so a parse that only reads branch lines cannot see the worktree a rewrite
    would strand."""
    doomed = tmp_path / "detached-checkout"
    collision.git("worktree", "add", "-q", "--detach", str(doomed), "side")
    collision.git("checkout", "-q", "side")

    assert collision.cl("renumber", "--onto", "main", "--write") == 2
    assert (collision.entries / "A0002-beta-claim.md").exists()


SECOND_NOTE = """# note 002

## Observation Late

At a stale fraction of 0.5 the measured error was 0.20.
Stated as a claim here (A0002-late-claim, cites-as-live).
"""


def test_an_anchor_is_decided_from_the_tip_not_from_where_it_first_could_be(project):
    """The entry is committed in one commit and the artifact its ground names arrives in
    the next — so at the commit that creates the entry there is no section to compare and
    no answer to be had.

    Asked per commit, that commit records nothing, the next one decides and re-pins, and
    the entry ends up carrying one frozen region where it is created and another after
    it: `validate` refuses that with `differs from the blob at the creating commit`.
    Asked once from the tip, there is one answer and every commit gets it.
    """
    project.git("init")
    project.git("add", "-A")
    project.git("commit", "-m", "base")
    project.git("branch", "-M", "main")
    project.git("checkout", "-q", "-b", "side")

    note = project.root / "docs" / "note-002.md"
    note.write_text(SECOND_NOTE, encoding="utf-8")
    assert project.cl("new", "late-claim", "--id", "A0002", "--force") == 0
    path = project.entry("A0002-late-claim.md")
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "TODO: the claim, in this project's words. No quotation marks.",
        "The late reading is recorded.",
    )
    text = re.sub(
        r"- TODO: one typed pointer[^\n]*\n",
        '- lab: docs/note-002.md § "Observation Late" =?\n',
        text,
    )
    text = text.replace(
        "TODO: the rule by which the grounds support the assertion.",
        "The section states the reading.",
    )
    text = text.replace("metric: TODO", "metric: the recorded reading")
    text = text.replace("cohort: TODO", "cohort: observation late")
    text = text.replace("condition: TODO", "condition: as written")
    text = text.rstrip("\n") + "\n\n- docs/note-002.md · standing · cites-as-live\n"
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0

    # the entry lands first, anchored to a section the branch does not carry yet
    note.unlink()
    project.git("add", "-A")
    project.git("commit", "-m", "the late claim, before the note it rests on")
    note.write_text(SECOND_NOTE, encoding="utf-8")
    project.git("add", "-A")
    project.git("commit", "-m", "and the note, a commit later")
    assert project.cl("check") == 0, "the branch is green before the renumber"

    project.git("checkout", "-q", "main")
    assert project.cl("new", "other-claim", "--id", "A0002", "--force", "--grade", "asserted") == 0
    other = project.entry("A0002-other-claim.md")
    body = other.read_text(encoding="utf-8")
    body = body.replace(
        "TODO: the claim, in this project's words. No quotation marks.", "Something else entirely."
    )
    body = re.sub(
        r"- TODO: one typed pointer[^\n]*\n", "- entry: A0002-late-claim · distinguishes\n", body
    )
    body = body.replace(
        "TODO: the rule by which the grounds support the assertion.", "It is a different claim."
    )
    body = body.replace("metric: TODO", "metric: nothing").replace("cohort: TODO", "cohort: none")
    body = body.replace("condition: TODO", "condition: as written")
    other.write_text(body, encoding="utf-8")
    project.git("add", "-A")
    project.git("commit", "-m", "main takes A0002 as well")
    project.git("checkout", "-q", "side")

    assert project.cl("renumber", "--onto", "main", "--write") == 0
    assert project.cl("validate") == 0, "the frozen region differs across the rewritten commits"
    assert not [r for r in _freshness_reports(project) if "has moved" in r.message]


def test_a_bare_number_another_entry_still_answers_to_is_left_alone(project):
    """Under an intra-branch double one id keeps the number and the other moves. A bare
    number in prose then means the entry that kept it, so rewriting it would point every
    such sentence at the entry that left — silently, since no checker reads a bare
    number."""
    (project.root / "docs" / "note-001.md").write_text(NOTE, encoding="utf-8")
    project.git("init")
    project.git("add", "-A")
    project.git("commit", "-m", "base")
    project.git("branch", "-M", "main")
    project.git("checkout", "-q", "-b", "side")
    entry(project, "A0009", "alpha-claim", "Observation Alpha")
    entry(project, "A0009", "beta-claim", "Observation Beta")
    note = project.root / "docs" / "note-001.md"
    note.write_text(
        note.read_text(encoding="utf-8").replace(
            "## Observation Base", "The base reading is recorded in A0009.\n\n## Observation Base"
        ),
        encoding="utf-8",
    )
    project.git("add", "-A")
    project.git("commit", "-m", "two entries under one number, and prose naming it")

    assert project.cl("renumber", "--onto", "main", "--write") == 0
    kept = sorted(p.stem for p in project.entries.glob("A0009-*.md"))
    assert len(kept) == 1, kept
    assert "recorded in A0009." in note.read_text(encoding="utf-8")


def test_a_merge_is_not_allowed_when_the_commit_walk_is_the_question_git_declined(collision):
    """The other half of the same rule. Round 1 named two paths on which git declines and
    only one was converted; this is the walk, and it has to refuse the merge too."""
    ghost = Path(collision.root) / ".git" / "refs" / "heads" / "ghost"
    ghost.write_text("0000000000000000000000000000000000000001\n", encoding="utf-8")
    assert collision.cl("renumber", "--onto", "main", "--on-merge") == 1


def test_a_declined_commit_walk_refuses_the_merge_too(collision):
    """Round 1 named two paths on which git declines and the first fix converted one.
    This is the walk: an object the history needs, removed from the store, so `rev-list`
    exits non-zero while the branch tips still resolve. Produced by removing an object
    rather than by patching git."""
    collision.git("checkout", "-q", "side")
    (collision.root / "docs" / "note-001.md").write_text(
        NOTE + "\nA later edit.\n", encoding="utf-8"
    )
    collision.git("commit", "-a", "-m", "a second commit on the branch")
    middle = head(collision, "rev-parse", "HEAD~1")
    loose = Path(collision.root) / ".git" / "objects" / middle[:2] / middle[2:]
    if not loose.exists():  # packed; the test needs a loose object to remove
        pytest.skip("the intermediate commit is packed, so there is no loose object to remove")
    loose.unlink()

    assert collision.cl("renumber", "--onto", "main", "--on-merge") == 1


def test_an_abbreviated_pin_is_recognised(collision):
    """A ground stated by reference may name the commit the way `git log --abbrev` prints
    it. Found by pattern-matching for forty hex characters, that pin is invisible and the
    rewrite drops the commit it rests on without a word; asked of git, it resolves."""
    pinned = head(collision, "rev-parse", "--short", "HEAD")
    assert len(pinned) < 40
    path = collision.entries / "A0002-beta-claim.md"
    path.write_text(
        re.sub(
            r'(lab: docs/note-001\.md § "Observation Beta" )=sha256:[0-9a-f]{64}',
            rf"\1@{pinned}",
            path.read_text(encoding="utf-8"),
            count=1,
        ),
        encoding="utf-8",
    )
    collision.git("commit", "-a", "-m", "a ground pinned at an abbreviated commit")

    ledger = open_ledger(root=collision.root)
    refused = renumber.refusals(ledger, renumber.plan(ledger, "main", "HEAD"))
    assert any("by reference" in r for r in refused), refused
    assert collision.cl("renumber", "--onto", "main", "--write") == 2


def test_a_repository_that_signs_its_commits_is_refused(collision):
    """`commit-tree` does not honour `commit.gpgsign` — measured, it writes an unsigned
    commit at exit 0 and says nothing — so a signing project would find every rewritten
    commit unsigned, with no second rewrite available to repair it."""
    collision.git("config", "commit.gpgsign", "true")
    ledger = open_ledger(root=collision.root)
    refused = renumber.refusals(ledger, renumber.plan(ledger, "main", "HEAD"))
    assert any("unsigned" in r for r in refused), refused
    assert collision.cl("renumber", "--onto", "main", "--write") == 2
    assert (collision.entries / "A0002-beta-claim.md").exists()


def test_force_rewrites_past_a_refusal_and_lands_what_it_said_it_would(collision):
    """`--force` is the one flag that disarms `refusals()`, and `renumber` is the only
    command in the package that rewrites commits and moves a ref. Every one of the
    refusals had a test; the branch past them had none.

    Signing is the refusal driven here because it is orthogonal to the rewrite: `commit`
    `-tree` writes unsigned commits whatever `commit.gpgsign` says, so the rewrite can
    proceed and be checked while the refusal is live. The conjunction is what is unheld —
    that a rewrite which goes ahead over a printed refusal still produces the ids it said
    it would, remaps parents, re-pins anchors, and leaves the ref and the checkout where
    the unforced path would have left them.

    The negative control is the assertion above it: the same command without `--force`
    exits 2 and leaves `A0002` where it was, so this is testing the flag and not the
    fixture.
    """
    collision.git("config", "commit.gpgsign", "true")
    ledger = open_ledger(root=collision.root)
    planned = renumber.plan(ledger, "main", "HEAD")
    refused = renumber.refusals(ledger, planned)
    assert any("unsigned" in r for r in refused), refused
    before = head(collision, "rev-parse", "side")

    assert collision.cl("renumber", "--onto", "main", "--write") == 2
    assert (collision.entries / "A0002-beta-claim.md").exists()
    assert head(collision, "rev-parse", "side") == before, "the refused run moved the ref"

    assert collision.cl("renumber", "--onto", "main", "--write", "--force") == 0

    # The ids it said it would: the plan is read before the rewrite, and what landed is
    # compared against it rather than against a number written here.
    assert planned.mapping == {"A0002-beta-claim": "A0003-beta-claim"}, planned.mapping
    assert (collision.entries / "A0003-beta-claim.md").exists()
    assert not (collision.entries / "A0002-beta-claim.md").exists()

    # The ref moved and the checkout came with it.
    after = head(collision, "rev-parse", "side")
    assert after != before
    assert head(collision, "rev-parse", "HEAD") == after
    assert head(collision, "status", "--porcelain") == ""

    # Parents remapped rather than grafted: the rewritten commit sits on the base the plan
    # named, and the commits it replaced are on no ref.
    assert head(collision, "rev-parse", f"{after}^") == planned.base
    assert head(collision, "for-each-ref", "--format=%(refname)", "--contains", before) == ""

    # The citation moved with the id and the anchor was re-pinned, which is what makes the
    # forced rewrite a rewrite and not a rename.
    note = (collision.root / "docs" / "note-001.md").read_text(encoding="utf-8")
    assert "(A0003-beta-claim, cites-as-live)" in note and "A0002-beta-claim" not in note
    assert collision.cl("check") == 0


def test_force_does_not_reach_the_refusals_that_protect_uncommitted_work(collision):
    """`--force` disarms `refusals()` and nothing else, and the difference is the whole
    reason it is safe to have.

    `refusals()` holds judgements the tool cannot always make correctly — a by-reference
    pin it could not recognise is named in `renumber.py` as a commit the rewrite drops in
    silence — so an operator who has checked by hand needs a way past. The three raised
    after it are not judgements: a dirty tree and a branch another checkout holds are ways
    to lose work that was never committed, and a detached HEAD is a rewrite with no ref to
    land on. Nothing is gained by letting a flag through those, so nothing does.

    `docs/OPERATING.md` lists all six in one sentence and then says to check what the
    command reports before reaching for `--force`, which reads as though the flag covered
    them all. It says which three it covers now, and this is what holds that.
    """
    collision.git("config", "commit.gpgsign", "true")  # a refusal `--force` does cover
    (collision.root / "docs" / "note-001.md").write_text("uncommitted\n", encoding="utf-8")

    assert collision.cl("renumber", "--onto", "main", "--write", "--force") == 2
    assert (collision.entries / "A0002-beta-claim.md").exists(), "the rewrite went ahead"
    assert (collision.root / "docs" / "note-001.md").read_text(encoding="utf-8") == (
        "uncommitted\n"
    ), "the uncommitted edit `--force` was refused over did not survive"
