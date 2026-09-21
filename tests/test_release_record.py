"""What the package publishes about itself, held to what it actually does.

`README.md` states a seed count and names the interpreters CI runs; `ci.yml` and
`release.yml` state what is checked before an upload. Every one of those is a promise to
a stranger, and none of them is checked by running the package — a number in prose stays
green forever after it stops being true.

These read the checkout. A wheel-only install has none, which is why the tests that need
one are in `tests/` rather than in the corpus.
"""

from __future__ import annotations

import os
import re
import tempfile
import tomllib
import zipfile
from pathlib import Path

import pytest
from test_corpus_integrity import SEEDS

import claims_ledger

PROJECT = Path(__file__).resolve().parent.parent


def project_file(*parts):
    """A file in the checkout. A wheel-only install has none, so a test that reads one
    skips rather than fails: these are about the repository, not about the package."""
    path = PROJECT.joinpath(*parts)
    if not path.is_file():
        pytest.skip(f"{path} is not in this tree (installed, not a checkout)")
    return path


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


def test_every_shipped_document_states_the_seed_count_correctly():
    """`examples/FEATURES.md` said `all 95 corpus seeds` while the corpus held 96, and
    three separate things that look like they would hold it did not. MEDIUM-48's regression
    above reads README.md and nothing else; `examples/` is outside the configured document
    globs on purpose, so no checker reads the guide; and `tests/test_examples.py` holds its
    snippets to the files they came from without ever looking at its prose. The guide ships
    in the sdist, so the wrong number was published.

    CHANGELOG.md is exempt, and not by oversight: it records what each release shipped, so
    `the release ships 95` goes on being true after the corpus grows. A count in a
    changelog is a historical fact; a count in a guide is a claim about now.
    """
    from claims_ledger.corpus.run import CORPUS

    n = len([p for p in (Path(CORPUS) / "seeds").iterdir() if p.is_dir()])
    pattern = r"\b(\d+)(?:[ /]\d*)?(?:\s+\w+){0,2}\s+seeds?\b"
    for parts in (("README.md",), ("QUALITY.md",), ("examples", "FEATURES.md")):
        text = project_file(*parts).read_text(encoding="utf-8")
        wrong = sorted({m.group(1) for m in re.finditer(pattern, text)} - {str(n)})
        assert not wrong, f"{'/'.join(parts)} claims {wrong} seeds; there are {n}"


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


def test_the_readme_seed_count_is_the_seed_count():
    readme = project_file("README.md").read_text(encoding="utf-8")
    wrong = sorted(
        {m.group(0) for m in re.finditer(r"\b\d+(?=[ /]\d*\s*seeds?\b)", readme)}
        - {str(len(SEEDS))}
    )
    assert not wrong, f"README claims {wrong} seeds; there are {len(SEEDS)}"


def test_every_test_file_the_live_documents_name_exists():
    """A coverage claim naming a file is only worth the file being there. `README.md`,
    `QUALITY.md` and the corpus README each say which tests hold a rule the corpus does
    not, and prose does not go red when a rename makes it false — which is exactly what a
    rename did here, leaving the corpus README pointing at a file that no longer existed.

    `docs/audits/` is deliberately not read: an audit records what a pass wrote when it
    wrote it, one of its sentences quotes a `git diff` that was actually run, and its
    header says so. History is allowed to name what has since moved; a live claim is not.
    """
    live = ("README.md", "QUALITY.md", "src/claims_ledger/corpus/README.md")
    missing = []
    for name in live:
        text = project_file(*name.split("/")).read_text(encoding="utf-8")
        for named in sorted(set(re.findall(r"tests/test_[a-z0-9_]+\.py", text))):
            if not (PROJECT / named).is_file():
                missing.append(f"{name} names {named}, which does not exist")
    assert not missing, missing


def test_the_version_is_the_same_in_every_place_it_is_written():
    """`__init__.py` is the single source; the metadata and the changelog must agree."""
    from importlib.metadata import version

    assert version("claims-ledger") == claims_ledger.__version__
    changelog = project_file("CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [{claims_ledger.__version__}]" in changelog
    assert f"[{claims_ledger.__version__}]: https://" in changelog


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


def release_yml_build():
    """The text of release.yml's `build` job."""
    text = release_yml()
    return text[text.index("\n  build:") : text.index("\n  publish:")]


def commands_only(text):
    """`text` with its comment lines dropped.

    Containment against the raw job text is satisfied by a mention, and a mention is not a
    gate: `claims-ledger check` written in a `# TODO` in the same job passed this file's
    whole suite. The thing being asserted is that the command runs, so the comments — where
    this repository does most of its explaining — must not be part of what is searched.
    """
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))


