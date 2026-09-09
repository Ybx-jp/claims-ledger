"""The shipped agent harness, and what `claims-ledger harness install` promises about it.

The hooks and skills are package data now rather than an example somebody copies, so what
holds them is the same thing that holds the checkers: a test per promise. The install
writes into a project's own directories, and every one of these is about not damaging
something a person put there.
"""

import json
import os
import stat

import pytest

from claims_ledger import cli, harness

AGENTS = sorted(harness.TARGETS)


def install(root, *args):
    return cli.main(["--root", str(root), "harness", "install", *args])


def test_every_agent_gets_every_skill_with_its_reference_directory(tmp_path):
    for agent in AGENTS:
        root = tmp_path / agent
        root.mkdir()
        assert install(root, "--agent", agent) == 0
        target = harness.TARGETS[agent]
        for name in harness.skill_names():
            entry = root / target.skills / name / "SKILL.md"
            assert entry.is_file(), entry
            assert entry.read_text(encoding="utf-8").strip()
            reference = root / target.skills / name / "reference"
            assert sorted(p.name for p in reference.glob("*.md")) == sorted(
                p.name for p in (harness.SKILLS / name / "reference").glob("*.md")
            )


def test_a_skill_installs_as_the_same_file_under_every_agent(tmp_path):
    """One skill, not one per agent: only the directory it lands in differs."""
    shipped = (harness.SKILLS / "repair-a-drifted-pin" / "SKILL.md").read_bytes()
    for agent in AGENTS:
        root = tmp_path / agent
        root.mkdir()
        assert install(root, "--agent", agent) == 0
        target = harness.TARGETS[agent]
        assert (root / target.skills / "repair-a-drifted-pin" / "SKILL.md").read_bytes() == shipped


def test_every_agent_gets_the_hooks_and_a_settings_file_naming_them(tmp_path):
    for agent in AGENTS:
        root = tmp_path / agent
        root.mkdir()
        assert install(root, "--agent", agent) == 0
        target = harness.TARGETS[agent]
        assert (root / target.hooks / "merge-guard.sh").is_file()
        assert "pin-guard.sh" in (root / target.wiring).read_text(encoding="utf-8")


def test_no_hooks_writes_the_skills_only(tmp_path):
    """For a project running the shipped hooks from where they already are."""
    assert install(tmp_path, "--agent", "claude", "--no-hooks") == 0
    assert (tmp_path / ".claude" / "skills").is_dir()
    assert not (tmp_path / ".claude" / "hooks").exists()


def test_the_hooks_are_installed_executable_where_the_agent_runs_them(tmp_path):
    assert install(tmp_path, "--agent", "claude") == 0
    hooks = tmp_path / ".claude" / "hooks"
    assert (hooks / "merge-guard.cases").is_file()  # the guard's committed verdicts
    for script in hooks.glob("*.sh"):
        assert stat.S_IMODE(script.stat().st_mode) & 0o111 == 0o111, script


def test_the_settings_file_is_written_when_the_project_has_none(tmp_path, capsys):
    assert install(tmp_path, "--agent", "claude") == 0
    settings = json.loads((tmp_path / ".claude" / "settings.json").read_text(encoding="utf-8"))
    commands = [
        hook["command"]
        for event in settings["hooks"].values()
        for matcher in event
        for hook in matcher["hooks"]
    ]
    assert commands == [
        "$CLAUDE_PROJECT_DIR/.claude/hooks/ledger-orientation.sh",
        "$CLAUDE_PROJECT_DIR/.claude/hooks/merge-guard.sh",
        "$CLAUDE_PROJECT_DIR/.claude/hooks/pin-guard.sh",
        "$CLAUDE_PROJECT_DIR/.claude/hooks/status-guard.sh",
    ]

    # An agent with no project-directory variable of its own gets the same file with
    # project-relative commands; the scripts find the root themselves either way.
    other = tmp_path / "codex-project"
    other.mkdir()
    assert install(other, "--agent", "codex") == 0
    assert '".codex/hooks/pin-guard.sh"' in (other / ".codex" / "settings.json").read_text("utf-8")


def test_a_settings_file_that_is_already_there_is_printed_to_and_never_edited(tmp_path, capsys):
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True)
    mine = '{\n  "permissions": {"allow": ["Bash(git status)"]}\n}\n'
    settings.write_text(mine, encoding="utf-8")

    assert install(tmp_path, "--agent", "claude") == 1
    assert settings.read_text(encoding="utf-8") == mine
    printed = capsys.readouterr()
    assert "is not edited by this command" in printed.err
    assert "pin-guard.sh" in printed.out


def test_a_file_that_differs_is_left_alone_and_the_exit_says_so(tmp_path, capsys):
    assert install(tmp_path, "--agent", "claude") == 0
    guard = tmp_path / ".claude" / "hooks" / "merge-guard.sh"
    guard.write_text("# mine now\n", encoding="utf-8")

    assert install(tmp_path, "--agent", "claude") == 1
    assert guard.read_text(encoding="utf-8") == "# mine now\n"
    assert "left alone" in capsys.readouterr().err

    assert install(tmp_path, "--agent", "claude", "--force") == 0
    assert "permissionDecision" in guard.read_text(encoding="utf-8")


