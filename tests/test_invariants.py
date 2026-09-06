"""Invariant and metamorphic properties the unit tests and the red-team corpus do not,
by themselves, check: idempotency of every write path, independence from orders the
schema does not fix, normalization invariance, the corpus as a metamorphic base,
append-only monotonicity, and cross-checker consistency.

Every property below is grounded in a promise from README.md or docs/SCHEMA.md, cited
in the test's docstring. Where a property genuinely fails, the test is kept and marked
`xfail(strict=True, reason="BUG: ...")` rather than weakened to match the bug.

This file only reads from and writes into tmp_path-based projects (via the `project`
fixture and `Project` helper from conftest.py) and copies of the shipped corpus seeds;
nothing under src/ or the real corpus/ is ever modified.
"""

from __future__ import annotations

import shutil
import unicodedata
from pathlib import Path
from types import SimpleNamespace

import pytest
from conftest import LAB_NOTE, QUOTE, SOURCE_TEXT, Project

from claims_ledger import authoring, cli, propagate, references, resolve, validate
from claims_ledger.corpus import run as corpus_run
from claims_ledger.schema import (
    Verdict,
    derive_status,
    exit_code,
    fingerprint,
    load_entries,
    open_ledger,
)

CORPUS = corpus_run.CORPUS
ALL_SEEDS = sorted(p for p in (CORPUS / "seeds").iterdir() if p.is_dir())
HISTORY_SEEDS = [s for s in ALL_SEEDS if (s / "commits").is_dir()]
FLAT_SEEDS = [s for s in ALL_SEEDS if s not in HISTORY_SEEDS]


# === shared helpers ==================================================================


def fill_entry(
    p,
    path,
    *,
    assertion,
    grounds,
    warrant,
    backing,
    metric="a metric",
    cohort="a cohort",
    condition="a condition",
):
    """The general form of conftest's write_full_entry: turn a scaffolded entry into one
    that resolves, with the caller's own Grounds/Warrant/Backing text. Needed here to
    build entries that cite each other, or that carry exactly one deliberate defect."""
    text = path.read_text(encoding="utf-8")
    for old, new in (
        (authoring.PLACEHOLDER_ASSERTION, assertion),
        ("metric: TODO", f"metric: {metric}"),
        ("cohort: TODO", f"cohort: {cohort}"),
        ("condition: TODO", f"condition: {condition}"),
        (authoring.PLACEHOLDER_GROUNDS, grounds),
        (authoring.PLACEHOLDER_WARRANT, warrant),
        (
            "## Backing\n\nnone",
            "## Backing\n\n" + backing if backing != "none" else "## Backing\n\nnone",
        ),
    ):
        assert old in text, old
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    assert p.cl("sha", "--write", str(path)) == 0
    return path


def set_stated(path, timestamp):
    """Rewrite the frontmatter `stated:` line. Not part of the fingerprint, so this is
    safe on an uncommitted draft and lets a test control verdict-timestamp ordering
    without depending on wall-clock time."""
    text = path.read_text(encoding="utf-8")
    old_line = next(ln for ln in text.splitlines() if ln.startswith("stated: "))
    path.write_text(text.replace(old_line, f"stated: {timestamp}", 1), encoding="utf-8")


def append_verdict_text(path, *, timestamp, status, grade, author, evidence, note=None):
    """Splice a verdict block in just before `## References`, matching the layout real
    corpus entries use for a second verdict (blocks run back to back, no blank line
    between them, one blank line after the `## Verdicts` heading for the first one)."""
    block = f"- {timestamp} · {status} · grade: {grade} · author: {author}\n"
    block += f"  evidence: {evidence}\n"
    if note:
        block += f"  note: {note}\n"
    text = path.read_text(encoding="utf-8")
    marker = "\n## References"
    assert marker in text
    head, tail = text.split(marker, 1)
    if head.rstrip("\n").endswith("## Verdicts"):
        head = head.rstrip("\n") + "\n\n"
    else:
        head = head.rstrip("\n") + "\n"
    path.write_text(head + block + marker + tail, encoding="utf-8")


def run_all_checkers(ledger, *, write=False):
    return {
        "validate": validate.run(ledger),
        "resolve": resolve.run(ledger),
        "references": references.run(ledger),
        "propagate": propagate.run(ledger, write=write),
    }


def report_bag(reports):
    return sorted((r.outcome, r.entry or "", r.part, r.message) for r in reports)


def all_reports_by_checker(root):
    return {name: report_bag(rs) for name, rs in run_all_checkers(open_ledger(root=root)).items()}


