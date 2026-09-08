# Agent skills

Three skills for a coding-agent harness working in a repository whose ledger pins claims
to code. Like the hooks in `../agent-harness/`, they are **examples, not part of the
package**: nothing installs them, nothing supports them, and the package itself has no
dependency on any agent harness. Copy them into your project and adapt.

This repository uses them on itself. `.claude/skills/` holds symlinks into this directory
rather than copies, for the same reason `.claude/settings.json` points at the hooks here:
one copy is what stops the example rotting.

They can show citation syntax literally — `(L0001-a-slug, cites-as-live)` — because
neither `examples/` nor `.claude/` is a configured document, so nothing scans them for
citations. Keep it that way if you move them: a skill inside the document globs would have
its examples checked as real citations and fail.

## What they are for

The five checkers say precisely what is wrong. They do not say which of several
legitimate repairs is the right one, and that is where an agent goes wrong — reliably,
and in the same direction each time.

| skill | the mistake it exists to prevent |
| --- | --- |
| `tagging-prose-with-claims` | Writing entries before deciding where their citations will physically sit. A citation inside a pinned section drifts every claim pinned there, so the Nth citation added to a definition supersedes the N−1 entries already on it. Decided up front, the cost is paid once. |
| `choosing-a-citation-act` | Treating `contested` as an emergency. `cites-as-live` is not the goal — an honest status with a matching act is. There are four legitimate outcomes when an entry's status moves, and supersession is the most expensive of them. |
| `repair-a-drifted-pin` | Reaching for the drift procedure when the finding was not drift, and carrying a wrong ground forward into the successor so the next unrelated edit costs another supersession. |

They divide the same way the checkers do: `tagging-prose-with-claims` is for writing,
`choosing-a-citation-act` is for `references`, `repair-a-drifted-pin` is for `freshness`.
Each says at the top when it is the wrong skill and which is the right one.

## Installing them (Claude Code)

Copy this directory into your project, then either point `.claude/skills/` at it —

    mkdir -p .claude/skills
    ln -s ../../examples/agent-skills/choosing-a-citation-act .claude/skills/
    ln -s ../../examples/agent-skills/tagging-prose-with-claims .claude/skills/
    ln -s ../../examples/agent-skills/repair-a-drifted-pin .claude/skills/

— or copy the directories in, if your harness does not follow symlinks. Symlinks are what
this repository uses, so that editing the shipped example and editing the skill the agent
loads are the same act.

`../agent-harness/ledger-orientation.sh` names all three at session start; the hooks name
the relevant one at the moment its failure appears.

## Writing another one

Keep them project-agnostic, as the hooks are: ask the tool rather than restating what it
would say. **Do not write counts into a skill** — "eight entries, all pinned into commit
`4023af40`" was true for about a day, and nothing checks a number in prose. `claims-ledger
status` is the count.