def ci_gate_commands():
    """Every command ci.yml's `test` job runs as a gate, installation excluded. Derived
    from the file rather than listed here: a gate added to CI and not mirrored into
    release.yml is precisely the drift this is here to catch, and a hand-written list
    cannot see it."""
    text = project_file(".github", "workflows", "ci.yml").read_text(encoding="utf-8")
    job = text[text.index("\n  test:") : text.index("\n  wheel:")]
    lines = job.splitlines()
    commands = []
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        block = re.match(r"(\s*)(?:- )?run: \|", line)
        if block is not None:
            # A gate moved into a block scalar is still a gate. Reading only `run: <cmd>`
            # made a new CI check added this way invisible here, which is the drift this
            # derivation exists to catch, arriving in the shape it cannot see.
            indent = len(block.group(1)) + 2
            while index < len(lines):
                nested = lines[index]
                if nested.strip() and len(nested) - len(nested.lstrip()) < indent:
                    break
                index += 1
                if nested.strip():
                    commands.append(nested.strip())
            continue
        match = re.match(r"\s*(?:- )?run: (.+)", line)
        if match is not None:
            commands.append(match.group(1).strip())
    return [command for command in commands if "pip install" not in command]


def test_a_tag_runs_the_whole_suite_before_anything_is_built():
    """The second half of the thread, and the defect that sheltered behind its own
    regression. `release.yml` promises in a comment that publication is gated on every
    check CI runs, `not on a subset of them`; the test written to hold that promise listed
    four commands, and `claims-ledger check` — the one command that holds this package's
    own ledger to its code — ran in ci.yml and nowhere in release.yml. A tag could
    therefore publish over a ledger no release gate had read. A regression that enumerates
    part of what it guards cannot report what is absent from it, so the list is derived
    from ci.yml now and the assertion is containment, not a spot check."""
    build = commands_only(release_yml_build())
    gates = ci_gate_commands()
    assert "claims-ledger check" in gates, "ci.yml no longer runs the ledger check"
    missing = [command for command in gates if command not in build]
    assert not missing, f"release.yml's build job does not run {missing}, which CI runs"
    assert build.index("pytest -q") < build.index("python -m build")
    assert "needs: build" in release_yml()


def test_the_sdist_is_proven_from_a_clean_environment_too():
    text = release_yml()
    build = text[text.index("\n  build:") : text.index("\n  publish:")]
    proof = build[build.index("proves itself from elsewhere") :]
    assert "tar.gz" in proof, "no clean-environment install of the sdist"


def test_every_sdist_include_pattern_is_anchored_to_the_root():
    """The sdist `include` list is gitignore-style, so an unanchored `README.md` matches at
    any depth — and it did: `.qe/probe7/revert-experiment/README.md`, one file out of the
    audit-record directory `[tool.ruff]` excludes on purpose, was shipping to PyPI. A
    leading `/` is what confines each entry to the root, and the list is only as narrow as
    its loosest pattern."""
    config = tomllib.loads(project_file("pyproject.toml").read_text(encoding="utf-8"))
    include = config["tool"]["hatch"]["build"]["targets"]["sdist"]["include"]
    unanchored = [pattern for pattern in include if not pattern.startswith("/")]
    assert not unanchored, unanchored


def test_the_sdist_carries_the_trees_its_own_tests_read():
    """`tests/` ships, and `tests/test_examples.py` reads `examples/`. With the include
    list unanchored the sdist carried 10 of the example tree's files — the ones that
    happened to live under a directory called `src` or `docs` — and the suite inside the
    distribution failed four ways on a missing `examples/FEATURES.md`. Anchoring the
    patterns fixed the leak out of `.qe` and made this hole exact rather than accidental.
    (docs/audits/0.1.0.md, QE9-94.)"""
    config = tomllib.loads(project_file("pyproject.toml").read_text(encoding="utf-8"))
    include = config["tool"]["hatch"]["build"]["targets"]["sdist"]["include"]
    for required in ("/src", "/tests", "/docs", "/examples"):
        assert required in include, required


def test_the_sdists_own_suite_is_run_from_the_extracted_tree():
    """The corpus proves the checkers ship. Nothing proved the *tests* ship, and a
    distribution carrying a suite that cannot pass inside it would have reached PyPI:
    `twine check` reads metadata, and the corpus rides in the package rather than in the
    tarball. The gate has to run pytest from the extracted sdist, against the copy
    installed from a clean environment.

    Asserted line by line rather than as `"pytest" in build`, which four mutants of this
    step satisfied: running the *checkout's* suite instead, `--collect-only`, `|| true`,
    and the literal string `echo pytest skipped`. Six letters in the right region of a
    file is not a gate. (docs/audits/0.1.0.md, QE10-2.)
    """
    build = release_yml()
    build = build[build.index("\n  build:") : build.index("\n  publish:")]
    assert "tar -xzf" in build, "the sdist is never extracted"
    assert build.index("tar -xzf") > build.index("proves itself from elsewhere")

    runs = [line.strip() for line in build.splitlines() if "-m pytest" in line]
    assert len(runs) == 1, runs
    (run,) = runs
    assert 'cd "$extracted"' in run, run
    assert "/tmp/clean-sdist/bin/python -m pytest" in run, run
    for defeat in ("|| true", "|| :", "--collect-only", "GITHUB_WORKSPACE", "--co"):
        assert defeat not in run, run


