"""The coding-agent harness this package ships, and where each agent keeps it.

The hooks and the skills used to sit in `examples/`, where nothing installed them: a
reader copied the directory, adjusted the `..` counts, and wrote the hook wiring out by
hand. They are package data now, under `resources/`, so an installed copy carries them
and `claims-ledger harness install` writes them into a project that has never seen this
repository.

Nothing in them is agent-specific: the skills are `SKILL.md` with a `reference/` beside
it and the hooks are scripts speaking one JSON protocol, and the agents keep both in the
same shape under a directory of their own. So an agent is one row of `TARGETS` — its
name and its directory — and adding one is a row rather than a branch.

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
    """One agent: its directory, the file that arms its hooks, and the shape that file takes.

    The three fields after the directory are measured rather than assumed, and each one
    is a place a harness differs from Claude Code:

    `wiring` — Cursor and codex declare hooks in `hooks.json`, not `settings.json`.

    `schema` — codex's `hooks.json` *is* Claude Code's block: event keys, matcher groups,
    `{"type": "command", …}` entries. Cursor's is its own: a `version`, its own event
    names, and a flat list per event with no matchers.

    `user_home` — codex reads hooks only from `$CODEX_HOME/hooks.json`. A project-level
    `.codex/hooks.json` is not discovered, so writing one would arm nothing and say it
    had. The row carries the variable and the default rather than a resolved path,
    because the variable is read when the install runs: it is the seam a throwaway home
    reaches through, which is what lets this be tested without writing into the home
    directory of whoever runs the suite.
    """

    label: str
    directory: str
    wiring_file: str = "settings.json"
    schema: str = "claude"
    project_dir: str | None = None
    user_home: tuple[str, str] | None = None

    @property
    def skills(self):
        return f"{self.directory}/skills"

    @property
    def hooks(self):
        return f"{self.directory}/hooks"

    @property
    def wiring(self):
        """Where the wiring goes, as a label: a project-relative path, or the home it lives in."""
        if self.user_home:
            return f"${self.user_home[0]}/{self.wiring_file} (default {self.user_home[1]})"
        return f"{self.directory}/{self.wiring_file}"


TARGETS = {
    "claude": Target("Claude Code", ".claude", project_dir="$CLAUDE_PROJECT_DIR"),
    "codex": Target(
        "Codex", ".codex", wiring_file="hooks.json", user_home=("CODEX_HOME", "~/.codex")
    ),
    "cursor": Target("Cursor", ".cursor", wiring_file="hooks.json", schema="cursor"),
    "agent": Target("any other agent", ".agent"),
}
# One row per agent: its directory, the file that arms its hooks, and which of the two
# schemas that file takes. The scripts and the skills do not vary — they go to
# `<dir>/hooks/` and `<dir>/skills/<name>/SKILL.md` for every agent, and the scripts read
# both payload dialects themselves — so an agent is a row rather than a fork
# (L0179-an-agent-is-a-row-in-one-table, cites-as-live).

WIRING = [
    ("SessionStart", None, "sessionStart", "ledger-orientation.sh"),
    ("PreToolUse", "Bash", "beforeShellExecution", "merge-guard.sh"),
    ("PostToolUse", EDITS := "Edit|Write|MultiEdit|apply_patch", "postToolUse", "pin-guard.sh"),
    ("PostToolUse", EDITS, "postToolUse", "status-guard.sh"),
]
# What runs when, in both vocabularies at once, so that the two schemas below are two
# renderings of one table rather than two tables that can disagree.
#
# `apply_patch` rides in the edit matcher because it is how codex edits a file; the name
# is harmless on a harness that has no such tool. The edit guards take Cursor's
# `postToolUse` rather than its `afterFileEdit`, which is the event that describes what
# happened: measured in cursor-agent 2026.08.11, `afterFileEdit`'s return value is read
# only for file contents, and the events whose `additional_context` reaches the agent are
# exactly sessionStart, beforeSubmitPrompt, preToolUse and postToolUse. A guard wired
# where nothing can hear it is a guard that does not exist
# (L0192-the-cursor-events-are-the-ones-that-can-carry-a-word, cites-as-live).


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


def wiring_json(target, root=None):
    """The hook wiring for `target`, in the schema that agent reads.

    The command path follows the same measurement: `$CLAUDE_PROJECT_DIR` where the agent
    expands it, an absolute path for codex, whose wiring is not in the project at all,
    and a project-relative path for Cursor, which runs a project hook from the project
    root.
    """
    if target.schema == "cursor":
        block = {}
        for _event, _matcher, cursor_event, script in WIRING:
            entry = {"type": "command", "command": f"./{target.hooks}/{script}"}
            block.setdefault(cursor_event, []).append(entry)
        return json.dumps({"version": 1, "hooks": block}, indent=2) + "\n"

    block = {}
    for event, matcher, _cursor_event, script in WIRING:
        entry = {"type": "command", "command": f"{hook_command_prefix(target, root)}{script}"}
        for group in block.setdefault(event, []):
            if group.get("matcher") == matcher:
                group["hooks"].append(entry)
                break
        else:
            group = {"hooks": [entry]}
            if matcher is not None:
                group["matcher"] = matcher
            block[event].append(group)
    return json.dumps({"hooks": block}, indent=2) + "\n"


def wiring_path(target, root):
    """The file that arms `target`'s hooks, resolved now rather than at import.

    codex's is not under the project: the variable is read here so that a session, a test
    or a throwaway home points the write where it belongs.
    """
    if target.user_home:
        env, default = target.user_home
        return Path(os.environ.get(env) or Path(default).expanduser()) / target.wiring_file
    return root / target.directory / target.wiring_file


def hook_command_prefix(target, root=None):
    if target.project_dir:
        return f"{target.project_dir}/{target.hooks}/"
    if target.user_home:
        # codex resolves a relative command against the session's own working directory,
        # and its wiring is one file for every project on the machine, so the only path
        # that names this project's scripts is an absolute one.
        return f"{Path(root or Path.cwd()).resolve() / target.hooks}/"
    return f"{target.hooks}/"


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
        # The same bytes under every agent. A skill rewritten per agent is one skill per
        # agent to keep true, and the `reference/` links in the body are relative, so the
        # directory it sits in is part of what makes it readable
        # (L0191-a-skill-installs-as-the-same-file-under-every-agent, cites-as-live).
        text = (source / "SKILL.md").read_text(encoding="utf-8")
        files.append((skill_dir / "SKILL.md", text))
        for path in sorted((source / "reference").glob("*.md")):
            files.append((skill_dir / "reference" / path.name, path.read_text(encoding="utf-8")))
    planned = [(path, text.encode("utf-8"), None) for path, text in files]

    if hooks is None or hooks:
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
            # (L0193-a-write-is-confined-to-the-directory-it-belongs-to, cites-as-live).
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


def wiring_marker(target):
    """The string whose presence in the wiring file means this install is already wired.

    A script's name rather than the path this install would have written, because the
    question is whether the settings file already names these hooks and not whether it
    names them where this command would have put them: a project running the copy inside
    the installed package — which is what this repository does — is wired, and telling it
    otherwise on every run would teach it to ignore the answer.
    """
    return "pin-guard.sh"


def install_wiring(target, root):
    """Write the file that arms the hooks, or report that the agent already has one.

    A wiring file is written when the agent has none and is never edited when it has one:
    it is where people keep their own hooks and permissions, and a merge performed behind
    them would be a change to their harness they did not make. The text it needs is
    printed instead (L0184-a-settings-file-is-written-when-absent-and-printed-when-not,
    cites-as-live).

    codex's file is not in the project — it reads hooks from `$CODEX_HOME/hooks.json` and
    nowhere else — so containment is asked against the directory the file belongs to
    rather than against the project root, which is the question `hook --install` asks of
    the hooks directory version control names
    (L0193-a-write-is-confined-to-the-directory-it-belongs-to, cites-as-live).
    """
    text = wiring_json(target, root)
    path = wiring_path(target, root)
    outside = leaves_root(path.parent if target.user_home else root, path)
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
