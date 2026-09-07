# nothing-falls-silently — beat sheet

**One sentence.** A claim carries its evidence; a verdict is a row that only ever gets
appended; the status is derived from the last row; and when a claim falls, everything
that rested on it — entries and documents — is told, and the commit is refused until
they say so too.

**Audience** a reader arriving at the README. **Duration** 32 s (960 frames at 30 fps).
**Frame** 1920 × 1080. **Delivery** silent H.264 (`--muted`), plus a GIF for the README.
**Sound** none.

**Surfaces.** Two, and the product has exactly these two: a file and a shell. Every
line drawn is a line `tools/capture.py` captured from a fresh materialization of
`examples/` — the R0001 entry, the verdict a person appends, each command's output, the
hook's refusal — with provenance (date, claims-ledger commit, pinned commit) recorded in
`src/captures.ts`. The status table is cropped to the three entries in the story and
says how many rows it elides. Nothing on screen is invented; the film adds order,
emphasis and time.

| beat | frames | file pane | shell | the viewer should understand |
|---|---|---|---|---|
| entry | 0–120 | R0001 from its Assertion: Scope, Grounds (an experiment at a commit, a registered source) | `status` — R0001 open | a claim file, with its evidence, and a status |
| check | 120–210 | — | `check` — five lines, all zero, exit 0 | five checkers, all clean |
| verdict | 210–390 | scrolls to the APPEND marker; a `refuted` row lands under Verdicts, `author: main` | `status` — R0001 refuted | one row appended by hand; the status follows it, nothing else edited |
| fail | 390–540 | — | `check` — FAIL R0002, R0003, README.md, ROSTER.md; propagate FAIL ×2; exit 1 | everything that cited it live now fails |
| propagate | 540–720 | cuts to R0003: a `contested` row, `author: propagation`, `evidence: … R0001 · fallen` | `propagate --write` — FLAG appended; `status` — R0002, R0003 contested | the machine writes the dependents their row |
| gate | 720–840 | — | `git commit` — the hook runs `check`, 8 FAIL lines, exit 1 | the commit is refused until the citations are fixed |
| thesis | 840–960 | — | — | *Nothing falls silently.* |

**Emphasis, and what it rests on.** The shell's own tokens `FAIL` and `FLAG` carry the
accent on their whole line, as a colouring shell would show them; a status that has just
changed and a verdict row that has just landed sit on accent-soft while they are new and
settle to plain. The `→ exit N` after a command is the one authorial annotation: a shell
does not print its exit code, and the film's claim about the gate rests on it.

**Motion.** The one tracked move is the file pane's scroll to the APPEND marker, on the
quadratic slow-in/slow-out Dragicevic et al. (CHI 2011) measured; the track matte
checks it against `fileScrollPx`. Lines arrive one after another and accumulate; a
command's output replaces the previous command's at a beat boundary, as a terminal
would scroll it away. Fades are linear and monotonic.

**Dwell.** The longest unit a beat asks to be read is a FAIL line of ~150 characters; at
12–20 cps that is 7.5–12.5 s, and the beat that shows six of them holds 5 s. The intent
is that the viewer reads `FAIL`, the four names and the exit code, not every clause;
the clauses are there because they are what the product says.