def snapshot(root: Path):
    """{relative path: bytes} for every file under `root` -- a byte-exact comparison
    across a --write run, so "appends nothing" means nothing, down to the byte."""
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def new_bare_project(root: Path, source_id="fx-source"):
    """A second, independent project (the `project` fixture only gives one), set up the
    same way conftest's fixture is, so `Project.write_full_entry` works on it too."""
    root.mkdir(parents=True)
    p = Project(root)
    assert p.cl("init") == 0
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs" / "note-001.md").write_text(LAB_NOTE, encoding="utf-8")
    source = root.parent / f"{root.name}-source.txt"
    source.write_text(SOURCE_TEXT, encoding="utf-8")
    assert (
        p.cl(
            "source",
            "add",
            str(source),
            "--id",
            source_id,
            "--type",
            "paper",
            "--citation",
            "A synthetic source (these tests)",
            "--authors",
            "Okafor",
        )
        == 0
    )
    return p


def _stage_seed_final_state(seed, dst):
    """A seed's entries/docs as a flat directory, for a checker call that has no need of
    git history: a plain seed as-is, or a history seed's last committed state."""
    if (seed / "commits").is_dir():
        commits = sorted(p for p in (seed / "commits").iterdir() if p.is_dir())
        corpus_run.stage(commits[-1], dst)
    else:
        corpus_run.stage(seed, dst)


# === 1. Idempotency of write paths ===================================================
# README.md: "sha --write refuses on an entry git already has." "Registering a source
# stores its bytes in the same call that writes the row." "hook --install ... writes it"
# and (cli.py cmd_hook) leaves an existing hook alone. propagate.py: "--write appends the
# missing verdicts ... the run still exits non-zero so the change is looked at before it
# is committed" -- which only makes sense if a second run, with nothing left missing, is
# clean: the writer must reach a fixed point.


def test_sha_write_is_a_no_op_once_the_declared_value_is_correct(project):
    project.cl("new", "claim")
    path = project.write_full_entry(project.entry("A0001-claim.md"))
    before = path.read_bytes()
    assert project.cl("sha", "--write", str(path)) == 0
    assert path.read_bytes() == before


def test_init_twice_refuses_without_force_and_does_not_corrupt(project):
    """cli.py cmd_init: "already exists; pass --force to write over it." The project
    fixture already ran `init` once; a second call must refuse and touch nothing."""
    cfg = project.root / "claims-ledger.toml"
    before = cfg.read_bytes()
    entries_before = sorted(project.entries.glob("*"))
    assert project.cl("init") == 1
    assert cfg.read_bytes() == before
    assert sorted(project.entries.glob("*")) == entries_before


def test_source_add_the_same_id_twice_is_refused_and_does_not_corrupt(project, tmp_path):
    """authoring.register_source: "source id `{source_id}` is already registered." The
    registry row and bytes written by the first call must be untouched by the refused
    second one."""
    registry = project.root / "ledger" / "sources.jsonl"
    before = registry.read_bytes()
    cache_before = snapshot(project.root / "ledger" / "cache")
    dup = tmp_path / "dup.txt"
    dup.write_text("entirely different bytes", encoding="utf-8")
    code = project.cl(
        "source",
        "add",
        str(dup),
        "--id",
        "fx-source",
        "--type",
        "paper",
        "--citation",
        "a different citation",
        "--authors",
        "Someone",
    )
    assert code == 2  # AuthoringError, per cli.main's exception table
    assert registry.read_bytes() == before
    assert snapshot(project.root / "ledger" / "cache") == cache_before


def test_hook_install_twice_leaves_the_existing_hook_untouched(project):
    """cli.py cmd_hook: "{path} exists; leaving it alone.\""""
    project.git("init", "-q")
    assert project.cl("hook", "--install") == 0
    hook_path = project.root / ".git" / "hooks" / "pre-commit"
    before = hook_path.read_bytes()
    assert project.cl("hook", "--install") == 1
    assert hook_path.read_bytes() == before


