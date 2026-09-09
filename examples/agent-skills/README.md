# Agent skills

Three skills for a coding-agent harness working in a project that keeps a claims ledger.
Like the hooks in `../agent-harness/`, they are **examples, not part of the package**:
nothing installs them, nothing supports them, and the package has no dependency on any
agent harness. Copy them into your project and adapt.

They ship as defaults, so they carry no citations and name no entry ids — your ledger has
its own — and they describe the ledger through the two interfaces you actually have: the
`claims-ledger` command and the importable package. Neither points at the package's own
source files, nor at documentation that is not installed alongside it.

A ledger holds claims about whatever the project is answerable for, and the evidence types
a claim may rest on are configured per project: `lab` and `experiment` out of the box, and
a project keeping its ledger over source will usually add `code` and `toml`. Nothing here
assumes what an artifact is. A ground can name a section of a module, a key in a settings
file, a passage in a design document, a notebook, or a run. A frontend and a backend can
share one ledger; so can a paper and the analysis behind it.

## Routing

The checkers name a finding precisely and leave the repair open. Start from what you were
told:

| what you are holding | skill |
| --- | --- |
| prose that promises something and cites nothing | `tagging-prose-with-claims` |
| `<act> against <id>, whose status is …` | `choosing-a-citation-act` |
| `is shaped like a citation but … is not a citation act` | `choosing-a-citation-act` |
| `cites … from outside § "…"` | `choosing-a-citation-act`, then `repair-a-drifted-pin` for the flags moving it causes |
| an entry's status moved and its citations need deciding | `choosing-a-citation-act` |
| two entries that may be about the same thing, or a `claims-ledger neighbours` answer | `choosing-a-citation-act` |
| `has moved`, `withdrawn`, `unstable pin`, `unknown` | `repair-a-drifted-pin` |
| a Scope that names a narrower population than its own metric | `repair-a-drifted-pin` |
| the pre-commit hook refused a commit | run `claims-ledger check`, route on its wording |

| skill | what it covers |
| --- | --- |
| `tagging-prose-with-claims` | Turning a sentence that promises something into an entry: where the citation sits and what that costs, the two-commit shape, choosing a ground, asking which entries are already about it, and the rules `validate` applies to the wording. |
| `choosing-a-citation-act` | Matching an act to a status, the repairs available when a status moves, and relating two entries that turn out to be about the same artifact. |
| `repair-a-drifted-pin` | The findings `freshness` reports, which of them are drift, and how each is discharged — including the supersessions no checker asks for. |

Each skill says at the top when it is the wrong one and which takes over, and carries a
`reference/` directory with the longer material — so the skill itself stays short and the
detail is fetched when it is wanted.

## Installing them (Claude Code)

Copy this directory into your project, then either point `.claude/skills/` at it —

    mkdir -p .claude/skills
    ln -s ../../examples/agent-skills/choosing-a-citation-act .claude/skills/
    ln -s ../../examples/agent-skills/tagging-prose-with-claims .claude/skills/
    ln -s ../../examples/agent-skills/repair-a-drifted-pin .claude/skills/

— or copy the directories in, if your harness does not follow symlinks. Symlinks are what
this repository uses, so that editing the shipped example and editing the skill an agent
loads are the same act.

`../agent-harness/ledger-orientation.sh` hands over the same routing at session start; the
other hooks name the relevant skill when a finding appears.

## Writing another one

**Speak through the CLI and the package.** `claims-ledger --help` lists every command and
`claims-ledger <command> --help` its options. The package exports its own vocabulary —

    python -c "from claims_ledger import STATUSES, ACTS, ENTRY_ACTS, GRADES, KINDS; print(STATUSES)"

— so a skill can say where to look something up instead of copying a table that will be
wrong later. A skill naming a file inside the package, or a document not installed with
it, is pointing somewhere its reader cannot go.

**No counts.** A skill that says how many entries a ledger has, or which commit its pins
sit on, is wrong as soon as an entry lands, and nothing checks a number in prose.
`claims-ledger status` is the count.

**No project-specific assumptions.** The interpreter, the document list, the evidence
types and the statuses are all askable. Ask.

**Hand over the line, not the homework.** A skill that stops at *this is wrong* leaves the
reader to compose the repair from memory. Where the repair has a fixed shape — a ground
line, a verdict block, a command with its flags — write it out, and leave the judgement of
whether to use it where it belongs. `claims-ledger neighbours` is the same idea in the
package: it decides nothing and still prints the exact ground line each of its answers
would take.

**An entry that is owed is written in the pass that owes it.** Prose that promises
something and cites nothing passes every check, so there is nothing that will come back for
a deferred entry. A skill that offers *note it for later* as an outcome is offering the one
outcome the ledger cannot enforce.
