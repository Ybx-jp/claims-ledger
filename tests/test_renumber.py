"""Reconciling two branches that minted one number, by rewriting the one that has not
merged.

The scenario each test builds is the one that actually happens: two branches cut from one
base, each minting the same number for a different claim, each clean on its own. Merged as
they stand they produce two entries carrying one number — and with different slugs git
merges them without a conflict and every checker reads the result at exit 0.
"""

import re

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


def entry(project, ident, slug, section, pin="=?"):
    """An entry resting on one section of the note, cited from inside that section.

    Inside it, because that is where this project's own citations sit and because it is
    what makes a renumber move the digest the entry is anchored to — the case the
    re-pinning has to get right.
    """
    assert project.cl("new", slug, "--id", ident) == 0
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

    note = project.root / "docs" / "note-001.md"
    body = note.read_text(encoding="utf-8")
    line = SECTIONS[section]
    note.write_text(
        body.replace(line, f"{line}\nStated as a claim here ({ident}-{slug}, cites-as-live)."),
        encoding="utf-8",
    )
    assert project.cl("sha", "--write", str(path)) == 0
    return path


@pytest.fixture
def collision(project):
    """Two branches off one base, each holding A0002 for a different claim."""
    (project.root / "docs" / "note-001.md").write_text(NOTE, encoding="utf-8")
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
    assert collision.cl("renumber", "--onto", "main") == 0
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
        path.read_text(encoding="utf-8").replace(
            'lab: docs/note-001.md § "Observation Beta" =sha256:',
            f'lab: docs/note-001.md § "Observation Beta" @{pinned} =sha256:',
            1,
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