def test_propagate_write_reaches_a_fixed_point(project):
    """propagate.py module docstring: "--write appends the missing verdicts ... the run
    still exits non-zero so the change is looked at before it is committed." A second
    --write, with nothing left missing, must append nothing and exit 0 -- otherwise the
    writer never stabilizes and every commit re-triggers it. It must also leave the
    entry passing propagate's own read-only check: "a writer that does not satisfy its
    own checker is a bug.\""""
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

    assert project.cl("propagate") == 1  # missing contested verdict, reported

    before_write = snapshot(project.root)
    assert project.cl("propagate", "--write") == 1  # flags the run that fixed it
    after_first_write = snapshot(project.root)
    assert after_first_write != before_write  # the verdict really was appended

    assert project.cl("propagate") == 0  # propagate's own checker, now satisfied
    assert project.cl("validate") == 0  # the appended verdict is itself well-formed

    assert project.cl("propagate", "--write") == 0  # fixed point
    after_second_write = snapshot(project.root)
    assert after_second_write == after_first_write  # nothing appended, byte for byte


def test_propagate_write_reaches_a_fixed_point_on_the_challenges_branch(project):
    """The `challenges` branch of propagate.run appends to the *target*, not the citing
    entry -- a different code path from the `cites-as-live` -> fallen branch above, and
    one this test exercises on its own so a divergence between the two isn't masked."""
    project.cl("new", "target-claim")
    target = project.write_full_entry(project.entry("A0001-target-claim.md"))

    project.cl("new", "challenger-claim")
    challenger = project.entry("A0002-challenger-claim.md")
    fill_entry(
        project,
        challenger,
        assertion="A claim that challenges the target claim.",
        grounds=(
            '- lab: docs/note-001.md § "Observation" @working\n'
            "- source: fx-source · whole text\n"
            "- entry: A0001-target-claim · challenges"
        ),
        warrant="This attacks a datum the target claim rests on.",
        backing=(
            "- source: fx-source · whole text\n"
            "  speaker: Okafor\n"
            '  quote: "That is the whole of the result."'
        ),
    )

    assert project.cl("propagate") == 1  # target carries no propagated contested verdict

    before = snapshot(project.root)
    assert project.cl("propagate", "--write") == 1
    after_first_write = snapshot(project.root)
    assert after_first_write != before
    assert target.read_bytes() != before[str(target.relative_to(project.root))]

    assert project.cl("propagate") == 0
    assert project.cl("validate") == 0

    assert project.cl("propagate", "--write") == 0  # fixed point
    assert snapshot(project.root) == after_first_write


# === 2. Ordering independence ========================================================
# The schema fixes an order only where it says so: Verdicts (non-decreasing timestamps,
# validate.py check_verdicts), and the section order within one entry (SECTIONS +
# TAIL_SECTIONS). Nothing orders one entry's file against another's, or one Grounds/
# Backing/References line against its siblings; schema.py's fingerprint explicitly sorts
# Backing blocks so their order carries no information at all.


@pytest.mark.parametrize("seed", FLAT_SEEDS, ids=lambda s: s.name)
def test_checkers_do_not_depend_on_filesystem_enumeration_order(seed, tmp_path, monkeypatch):
    """schema.py load_entries: "Every entry under entries_dir, sorted by filename" -- an
    iteration order, not a meaning. Every non-history seed's set of reported failures,
    across all four checkers, must be identical whether entries are loaded in that order
    or in reverse."""
    staged = tmp_path / "staged"
    _stage_seed_final_state(seed, staged)
    ledger = corpus_run.seed_ledger(CORPUS, staged)
    baseline = {name: report_bag(rs) for name, rs in run_all_checkers(ledger).items()}

    real_load_entries = load_entries

    def reversed_load_entries(ledger, cached=False):
        return list(reversed(real_load_entries(ledger, cached=cached)))

    monkeypatch.setattr(validate, "load_entries", reversed_load_entries)
    monkeypatch.setattr(resolve, "load_entries", reversed_load_entries)
    monkeypatch.setattr(references, "load_entries", reversed_load_entries)
    monkeypatch.setattr(propagate, "load_entries", reversed_load_entries)

    reversed_reports = {name: report_bag(rs) for name, rs in run_all_checkers(ledger).items()}
    assert reversed_reports == baseline


