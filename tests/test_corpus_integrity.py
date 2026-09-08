"""Fifth-pass QE: the corpus as a metamorphic base, and the release gates around it.

`tests/test_corpus.py` asks whether the corpus is well-formed and whether the checkers
reproduce it. These tests ask two harder questions the first file cannot:

1. **Is a seed's pass load-bearing?** A seed passes when the named checker produces the
   named outcome at the named place — and a place that two rules both fail at used to be
   claimed by whichever rule survived, because the runner compared neither the message nor
   the place exactly. The mutation tests below delete one rule from a copy of the source
   tree and ask the corpus to notice. Where it does not, the seed's coverage claim is
   decoration.

2. **Does a transformation that must not change the verdict change it, and does one that
   must, not?** Line endings, Unicode normalization form, frontmatter key order, Backing
   block order and a consistent id rename are all things an editor, a filesystem or an
   author does; none of them is a change to what an entry says.

Plus the gates: what an empty or unmatched corpus run reports, and what `release.yml`
proves before it uploads.

Findings are written up in `.qe/findings-corpus-release.md`.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

from claims_ledger.corpus import run as corpus_run

CORPUS = Path(corpus_run.CORPUS)
SEEDS = sorted(p for p in (CORPUS / "seeds").iterdir() if p.is_dir())
SEED_NAMES = [s.name for s in SEEDS]
# The tree these tests were read from, not the tree the *module* was imported from. It
# was `CORPUS.parents[2]`, which under an installed copy is a directory inside the
# environment — so every test here that reads a repository file skipped rather than ran,
# including inside a source distribution that carries all of them. Seven tests, silently.
# (docs/audits/0.1.0.md, QE10-3.)
REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src"
WORKFLOWS = REPO / ".github" / "workflows"


def project_file(*parts):
    """A file in the checkout. A wheel-only install has no checkout, so tests that read
    one skip rather than fail: they are about the repository, not about the package."""
    path = REPO.joinpath(*parts)
    if not path.is_file():
        pytest.skip(f"{path} is not in this tree (installed, not a checkout)")
    return path


# ---------------------------------------------------------------------------
# The runner's own exit contract: a run that checked nothing is not a pass.
# ---------------------------------------------------------------------------


def test_an_empty_corpus_is_not_a_pass(capsys, tmp_path):
    (tmp_path / "seeds").mkdir()
    code = corpus_run.main(["--corpus", str(tmp_path)])
    out = capsys.readouterr().out
    assert code != 0, out


def test_a_filter_that_matches_nothing_is_not_a_pass(capsys):
    code = corpus_run.main(["THERE-IS-NO-SUCH-SEED"])
    out = capsys.readouterr().out
    assert code != 0, out


def test_a_filter_that_matches_something_still_runs_it(capsys):
    """The control for the two above: the filter itself works."""
    code = corpus_run.main(["K01"])
    out = capsys.readouterr().out
    assert code == 0, out
    assert "1/1 seeds pass" in out


# ---------------------------------------------------------------------------
# Expectation rows: one row, one report.
# ---------------------------------------------------------------------------


def produced_for(seed):
    ok, lines, produced = corpus_run.run_seed(seed, CORPUS)
    assert ok, f"{seed.name}: {lines}"
    return produced


def binding_rows(seed):
    exp = json.loads((seed / "expected.json").read_text(encoding="utf-8"))
    return [
        r
        for r in exp["expect"]
        if r["checker"] in corpus_run.CHECKERS and r["outcome"] in ("fail", "flag")
    ]


def hits_for(row, produced):
    commit, entry, part = corpus_run.parse_where(row["where"])
    return [
        r
        for r in produced[row["checker"]]
        if corpus_run.matches(r, commit, entry, part) and r.outcome == row["outcome"]
    ]


def test_no_expectation_row_is_satisfied_by_more_than_one_report():
    ambiguous = []
    for seed in SEEDS:
        produced = produced_for(seed)
        for row in binding_rows(seed):
            hits = hits_for(row, produced)
            if len(hits) > 1:
                ambiguous.append(
                    (seed.name, row["where"], [f"{h.part}: {h.message[:50]}" for h in hits])
                )
    assert not ambiguous, ambiguous


def test_every_expectation_row_names_the_report_place_exactly():
    loose = []
    for seed in SEEDS:
        produced = produced_for(seed)
        for row in binding_rows(seed):
            _, _, part = corpus_run.parse_where(row["where"])
            for hit in hits_for(row, produced):
                if hit.part.casefold() != part.casefold():
                    loose.append((seed.name, row["where"], hit.part))
    assert not loose, sorted(set(loose))


def test_only_the_documented_seeds_produce_no_report_at_all():
    """A defect seed that trips nothing is review-only, and the corpus README names which
    ones those are. A new silent seed would be a defect class nobody is checking."""
    documented = {"D11", "D13", "D33", "D40", "D41"}
    silent = {
        s.name.split("-")[0]
        for s in SEEDS
        if not any(produced_for(s).values()) and s.name.startswith("D")
    }
    assert silent == documented, silent ^ documented


def test_no_two_seeds_are_the_same_case():
    """Ids repeat across seeds and mean nothing outside them, so two seeds that differ
    only in their ids would be one case counted twice."""

    def signature(seed):
        parts = []
        for path in sorted(p for p in seed.rglob("*") if p.is_file()):
            if path.name == "expected.json":
                continue
            # Bytes, so that a seed whose whole point is a document that will not decode
            # is signed like every other one.
            data = re.sub(rb"[A-Z]\d{4}", b"ID", path.read_bytes())
            parts.append(path.relative_to(seed).as_posix().encode("utf-8") + b"\n" + data)
        return hashlib.sha256(b"\n".join(parts)).hexdigest()

    seen = {}
    for seed in SEEDS:
        seen.setdefault(signature(seed), []).append(seed.name)
    assert not [v for v in seen.values() if len(v) > 1], [v for v in seen.values() if len(v) > 1]


# ---------------------------------------------------------------------------
# Mutation: is the rule a seed exists for the rule that holds the seed up?
# ---------------------------------------------------------------------------

# Each anchor is the exact source of one report site. The corpus is asked to notice its
# removal. `test_the_mutation_anchors_are_still_in_the_source` is the guard that keeps a
# refactor from turning these into tests that pass by failing to find their target.

TERMINAL_VERDICT_RULE = (
    "validate.py",
    """                fail(
                    part,
                    f"follows a terminal `{terminal}` verdict; nothing may follow it"
""",
)
RESOLVES_WHEN_RULE = (
    "validate.py",
    """    if needs_credence and not f.get("resolves_when"):
        fail("frontmatter resolves_when", f"kind: {f.get('kind')} requires resolves_when")
""",
)
FRESHNESS_NOT_CHECKED_RULE = (
    "freshness.py",
    """                    f"`{raw}` was not checked: {detail}",
""",
)
UNREADABLE_DOCUMENT_RULE = (
    "references.py",
    """        reports.append(Report("fail", None, name, problem))
""",
)
ANCHORS = {
    "terminal verdict": TERMINAL_VERDICT_RULE,
    "resolves_when": RESOLVES_WHEN_RULE,
    "freshness was-not-checked": FRESHNESS_NOT_CHECKED_RULE,
    "unreadable document": UNREADABLE_DOCUMENT_RULE,
}


def test_the_mutation_anchors_are_still_in_the_source():
    """If a refactor moves one of these, the mutation tests below would delete nothing
    and xfail for the wrong reason. This test goes red instead."""
    project_file("src", "claims_ledger", "validate.py")
    missing = []
    for name, (module, anchor) in ANCHORS.items():
        text = (SRC / "claims_ledger" / module).read_text(encoding="utf-8")
        if text.count(anchor) != 1:
            missing.append((name, module, text.count(anchor)))
    assert not missing, missing


def corpus_notices(tmp_path, module, anchor, replacement):
    """Copy src/, neutralize one report site, run the whole corpus against the copy.

    Returns True when the corpus fails — i.e. when some seed was actually holding that
    rule up. A subprocess, because the checkers are already imported in this one.
    """
    project_file("src", "claims_ledger", module)
    tree = tmp_path / "src"
    shutil.copytree(SRC, tree, ignore=shutil.ignore_patterns("__pycache__"))
    path = tree / "claims_ledger" / module
    text = path.read_text(encoding="utf-8")
    assert text.count(anchor) == 1, module
    path.write_text(text.replace(anchor, replacement), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; from claims_ledger.corpus import run; sys.exit(run.main([]))",
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
        env={"PYTHONPATH": str(tree), "PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
        timeout=600,
    )
    assert "seeds pass" in result.stdout, result.stdout + result.stderr
    return result.returncode != 0


def test_the_terminal_verdict_rule_is_load_bearing_in_the_corpus(tmp_path):
    module, anchor = TERMINAL_VERDICT_RULE
    neutered = (
        "                if False:\n"
        "                    fail(\n"
        "                    part,\n"
        '                    "",\n'
    )
    assert corpus_notices(tmp_path, module, anchor, neutered)


def test_the_resolves_when_rule_is_load_bearing_in_the_corpus(tmp_path):
    module, anchor = RESOLVES_WHEN_RULE
    assert corpus_notices(
        tmp_path,
        module,
        anchor,
        '    if False:\n        fail("frontmatter resolves_when", "")\n',
    )


def test_the_freshness_not_checked_rule_is_load_bearing_in_the_corpus(tmp_path):
    module, anchor = FRESHNESS_NOT_CHECKED_RULE
    assert corpus_notices(tmp_path, module, anchor, '                    "",\n')


def test_the_unreadable_document_rule_is_load_bearing_in_the_corpus(tmp_path):
    module, anchor = UNREADABLE_DOCUMENT_RULE
    assert corpus_notices(tmp_path, module, anchor, "        pass\n")


# ---------------------------------------------------------------------------
# Metamorphic relations: transformations that must not move a verdict.
# ---------------------------------------------------------------------------


def is_text(path):
    """Whether the file is a regular file this transformation can be applied to at all.
    D50's document is deliberately not UTF-8 — rewriting its line endings or its
    normalization form is not a transformation that says nothing new, it is a different
    file."""
    try:
        path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    return True


def seed_markdown(corpus):
    return [p for p in (corpus / "seeds").rglob("*.md") if p.is_file() and is_text(p)]


def to_crlf(corpus):
    for path in seed_markdown(corpus):
        data = path.read_bytes().replace(b"\r\n", b"\n")
        path.write_bytes(data.replace(b"\n", b"\r\n"))


def to_nfd(corpus):
    for path in seed_markdown(corpus):
        text = path.read_text(encoding="utf-8")
        path.write_text(unicodedata.normalize("NFD", text), encoding="utf-8")


def reverse_frontmatter(corpus):
    for path in seed_markdown(corpus):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        head, sep, body = text[4:].partition("\n---\n")
        if not sep:
            continue
        keys = [ln for ln in head.split("\n") if ln.strip()]
        path.write_text("---\n" + "\n".join(reversed(keys)) + "\n---\n" + body, encoding="utf-8")


BACKING_BLOCK = re.compile(r"(- source: .*\n(?:\s+\w+: .*\n?)*)")


def reverse_backing_blocks(corpus):
    for path in seed_markdown(corpus):
        text = path.read_text(encoding="utf-8")
        m = re.search(r"^## Backing\n(.*?)(?=^<!-- APPEND|^## )", text, re.MULTILINE | re.DOTALL)
        if not m:
            continue
        blocks = BACKING_BLOCK.findall(m.group(1))
        if len(blocks) < 2:
            continue
        swapped = "\n".join(b.rstrip("\n") for b in reversed(blocks)) + "\n\n"
        path.write_text(text[: m.start(1)] + swapped + text[m.end(1) :], encoding="utf-8")


def trailing_space_on_body_lines(corpus):
    """Two trailing spaces is Markdown's hard line break. Not the `---` fences: see
    test_a_frontmatter_fence_with_trailing_whitespace_is_still_frontmatter."""
    for path in seed_markdown(corpus):
        text = path.read_text(encoding="utf-8")
        lines = [
            ln if (not ln.strip() or ln.strip() == "---") else ln + "  " for ln in text.split("\n")
        ]
        path.write_text("\n".join(lines), encoding="utf-8")


INVARIANCES = {
    "crlf line endings": to_crlf,
    "nfd normalization": to_nfd,
    "frontmatter keys reversed": reverse_frontmatter,
    "backing blocks reversed": reverse_backing_blocks,
    "trailing whitespace on body lines": trailing_space_on_body_lines,
}


def copy_corpus(tmp_path):
    dst = tmp_path / "corpus"
    shutil.copytree(CORPUS, dst, ignore=shutil.ignore_patterns("__pycache__"))
    return dst


@pytest.mark.parametrize("name", sorted(INVARIANCES))
def test_a_transformation_that_says_nothing_new_moves_no_verdict(capsys, tmp_path, name):
    corpus = copy_corpus(tmp_path)
    INVARIANCES[name](corpus)
    code = corpus_run.main(["--corpus", str(corpus)])
    out = capsys.readouterr().out
    assert code == 0, f"{name}\n{out}"
    assert f"{len(SEEDS)}/{len(SEEDS)} seeds pass" in out


ENTRY_ID = re.compile(r"(?<![0-9A-Za-z])([A-Z])(\d{4})(?![0-9])")

# The one seed whose frozen region names another entry: D28's Scope line reads
# `condition: as in A0003`, so the fingerprint is coupled to A0003's id and a rename
# legitimately moves it. Recorded rather than worked around — it is the only one.
FINGERPRINT_NAMES_AN_ID = "D28-challenge-against-fallen-target"


def test_only_one_seed_couples_its_fingerprint_to_another_entrys_id():
    """The precondition for the rename test below, kept separate so a second such seed
    shows up as its own failure rather than as a mysterious rename regression."""
    coupled = []
    for seed in SEEDS:
        for path in seed.rglob("entries/*.md"):
            text = path.read_text(encoding="utf-8")
            m = re.search(r"^## Scope\n(.*?)^## Grounds", text, re.MULTILINE | re.DOTALL)
            frozen = (m.group(1) if m else "") + "".join(
                re.findall(
                    r"^## Backing\n(.*?)(?=^<!-- APPEND|^## )", text, re.MULTILINE | re.DOTALL
                )
            )
            if ENTRY_ID.search(frozen):
                coupled.append(seed.name)
    assert sorted(set(coupled)) == [FINGERPRINT_NAMES_AN_ID], sorted(set(coupled))


def test_a_consistent_entry_id_rename_moves_no_verdict(capsys, tmp_path):
    """Ids are labels. Shifting every well-formed id by a constant — in the files, in the
    filenames, in the documents that cite them and in the expectation rows — says nothing
    about any claim, so every seed must land exactly where it landed before.

    Five-digit and archived-prefix ids are left alone by the pattern itself: D20's
    `A10000` has a fifth digit, and `C0001` keeps its quarantined `C`.
    """
    corpus = copy_corpus(tmp_path)

    def bump(m):
        return f"{m.group(1)}{int(m.group(2)) + 500:04d}"

    for seed in sorted(p for p in (corpus / "seeds").iterdir() if p.is_dir()):
        if seed.name == FINGERPRINT_NAMES_AN_ID:
            continue
        for path in sorted(p for p in seed.rglob("*") if p.is_file()):
            if not is_text(path):
                continue  # no id in it to rename, and nothing that reads it decodes it
            text = path.read_text(encoding="utf-8")
            renamed = ENTRY_ID.sub(bump, text)
            if renamed != text:
                path.write_text(renamed, encoding="utf-8")
        for path in sorted(seed.rglob("*.md"), key=lambda p: -len(p.parts)):
            if ENTRY_ID.match(path.name):
                path.rename(path.with_name(ENTRY_ID.sub(bump, path.name, count=1)))

    code = corpus_run.main(["--corpus", str(corpus)])
    out = capsys.readouterr().out
    assert code == 0, out
    assert f"{len(SEEDS)}/{len(SEEDS)} seeds pass" in out


def test_a_frontmatter_fence_with_trailing_whitespace_is_still_frontmatter(capsys, tmp_path):
    corpus = copy_corpus(tmp_path)
    for path in (corpus / "seeds" / "K01-measured-claim").rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        path.write_text(
            "\n".join(ln + " " if ln.strip() == "---" else ln for ln in text.split("\n")),
            encoding="utf-8",
        )
    code = corpus_run.main(["K01", "--corpus", str(corpus)])
    out = capsys.readouterr().out
    assert code == 0, out


# ---------------------------------------------------------------------------
# What the corpus says about itself, and what the release says about the corpus.
# ---------------------------------------------------------------------------


def test_every_seed_is_named_in_the_corpus_readme():
    readme = (CORPUS / "README.md").read_text(encoding="utf-8")
    missing = [n for n in SEED_NAMES if not re.search(rf"\b{n.split('-')[0]}\b", readme)]
    assert not missing, missing


def test_the_corpus_the_package_ships_is_the_corpus_the_repository_has():
    """`hatchling` takes `packages = ["src/claims_ledger"]`, so the seeds ride along inside
    the package. This is the invariant the empty-corpus gate (above) is there to protect:
    a wheel that shipped a partial corpus would still print `N/N seeds pass`."""
    assert CORPUS.parent.name == "claims_ledger"
    assert len(SEEDS) == 80
    assert {n[0] for n in SEED_NAMES} == {"D", "K"}
    for seed in SEEDS:
        assert (seed / "expected.json").is_file(), seed.name


# ---------------------------------------------------------------------------
# What a seed's pass is worth: a floor under a single seed, and under a row.
# ---------------------------------------------------------------------------


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


def test_a_blob_token_naming_nothing_is_a_seed_error_not_a_bug_report(tmp_path):
    """QE8-92 — QE7-76's shape in new code. A seed-authoring mistake reached the CLI's
    catch-all as `unexpected FileNotFoundError … this is a bug. Please report it`, on the
    surface `release.yml` runs against both built artifacts."""
    from claims_ledger.corpus import run as corpus_run
    from claims_ledger.schema import LedgerError

    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    with pytest.raises(LedgerError, match="not a file in this seed"):
        corpus_run.blob_id(repo, tmp_path / "commits", "07", "docs/nope.md", {})


# ---------------------------------------------------------------------------
# The inventory: a report site nobody has swept
# ---------------------------------------------------------------------------


REPORT_SITE_COUNTS = {
    # 75 + 1: the history a ledger inside somebody else's repository never read
    # (ARCH-AUDIT.md finding 3). Swept — deleting it reddens
    # test_a_ledger_inside_someone_elses_repository_says_its_history_was_not_read.
    "validate.py": 76,
    "resolve.py": 16,
    "references.py": 15,
    "propagate.py": 5,
    "freshness.py": 13,
}


def report_sites(module):
    """Every statement in `module` that emits a Report, by the same definition the sweep
    under `.qe/probe6/enumerate_sites.py` uses: a bare `fail(...)`/`flag(...)` call, a
    bare `<list>.append(Report(...))`, or a `return [Report(...), ...]`.

    Duplicated here rather than imported because `.qe/` is the record of an adversarial
    pass and does not ship; this file has to answer the question from the package alone.
    """
    path = project_file("src", "claims_ledger", module)
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def emits(node):
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in ("fail", "flag", "Report")
        )

    sites = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr):
            value = node.value
            if emits(value) or (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Attribute)
                and value.func.attr == "append"
                and value.args
                and emits(value.args[0])
            ):
                sites.append(node)
        elif isinstance(node, ast.Return) and isinstance(node.value, ast.List):
            if any(emits(elt) for elt in node.value.elts):
                sites.append(node)
    return sites


def test_every_report_site_has_been_through_the_sweep():
    """A report site is a sentence the checkers promise to say. Whether anything holds
    one up is not knowable by reading it -- it is answered by deleting it and seeing
    whether the corpus or this suite goes red, which is what the sweep does.

    The sweep is not run in CI: it is minutes per site, and it needs a copy of the tree
    per mutant. So this stands in its place. It does not prove a site is held; it proves
    nobody added one *without being asked the question*. Fourteen sites accumulated
    unswept between the sixth pass and here, and two of those turned out to be held by
    nothing at all -- both silent-pass paths under a checkout whose git had stopped
    answering.

    When this goes red you have added or removed a report site. Sweep it before you
    change the number: `.qe/probe6/enumerate_sites.py` lists the sites, `mutate_one.py`
    deletes one and runs both gates against the result. A site that survives both needs
    a test, or a documented reason it cannot have one -- `corpus/README.md` names the
    four that cannot.
    """
    counts = {module: len(report_sites(module)) for module in REPORT_SITE_COUNTS}
    assert counts == REPORT_SITE_COUNTS
