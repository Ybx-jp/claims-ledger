# then-and-later — beat sheet

**One idea.** A sentence outlives what made it true; the ledger notices, prose does not.

**Audience** a reader arriving at the README. **Duration** 24 s (720 frames at 30 fps).
**Frame** 1920 × 1080. **Delivery** silent H.264 (`--muted`), plus a GIF for the README.
**Sound** none.

The words are real and there are few of them. The claim is the Nimbus portfolio's
threshold claim; the source is its API contract; the change that happens later is the
one the examples are built around — the numeral moves from 0.72 to 0.75 and the
sentence above it does not.

| beat | frames | what changes | what stays | the viewer should understand |
|---|---|---|---|---|
| establish | 0–75 | the sentence settles in, centred | — | here is a sentence someone wrote |
| source | 75–165 | the source document rises beneath it; the same words light up in both | the sentence | the sentence quotes this line |
| split | 165–225 | the panel slides left; a copy fades in on the right; PROSE / LEDGER | the words | two worlds, same starting point |
| bind | 225–315 | ledger: a line ties the quotation to the span, the bytes get a fingerprint, the claim is corroborated; prose: the source highlight fades — nothing holds it | the sentence, the source | the ledger keeps the link; prose keeps only the sentence |
| time | 315–405 | a hairline sweeps across the top; LATER; the numeral in the source turns from 0.72 to 0.75 in both worlds | the sentence, in both worlds | the world moved under the sentence |
| outcome | 405–495 | ledger: the line turns accent from the source up, the span becomes an empty dashed place, the fingerprint changes, the chip flips to contested — caught. prose: nothing happens | everything else | one world noticed |
| hold | 495–600 | — | both worlds | compare at leisure |
| thesis | 600–720 | the worlds fade to paper; the one sentence of the film | — | the title, earned |

**Motion choices and what they rest on.**
- The only tracked move is the panel's slide at the split (430 px, half its own width).
  It uses the quadratic slow-in/slow-out Dragicevic et al. (CHI 2011) measured as the
  lowest tracking error of four pacings. One object crosses the frame; the copy fades in
  place rather than moving, so the viewer holds one identity, not two.
- Fades are linear and monotonic; nothing is asked to be read below the AA line — every
  text unit is fully arrived before its dwell is counted.
- Dwell: the sentence is 38 characters, the quotation 52, the source line 52. At 12–20
  characters per second (Szarkowska & Gerber-Morón 2018) each needs 2.6–4.3 s; the
  shortest hold after full arrival is the source beat's 1.5 s plus the split's 2 s in
  which the words do not change, and the words then stay on screen for 14 s more.
- The numeral change is a cross-fade of two digits in the same mono cells, so the line
  does not reflow and the eye is not pulled off the sentence.
- Text accumulates; nothing is wiped by its successor until the thesis, which replaces
  everything at once.