def test_a_defects_report_travels_with_the_entrys_content_not_its_id_slot(tmp_path):
    """Nothing in the schema makes one independent entry's report depend on which id or
    filename slot a second, unrelated entry occupies (an id must match its own filename
    -- validate.py check_frontmatter -- but there is no rule tying two different entries'
    identities together). Building the same two entries in the two possible creation
    orders assigns them opposite ids, since `authoring.next_id` numbers by creation
    order; the reports attached to each entry's content must be the same either way."""
    bad_assertion = "An unrelated claim, used only to carry one isolated defect."

    def build(root, good_first):
        p = new_bare_project(root)
        names = (
            ["well-formed", "broken-warrant"] if good_first else ["broken-warrant", "well-formed"]
        )
        for slug in names:
            p.cl("new", slug)
        good_path = next(p.entries.glob("*-well-formed.md"))
        bad_path = next(p.entries.glob("*-broken-warrant.md"))
        p.write_full_entry(good_path)
        fill_entry(
            p,
            bad_path,
            assertion=bad_assertion,
            grounds=(
                '- lab: docs/note-001.md § "Observation" @working\n- source: fx-source · whole text'
            ),
            warrant="",  # the one deliberate defect: an empty Warrant
            backing=f'- source: fx-source · whole text\n  speaker: Okafor\n  quote: "{QUOTE}"',
        )
        return p

    def reports_by_content(p):
        ledger = open_ledger(root=p.root)
        entries = load_entries(ledger)
        id_to_assertion = {e.prefix: e.assertion for e in entries}  # Report.entry is e.prefix
        out = set()
        for name, reports in run_all_checkers(ledger).items():
            for r in reports:
                out.add((name, id_to_assertion.get(r.entry, r.entry), r.part, r.outcome, r.message))
        return out

    order_a = build(tmp_path / "order-a", good_first=True)
    order_b = build(tmp_path / "order-b", good_first=False)
    assert reports_by_content(order_a) == reports_by_content(order_b)