def test_an_install_that_changed_nothing_exits_zero(tmp_path, capsys):
    assert install(tmp_path, "--agent", "claude") == 0
    capsys.readouterr()
    assert install(tmp_path, "--agent", "claude") == 0
    out = capsys.readouterr().out
    assert "wrote" not in out
    assert (
        out.count("present") == len(harness.plan(harness.TARGETS["claude"], tmp_path)) + 1
    )  # the settings file, which already names these hooks


def test_nothing_is_written_through_a_link_that_leaves_the_project(tmp_path, capsys):
    outside = tmp_path / "outside"
    outside.mkdir()
    root = tmp_path / "project"
    (root / ".claude").mkdir(parents=True)
    (root / ".claude" / "hooks").symlink_to(outside)

    assert install(root, "--agent", "claude") == 2
    assert not list(outside.iterdir())
    assert "outside the project" in capsys.readouterr().err


def test_the_installer_needs_no_ledger(tmp_path):
    """Installing the harness is a thing to do before `init`, not after it."""
    assert not (tmp_path / "claims-ledger.toml").exists()
    assert install(tmp_path, "--agent", "claude") == 0


def test_list_prints_a_row_for_every_agent(capsys):
    assert cli.main(["harness", "list"]) == 0
    out = capsys.readouterr().out
    for agent in AGENTS:
        assert agent in out


@pytest.mark.parametrize("script", sorted(p.name for p in harness.HOOKS.glob("*.sh")))
def test_no_hook_script_counts_directories_to_the_project_root(script):
    """The same file runs from inside the package and from a project's own hook directory,
    so a fixed `..` count would guard the wrong tree from one of them."""
    text = (harness.HOOKS / script).read_text(encoding="utf-8")
    if "project_root" not in text:
        pytest.skip(f"{script} needs no project root")
    assert 'cd -- "$here/../.."' not in text
    assert "CLAIMS_LEDGER_PROJECT_DIR" in text


def test_the_shipped_resources_are_beside_the_package(tmp_path):
    """What a wheel carries is what these paths name, so they are asserted rather than
    assumed: an install from a wheel with no `resources/` in it would write nothing and
    say it had."""
    assert (harness.HOOKS / "merge-guard.sh").is_file()
    assert harness.skill_names() == [
        "choosing-a-citation-act",
        "repair-a-drifted-pin",
        "tagging-prose-with-claims",
    ]
    assert os.path.samefile(harness.RESOURCES.parent, os.path.dirname(cli.__file__))


def test_an_install_with_nothing_to_install_refuses(tmp_path, monkeypatch, capsys):
    """A package that carries no resources writes nothing, and must not report success."""
    empty = tmp_path / "empty-resources"
    (empty / "agent-skills").mkdir(parents=True)
    (empty / "agent-harness").mkdir()
    monkeypatch.setattr(harness, "RESOURCES", empty)
    monkeypatch.setattr(harness, "SKILLS", empty / "agent-skills")
    monkeypatch.setattr(harness, "HOOKS", empty / "agent-harness")

    root = tmp_path / "project"
    root.mkdir()
    assert install(root, "--agent", "claude") == 2
    assert "carries no skills" in capsys.readouterr().err
    assert not (root / ".claude").exists()


def test_no_symlink_in_the_repository_reaches_into_the_package(repository):
    """A symlink out of `.claude/` into `src/` silently empties the distribution.

    hatchling follows it, counts each file as seen at a path no `include` covers, and
    drops the real one from the wheel and the sdist with no error at all. The skills were
    symlinked that way and shipped as nothing; `.claude/skills/` is a local install now,
    and this is what stops the shortcut coming back.
    """
    package = (repository / "src" / "claims_ledger").resolve()
    for path in repository.rglob("*"):
        if not path.is_symlink() or ".git/" in str(path) or "/worktrees/" in str(path):
            continue
        resolved = (path.parent / os.readlink(path)).resolve()
        assert package not in resolved.parents and resolved != package, path


def test_a_built_distribution_carries_every_shipped_resource(tmp_path, repository):
    """What the wheel holds is what an installed copy can write, so it is measured."""
    build = pytest.importorskip("hatchling.build")
    shipped = {
        str(p.relative_to(repository / "src"))
        for p in (harness.RESOURCES).rglob("*")
        if p.is_file()
    }
    cwd = os.getcwd()
    os.chdir(repository)
    try:
        name = build.build_wheel(str(tmp_path))
    finally:
        os.chdir(cwd)
    import zipfile

    with zipfile.ZipFile(tmp_path / name) as wheel:
        carried = {n for n in wheel.namelist() if "/resources/" in n}
    assert {n for n in shipped} == carried
