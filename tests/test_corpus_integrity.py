"""Fifth-pass QE: the corpus as a metamorphic base, and the release gates around it.

`tests/test_corpus.py` asks whether the corpus is well-formed and whether the checkers
reproduce it. These tests ask two harder questions the first file cannot:

1. **Is a seed's pass load-bearing?** A seed passes when the named checker produces the
   named outcome at the named place. The runner never compares the report's *message*,
   so a place that two rules both fail at is claimed by whichever rule survives. The
   mutation tests below delete one rule from a copy of the source tree and ask the corpus
   to notice. Where it does not, the seed's coverage claim is decoration.

2. **Does a transformation that must not change the verdict change it, and does one that
   must, not?** Line endings, Unicode normalization form, frontmatter key order, Backing
   block order and a consistent id rename are all things an editor, a filesystem or an
   author does; none of them is a change to what an entry says.

Plus the gates: what an empty or unmatched corpus run reports, and what `release.yml`
proves before it uploads.

Findings are written up in `.qe/findings-corpus-release.md`.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

import claims_ledger
from claims_ledger.corpus import run as corpus_run

CORPUS = Path(corpus_run.CORPUS)
SEEDS = sorted(p for p in (CORPUS / "seeds").iterdir() if p.is_dir())
SEED_NAMES = [s.name for s in SEEDS]
REPO = CORPUS.parents[2]  # …/<root>/src/claims_ledger/corpus -> <root>
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


@pytest.mark.xfail(
    strict=True,
    reason="BUG: an empty corpus prints `0/0 seeds pass` and exits 0. The release gate "
    "is `claims-ledger corpus` run against the installed wheel; a wheel that shipped no "
    "seeds would pass it.",
)
def test_an_empty_corpus_is_not_a_pass(capsys, tmp_path):
    (tmp_path / "seeds").mkdir()
    code = corpus_run.main(["--corpus", str(tmp_path)])
    out = capsys.readouterr().out
    assert code != 0, out


@pytest.mark.xfail(
    strict=True,
    reason="BUG: a seed filter that matches nothing prints `0/0 seeds pass` and exits 0, "
    "so `claims-ledger corpus D3` (for the seed named D03) is a green run over nothing.",
)
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


@pytest.mark.xfail(
    strict=True,
    reason="BUG: D17 and D19 each have one expectation row that two different checker "
    "reports satisfy. The runner matches on (commit, entry, part, outcome) and never on "
    "the message, so the row is held up by whichever rule happens to exist — see "
    "test_the_terminal_verdict_rule_is_load_bearing_in_the_corpus.",
)
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


@pytest.mark.xfail(
    strict=True,
    reason="BUG: D19's row `A0001 frontmatter` is a prefix of the two reports it must "
    "distinguish (`frontmatter credence`, `frontmatter resolves_when`), and "
    "corpus_run.matches() accepts a prefix, so either rule alone satisfies the seed.",
)
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
            text = re.sub(r"[A-Z]\d{4}", "ID", path.read_text(encoding="utf-8"))
            parts.append(path.relative_to(seed).as_posix() + "\n" + text)
        return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()

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


@pytest.mark.xfail(
    strict=True,
    reason="BUG: deleting `follows a terminal verdict; nothing may follow it` from "
    "validate.py leaves the corpus at 72/72. D17 is the only seed for the class and its "
    "one row is also satisfied by the corroborating-ground fail at the same place.",
)
def test_the_terminal_verdict_rule_is_load_bearing_in_the_corpus(tmp_path):
    module, anchor = TERMINAL_VERDICT_RULE
    neutered = (
        "                if False:\n"
        "                    fail(\n"
        "                    part,\n"
        '                    "",\n'
    )
    assert corpus_notices(tmp_path, module, anchor, neutered)


@pytest.mark.xfail(
    strict=True,
    reason="BUG: deleting the `requires resolves_when` fail from validate.py leaves the "
    "corpus at 72/72. D19's row names `A0001 frontmatter`, a prefix that the credence "
    "fail at the same entry already satisfies.",
)
def test_the_resolves_when_rule_is_load_bearing_in_the_corpus(tmp_path):
    module, anchor = RESOLVES_WHEN_RULE
    assert corpus_notices(
        tmp_path,
        module,
        anchor,
        '    if False:\n        fail("frontmatter resolves_when", "")\n',
    )


@pytest.mark.xfail(
    strict=True,
    reason="BUG: no seed holds freshness's `was not checked` failure. That report is the "
    "package's reason to exist — a ground the checker could not examine must not be "
    "reported as a ground that passed — and the corpus stays at 72/72 without it.",
)
def test_the_freshness_not_checked_rule_is_load_bearing_in_the_corpus(tmp_path):
    module, anchor = FRESHNESS_NOT_CHECKED_RULE
    assert corpus_notices(tmp_path, module, anchor, '                    "",\n')


@pytest.mark.xfail(
    strict=True,
    reason="BUG: no seed holds references's report for a document that could not be "
    "opened. That is the third pass's HIGH-17 fix; it has unit tests, but the corpus — "
    "which is what the release workflow runs against the built wheel — stays at 72/72 "
    "with the rule removed.",
)
def test_the_unreadable_document_rule_is_load_bearing_in_the_corpus(tmp_path):
    module, anchor = UNREADABLE_DOCUMENT_RULE
    assert corpus_notices(tmp_path, module, anchor, "        pass\n")


# ---------------------------------------------------------------------------
# Metamorphic relations: transformations that must not move a verdict.
# ---------------------------------------------------------------------------


def seed_markdown(corpus):
    return [p for p in (corpus / "seeds").rglob("*.md")]


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


@pytest.mark.xfail(
    strict=True,
    reason="BUG: `--- ` (a trailing space on the frontmatter fence) is read as no "
    "frontmatter at all. schema.py splits on the literal `\\n---\\n`, so an entry that "
    "plainly has frontmatter is reported as having none, plus eight cascading `None` "
    "errors. YAML permits trailing space after a document marker and editors add it.",
)
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


@pytest.mark.xfail(
    strict=True,
    reason="BUG: D45–D49 and K19–K23 — every freshness seed — appear nowhere in the "
    "corpus README. Its Coverage table and known-good list stop at K18, while the same "
    "file claims a seed for every rule the schema's structure creates.",
)
def test_every_seed_is_named_in_the_corpus_readme():
    readme = (CORPUS / "README.md").read_text(encoding="utf-8")
    missing = [n for n in SEED_NAMES if not re.search(rf"\b{n.split('-')[0]}\b", readme)]
    assert not missing, missing


@pytest.mark.xfail(
    strict=True,
    reason="BUG: README.md says the corpus is 70 seeds, in prose twice and in a "
    "transcript of the command's output once. It is 72, and README.md is the package's "
    "PyPI long description.",
)
def test_the_readme_seed_count_is_the_seed_count():
    readme = project_file("README.md").read_text(encoding="utf-8")
    wrong = sorted(
        {m.group(0) for m in re.finditer(r"\b\d+(?=[ /]\d*\s*seeds?\b)", readme)}
        - {str(len(SEEDS))}
    )
    assert not wrong, f"README claims {wrong} seeds; there are {len(SEEDS)}"


def test_the_version_is_the_same_in_every_place_it_is_written():
    """`__init__.py` is the single source; the metadata and the changelog must agree."""
    from importlib.metadata import version

    assert version("claims-ledger") == claims_ledger.__version__
    changelog = project_file("CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [{claims_ledger.__version__}]" in changelog
    assert f"[{claims_ledger.__version__}]: https://" in changelog


@pytest.mark.xfail(
    strict=True,
    reason="BUG: CHANGELOG.md carries an `## [Unreleased]` section whose whole content — "
    "the freshness checker and ten seeds — is already in the tree, and therefore in any "
    "wheel built today, which calls itself 0.1.0. The third pass fixed exactly this and "
    "nothing stopped it coming back.",
)
def test_the_changelog_has_no_unreleased_section_at_the_current_version():
    changelog = project_file("CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [Unreleased]" not in changelog


# ---------------------------------------------------------------------------
# The release workflow. Text, not YAML: the package has no runtime dependencies.
# ---------------------------------------------------------------------------


def release_yml():
    return project_file(".github", "workflows", "release.yml").read_text(encoding="utf-8")


def test_only_a_tag_reaches_the_publish_job():
    """The first half of the standing `harden-release-publication-gates` thread. It holds:
    a workflow_dispatch from a branch builds and stops."""
    text = release_yml()
    publish = text[text.index("\n  publish:") :]
    assert "startsWith(github.ref, 'refs/tags/')" in publish
    assert "id-token: write" in publish
    assert "environment: pypi" in publish


def test_a_tag_runs_the_whole_suite_before_anything_is_built():
    """The second half of the thread. It holds: ruff, ty and pytest run unconditionally in
    `build`, and `publish` needs `build`."""
    text = release_yml()
    build = text[text.index("\n  build:") : text.index("\n  publish:")]
    for command in ("ruff check .", "ruff format --check .", "ty check", "pytest -q"):
        assert command in build, command
    assert build.index("pytest -q") < build.index("python -m build")
    assert "needs: build" in text


@pytest.mark.xfail(
    strict=True,
    reason="BUG: release.yml proves only the wheel from a clean environment; the sdist is "
    "uploaded to PyPI having been `twine check`ed and nothing more. An sdist is what pip "
    "falls back to wherever wheels are refused.",
)
def test_the_sdist_is_proven_from_a_clean_environment_too():
    text = release_yml()
    build = text[text.index("\n  build:") : text.index("\n  publish:")]
    proof = build[build.index("proves itself from elsewhere") :]
    assert "tar.gz" in proof, "no clean-environment install of the sdist"


@pytest.mark.xfail(
    strict=True,
    reason="BUG: every `uses:` is a mutable ref, including "
    "`pypa/gh-action-pypi-publish@release/v1` — a branch — in the one job holding "
    "`id-token: write` and the pypi environment.",
)
def test_every_action_the_release_uses_is_pinned_to_a_commit():
    unpinned = [
        line.strip()
        for line in release_yml().splitlines()
        if "uses:" in line and not re.search(r"@[0-9a-f]{40}\b", line)
    ]
    assert not unpinned, unpinned


def test_the_corpus_the_package_ships_is_the_corpus_the_repository_has():
    """`hatchling` takes `packages = ["src/claims_ledger"]`, so the seeds ride along inside
    the package. This is the invariant the empty-corpus gate (above) is there to protect:
    a wheel that shipped a partial corpus would still print `N/N seeds pass`."""
    assert CORPUS.parent.name == "claims_ledger"
    assert len(SEEDS) == 72
    assert {n[0] for n in SEED_NAMES} == {"D", "K"}
    for seed in SEEDS:
        assert (seed / "expected.json").is_file(), seed.name