def test_grounds_and_references_line_order_does_not_change_the_verdict(project):
    """docs/SCHEMA.md describes Grounds and References as sets of typed pointers, one
    per line, with no ordering rule (unlike Verdicts). Swapping the order of an entry's
    Grounds lines does not change verbatim_sha (Grounds are excluded from the
    fingerprint) and must not change any checker's report."""
    project.cl("new", "claim")
    path = project.entry("A0001-claim.md")
    fill_entry(
        project,
        path,
        assertion="A claim with two independently-ordered grounds.",
        grounds=(
            '- source: fx-source · whole text\n- lab: docs/note-001.md § "Observation" @working'
        ),
        warrant="The lab observation and the source together support this.",
        backing=f'- source: fx-source · whole text\n  speaker: Okafor\n  quote: "{QUOTE}"',
    )
    ledger = open_ledger(root=project.root)
    forward_sha = path.read_text(encoding="utf-8").split("verbatim_sha:")[1].splitlines()[0]
    forward = {name: report_bag(rs) for name, rs in run_all_checkers(ledger).items()}

    text = path.read_text(encoding="utf-8")
    swapped = text.replace(
        '- source: fx-source · whole text\n- lab: docs/note-001.md § "Observation" @working',
        '- lab: docs/note-001.md § "Observation" @working\n- source: fx-source · whole text',
    )
    assert swapped != text
    path.write_text(swapped, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0  # Grounds excluded: nothing to restamp
    reswapped_sha = path.read_text(encoding="utf-8").split("verbatim_sha:")[1].splitlines()[0]
    assert reswapped_sha == forward_sha

    ledger2 = open_ledger(root=project.root)
    reversed_reports = {name: report_bag(rs) for name, rs in run_all_checkers(ledger2).items()}
    assert reversed_reports == forward


def test_backing_block_order_does_not_change_the_fingerprint_or_the_verdict(project):
    """docs/SCHEMA.md, verbatim_sha: "reordering Backing blocks ... changes nothing."
    K11 in the corpus proves this for a supersession chain; here it is checked directly
    against the live checkers over a two-block entry."""
    project.cl("new", "claim")
    path = project.entry("A0001-claim.md")
    block1 = f'- source: fx-source · whole text\n  speaker: Okafor\n  quote: "{QUOTE}"'
    block2 = (
        "- source: fx-source · whole text\n"
        "  speaker: Okafor\n"
        '  quote: "That is the whole of the result."'
    )
    fill_entry(
        project,
        path,
        assertion="A claim backed by two independently-ordered quotes.",
        grounds="- source: fx-source · whole text",
        warrant="Both quotations, in either order, back the same claim.",
        backing=f"{block1}\n{block2}",
    )
    sha_forward = path.read_text(encoding="utf-8").split("verbatim_sha:")[1].splitlines()[0]
    forward = all_reports_by_checker(project.root)

    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(f"{block1}\n{block2}", f"{block2}\n{block1}"), encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    sha_reversed = path.read_text(encoding="utf-8").split("verbatim_sha:")[1].splitlines()[0]
    assert sha_reversed == sha_forward

    assert all_reports_by_checker(project.root) == forward


# === 3. Normalization invariance =====================================================
# docs/SCHEMA.md, verbatim_sha: "Unicode NFC, the markdown emphasis markers `*` and
# backtick removed, whitespace collapsed to single spaces ... Resolution applies the
# same normalization when it matches spans, so the two never disagree about what a
# change is." That is the promise this section holds the code to, in both directions.


def test_the_fingerprint_changes_when_the_verbatim_record_actually_changes():
    """docs/SCHEMA.md: "a quote moved to a different source or a different speaker
    changes the fingerprint"; a changed Scope value changes what the assertion claims to
    hold over. The required direction of the promise: these must NOT collide."""
    scope = "metric: m\ncohort: c\ncondition: d"
    base = fingerprint(scope, [("src · loc", "Okafor", '"a quote."')])
    assert (
        fingerprint("metric: m2\ncohort: c\ncondition: d", [("src · loc", "Okafor", '"a quote."')])
        != base
    )
    assert fingerprint(scope, [("src · loc", "SomeoneElse", '"a quote."')]) != base
    assert fingerprint(scope, [("other-src · loc", "Okafor", '"a quote."')]) != base
    assert fingerprint(scope, [("src · loc", "Okafor", '"a different quote."')]) != base


def test_the_fingerprint_is_unchanged_by_what_the_schema_declares_irrelevant():
    """docs/SCHEMA.md, verbatim_sha: "reordering Backing blocks, changing emphasis or
    whitespace, or writing an accented word in another normalization form changes
    nothing." The other required direction: these must all collide with the base."""
    scope = "metric: café\ncohort: c\ncondition: d"
    blocks = [
        ("src · loc", "Okafor", '"first quote."'),
        ("src2 · loc2", "Lindqvist", '"second quote."'),
    ]
    base = fingerprint(scope, blocks)

    assert fingerprint(scope, list(reversed(blocks))) == base
    assert fingerprint("metric: *café*\ncohort: c\ncondition: d", blocks) == base
    assert fingerprint("metric:   café  \ncohort: c\ncondition:   d", blocks) == base
    assert fingerprint(unicodedata.normalize("NFD", scope), blocks) == base
    # emphasis and backticks are stripped from a Backing line exactly as from a Scope
    # line: "*first* quote." and "`first` quote." both normalize to "first quote."
    emphasized_blocks = [("src · loc", "Okafor", '"*first* quote."'), blocks[1]]
    backticked_blocks = [("src · loc", "Okafor", '"`first` quote."'), blocks[1]]
    assert fingerprint(scope, emphasized_blocks) == base
    assert fingerprint(scope, backticked_blocks) == base


def test_entries_written_with_crlf_line_endings_verify_identically_to_lf(project, tmp_path):
    """Not an explicit README promise by name, but the only sensible reading of "the
    checkers use the standard library only" plus SCHEMA.md's line-oriented grammar: an
    entry saved by an editor that writes CRLF must check the same as one written LF.
    schema.py's own file reads (read_text_or_raise, and subprocess text=True for `git
    show`) go through Python's universal-newlines translation, which normalizes CRLF to
    LF before any parsing sees it -- this test holds that behavior in place."""
    project.cl("new", "claim")
    path = project.write_full_entry(project.entry("A0001-claim.md"))
    lf_reports = all_reports_by_checker(project.root)

    final_text = path.read_text(encoding="utf-8")
    # Write real CRLF bytes directly -- write_text() would translate a bare "\n" back to
    # os.linesep and silently undo the conversion on this platform.
    path.write_bytes(final_text.replace("\n", "\r\n").encode("utf-8"))
    assert b"\r\n" in path.read_bytes()

    assert all_reports_by_checker(project.root) == lf_reports


def test_crlf_in_a_source_file_does_not_break_a_quote_that_spans_the_line_break(tmp_path):
    """schema.normalize(): "whitespace collapsed to single spaces" -- str.split() treats
    \\r as whitespace along with \\n, so a quote whose contiguous span crosses a CRLF
    line break in the *source* (read as raw bytes in resolve.source_bytes, unlike an
    entry) must still resolve."""
    p = new_bare_project(tmp_path / "crlf-source")
    source_text = "Alpha line one continues onto\nline two of the same sentence, done.\n"
    source = tmp_path / "crlf-source.txt"
    source.write_bytes(source_text.replace("\n", "\r\n").encode("utf-8"))
    assert (
        p.cl(
            "source",
            "add",
            str(source),
            "--id",
            "fx-crlf",
            "--type",
            "paper",
            "--citation",
            "c",
            "--authors",
            "A",
        )
        == 0
    )
    p.cl("new", "claim")
    path = p.entry("A0001-claim.md")
    quote = "Alpha line one continues onto line two of the same sentence, done."
    fill_entry(
        p,
        path,
        assertion="A claim quoting across a CRLF line break.",
        grounds="- source: fx-crlf · whole text",
        warrant="The source states this directly.",
        backing=f'- source: fx-crlf · whole text\n  speaker: A\n  quote: "{quote}"',
    )
    reports = resolve.run(open_ledger(root=p.root))
    assert not any(r.outcome == "fail" for r in reports), reports


def test_trailing_whitespace_and_a_missing_final_newline_do_not_change_the_verdict(project):
    """The same whitespace-collapse promise, at the level of a whole file: trailing
    spaces on content lines, and the presence or absence of a final newline, are not
    part of what any line says."""
    project.cl("new", "claim")
    path = project.write_full_entry(project.entry("A0001-claim.md"))
    baseline = all_reports_by_checker(project.root)

    text = path.read_text(encoding="utf-8")
    padded = "\n".join(ln if ln.strip() in ("", "---") else ln + "   " for ln in text.split("\n"))
    path.write_text(padded, encoding="utf-8")
    assert all_reports_by_checker(project.root) == baseline

    # and again with the final newline stripped
    path.write_text(padded.rstrip("\n"), encoding="utf-8")
    assert all_reports_by_checker(project.root) == baseline


def test_quote_resolution_is_nfc_nfd_agnostic_between_source_and_entry(tmp_path):
    """docs/SCHEMA.md: "Resolution applies the same normalization when it matches spans,
    so the two never disagree about what a change is." Here the source is stored in NFD
    and the entry's quote is written in NFC."""
    p = new_bare_project(tmp_path / "nfd-project")
    source_nfd = unicodedata.normalize(
        "NFD", "The café result replicates under mean aggregation.\n"
    )
    source = tmp_path / "nfd-source.txt"
    source.write_bytes(source_nfd.encode("utf-8"))
    assert (
        p.cl(
            "source",
            "add",
            str(source),
            "--id",
            "fx-nfd",
            "--type",
            "paper",
            "--citation",
            "c",
            "--authors",
            "A",
        )
        == 0
    )
    p.cl("new", "claim")
    path = p.entry("A0001-claim.md")
    quote_nfc = unicodedata.normalize("NFC", "The café result replicates under mean aggregation.")
    fill_entry(
        p,
        path,
        assertion="A claim quoting an NFD source with an NFC quote.",
        grounds="- source: fx-nfd · whole text",
        warrant="The source states this directly.",
        backing=f'- source: fx-nfd · whole text\n  speaker: A\n  quote: "{quote_nfc}"',
    )
    reports = resolve.run(open_ledger(root=p.root))
    assert not any(r.outcome == "fail" for r in reports), reports


def test_straight_and_curly_quote_delimiters_both_resolve_but_change_the_fingerprint(project):
    """schema.QUOTE_MARKS accepts straight and curly quotation marks interchangeably as
    the delimiter of a quoted span (parse_quote), and resolve() matches the span inside
    them regardless of which style delimits it. But the fingerprint hashes a Backing
    block's `quote:` value verbatim, marks included, and the schema's normalize() maps
    neither style to the other -- so changing delimiter style is NOT declared irrelevant
    the way reordering or whitespace is. This documents the actual, undeclared behavior:
    the verbatim_sha changes, while resolve() still verifies the quote."""
    project.cl("new", "claim")
    path = project.entry("A0001-claim.md")
    fill_entry(
        project,
        path,
        assertion="A claim quoted with straight quotation marks.",
        grounds="- source: fx-source · whole text",
        warrant="The source states this directly.",
        backing=f'- source: fx-source · whole text\n  speaker: Okafor\n  quote: "{QUOTE}"',
    )
    straight_sha = path.read_text(encoding="utf-8").split("verbatim_sha:")[1].splitlines()[0]
    straight_reports = resolve.run(open_ledger(root=project.root))
    assert not any(r.outcome == "fail" for r in straight_reports)

    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(f'"{QUOTE}"', f"“{QUOTE}”"), encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    curly_sha = path.read_text(encoding="utf-8").split("verbatim_sha:")[1].splitlines()[0]
    curly_reports = resolve.run(open_ledger(root=project.root))

    assert not any(r.outcome == "fail" for r in curly_reports)  # resolve is style-agnostic
    assert curly_sha != straight_sha  # the fingerprint is not


# === 4. The corpus as a metamorphic base =============================================
# README.md: "62 seeds, each a small ledger with committed expected outcomes." Adding
# trailing whitespace to every content line (the frontmatter `---` fences and blank
# lines excepted, so the very structure the parser locates by an exact "---\n" is left
# alone) changes nothing any checker's grammar cares about -- per the normalization
# promise checked directly in section 3 -- so every seed's expected.json verdict must be
# reproduced exactly, including the seeds whose history runs across several commits.


def _add_trailing_whitespace(text):
    out = []
    for ln in text.split("\n"):
        out.append(ln if ln.strip() in ("", "---") else ln + "   ")
    return "\n".join(out)


def _transform_seed_tree(src, dst, transform):
    shutil.copytree(src, dst)
    for p in dst.rglob("*.md"):
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # D50's document is not text; a transformation of text does not reach it
        p.write_text(transform(text), encoding="utf-8")


@pytest.mark.parametrize("seed", ALL_SEEDS, ids=lambda s: s.name)
def test_trailing_whitespace_does_not_change_a_seeds_expected_verdict(seed, tmp_path):
    dst = tmp_path / "seed"
    _transform_seed_tree(seed, dst, _add_trailing_whitespace)
    ok, lines, _ = corpus_run.run_seed(dst, CORPUS)
    assert ok, "\n".join(lines)


# === 5. Monotonicity / append-only ===================================================


def test_appending_a_verdict_does_not_change_an_unrelated_entrys_status(project):
    """schema.py Entry.status(): a pure function of that entry's own verdict list.
    Appending a verdict to one entry must not move a second, unrelated entry's derived
    status."""
    project.cl("new", "first")
    first = project.write_full_entry(project.entry("A0001-first.md"))
    project.cl("new", "second")
    second = project.entry("A0002-second.md")
    fill_entry(
        project,
        second,
        assertion="A second, unrelated claim.",
        grounds="- source: fx-source · whole text",
        warrant="The source states this directly.",
        backing=(
            "- source: fx-source · whole text\n"
            "  speaker: Okafor\n"
            '  quote: "That is the whole of the result."'
        ),
    )
    status_before = open_ledger(root=project.root)
    entries_before = {e.id: e.status() for e in load_entries(status_before)}
    assert entries_before[second.stem] == "open"

    set_stated(first, "2020-01-01T00:00:00+00:00")
    append_verdict_text(
        first,
        timestamp="2020-02-01T00:00:00+00:00",
        status="corroborated",
        grade="measured",
        author="main",
        evidence='search: corpus=arxiv; query="a second reading"; date=2020-01-15',
        note="a second reading of the same note",
    )
    entries_after = {e.id: e.status() for e in load_entries(open_ledger(root=project.root))}
    assert entries_after[second.stem] == "open"  # unrelated, and unmoved
    assert entries_after[first.stem] == "corroborated"  # the one that actually changed


def test_a_verdict_after_a_terminal_verdict_is_caught(project):
    """docs/SCHEMA.md, Statuses: terminal statuses "stop the walk"; validate.py
    check_verdicts: a verdict "follows a terminal ... verdict; nothing may follow it"
    (barring the one documented reinstatement exception, which this is not)."""
    project.cl("new", "claim")
    path = project.write_full_entry(project.entry("A0001-claim.md"))
    set_stated(path, "2020-01-01T00:00:00+00:00")
    append_verdict_text(
        path,
        timestamp="2020-02-01T00:00:00+00:00",
        status="refuted",
        grade="measured",
        author="main",
        evidence="source: fx-source · whole text",
        note="contradicted",
    )
    append_verdict_text(
        path,
        timestamp="2020-03-01T00:00:00+00:00",
        status="corroborated",
        grade="measured",
        author="main",
        evidence='lab: docs/note-001.md § "Observation" @working',
    )
    reports = validate.run(open_ledger(root=project.root))
    assert any(
        r.outcome == "fail" and r.part == "verdict 2" and "terminal" in r.message for r in reports
    )


def test_derive_status_is_a_deterministic_function_of_the_verdict_list():
    """schema.py Entry.status(): "derive_status(self.verdicts)" -- calling it twice on
    the same list must give the same answer."""

    def v(status):
        return Verdict(index=1, raw="", status=status)

    verdicts = [v("corroborated"), v("contested"), v("refuted")]
    assert derive_status(verdicts) == derive_status(verdicts) == derive_status(list(verdicts))


def test_derive_status_is_order_sensitive_only_the_way_the_docs_say():
    """docs/SCHEMA.md, Statuses: "the status of the last legal verdict" -- reordering two
    non-terminal verdicts changes which one is last, and must change the result. The one
    documented exception is directional: "refuted or non-comparable may be followed by
    exactly one superseded" reinstates; a superseded verdict is not itself un-terminal,
    so a refuted verdict following it does nothing (no exception the other way)."""

    def v(status):
        return Verdict(index=1, raw="", status=status)

    assert derive_status([v("corroborated"), v("contested")]) == "contested"
    assert derive_status([v("contested"), v("corroborated")]) == "corroborated"
    assert derive_status([v("corroborated"), v("contested")]) != derive_status(
        [v("contested"), v("corroborated")]
    )

    assert derive_status([v("refuted"), v("superseded")]) == "superseded"  # reinstated
    assert derive_status([v("superseded"), v("refuted")]) == "superseded"  # not reinstated backward


def test_editing_the_frozen_region_after_a_commit_is_caught(project):
    """docs/SCHEMA.md, Immutability: "The region above the APPEND marker never changes
    after the commit that created the entry ... checked against git over the whole
    history, so a commit that bypassed the check is caught by the next run anywhere.\""""
    project.cl("new", "claim")
    path = project.write_full_entry(project.entry("A0001-claim.md"))
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "initial")
    assert validate.run(open_ledger(root=project.root)) == []  # committed, unedited: clean

    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace("A measured error", "A carefully measured error"), encoding="utf-8"
    )
    reports = validate.run(open_ledger(root=project.root))
    assert any(r.outcome == "fail" and "immutable" in r.message for r in reports)


