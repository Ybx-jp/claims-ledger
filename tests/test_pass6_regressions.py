"""Sixth pass: the fifth pass's fixes, verified, and what verifying them found.

Every one of the fifth pass's twenty-four findings is genuinely fixed — this file holds
no case for any of them. What it holds is the defects that verifying those fixes turned
up, and three of them are *in* the fixes: new code, merged the same day, reopening the
class it was written to close.

Each case was a strict xfail naming the sentence it holds the code to; every one is now
green, and each opens with the defect it was written against so the sentence and the fix
stay together. They are kept here, in the pass that found them, rather than distributed
into the dimension files as the header first proposed: the fifth pass's flipped
regressions are scattered across six files, and finding out what a pass actually proved
now means reading six diffs. One file per pass is the record a reader can check. Each
opening paragraph is the xfail's own `reason=` text, unedited, so what the pass claimed
and what the fix answers can be read against each other.

They are not what holds these fixes on their own. Every one of them is also held by
tests in the file whose subject it is — `test_freshness_spec.py` for the orphan rule,
`test_section_scoping.py` for what a heading is, `test_write_paths.py` for the write
funnel — and by `D53-laundered-freshness-discharge` in the corpus. This file is where
the pass's own case sits; those are where the class is held.

Nothing here patches git, the filesystem or the package. Every repository is real and
every git failure is produced by putting a shim on PATH, not by patching `schema.git`
— `freshness.py` does `from .schema import git`, so patching the module attribute would
not reach it anyway.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from test_freshness import pinned  # noqa: F401  — the fixture, reused as-is
from test_freshness_spec import build

from claims_ledger import freshness, resolve
from claims_ledger.cli import hook_text
from claims_ledger.config import default_config
from claims_ledger.schema import open_ledger, section_text

PROJECT = Path(__file__).resolve().parent.parent

# A lab note whose Observation section carries a code snippet, which is the ordinary
# shape of the artifact this checker compares. The `#` inside the fence is a comment.
FENCED_NOTE = (
    "# note 001\n\n"
    "## Observation\n\n"
    "At a stale fraction of 0.1 the measured error was 0.04.\n\n"
    "```python\n"
    "# the sweep, as run\n"
    "sweep(stale=0.1)\n"
    "```\n\n"
    "The error does not grow with degree.\n"
)


def project_file(*parts):
    return PROJECT.joinpath(*parts)


def outcomes(root):
    return [(r.outcome, r.part, r.message) for r in freshness.run(open_ledger(root=root))]


def shim_git(tmp_path, failing_subcommand):
    """A `git` on PATH that fails one subcommand and delegates everything else to the real one. A
    repository this git cannot fully answer is an ordinary condition — a corrupted object, a
    clean filter that fails, a history too large for the timeout — and the package's own rule
    is that a git which cannot answer is not a git saying no.
    """
    d = tmp_path / "shim-bin"
    d.mkdir(exist_ok=True)
    real = subprocess.run(["which", "git"], capture_output=True, text=True, check=True)
    (d / "git").write_text(
        "#!/bin/sh\n"
        f'for a in "$@"; do [ "$a" = "{failing_subcommand}" ] && exit 128; done\n'
        f'exec {real.stdout.strip()} "$@"\n',
        encoding="utf-8",
    )
    (d / "git").chmod(0o755)
    return d


# The forgery the orphan rule exists to refuse: a `contested` verdict in the propagation
# author's name, written before the ground it names has moved at all.
FORGERY = (
    "- 2026-11-20T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
    '  evidence: lab: docs/note-001.md § "Observation" @{pin}\n'
    "  note: propagated from a moved ground\n"
)


# === the orphan rule, and what the fifth pass's fix did to it ==========================
#
# MEDIUM-34 was that undoing a drift wedged the ledger: `orphans()` called the checker's
# own discharge an orphan forever. The fix asks `ever_drifted()` — "did any commit
# between the pin and HEAD touch this artifact at all" — and treats a yes as proof the
# verdict was caused. That is not the question the rule needs answered, and it is a
# question the person writing the forged verdict controls.


def test_a_forged_discharge_is_not_laundered_by_a_no_op_commit(pinned):  # noqa: F811
    """Fixed. The defect, as this pass wrote it: ever_drifted() asks whether the artifact was
    ever touched since the pin, not whether this verdict was caused, so one no-op commit that
    edits the artifact and puts it back launders a pre-emptively written discharge permanently

    docs/FRESHNESS.md justifies the orphan rule as stopping a *pre-emptive* forgery:
    "Otherwise the discharge is forgeable by writing the verdict pre-emptively." The artifact
    here is byte-identical to the blob at the pin the whole way through. One commit touches
    it, the next puts it back, and nothing about the ground has changed.
    """
    pinned.append(FORGERY.format(pin=pinned.pin))
    assert [o for o, _, _ in outcomes(pinned.root)] == ["fail"], (
        "the control: the forgery is caught while the artifact has never been touched"
    )

    note = pinned.root / "docs" / "note-001.md"
    original = note.read_bytes()
    note.write_bytes(original.replace(b"0.04", b"0.99"))
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "a touch")
    note.write_bytes(original)
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "and back again")
    assert note.read_bytes() == original

    assert [o for o, _, _ in outcomes(pinned.root)] == ["fail"], (
        "the ground is where the pin left it; the discharge names a drift that never "
        "happened and is still an orphan"
    )


def test_a_git_that_cannot_answer_does_not_retire_the_orphan_check(pinned, tmp_path, monkeypatch):  # noqa: F811
    """Fixed. The defect, as this pass wrote it: ever_drifted() reads a git that could not answer
    as `it drifted` — `not count.isdigit() or int(count) > 0` — so a rev-list that fails or
    times out retires the forged-discharge check silently, with no report that it did not run

    The fourth pass closed this class across six findings: a git that cannot answer is not a
    git answering no. `ever_drifted()` is the one git call in the package with no channel for
    `could not be established`, and it fails open — toward silence.
    """
    pinned.append(FORGERY.format(pin=pinned.pin))
    assert [o for o, _, _ in outcomes(pinned.root)] == ["fail"], "the control"

    monkeypatch.setenv("PATH", f"{shim_git(tmp_path, 'rev-list')}{os.pathsep}{os.environ['PATH']}")
    got = outcomes(pinned.root)
    assert got, "a check that could not run is not a check that passed; this run said nothing"
    assert [o for o, _, _ in got] == ["fail"]


# === a section's span, and what still ends one ========================================


def test_a_hash_inside_a_fenced_code_block_does_not_end_the_section():
    """Fixed. The defect, as this pass wrote it: section_span() has no fence awareness, so a
    `#`-led line inside a ```fenced``` code block is read as a heading and ends the section it
    sits in; everything below it is outside the comparison for both freshness and resolve

    HIGH-31's `depth` group settled which *headings* end a section. It did not settle what a
    heading is. A Markdown lab note carrying a code snippet is the ordinary shape of the
    artifact this checker compares, and `# a comment` is the ordinary content of one.
    """
    doc = (
        "# note 001\n\n"
        "## Observation\n\n"
        "At a stale fraction of 0.1 the measured error was 0.04.\n\n"
        "```python\n"
        "# a comment, not a heading\n"
        "x = 1\n"
        "```\n\n"
        "Conclusion: the result holds.\n\n"
        "## Method\n\n"
        "Star graphs, one layer, sixteen dimensions.\n"
    )
    span = section_text(doc, default_config(PROJECT), "lab", "Observation")
    assert span is not None
    assert "Conclusion: the result holds." in span, (
        f"the section ended at the fence; the compared span was {span!r}"
    )


def test_an_edit_below_a_fence_inside_the_pinned_section_is_still_caught(project):
    """Fixed. The defect, as this pass wrote it: the same defect end to end — an edit below a
    fenced code block inside the pinned section is invisible to freshness and to resolve, so a
    claim's own evidence can be inverted with every checker green

    The severity of the one above. This is not a wording question: the sentence that is
    inverted is the one the claim rests on. The fence is in the note *at the pin*, so the only
    thing that changes afterwards is the conclusion below it.
    """
    note = project.root / "docs" / "note-001.md"
    note.write_text(FENCED_NOTE, encoding="utf-8")
    build(project, ['lab: docs/note-001.md § "Observation" @{pin}'])
    note.write_text(
        FENCED_NOTE.replace(
            "The error does not grow with degree.",
            "The error GROWS with degree, which is the claim inverted.",
        ),
        encoding="utf-8",
    )
    assert [o for o, _, _ in outcomes(project.root)] == ["flag"], (
        "the pinned section's own evidence was inverted and the checker said nothing"
    )


# === the surface the tool is actually installed as ====================================


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


# === the write paths, and what the atomic-write funnel changed ========================


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


# === what a pin is ====================================================================


def test_an_option_shaped_pin_is_not_reported_as_an_unstable_pin(pinned):  # noqa: F811
    r"""Fixed. The defect, as this pass wrote it: `git rev-parse --symbolic-full-name --upload-
    pack=x` exits 0 and echoes its own argument, which is git's parse-options behaviour for an
    unrecognised double-dash argument and not a refname; is_object_name() reads it as a
    symbolic ref, so an option-shaped pin gets an unstable-pin flag and resolve's `does not
    resolve` both — the two contradictory names LOW-36 was fixed to stop

    LOW-36's fix deleted OBJECT_NAME_RE and made git the arbiter for every pin. Pins are free
    text in the schema (`\S+`), so a pin beginning with a dash is a typo away, and git answers
    a question it was not asked.
    """
    path = pinned.entry_path()
    path.write_text(
        path.read_text(encoding="utf-8").replace(f"@{pinned.pin}", "@--upload-pack=x"),
        encoding="utf-8",
    )
    assert pinned.p.cl("sha", "--write", str(path)) == 0
    flags = [m for o, _, m in outcomes(pinned.root) if "can never go stale" in m]
    assert not flags, f"one defect under two contradictory names: {flags}"
    # `resolve.run()` answers with Reports, not the (outcome, part, message) triples
    # `outcomes()` builds above. Written as an unpack, this line raised TypeError instead
    # of asserting — reachable only once the flag above it stops firing, which is why the
    # xfail check the pass ran (fails for the reason it names) did not reach it.
    assert [r.outcome for r in resolve.run(open_ledger(root=pinned.root))].count("fail") == 1


# === the record the package publishes about itself ====================================


def test_the_readme_states_the_seed_count_correctly_wherever_it_states_it():
    """Fixed. The defect, as this pass wrote it: README.md says `All 62 corpus seeds pass
    unchanged`; the corpus is 75. MEDIUM-48's regression only matches a count directly
    adjacent to the word, so the one site with a word in between stayed stale underneath a
    green test.

    README.md is the PyPI long description. MEDIUM-48 was this defect at three sites; the
    regression written for it guards exactly the phrasings that were already wrong. A
    regression narrower than its finding is how a defect comes back.
    """
    from claims_ledger.corpus.run import CORPUS

    n = len([p for p in (Path(CORPUS) / "seeds").iterdir() if p.is_dir()])
    readme = project_file("README.md").read_text(encoding="utf-8")
    wrong = sorted(
        {m.group(1) for m in re.finditer(r"\b(\d+)(?:[ /]\d*)?(?:\s+\w+){0,2}\s+seeds?\b", readme)}
        - {str(n)}
    )
    assert not wrong, f"README claims {wrong} seeds; there are {n}"


def test_the_readme_names_every_interpreter_ci_runs():
    """Fixed. The defect, as this pass wrote it: README.md says CI runs `Python 3.11, 3.12 and
    3.13`; ci.yml's matrix is 3.11, 3.12, 3.13 and 3.14, and 3.14 is in the package's own
    classifiers

    The PyPI long description is where a user reads which interpreters this is held to.
    Claiming fewer than are run is the harmless direction and still wrong.
    """
    ci = project_file(".github", "workflows", "ci.yml").read_text(encoding="utf-8")
    matrix = re.search(r"python:\s*\[([^\]]*)\]", ci)
    assert matrix is not None, "ci.yml has no interpreter matrix to compare against"
    readme = project_file("README.md").read_text(encoding="utf-8")
    missing = [v for v in re.findall(r"3\.\d+", matrix.group(1)) if v not in readme]
    assert not missing, f"README does not name {missing}, which CI runs"


def test_the_release_workflow_names_the_page_a_first_publish_actually_needs():
    """Fixed. The defect, as this pass wrote it: release.yml sends the operator to
    pypi.org/manage/project/claims- ledger/settings/publishing/ to configure Trusted
    Publishing. That page cannot exist before the first upload; a never-published project
    needs the account-level pending publisher. Followed literally, the first tag push fails at
    the publish step.

    The workflow's comment is the only written record of how to publish this package. A first
    release has no project page to configure a publisher on.
    """
    text = project_file(".github", "workflows", "release.yml").read_text(encoding="utf-8")
    assert "manage/account/publishing" in text, (
        "the only publishing instructions point at a project-settings page that does not "
        "exist until after the first upload"
    )


def test_ci_checks_the_metadata_the_way_the_release_does():
    """Fixed. The defect, as this pass wrote it: release.yml runs `twine check --strict`, ci.yml
    runs plain `twine check`, so a metadata regression that only --strict catches passes every
    PR and first fails at the tag, which is the run with no cheap way back

    The value of a pre-merge gate is that it fails before the irreversible step. A gate weaker
    than the one it stands in front of is not one.
    """
    ci = project_file(".github", "workflows", "ci.yml").read_text(encoding="utf-8")
    assert "twine check --strict" in ci


# === what the corpus proves, against what it says it proves ===========================


def test_a_ground_citing_an_entry_that_does_not_exist_is_load_bearing(tmp_path):
    """Fixed. The defect, as this pass wrote it: corpus/README.md says the corpus proves `every
    rule about not silently passing`. Deleting references.py's `cites X, which does not exist`
    leaves the corpus at 75/75 and the unit suite green — one of seven semantic rules an
    independent AST sweep found held by neither gate

    A Grounds pointer naming an entry the ledger does not have is the dead-pointer class,
    which `corpus/README.md`'s Coverage table lists as `catch, loudly`. It is the minimal case
    of the sweep's finding, and the cheapest one to keep.
    """
    from test_corpus_integrity import corpus_notices

    anchor = (
        "                reports.append(\n"
        '                    Report("fail", e.prefix, "Grounds", '
        'f"cites {p.target}, which does not exist")\n'
        "                )"
    )
    assert corpus_notices(tmp_path, "references.py", anchor, "                pass")


def test_a_seed_that_expects_nothing_is_not_a_pass(capsys, tmp_path):
    """Fixed. The defect, as this pass wrote it: a seed whose expected.json carries an empty
    `expect` array counts as a full pass — `1/1 seeds pass`, exit 0, over a seed that checked
    nothing. HIGH-45 put a floor under the corpus; there is none under a single seed.

    HIGH-45's own reasoning, one level down: a gate that can be made green by an absence is
    not a gate. `run.py` is what an installed wheel runs, so a dev-time assertion in `tests/`
    does not stand where this one has to.
    """
    import json

    from claims_ledger.corpus import run as corpus_run

    seed = tmp_path / "seeds" / "Z01-expects-nothing"
    (seed / "entries").mkdir(parents=True)
    (seed / "expected.json").write_text(
        json.dumps({"note": "a seed that asserts nothing at all", "expect": []}),
        encoding="utf-8",
    )
    code = corpus_run.main(["--corpus", str(tmp_path)])
    out = capsys.readouterr().out
    assert code != 0, out


def test_an_empty_expected_message_does_not_match_every_report():
    """Fixed. The defect, as this pass wrote it: matches() tests `message.casefold() in
    report.message.casefold()`, and `"" in x` is always true, so an expectation row carrying
    `"message": ""` is indistinguishable from one that omits the field and pins nothing

    Not exploitable today — the one-row-one-report bijection catches HIGH-46's case regardless
    of message content. Held so the next seed author who writes `""` meaning `no message yet`
    is told rather than quietly satisfied.
    """
    from types import SimpleNamespace

    from claims_ledger.corpus.run import matches

    report = SimpleNamespace(
        commit="01", entry="A0001", part="Grounds", message="cites A0002, which does not exist"
    )
    # The control: a message that really is a substring of the report's does match, and a
    # message that is not does not. Only the empty string is the question here.
    assert matches(report, "01", "A0001", "Grounds", message="does not exist")
    assert not matches(report, "01", "A0001", "Grounds", message="some other rule")
    assert not matches(report, "01", "A0001", "Grounds", message=""), (
        "an empty message substring matched a report it names nothing about"
    )
