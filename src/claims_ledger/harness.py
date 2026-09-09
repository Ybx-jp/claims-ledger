"""The coding-agent harness this package ships, and where each agent keeps it.

The hooks and the skills used to sit in `examples/`, where nothing installed them: a
reader copied the directory, adjusted the `..` counts, and wrote the hook wiring out by
hand. They are package data now, under `resources/`, so an installed copy carries them
and `claims-ledger harness install` writes them into a project that has never seen this
repository.

Nothing in them is agent-specific — the scripts speak one JSON hook protocol and the
skills are Markdown with frontmatter — so what an agent changes is only *where* the files
go, what the skill's entry file is called, and how the agent is told the hooks exist. That
is a table, `TARGETS`, and adding an agent is a row rather than a branch.

The package still declares no runtime dependencies. The hook scripts need `jq` when they
run, which is a property of a shell script somebody chose to install, not of importing
this module or of the checkers a pre-commit hook runs.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from .config import leaves_root
from .schema import write_bytes_atomically

RESOURCES = Path(__file__).resolve().parent / "resources"
# A plain path rather than `importlib.resources`, and the same idiom the corpus runner
# uses for its seeds: both are directory trees inside the package, read from a wheel
# unpacked onto a filesystem, and a Traversable buys nothing a zip-imported copy could
# use — the hook scripts have to become real files at real paths before any agent can
# execute them (L0178-the-shipped-harness-is-found-beside-the-package, cites-as-live).

HOOKS = RESOURCES / "agent-harness"
SKILLS = RESOURCES / "agent-skills"


@dataclass(frozen=True)
class Target:
    """One agent: where its skills and hooks live, and what tells it they are there."""

    label: str
    skills: str
    entry: str
    hooks: str
    wiring: str | None
    wires_hooks: bool


TARGETS = {
    "claude": Target(
        label="Claude Code",
        skills=".claude/skills",
        entry="SKILL.md",
        hooks=".claude/hooks",
        wiring=".claude/settings.json",
        wires_hooks=True,
    ),
    "codex": Target(
        label="Codex",
        skills=".codex/skills",
        entry="SKILL.md",
        hooks=".codex/hooks",
        wiring="AGENTS.md",
        wires_hooks=False,
    ),
    "cursor": Target(
        label="Cursor",
        skills=".cursor/rules",
        entry="{name}.mdc",
        hooks=".cursor/hooks",
        wiring=None,
        wires_hooks=False,
    ),
    "agents": Target(
        label="an AGENTS.md agent",
        skills=".agents/skills",
        entry="SKILL.md",
        hooks=".agents/hooks",
        wiring="AGENTS.md",
        wires_hooks=False,
    ),
}
# One row per agent, and every difference between them is in it: the skill directory, the
# name the entry file takes there, where the scripts go, and the file that has to name
# them. A target whose hook protocol this package cannot write says so with `wires_hooks`
# rather than being left out — the scripts are still worth installing for somebody
# adapting them, which is what `--hooks` asks for
# (L0179-an-agent-is-a-row-in-one-table, cites-as-live).


def skill_names():
    return sorted(p.name for p in SKILLS.iterdir() if (p / "SKILL.md").is_file())


class MissingResources(Exception):
    """Raised when the installed package does not carry what it is being asked to write."""


def resources_or_refuse():
    """The skills and the hook scripts, or an exception naming what is not there.

    An install writes what the package carries, so a package that carries nothing writes
    nothing — and printed a clean report of a plan with no files in it, exit 0, which is
    the one report this tool must never produce. It is not hypothetical: a symlink from
    `.claude/skills/` into `src/` makes the build follow it, count each skill as seen at
    a path no distribution includes, and drop all three from the wheel and the sdist
    without a word (L0187-an-install-with-nothing-to-install-refuses, cites-as-live).
    """
    try:
        skills = skill_names()
        scripts = sorted(p.name for p in HOOKS.glob("*.sh"))
    except OSError as exc:
        raise MissingResources(f"{RESOURCES} could not be read ({exc.strerror or exc})") from exc
    if not skills or not scripts:
        raise MissingResources(
            f"the installed package carries no {'skills' if not skills else 'hook scripts'} "
            f"under {RESOURCES}; nothing was installed, because an install that writes "
            "nothing and reports success is worse than one that fails"
        )
    return skills, scripts


def frontmatter(text):
    """(the frontmatter of a skill as a dict, the body after it).

    Two fields and no parser: the skills this ships carry `name` and `description`, both
    written on one line, and a YAML dependency to read two keys would be a runtime
    dependency this package does not have.
    """
    if not text.startswith("---\n"):
        return {}, text
    head, _, body = text[4:].partition("\n---\n")
    fields = {}
    for line in head.splitlines():
        key, sep, value = line.partition(":")
        if sep and not key.startswith(" "):
            fields[key.strip()] = value.strip()
    return fields, body


def entry_text(target, name, source_text):
    """The skill's entry file as `target` wants it written.

    Only Cursor asks for anything: it reads `.cursor/rules/**/*.mdc`, whose frontmatter is
    `description` and `alwaysApply` rather than a skill's `name` and `description`. The
    body is untouched in every case — a skill rewritten per agent is three skills to keep
    true instead of one, and the reference/ links in it are relative, which is why the
    rule file goes in a directory of its own rather than beside its own reference/
    (L0180-a-skill-is-installed-once-and-reframed-never, cites-as-live).
    """
    if not target.entry.endswith(".mdc"):
        return source_text
    fields, body = frontmatter(source_text)
    description = fields.get("description", name)
    return f"---\ndescription: {description}\nalwaysApply: false\n---\n{body}"


def settings_json(target):
    """The hook wiring for an agent whose protocol this package can write."""

    def command(script):
        return {"type": "command", "command": f"$CLAUDE_PROJECT_DIR/{target.hooks}/{script}"}

    return (
        json.dumps(
            {
                "hooks": {
                    "SessionStart": [{"hooks": [command("ledger-orientation.sh")]}],
                    "PreToolUse": [{"matcher": "Bash", "hooks": [command("merge-guard.sh")]}],
                    "PostToolUse": [
                        {
                            "matcher": "Edit|Write|MultiEdit",
                            "hooks": [command("pin-guard.sh"), command("status-guard.sh")],
                        }
                    ],
                }
            },
            indent=2,
        )
        + "\n"
    )


def agents_paragraph(target):
    """What to add to an AGENTS.md, for an agent that reads one and runs no hooks."""
    return (
        "## The claims ledger\n\n"
        "This project keeps a claims ledger: entries stating what it is answerable for, "
        "each grounded in the artifact that makes it true and cited from the prose that "
        "says the same thing in words. `claims-ledger check` runs the five checkers, and "
        "`claims-ledger --help` lists every command.\n\n"
        f"The procedures for the findings they report are in `{target.skills}/`: "
        + ", ".join(f"`{name}`" for name in skill_names())
        + ". Read the one the finding routes to before repairing anything.\n"
    )


@dataclass
class Written:
    """What one planned file did: written, already there, or left alone because it differs."""

    path: Path
    state: str


def plan(target, root, hooks=None):
    """[(destination, bytes, mode)] for every file this install would write.

    Composed before anything is written, so that the containment question can be asked of
    every name before the first one lands, and so that `harness list` can print where an
    agent's files would go without writing any of them.
    """
    files = []
    for name in resources_or_refuse()[0]:
        source = SKILLS / name
        skill_dir = root / target.skills / name
        text = (source / "SKILL.md").read_text(encoding="utf-8")
        files.append((skill_dir / target.entry.format(name=name), entry_text(target, name, text)))
        for path in sorted((source / "reference").glob("*.md")):
            files.append((skill_dir / "reference" / path.name, path.read_text(encoding="utf-8")))
    planned = [(path, text.encode("utf-8"), None) for path, text in files]

    if target.wires_hooks if hooks is None else hooks:
        for path in sorted(HOOKS.iterdir()):
            if not path.is_file():
                continue
            # Mode 0o755 is asserted rather than carried over. A wheel is a zip and an
            # installer need not take an executable bit out of one, so a hook written with
            # whatever permissions the packaged file happens to have is a hook the agent
            # silently never runs — a guard that does not exist, installed
            # (L0181-an-installed-hook-script-is-executable, cites-as-live).
            mode = 0o755 if path.suffix == ".sh" else None
            planned.append((root / target.hooks / path.name, path.read_bytes(), mode))
    return planned


def install(target, root, hooks=None, force=False):
    """Write the plan, and say of every file which of three things happened to it.

    Nothing already in the project is written over. A file whose bytes already match is
    `present` and the install is idempotent; a file that differs is `differs` and is left
    exactly as it was, because a project's `.claude/` is a place people edit and an
    installer that overwrites an edited hook is an installer nobody can re-run
    (L0182-an-install-writes-over-nothing-it-did-not-write, cites-as-live).
    """
    written = []
    for path, data, mode in plan(target, root, hooks=hooks):
        outside = leaves_root(root, path)
        if outside is not None:
            # Every name is asked where it really leads before the write, the question
            # `init` and `hook --install` ask of theirs: a symlink planted at any of these
            # paths is a write outside the project reported as a write inside it
            # (L0183-the-harness-is-not-installed-through-an-escaping-link, cites-as-live)
            written.append(Written(path, f"outside the project, at {outside}"))
            continue
        if os.path.lexists(path):
            try:
                same = path.is_file() and path.read_bytes() == data
            except OSError:
                same = False
            if same:
                written.append(Written(path, "present"))
                continue
            if not force:
                written.append(Written(path, "differs"))
                continue
        path.parent.mkdir(parents=True, exist_ok=True)
        write_bytes_atomically(path, data, mode=mode)
        written.append(Written(path, "wrote"))
    return written


def wiring_text(target):
    """What has to name the hooks, for the file `target` keeps it in; None when nothing does."""
    if target.wiring is None:
        return None
    return settings_json(target) if target.wires_hooks else agents_paragraph(target)


def wiring_marker(target):
    """The string whose presence in the wiring file means this install is already wired.

    A script's name rather than the path this install would have written, because the
    question is whether the settings file already names these hooks and not whether it
    names them where this command would have put them: a project running the copy inside
    the installed package — which is what this repository does — is wired, and telling it
    otherwise on every run would teach it to ignore the answer.
    """
    return "pin-guard.sh" if target.wires_hooks else f"{target.skills}/"


def install_wiring(target, root):
    """Write the file that names the hooks, or report that the project already has one.

    A settings file is written when the project has none and is never edited when it has
    one: it is a file people put their own hooks and permissions in, and a merge this
    package performed behind them would be a change to their harness they did not make.
    An existing file that already names these hooks is `present` and the install is
    idempotent; one that does not is `exists`, and the text it needs is printed for a
    person to place (L0184-a-settings-file-is-written-when-absent-and-printed-when-not,
    cites-as-live).
    """
    text = wiring_text(target)
    if text is None:
        return None
    path = root / target.wiring
    outside = leaves_root(root, path)
    if outside is not None:
        return Written(path, f"outside the project, at {outside}")
    if os.path.lexists(path):
        try:
            already = wiring_marker(target) in path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            already = False
        return Written(path, "present" if already else "exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    write_bytes_atomically(path, text.encode("utf-8"))
    return Written(path, "wrote")