def test_editing_a_committed_verdict_is_caught(project):
    """docs/SCHEMA.md, Immutability: "a verdict once committed is never edited or
    removed." validate.py check_history walks every consecutive pair of revisions and
    fails when a verdict block present in an earlier one differs in a later one."""
    project.cl("new", "claim")
    path = project.write_full_entry(project.entry("A0001-claim.md"))
    set_stated(path, "2020-01-01T00:00:00+00:00")
    append_verdict_text(
        path,
        timestamp="2020-02-01T00:00:00+00:00",
        status="corroborated",
        grade="measured",
        author="main",
        evidence='search: corpus=arxiv; query="mean aggregation replication"; date=2020-01-15',
        note="original note",
    )
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "initial with one verdict")
    assert validate.run(open_ledger(root=project.root)) == []

    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("original note", "a rewritten note"), encoding="utf-8")
    reports = validate.run(open_ledger(root=project.root))
    assert any(
        r.outcome == "fail" and r.part == "verdict 1" and "append and only append" in r.message
        for r in reports
    )


# === 6. Cross-checker consistency ====================================================
# cli.py cmd_check: runs the four checkers and prints each; README.md: "claims-ledger
# check runs all four." The exit code must be the worst of the four, and the set of
# reports it is built from is exactly their union -- over hand-built project states and
# every corpus seed.


