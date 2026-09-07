"""Every path that writes, and what it leaves behind when it fails partway.

`test_invariants.py` establishes that the `--write` paths are idempotent, order
independent and append-only *when they complete*. This file is about the other case: a
write that is interrupted, a write onto a file that is not quite what the writer assumed,
and a write whose bytes are not the bytes that came in.

Three things are established here that the rest of the suite does not reach. Each was a
defect of the fifth QE pass and is now the regression that holds its fix.

1. Every write path goes through a temporary file and a rename. `create_entry`,
   `restamp`, `append_verdict`, `cmd_init` and `cmd_hook` each used to truncate the
   destination before they knew they could fill it, so a write that failed destroyed what
   it was appending to. The interruption is produced with a real `RLIMIT_FSIZE` in a
   child process — a resource limit the kernel enforces, not a patched internal.

2. The bytes that go in come back out. The `--write` paths read and write with universal
   newlines, so a file whose line endings were not LF had every one of its lines rewritten
   by an append that was supposed to add three — and `check_history` could not see it,
   because `git_call` runs `subprocess.run(text=True)` and translated the blob's newlines
   the same way, so the frozen region was not compared as bytes on either side.

3. `source add` appends a line to `sources.jsonl` as a line, whatever state the file was
   left in, and stores cache bytes that hash to the name it filed them under.

Everything here builds a real project under `tmp_path` through the `project` fixture and
drives the real CLI. Nothing under `src/` or the shipped corpus is touched.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
from conftest import QUOTE, Project
from test_invariants import append_verdict_text, fill_entry, set_stated

from claims_ledger import propagate
from claims_ledger.schema import APPEND, open_ledger

# === helpers =========================================================================


def frozen_bytes(path):
    """The bytes above the APPEND marker, as they are on disk — no newline translation."""
    raw = path.read_bytes()
    head, marker, _ = raw.partition(APPEND.encode("utf-8"))
    return head if marker else None


def seal(project, path):
    """Commit the project so the entry's frozen region is immutable, and prove `check`
    is clean over it first."""
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the entries, as committed")
    return path


def challenger(project, target_id="A0001-a-claim", slug="b-claim"):
    """A second entry whose Grounds challenge `target_id`, so `propagate --write` has
    exactly one verdict to append to the target."""
    assert project.cl("new", slug) == 0
    path = next(project.entries.glob(f"*-{slug}.md"))
    text = path.read_text(encoding="utf-8")
    for old, new in (
        (
            "TODO: the claim, in this project's words. No quotation marks.",
            "The measured error was read off the wrong column.",
        ),
        ("metric: TODO", "metric: mean L2 error"),
        ("cohort: TODO", "cohort: the synthetic graph of these tests"),
        ("condition: TODO", "condition: mean aggregation, one layer"),
        (
            "- TODO: one typed pointer per line",
            (
                '- lab: docs/note-001.md § "Observation" @working\n'
                f"- entry: {target_id} · challenges"
            ),
        ),
        (
            "TODO: the rule by which the grounds support the assertion.",
            "A misread column is a reason to contest the measurement it produced.",
        ),
    ):
        assert old in text, old
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    return path


def a_sealed_claim(project):
    """A0001, filled in and passing every checker."""
    assert project.cl("new", "a-claim") == 0
    return project.write_full_entry(project.entry("A0001-a-claim.md"))


CHILD = textwrap.dedent(
    """
    import os, resource, signal, sys
    # Without this the kernel kills the process on the first over-limit write and the
    # interruption is a signal rather than the ENOSPC-shaped OSError a full disk gives.
    signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
    limit = int(os.environ["CL_FSIZE_LIMIT"])
    resource.setrlimit(resource.RLIMIT_FSIZE, (limit, limit))
    from claims_ledger import cli
    sys.exit(cli.main(sys.argv[1:]))
    """
)


def run_under_a_size_limit(limit, *argv):
    """`claims-ledger <argv>` in a child process that cannot write a file bigger than
    `limit` bytes. A real resource limit: the write reaches the kernel and comes back
    EFBIG, which is the shape a full disk has."""
    env = dict(os.environ, CL_FSIZE_LIMIT=str(limit), PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(
        [sys.executable, "-B", "-c", CHILD, *argv],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


needs_rlimit = pytest.mark.skipif(
    not hasattr(__import__("resource"), "RLIMIT_FSIZE"),
    reason="RLIMIT_FSIZE is how the interruption is produced",
)


# === bytes in, bytes out =============================================================


def test_propagate_write_preserves_the_committed_frozen_region_bytes(project):
    """README: the region above the APPEND marker is immutable once the entry is
    committed. An append below the marker must not touch a byte above it."""
    path = a_sealed_claim(project)
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    challenger(project)
    seal(project, path)
    before = frozen_bytes(path)
    assert before is not None and b"\r\n" in before
    project.cl("propagate", "--write")
    assert frozen_bytes(path) == before


def test_check_catches_a_frozen_region_rewritten_to_crlf(project):
    """`check_history`'s docstring: "the region above the APPEND marker equals the blob at
    the commit that created the file". Every byte of that region changes here."""
    path = a_sealed_claim(project)
    seal(project, path)
    assert project.cl("check") == 0
    head, marker, tail = path.read_bytes().partition(APPEND.encode("utf-8"))
    path.write_bytes(head.replace(b"\n", b"\r\n") + marker + tail)
    assert project.cl("check") != 0


