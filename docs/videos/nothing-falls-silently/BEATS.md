# Two films on the product's own surfaces

**nothing-falls-silently** (70.5 s) and **replaced-never-edited** (51.7 s). Both are built
from one timeline vocabulary (`src/timeline.ts`) by one builder each (`src/scenarios.ts`),
and rendered by one component (`src/Film.tsx`) that draws whatever the timeline says.

**Audience** a reader arriving at the README. **Frame** 1920 × 1080 at 30 fps.
**Delivery** silent H.264 (`--muted`) and a 960-wide GIF at 10 fps. **Sound** none.

**Surfaces.** Two, and the product has exactly these two: a file and a shell. Every line
drawn is a line `tools/capture.py` captured from a fresh materialization of `examples/`
— the entries, the new entry an author writes and fingerprints with `sha --write`, the
verdict a person appends, each command's output, the hook's answer — with provenance
(date, claims-ledger commit, pinned commit) recorded in `src/captures.ts`. The status
table is cropped to the entries in the story and says how many rows it elides. Nothing
on screen is invented; the films add order, emphasis and time.

## nothing-falls-silently — the refuted case

| beat | file pane | shell | the viewer should understand |
|---|---|---|---|
| 1 · a claim | R0001 from its Assertion; spotlight on Grounds | `status`; spotlight: *Its status is open: no verdict has been written.* | a claim file, with its evidence, and a status |
| 2 · check | — | `check`, five zeros, exit 0 | five checkers, all clean |
| 3 · a new claim | cuts to R0013, spotlight on its Assertion: *A new claim is written. It refutes R0001.*; cuts to R0001 at the APPEND marker, spotlight on the empty place: *R0001 is refuted. The verdict names the new claim.* — and the row lands inside it, `evidence: entry: R0013 · cites-as-live` | `status`: *The status follows the last verdict: refuted.* | a new claim is written; the old one gets a verdict naming it; the status follows |
| 4 · what fails | — | `check`: FLAG (measured evidence against a preregistered claim, for review), FAIL R0002, R0003, README.md, ROSTER.md, propagate FAIL ×2, exit 1; spotlight on the four | everything that cited it live now fails |
| 5 · propagate | cuts to R0003: a `contested` row, `author: propagation`, `evidence: … R0001 · fallen` | `propagate --write` FLAG appended; `status`: both dependents contested | the machine writes the dependents their row |
| 6 · the gate | — | `git commit`: the hook runs the five checkers, exit 1 | the commit is refused until the citations are fixed |
| thesis | | | *Nothing falls silently.* |

## replaced-never-edited — the superseded case

| beat | file pane | shell | the viewer should understand |
|---|---|---|---|
| 1 · a claim | R0006 from its Assertion; spotlight on Grounds | `status` — R0005 already superseded, R0006 open | a claim file, with its evidence, and a status |
| 2 · check | — | `check`, clean | five checkers, all clean |
| 3 · a successor | cuts to R0013, spotlight on `supersedes: R0006…`: *A new claim is written. It supersedes R0006.*; cuts to R0006 at the marker: *R0006 is superseded. The verdict names its successor.* — the row lands, `evidence: entry: R0013 · supersedes` | `status`: *The status follows the last verdict: superseded.* | succession is recorded on both sides |
| 4 · check | — | `check`, clean: *Successor and predecessor name each other. All clean.* | nothing cited R0006 live, and both sides agree, so nothing fails |
| 5 · the gate | — | `git commit`: the hook runs the five checkers, exit 0: *Accepted.* | the chain R0005 → R0006 → R0013 is on the record |
| thesis | | | *A claim is replaced, never edited.* |

The successor keeps the predecessor's Scope; a successor whose verbatim record differs
must declare `verbatim_change`, and the checker said so when the first draft did not.

## Captions

One concept each, in the product's words, at most ~55 characters so each reads in about
three seconds at 15 characters per second. The verdict is introduced as what it is — a
new claim, then the verdict on the old one naming it — not as the number the rerun
produced, which lives in the row. Holds are long: the first cut was judged too fast to
comprehend, and every spotlight now stays up 3–5 s.

## Emphasis, and what it rests on

The shell's own tokens `FAIL` and `FLAG` carry the accent on their whole line, as a
colouring shell would show them; a status that has just changed and a verdict row that
has just landed sit on accent-soft while they are new and settle to plain. The `→ exit N`
after a command is the one authorial annotation: a shell does not print its exit code,
and the films' claim about the gate rests on it.

## Render contract, and what it found

Two renders of each film are byte-identical; each stream is 1920 × 1080 at 30 fps with no
audio; the faces are verified by advance width; the contact sheets sample start, midpoint
and end of every move plus every hold, derived from the timeline.

Determinism was not free. The first full renders differed on 213 frames at ~57 dB.
Lossless stills of the same frames were identical, and ffmpeg encoded the same PNG
sequence identically with and without threads, so the encoder was cleared; PNG
sequences from the video path were not — the same frame came back in two variants at
random. Two causes, both measured by diffing the variants pixel by pixel:

- Text rows in the file pane, |Δ| up to 12 levels: LCD text antialiasing switching on
  and off with compositor layer promotion, which is timing-dependent for an element
  whose opacity changes every frame. Fixed by pinning `-webkit-font-smoothing:
  antialiased` and `will-change: opacity` on everything that fades (`STABLE`).
- Two pixels at (60,127) and (60,647), |Δ| 1: the antialiased top-left corners of the
  two clipping panes. Fixed by giving the panes square corners.

Neither is visible at playback; both would have made "the same source renders the same
pixels" a false statement, which is the contract the ladder holds films to.

There is no tracked move any more — the file pane cuts rather than scrolls — so the
track-matte instrument the earlier cut carried was retired with it.