def test_check_is_the_four_checkers_and_the_worst_of_their_exit_codes(project):
    project.cl("new", "claim")
    project.write_full_entry(project.entry("A0001-claim.md"))
    project.cl("new", "second")
    fill_entry(
        project,
        project.entry("A0002-second.md"),
        assertion="A second claim with a deliberately empty Warrant.",
        grounds="- source: fx-source · whole text",
        warrant="",
        backing=(
            "- source: fx-source · whole text\n"
            "  speaker: Okafor\n"
            '  quote: "That is the whole of the result."'
        ),
    )
    ledger = open_ledger(root=project.root)
    individual = run_all_checkers(ledger)
    exits = {name: exit_code(rs) for name, rs in individual.items()}
    assert exits["validate"] == 1  # the empty Warrant
    assert exits["propagate"] == 0

    code = cli.cmd_check(SimpleNamespace(cached=False), ledger)
    assert code == max(exits.values())


@pytest.mark.parametrize("seed", ALL_SEEDS, ids=lambda s: s.name)
def test_check_matches_the_four_checkers_over_every_corpus_seed(seed, tmp_path):
    staged = tmp_path / "staged"
    _stage_seed_final_state(seed, staged)
    ledger = corpus_run.seed_ledger(CORPUS, staged)
    individual = run_all_checkers(ledger)
    exits = [exit_code(rs) for rs in individual.values()]
    code = cli.cmd_check(SimpleNamespace(cached=False), ledger)
    assert code == max(exits), seed.name