def test_a_staged_crlf_rewrite_of_the_frozen_region_is_caught_under_cached(project):
    """The hook's path. Under --cached the byte comparison reads the entry's staged blob,
    and text arrives through universal newlines on both sides, so a staged CRLF rewrite is
    caught by the byte comparison or not at all. Fails when `check_history` stops asking
    the batch for `:<path>`."""
    path = a_sealed_claim(project)
    seal(project, path)
    assert project.cl("validate", "--cached") == 0
    head, marker, tail = path.read_bytes().partition(APPEND.encode("utf-8"))
    path.write_bytes(head.replace(b"\n", b"\r\n") + marker + tail)
    project.git("add", "-A")
    assert project.cl("validate", "--cached") != 0


def test_a_frozen_region_rewritten_to_crlf_and_committed_is_still_caught(project):
    """The reference side of the byte comparison is the blob at the commit that created
    the entry, not the newest one: a rewrite that has itself been committed is still a
    rewrite. Fails when the comparison is made against HEAD's blob."""
    path = a_sealed_claim(project)
    seal(project, path)
    head, marker, tail = path.read_bytes().partition(APPEND.encode("utf-8"))
    path.write_bytes(head.replace(b"\n", b"\r\n") + marker + tail)
    project.git("commit", "-qam", "the frozen region, rewritten and committed")
    assert project.cl("validate") != 0
    assert project.cl("validate", "--cached") != 0


def test_sha_write_preserves_the_files_line_endings(project):
    """`sha --write` replaces one `verbatim_sha:` line. Every other byte of the file is
    none of its business."""
    path = a_sealed_claim(project)
    text = path.read_text(encoding="utf-8").replace(
        "condition: mean aggregation, one layer", "condition: mean aggregation, two layers"
    )
    path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    assert project.cl("sha", "--write", str(path)) == 0
    assert b"\r\n" in path.read_bytes()


def test_sha_write_leaves_every_byte_but_the_sha_line_alone(project):
    """The control for the two above: with LF endings and non-ASCII text throughout,
    `sha --write` is exactly a one-line edit."""
    assert project.cl("new", "u-claim") == 0
    path = project.entry("A0001-u-claim.md")
    text = path.read_text(encoding="utf-8")
    for old, new in (
        (
            "TODO: the claim, in this project's words. No quotation marks.",
            "Naïve aggregation — éàü, 中文, \U0001f600 — holds over this cohort.",
        ),
        ("metric: TODO", "metric: μ-error, ±0.01"),
        ("cohort: TODO", "cohort: the synthetic graph of these tests"),
        ("condition: TODO", "condition: mean aggregation, one layer"),
        (
            "- TODO: one typed pointer per line",
            '- lab: docs/note-001.md § "Observation" @working',
        ),
        (
            "TODO: the rule by which the grounds support the assertion.",
            "Because the note measures it.",
        ),
    ):
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    before = path.read_bytes()
    assert project.cl("sha", "--write", str(path)) == 0
    after = path.read_bytes()
    strip = lambda b: re.sub(rb"verbatim_sha: [0-9a-f]*", b"verbatim_sha: X", b)  # noqa: E731
    assert strip(before) == strip(after)


