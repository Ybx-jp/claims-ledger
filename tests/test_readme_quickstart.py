"""The README's Quickstart is a transcript, not a story: every line after a `$ ` claims
to be what running that command actually prints. LOW-67 found that it was not — the
commands as shown left the entry's Grounds and grade unfilled, and `claims-ledger check`
reported a real failure where the transcript printed `0 failure(s)`.

This runs the transcript for real, against a fresh project, and checks each command's
actual output against what the README prints for it — so a Quickstart that drifts from
what it claims fails this suite before it fails a reader.
"""

from __future__ import annotations

import re
import shlex
import subprocess
from pathlib import Path

from claims_ledger import cli

PROJECT = Path(__file__).resolve().parent.parent


def quickstart_console_block():
    """The first ```console fence under the README's `## Quickstart` heading."""
    readme = (PROJECT / "README.md").read_text(encoding="utf-8")
    after_heading = readme.split("## Quickstart", 1)[1]
    fenced = after_heading.split("```console", 1)[1]
    return fenced.split("```", 1)[0].strip("\n")


def parse_transcript(block):
    """[(argv, None, expected_lines) | (None, (path, content), [])], in order.

    A step is either a `claims-ledger ...` invocation, whose argv is compared against
    `expected_lines`, or a `cat > path <<'EOF' ... EOF` heredoc — standing in for a
    reader's editor — that stages a file before the next command reads it.
    """
    lines = block.splitlines()
    steps = []
    i = 0
    while i < len(lines):
        if not lines[i].startswith("$ "):
            i += 1
            continue
        cmd = lines[i][2:]
        i += 1
        while cmd.rstrip().endswith("\\"):
            cmd = cmd.rstrip()[:-1] + " " + lines[i].strip()
            i += 1
        heredoc_open = re.search(r"<<'?(\w+)'?\s*$", cmd)
        if heredoc_open:
            delim = heredoc_open.group(1)
            target_match = re.match(r"cat > (\S+) <<", cmd)
            assert target_match, f"heredoc command is not `cat > path <<...`: {cmd!r}"
            target = target_match.group(1)
            body = []
            while lines[i] != delim:
                body.append(lines[i])
                i += 1
            i += 1  # past the delimiter line itself
            steps.append((None, (target, "\n".join(body) + "\n"), []))
            continue
        expected = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("$ "):
            expected.append(lines[i])
            i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        assert cmd.startswith("claims-ledger "), f"not a claims-ledger command: {cmd!r}"
        steps.append((shlex.split(cmd[len("claims-ledger ") :]), None, expected))
    return steps


def matches(want, got, root):
    """`want` is a line from the README: `…` stands for elided, machine-specific or
    content-addressed text (a hash, a truncated listing), and the literal placeholder
    path is the project root the test actually used."""
    want = want.replace("/home/you/project", str(root))
    pattern = "^" + re.escape(want).replace(re.escape("…"), ".*") + "$"
    return re.match(pattern, got) is not None


def test_the_quickstart_transcript_is_reproducible(tmp_path, capsys, monkeypatch):
    """Every command the README shows in Quickstart, run in order against a fresh
    project, prints what the README says it prints — including the final `check`,
    which is the line LOW-67 found lying."""
    root = tmp_path / "project"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(
        ["git", "-C", str(root), "config", "user.email", "quickstart@example.com"], check=True
    )
    subprocess.run(["git", "-C", str(root), "config", "user.name", "quickstart"], check=True)
    monkeypatch.chdir(root)

    steps = parse_transcript(quickstart_console_block())
    assert steps, "found no `claims-ledger` commands in the Quickstart console block"

    for argv, heredoc, expected in steps:
        if heredoc is not None:
            target, content = heredoc
            (root / target).write_text(content, encoding="utf-8")
            continue
        capsys.readouterr()
        code = cli.main(argv)
        out = capsys.readouterr().out.splitlines()
        command = "claims-ledger " + " ".join(argv)
        assert code == 0, f"`{command}` exited {code}, printing {out!r}"
        # The README may stop showing a command's output before the real thing does —
        # `init`'s trailing `Next: ...` hint is never shown — but never past it, and
        # never with a line that says something the command did not actually print.
        assert len(out) >= len(expected), (
            f"`{command}` printed {len(out)} line(s) {out!r}; "
            f"the README shows {len(expected)}, more than the command produced: {expected!r}"
        )
        for got, want in zip(out, expected, strict=False):
            assert matches(want, got, root), (
                f"`{command}` printed {got!r}; the README shows {want!r}"
            )