def test_every_tree_the_sdist_names_is_present_where_this_suite_runs():
    """The one assertion in this file that is load-bearing *inside* the distribution.

    The gate that runs this suite from an extracted sdist has an oracle problem: nearly
    every test here reads its file through `project_file`, which turns "absent from the
    distribution" into a skip because it cannot tell that from "not a checkout". Deleting
    `docs/` from an extracted sdist and running the gate's own command gives exit 0 with
    counts identical to a healthy tree; `LICENSE`, `QUALITY.md` and `CHANGELOG.md` go the
    same way, differing only in the skip count nothing pins. A floor on skips would have
    caught two of those four and missed `docs/` entirely. This reads the include list from
    the tree it is running in and requires every entry to be there, which is the question
    the gate was added to ask. (docs/audits/0.1.0.md, QE10-1.)
    """
    config = tomllib.loads((PROJECT / "pyproject.toml").read_text(encoding="utf-8"))
    include = config["tool"]["hatch"]["build"]["targets"]["sdist"]["include"]
    missing = [pattern for pattern in include if not (PROJECT / pattern.lstrip("/")).exists()]
    assert not missing, missing


def test_every_action_the_release_uses_is_pinned_to_a_commit():
    unpinned = [
        line.strip()
        for line in release_yml().splitlines()
        if "uses:" in line and not re.search(r"@[0-9a-f]{40}\b", line)
    ]
    assert not unpinned, unpinned


def test_the_tag_that_publishes_also_gets_a_github_release():
    """LOW-68: CHANGELOG.md links every version heading to `releases/tag/vX.Y.Z`, and
    nothing in this workflow ever made that page — only the tag and the PyPI upload did
    — so the link 404s after a successful publish as well as before it. A job here has
    to actually create the Release, gated and scoped the way `publish` itself is: only a
    tag, only after `publish` has succeeded, and `contents: write` no wider than the one
    job that needs it."""
    text = release_yml()
    release = text[text.index("\n  github_release:") :]
    assert "startsWith(github.ref, 'refs/tags/')" in release
    assert "needs: publish" in release
    assert "gh release create" in release
    assert "contents: write" in release
    # Scoped to this job alone: `publish` needs only `id-token: write`, and the
    # top-level block (every other job's default) is `contents: read`.
    granted = [
        ln
        for ln in text.splitlines()
        if "contents: write" in ln and not ln.lstrip().startswith("#")
    ]
    assert len(granted) == 1, granted


DOCS_NAMED = re.compile(r"docs/[A-Za-z0-9_./-]+\.md")
# The shape a module writes when it sends a reader to a document. Fixture paths in
# docstrings — `docs/bad.md`, `docs/note1.md` — match it too and are filtered by asking
# the repository whether the file is really there, which is the honest filter: a path that
# names nothing cannot be a promise to anyone.


def test_the_wheel_carries_every_document_a_shipped_string_names():
    """`pip install claims-ledger` resolves the `py3-none-any` wheel, and the wheel is
    built from `packages = ["src/claims_ledger"]` — so `docs/` was in the sdist include
    list and in no wheel at all, while `claims-ledger new` told every new project to read
    `docs/OPERATING.md` and a checker failure named it again. Measured against 0.0.3 from
    PyPI: no `docs` directory anywhere in the installed package.

    Built rather than read off the config, because the config is what was wrong. An
    `exclude` beside the force-include looks like it would keep the 11 MB of rendered
    videos out and does not — force-included files are not subject to it, measured: the
    wheel came to 11 MB with the videos in it. The subtrees are named one at a time now,
    and this is what says a document added beside them was added to that list too.
    """
    build = pytest.importorskip("hatchling.build")
    if not (PROJECT / "pyproject.toml").is_file():
        pytest.skip("not a checkout; this builds the distribution from it")

    named = set()
    for module in sorted((PROJECT / "src" / "claims_ledger").glob("*.py")):
        named |= set(DOCS_NAMED.findall(module.read_text(encoding="utf-8")))
    real = sorted(p for p in named if (PROJECT / p).is_file())
    assert real, "no module names a document; this test has stopped asking anything"

    cwd = os.getcwd()
    os.chdir(PROJECT)
    try:
        with tempfile.TemporaryDirectory() as out:
            name = build.build_wheel(out)
            with zipfile.ZipFile(Path(out) / name) as wheel:
                carried = set(wheel.namelist())
    finally:
        os.chdir(cwd)

    missing = [p for p in real if f"claims_ledger/{p}" not in carried]
    assert not missing, f"named by a shipped string and absent from the wheel: {missing}"

    # And the two heavy subtrees stay out, so the wheel does not grow by 11 MB of GIFs the
    # moment somebody widens the list above.
    heavy = sorted(n for n in carried if "/docs/videos/" in n or "/docs/figures/" in n)
    assert not heavy, f"the wheel carries what is served from the repository: {heavy[:4]}"