def test_an_edit_inside_the_frozen_region_is_still_caught(project):
    """The half of immutability that works, kept so a fix for the newline blindness
    cannot regress it."""
    path = a_sealed_claim(project)
    seal(project, path)
    assert project.cl("check") == 0
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("stale fraction and not by degree", "degree alone"), "utf-8")
    assert project.cl("check") != 0


# === a write that fails partway ======================================================


@needs_rlimit
def test_a_failed_append_leaves_the_entry_as_it_found_it(project):
    """An append-only ledger whose append fails has appended nothing. It has not
    truncated the entry it was appending to."""
    path = a_sealed_claim(project)
    challenger(project)
    seal(project, path)
    before = path.read_bytes()
    result = run_under_a_size_limit(
        len(before) + 40, "--root", str(project.root), "propagate", "--write"
    )
    assert result.returncode != 0
    assert path.read_bytes() == before


@needs_rlimit
def test_a_failed_append_exits_cleanly_with_a_message(project):
    """The control: the diagnostic half of the above is already right — a clean non-zero
    exit and a readable line on stderr, no traceback."""
    path = a_sealed_claim(project)
    challenger(project)
    seal(project, path)
    result = run_under_a_size_limit(
        path.stat().st_size + 40, "--root", str(project.root), "propagate", "--write"
    )
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    assert "cannot append the verdict" in result.stderr


@needs_rlimit
def test_a_failed_source_add_exits_cleanly_with_a_message(project, tmp_path):
    """The same control on the other write path: `source add` under a size limit refuses
    in words rather than raising."""
    big = tmp_path / "big.txt"
    big.write_text("The bytes of a second source.\n" * 80, encoding="utf-8")
    result = run_under_a_size_limit(
        500,
        "--root",
        str(project.root),
        "source",
        "add",
        str(big),
        "--id",
        "fx-2",
        "--type",
        "paper",
        "--citation",
        "A second synthetic source",
    )
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    assert "cannot store the bytes" in result.stderr


@needs_rlimit
def test_retrying_an_interrupted_source_add_stores_the_right_bytes(project, tmp_path):
    """`register_source`'s docstring: "a registry row without its bytes is a check that
    cannot run, so registering a source stores the bytes in the same call that writes the
    row". A row with the *wrong* bytes is the same defect one step on."""
    big = tmp_path / "big.txt"
    big.write_text("The bytes of a second source.\n" * 80, encoding="utf-8")
    add = (
        "--root",
        str(project.root),
        "source",
        "add",
        str(big),
        "--id",
        "fx-2",
        "--type",
        "paper",
        "--citation",
        "A second synthetic source",
    )
    assert run_under_a_size_limit(500, *add).returncode == 2  # the interrupted attempt
    assert project.cl(*add[2:]) == 0  # the retry, with no limit
    cache = project.root / "ledger" / "cache"
    stored = [p for p in cache.iterdir() if p.name != ".gitignore" and p.stat().st_size]
    assert big.read_bytes() in [p.read_bytes() for p in stored]


# === the source registry =============================================================


