# Agent skills

Three skills for a coding-agent harness working in a repository whose ledger pins claims
to code. Like the hooks in `../agent-harness/`, they are **examples, not part of the
package**: nothing installs them, nothing supports them, and the package itself has no
dependency on any agent harness. Copy them into your project and adapt.

This repository uses them on itself. `.claude/skills/` holds symlinks into this directory
rather than copies, for the same reason `.claude/settings.json` points at the hooks here:
one copy is what stops the example rotting.

They ship as defaults, so they carry no citations and name no entry ids — a stranger's
ledger has its own. They can show the citation syntax literally,
`(L0001-a-slug, cites-as-live)`, because neither `examples/` nor `.claude/` is a
configured document and nothing scans them for citations. Moving a skill inside the
document globs would have that example checked as a real citation.

## What they are for

The five checkers say precisely what is wrong. Several repairs are usually legitimate,
they differ in cost and in what they assert, and choosing among them is a judgement the
checkers deliberately leave open. These carry what that choice depends on.

| skill | what it covers |
| --- | --- |
| `tagging-prose-with-claims` | Turning prose into entries: where a citation will physically sit and what that costs, the two-commit shape, ground width, and the wording rules `validate` applies to an Assertion. |
| `choosing-a-citation-act` | The acts, the statuses each is legal against, and the four repairs available when an entry's status moves — what each asserts and what each costs. |
| `repair-a-drifted-pin` | The drift procedure, and how to tell a drift from the findings that look like one; choosing the successor's ground rather than carrying the old one forward. |

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
would say. **No counts.** A skill that names how many entries a ledger has, or which
commit its pins sit on, is wrong as soon as an entry lands, and nothing checks a number in
prose. `claims-ledger status` is the count.