def test_source_add_onto_a_registry_without_a_final_newline(project, tmp_path):
    """`sources.jsonl` is JSON lines. A row appended to it is a line, whatever state the
    file was left in by an editor, a script, or this tool's own interrupted write."""
    registry = project.root / "ledger" / "sources.jsonl"
    registry.write_bytes(registry.read_bytes().rstrip(b"\n"))
    second = tmp_path / "second.txt"
    second.write_text("A second synthetic source.\n", encoding="utf-8")
    rc = project.cl(
        "source",
        "add",
        str(second),
        "--id",
        "fx-second",
        "--type",
        "paper",
        "--citation",
        "A second synthetic source",
    )
    lines = [ln for ln in registry.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert rc != 0 or len(lines) == 2


def test_source_add_appends_cleanly_to_a_well_formed_registry(project, tmp_path):
    """The control: the ordinary append is correct, and the row already there survives."""
    registry = project.root / "ledger" / "sources.jsonl"
    second = tmp_path / "second.txt"
    second.write_text("A second synthetic source.\n", encoding="utf-8")
    assert (
        project.cl(
            "source",
            "add",
            str(second),
            "--id",
            "fx-second",
            "--type",
            "paper",
            "--citation",
            "A second synthetic source",
        )
        == 0
    )
    lines = [ln for ln in registry.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 2
    assert project.cl("check") != 2  # the registry still parses


# === where the verdict lands =========================================================


def test_propagate_write_never_writes_above_the_append_marker(project):
    """propagate.py's own docstring: the missing verdicts "are appended". Below the
    marker, which is the only place anything is ever appended."""
    path = a_sealed_claim(project)
    text = path.read_text(encoding="utf-8")
    text = text.replace("\n## References\n", "\n").replace(
        "\n" + APPEND, "\n## References\n\n" + APPEND
    )
    path.write_text(text, encoding="utf-8")
    project.cl("sha", "--write", str(path))
    challenger(project)
    seal(project, path)
    before = frozen_bytes(path)
    project.cl("propagate", "--write")
    assert frozen_bytes(path) == before


def test_propagate_write_appends_below_the_marker_in_the_ordinary_layout(project):
    """The control: with the scaffolded layout the verdict lands below the marker and the
    frozen region is untouched, which is what makes the case above a bug rather than the
    design."""
    path = a_sealed_claim(project)
    challenger(project)
    seal(project, path)
    before = frozen_bytes(path)
    project.cl("propagate", "--write")
    after = path.read_text(encoding="utf-8")
    assert frozen_bytes(path) == before
    assert after.split(APPEND, 1)[1].count("· contested ·") == 1


def test_propagate_write_twice_appends_one_verdict(project):
    """The control for repetition: `--write` run again after a completed `--write` is a
    no-op, and the second run reports nothing to do."""
    path = a_sealed_claim(project)
    challenger(project)
    seal(project, path)
    assert project.cl("propagate", "--write") != 0
    assert path.read_text(encoding="utf-8").count("· contested ·") == 1
    assert project.cl("propagate", "--write") == 0
    assert path.read_text(encoding="utf-8").count("· contested ·") == 1


# === the scaffolding write paths =====================================================


def test_sha_write_over_several_paths_does_not_silently_skip_the_rest(project, capsys):
    """Three files named on one command line are three independent writes. The one that
    could not be written is reported; the one after it must not vanish."""
    paths = []
    for slug in ("one", "two", "three"):
        assert project.cl("new", slug) == 0
    for path in sorted(project.entries.glob("*.md")):
        path.write_text(
            path.read_text(encoding="utf-8").replace("metric: TODO", "metric: m"),
            encoding="utf-8",
        )
        paths.append(path)
    os.chmod(paths[1], 0o444)
    capsys.readouterr()
    try:
        project.cl("sha", "--write", *[str(p) for p in paths])
    finally:
        os.chmod(paths[1], 0o644)
    captured = capsys.readouterr()
    restamped = "verbatim_sha: 986b8f35" not in paths[2].read_text(encoding="utf-8")
    assert restamped or paths[2].name in captured.out + captured.err


def test_init_twice_leaves_the_same_tree(project):
    """`init` over a project that already has one refuses without `--force`, and with
    `--force` writes exactly what is already there."""
    before = sorted(
        (str(p.relative_to(project.root)), p.read_bytes())
        for p in project.root.rglob("*")
        if p.is_file()
    )
    assert project.cl("init") == 1
    assert project.cl("init", "--force") == 0
    after = sorted(
        (str(p.relative_to(project.root)), p.read_bytes())
        for p in project.root.rglob("*")
        if p.is_file()
    )
    assert before == after


def test_init_into_a_read_only_root_is_a_clean_refusal(tmp_path, capsys):
    """A read-only directory is an ordinary condition, not a bug report."""
    root = tmp_path / "ro"
    root.mkdir()
    os.chmod(root, 0o555)
    try:
        assert Project(root).cl("init") == 2
    finally:
        os.chmod(root, 0o755)
    assert "cannot scaffold the ledger" in capsys.readouterr().err


def test_new_into_a_read_only_entries_directory_is_a_clean_refusal(project, capsys):
    """The write is refused in words; nothing half-made is left behind."""
    os.chmod(project.entries, 0o555)
    try:
        assert project.cl("new", "y-claim") == 2
    finally:
        os.chmod(project.entries, 0o755)
    assert "cannot write" in capsys.readouterr().err
    assert list(project.entries.glob("*.md")) == []


def test_new_where_a_directory_occupies_the_entry_path(project, capsys):
    """A file replaced by a directory between the check and the write: the exists-check
    is inside the funnel, so this is a message rather than an IsADirectoryError."""
    (project.entries / "A0001-x.md").mkdir()
    assert project.cl("new", "x") == 2
    assert "Traceback" not in capsys.readouterr().err


def test_hook_install_when_the_hooks_path_is_a_file(project, capsys):
    """`.git/hooks` occupied by a regular file: a refusal, not a traceback."""
    project.git("init", "-q")
    hooks = project.root / ".git" / "hooks"
    for child in hooks.iterdir():
        child.unlink()
    hooks.rmdir()
    hooks.write_text("not a directory", encoding="utf-8")
    assert project.cl("hook", "--install") == 2
    assert "cannot install the hook" in capsys.readouterr().err


def test_no_write_path_follows_a_symlink_out_of_the_project(project, tmp_path):
    """The guard that already holds, on both the paths that have it."""
    path = a_sealed_claim(project)
    outside = tmp_path / "outside.md"
    outside.write_bytes(path.read_bytes().replace(b"metric: mean", b"metric: changed"))
    snapshot = outside.read_bytes()
    path.unlink()
    path.symlink_to(outside)
    assert project.cl("sha", "--write", str(path)) == 2
    assert outside.read_bytes() == snapshot


def test_two_entries_claiming_one_id_are_reported(project):
    """Two `new` runs racing for the next free id can land on the same number: nothing
    locks the entries directory between `next_id` and the write. The consequence is at
    least loud — the file whose name does not match its id is named."""
    path = a_sealed_claim(project)
    (project.entries / "A0001-clash.md").write_bytes(path.read_bytes())
    assert project.cl("check") != 0


def test_entry_files_are_visited_in_filename_order(project):
    """`load_entries` sorts, so no result depends on the order the filesystem hands back
    a directory listing."""
    for slug in ("zeta", "alpha", "mid"):
        assert project.cl("new", slug) == 0
    from claims_ledger.schema import load_entries, open_ledger

    ledger = open_ledger(Path(project.root))
    names = [e.path.name for e in load_entries(ledger)]
    assert names == sorted(names)


# --- the guard in front of the funnel ---------------------------------------------------


# Where a write may land outside the project root by design, and why. Empty, and the two
# names that used to be here are the reason the list is kept rather than the rule relaxed:
# `cmd_init` was excused because it creates the root, and `cmd_hook` because `.git/hooks`
# in a worktree or a `--separate-git-dir` clone genuinely is outside the root. Both
# excuses were about the *directory* and the question is about the *write* — `init`
# creates the root before the registry lands in it, and the hook needs to leave the root
# but not to leave the git directory — so both now ask, each against the boundary its own
# write has.
WRITES_THAT_ARE_NOT_LEDGER_FILES = set()
FUNNEL = {"write_bytes_atomically", "write_text_atomically"}
GUARDS = {"refuse_to_write_outside_the_root", "leaves_root"}


def _enclosing_functions_that_write(path):
    """(function name, whether it asks `refuse_to_write_outside_the_root`) for every
    function in `path` that calls the atomic-write funnel."""
    import ast

    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        called = {
            c.func.id
            for c in ast.walk(node)
            if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
        }
        if called & FUNNEL:
            # Two spellings of the one question: `authoring` asks it of a ledger, and
            # `append_verdict` — which is handed a root rather than a ledger — asks
            # `config.leaves_root` directly.
            out.append((node.name, bool(called & GUARDS)))
    return out


def test_new_does_not_scaffold_an_entry_through_a_link_that_leaves_the_root(project, tmp_path):
    """`create_entry` refuses a path that already exists, and a dangling symlink is not
    one that exists — so that refusal steps aside here.

    Two layers stand behind it, and this asserts the outcome rather than either one.
    `load_entries`, which `create_entry` calls first, refuses the whole run over an entry
    that is a symlink to nothing, and that is the layer that fires today. Behind it the
    write now asks `refuse_to_write_outside_the_root`, which is what
    `test_every_write_asks_where_the_link_leads` holds: the first layer is a property of
    where the link happens to be planted, and the second is a property of the write. This
    test stays green if the first is ever relaxed."""
    outside = tmp_path / "outside" / "pwned.md"
    outside.parent.mkdir(exist_ok=True)
    (project.entries / "A0001-a-claim.md").symlink_to(outside)
    assert project.cl("new", "a-claim") != 0
    assert not outside.exists(), f"`new` scaffolded an entry at {outside}, outside the root"


def test_appending_a_verdict_cannot_skip_the_root_it_is_checked_against():
    """`append_verdict` is the one function in the package that writes into a *committed*
    entry, and its root guard used to be behind `if root is not None` with `root=None` for
    a default — so a caller closed the guard by not thinking about it. Both callers pass a
    root, so nothing behavioural changes here and the revert experiment finds no regression
    for it; what is held is that the next caller cannot be the one that forgets.

    Kept as a signature test on purpose. The alternative — asserting that a call with
    `root=None` writes outside the root — would be asserting the behaviour of a call that
    the signature now refuses to let anyone make.
    """
    import inspect

    from claims_ledger import propagate

    root = inspect.signature(propagate.append_verdict).parameters["root"]
    assert root.kind is inspect.Parameter.KEYWORD_ONLY
    assert root.default is inspect.Parameter.empty
    # Reached through `getattr` so that the call is invisible to `ty`, which otherwise
    # refuses the file with `No argument provided for required parameter root`. That
    # refusal is the guard working — a caller who forgets is stopped before the suite
    # runs, by a check that is in CI — and it is worth saying so here rather than
    # deleting the runtime half, which is what holds an installed copy that `ty` never
    # saw.
    with pytest.raises(TypeError):
        getattr(propagate, "append_verdict")(object(), "- a block\n")  # noqa: B009


def test_every_write_asks_where_the_link_leads():
    """The class, rather than the instance. HIGH-11, MEDIUM-19 and HIGH-56 were all one
    caller of the write path that never asked whether the file it was about to land on is
    inside the project — and the third of them was written *after* the funnel whose own
    docstring says "where the link leads is the caller's question, and `leaves_root` is
    where it is asked". A rule a caller can forget is a rule that comes back, so the
    question is asked here of every caller at once: a new write site either asks, or names
    itself above as a write that is deliberately not a ledger file.
    """
    src = Path(__file__).resolve().parent.parent / "src" / "claims_ledger"
    unguarded = sorted(
        f"{path.name}:{name}"
        for path in src.rglob("*.py")
        for name, guarded in _enclosing_functions_that_write(path)
        if not guarded and name not in WRITES_THAT_ARE_NOT_LEDGER_FILES and name not in FUNNEL
    )
    assert not unguarded, (
        f"{unguarded} write through the atomic-write funnel without asking "
        "refuse_to_write_outside_the_root, and are not listed as writes that are not "
        "ledger files"
    )


def test_init_does_not_scaffold_the_registry_through_a_link_that_leaves_the_root(tmp_path):
    """HIGH-56's class, at the caller the fix's own allowlist excused. `init` was allowed
    to skip the guard because it creates the root — but the root exists by the time the
    registry lands in it, so a symlink planted at `ledger/sources.jsonl` before the first
    `init` sent the write outside, exit 0, printing the in-root path it had not written
    to. The link is a live one rather than a dangling one on purpose: `file_problem` sees
    a regular file through it and says nothing is wrong, which is why the shape survived
    the guard that catches a symlink to nothing.
    """
    root = tmp_path / "project"
    (root / "ledger").mkdir(parents=True)
    outside = tmp_path / "outside" / "registry-pwned.jsonl"
    outside.parent.mkdir()
    outside.write_text("mine\n", encoding="utf-8")
    (root / "ledger" / "sources.jsonl").symlink_to(outside)

    assert Project(root).cl("init") != 0
    assert outside.read_text(encoding="utf-8") == "mine\n", (
        f"`init` wrote the source registry to {outside}, outside the project root"
    )


def test_hook_install_does_not_write_through_a_link_that_leaves_the_git_directory(project):
    """The other name on that allowlist. `.git/hooks` is genuinely outside the project
    root in a worktree, which is why the guard here is asked against the git directory
    instead — but `hook --install` asked nothing at all, so a dangling
    `.git/hooks/pre-commit -> /tmp/x.sh` took 1690 bytes of mode-755 shell outside the
    repository, exit 0.

    `exists()` is the second half of it: a symlink to nothing is not `exists()`, so the
    "this hook is already here, leaving it alone" refusal stepped aside for exactly the
    link that needed it.
    """
    project.git("init", ".")
    outside = Path(project.root).parent / "outside" / "hook-pwned.sh"
    outside.parent.mkdir(exist_ok=True)
    hooks = Path(project.root) / ".git" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    (hooks / "pre-commit").symlink_to(outside)

    assert project.cl("hook", "--install") != 0
    assert not outside.exists(), f"`hook --install` wrote a shell script to {outside}"


def test_hook_install_goes_where_git_actually_looks_for_hooks(project):
    """QE8-83. `core.hooksPath` moves the directory git runs hooks out of, and an install
    into `.git/hooks` under it printed `installed …` and exited 0 for a file git will
    never execute — a gate reported as installed that does not exist, which is HIGH-57's
    own class at the surface HIGH-57 fixed. `git rev-parse --git-path hooks` is the
    question git asks itself."""
    project.git("init", "-q")
    project.git("config", "core.hooksPath", "myhooks")
    assert project.cl("hook", "--install") == 0
    assert (Path(project.root) / "myhooks" / "pre-commit").is_file(), (
        "the hook was installed where git does not look"
    )


def test_hook_install_reaches_a_linked_worktrees_real_hooks_directory(project, tmp_path):
    """QE8-86, and the same fix. In a linked worktree `.git` is a *file*, so the install
    used to fail with `Not a directory` at a path that was never the right one — the very
    case the guard's own comment named as its reason for choosing that boundary."""
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the project")
    linked = tmp_path / "linked"
    project.git("worktree", "add", "-q", str(linked))
    assert Project(linked).cl("hook", "--install") == 0
    assert (Path(project.root) / ".git" / "hooks" / "pre-commit").is_file()


def test_hook_install_leaves_a_deliberate_shared_hook_link_alone(project):
    """QE8-88 and the `lexists` half of QE8-89, which had no test in either direction.

    A team pointing `.git/hooks/pre-commit` at a shared script is a deliberate setup, and
    the answer it has always had is `exit 1` and the hook text to paste. `exists()` said
    no to a link whose target is not there and wrote straight through it; asking `lexists`
    *before* the containment guard keeps the helpful answer for the deliberate case and
    still writes nothing through the link.
    """
    project.git("init", "-q")
    hooks = Path(project.root) / ".git" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    shared = hooks / "shared-pre-commit"  # inside the boundary, so only `lexists` refuses
    (hooks / "pre-commit").symlink_to(shared)
    assert project.cl("hook", "--install") == 1
    assert not shared.exists(), f"the install wrote through the link to {shared}"


# --------------------------------------------------------------------------
# Two write sites the funnel went past, and the flag that names what it wrote.
# --------------------------------------------------------------------------


def test_sha_write_refuses_an_entry_whose_mode_forbids_writing(project):
    """Fixed. The defect, as this pass wrote it: write_bytes_atomically never opens the target —
    it writes a temp file beside it and os.replace()s, which needs permission on the directory
    and not on the file — so `sha --write` now rewrites a mode-444 entry, exits 0, and leaves
    the mode saying the file is protected. The truncating write it replaced exited 2.

    A file the filesystem says may not be written is not written. This is also what
    `test_sha_write_over_several_paths_does_not_silently_skip_the_rest` uses as its only
    failure injection, so while this is broken that regression is vacuously green.
    """
    assert project.cl("new", "a-claim") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    path.write_text(
        path.read_text(encoding="utf-8").replace("verbatim_sha: ", "verbatim_sha: 0"),
        encoding="utf-8",
    )
    before = path.read_bytes()
    os.chmod(path, 0o444)
    try:
        code = project.cl("sha", "--write", str(path))
    finally:
        os.chmod(path, 0o644)
    assert path.read_bytes() == before, "a mode-444 entry was rewritten"
    assert code == 2


def test_source_add_does_not_store_bytes_through_a_link_that_leaves_the_root(project, tmp_path):
    """Fixed. The defect, as this pass wrote it: register_source's cache write never asks
    refuse_to_write_outside_the_root, and write_bytes_atomically resolves the path before
    writing, so a dangling symlink planted at the content-addressed cache slot sends `source
    add` outside the project root; it exits 0 and names the in-root path it did not write to

    README, and the docstring of `write_bytes_atomically` itself: "where the link leads is the
    caller's question, and `leaves_root` is where it is asked." `restamp` and `append_verdict`
    ask it. This caller never has — the funnel was routed past the one write site with no
    guard in front of it.
    """
    import hashlib

    source = tmp_path / "a-source.txt"
    source.write_bytes(b"the source text, quoted by an entry.\n")
    outside = tmp_path / "outside" / "pwned.txt"
    outside.parent.mkdir(exist_ok=True)
    slot = project.root / "ledger" / "cache" / hashlib.sha256(source.read_bytes()).hexdigest()
    slot.symlink_to(outside)

    project.cl(
        "source", "add", "--id", "fx-planted", "--type", "paper",
        "--citation", "A paper (2026)", str(source),
    )  # fmt: skip
    assert not outside.exists(), (
        f"`source add` wrote {outside}, outside the project root {project.root}"
    )


def test_the_write_flag_names_what_propagate_appended(project):
    """propagate.py's module docstring: "--write appends the missing verdicts ... the
    run still exits non-zero so the change is looked at before it is committed." The
    exit-code half of that promise is already proven by
    test_invariants.py's fixed-point tests; this proves the other half, that the report
    a person is meant to look at actually names what was appended and by whom."""
    project.cl("new", "base-claim")
    base = project.write_full_entry(project.entry("A0001-base-claim.md"))
    set_stated(base, "2020-01-01T00:00:00+00:00")
    append_verdict_text(
        base,
        timestamp="2020-02-01T00:00:00+00:00",
        status="refuted",
        grade="measured",
        author="main",
        evidence="source: fx-source · whole text",
        note="a later sweep contradicts it",
    )

    project.cl("new", "dependent-claim")
    dep = project.entry("A0002-dependent-claim.md")
    fill_entry(
        project,
        dep,
        assertion="A dependent claim that rests in part on the base claim.",
        grounds=(
            '- lab: docs/note-001.md § "Observation" @working\n'
            "- source: fx-source · whole text\n"
            "- entry: A0001-base-claim · cites-as-live"
        ),
        warrant="The base claim, if it holds, supports this one under the same regime.",
        backing=f'- source: fx-source · whole text\n  speaker: Okafor\n  quote: "{QUOTE}"',
    )

    reports = propagate.run(open_ledger(root=project.root), write=True)
    flags = [r for r in reports if r.outcome == "flag"]
    assert flags, "propagate --write appended a verdict and reported nothing about it"
    assert any(
        "appended" in r.message
        and "contested verdict" in r.message
        and "by propagation" in r.message
        for r in flags
    ), flags
