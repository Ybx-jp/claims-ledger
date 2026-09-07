import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {CAPTURES} from './captures';
import {MONO, SERIF} from './fonts';
import {
  BEATS,
  COPY,
  FILE_FONT,
  FILE_H,
  FILE_LINE,
  FILE_TOP,
  HEIGHT,
  LABEL_OFFSET,
  MOVES,
  PANE_PAD,
  PANE_W,
  PANE_X,
  SPOTS,
  SPOT_FADE,
  STEP_Y,
  T,
  TERM_FONT,
  TERM_H,
  TERM_LINE,
  TERM_TOP,
  WIDTH,
  fileScrollPx,
  lineIn,
  ramp,
} from './timing';

/**
 * nothing-falls-silently.
 *
 * Two surfaces the product actually has: a file and a shell. Every line drawn
 * is a line tools/capture.py captured from a fresh materialization of the
 * example portfolio — the entry, the verdict a person appends, each command's
 * output, the hook's refusal. Nothing on screen is invented; what the film
 * adds is order, emphasis and time.
 *
 * Emphasis: the terminal's own tokens FAIL and FLAG carry the accent, the way
 * a colouring shell would show them; a status that has just changed and a
 * verdict row that has just landed sit on accent-soft while they are new; and
 * a spotlight dims the frame to one region and names it in the product's own
 * words. A step strip across the top says which of the six moments this is.
 */

// ------------------------------------------------------------------ text

const ENTRY_BEFORE = CAPTURES.entryBefore.split('\n');
const ENTRY_AFTER = CAPTURES.entryAfter.split('\n');
const DEPENDENT = CAPTURES.dependentAfter.split('\n');
const APPEND_MARKER = '<!-- APPEND BELOW THIS LINE ONLY -->';
const APPEND_INDEX = ENTRY_AFTER.indexOf(APPEND_MARKER);
const DEPENDENT_APPEND_INDEX = DEPENDENT.indexOf(APPEND_MARKER);
const GROUNDS_INDEX = ENTRY_BEFORE.indexOf('## Grounds');
const VERDICT_LINES = CAPTURES.verdictRow.trimEnd().split('\n');
const ENTRY_PATH = 'ledger/entries/R0001-threshold-balances-review-errors.md';
const DEPENDENT_PATH = 'ledger/entries/R0003-threshold-generalizes.md';
const MONO_ADVANCE = 0.6;

/** The cast of the status table, and the footer; the other nine rows are elided honestly. */
const CAST = ['R0001', 'R0002', 'R0003'];
const cropStatus = (text: string): string[] => {
  const lines = text.split('\n');
  const rows = lines.filter((l) => CAST.some((id) => l.startsWith(id)));
  const footer = lines[lines.length - 1];
  const elided = lines.filter((l) => /^R\d{4}/.test(l)).length - rows.length;
  return [...rows, `  ⋮ ${elided} more`, '', footer];
};

type Line = {text: string; tone: 'ink' | 'muted' | 'accent'; soft?: boolean; wrap?: boolean};

const statusLines = (text: string, changed: string[]): Line[] =>
  cropStatus(text).map((l) => {
    const id = l.slice(0, 5);
    const hot = changed.includes(id);
    return {text: l, tone: CAST.includes(id) ? (hot ? 'accent' : 'ink') : 'muted', soft: hot};
  });

const outputLines = (text: string): Line[] =>
  text.split('\n').map((l) => ({
    text: l,
    tone: l.startsWith('FAIL') || l.startsWith('FLAG') ? 'accent' : 'ink',
    wrap: true,
  }));

// --------------------------------------------------------------- surfaces

/**
 * Grayscale antialiasing and an explicit compositor layer for everything that
 * fades. Chrome turns LCD text antialiasing off when an element is promoted to
 * its own layer, and promotion of an element whose opacity changes every frame
 * is timing-dependent — measured here as frames that differ between renders of
 * the same source. Pinning both removes the choice.
 */
const STABLE: React.CSSProperties = {WebkitFontSmoothing: 'antialiased', willChange: 'opacity'};
// The two panes clip their children and have square corners: an antialiased rounded corner on a
// clipping layer rasterized ±1 level differently between renders, measured at (60,127) and (60,647).

const Label: React.FC<{text: string; top: number; opacity?: number}> = ({text, top, opacity = 1}) => (
  <div
    style={{
      position: 'absolute',
      left: PANE_X,
      top: top - LABEL_OFFSET,
      fontFamily: MONO,
      fontSize: 18,
      color: T.muted,
      opacity,
      whiteSpace: 'nowrap',
    }}
  >
    {text}
  </div>
);

/** Which of the six moments this is. The current step is ink; the rest muted. */
const StepStrip: React.FC<{opacity: number}> = ({opacity}) => {
  const frame = useCurrentFrame();
  const steps = BEATS.filter((b) => b.step);
  const current = steps.find((b) => frame >= b.start && frame < b.end)?.id;
  return (
    <div
      style={{
        position: 'absolute',
        left: PANE_X,
        top: STEP_Y,
        display: 'flex',
        gap: 36,
        fontFamily: SERIF,
        fontSize: 20,
        letterSpacing: '0.04em',
        opacity,
      }}
    >
      {steps.map((b) => (
        <span key={b.id} style={{color: b.id === current ? T.ink : T.muted, transition: 'none'}}>
          {b.step}
        </span>
      ))}
    </div>
  );
};

const FilePane: React.FC<{
  path: string;
  lines: string[];
  scrollPx: number;
  opacity: number;
  lineOpacity: (i: number) => number;
  soft: (i: number) => number;
}> = ({path, lines, scrollPx, opacity, lineOpacity, soft}) => (
  <>
    <Label text={path} top={FILE_TOP} opacity={opacity} />
    <div
      style={{
        position: 'absolute',
        left: PANE_X,
        top: FILE_TOP,
        width: PANE_W,
        height: FILE_H,
        border: `2px solid ${T.rule}`,
        background: T.paper,
        overflow: 'hidden',
        opacity,
      }}
    >
      <div style={{position: 'absolute', left: PANE_PAD, top: PANE_PAD - scrollPx, right: PANE_PAD}}>
        {lines.map((l, i) => {
          const marker = l === APPEND_MARKER;
          const heading = l.startsWith('## ') || l === '---';
          return (
            <div
              key={i}
              style={{
                position: 'relative',
                height: FILE_LINE,
                lineHeight: `${FILE_LINE}px`,
                fontFamily: MONO,
                fontSize: FILE_FONT,
                whiteSpace: 'pre',
                color: marker ? T.accent : heading ? T.muted : T.ink,
                opacity: lineOpacity(i),
                ...STABLE,
              }}
            >
              <div
                style={{
                  position: 'absolute',
                  left: -10,
                  right: -10,
                  top: 0,
                  bottom: 0,
                  borderRadius: 4,
                  background: T.accentSoft,
                  opacity: soft(i),
                }}
              />
              <span style={{position: 'relative'}}>{l}</span>
            </div>
          );
        })}
      </div>
    </div>
  </>
);

type Block = {
  command: string;
  lines: Line[];
  cmd: readonly [number, number];
  out: readonly [number, number];
  exit?: {code: number; at: readonly [number, number]};
  until: number;
};

const Terminal: React.FC<{blocks: Block[]; opacity: number}> = ({blocks, opacity}) => {
  const frame = useCurrentFrame();
  const current = blocks.filter((b) => frame >= b.cmd[0] && frame < b.until);
  return (
    <>
      <Label text={`${COPY.repo} $`} top={TERM_TOP} opacity={opacity} />
      <div
        style={{
          position: 'absolute',
          left: PANE_X,
          top: TERM_TOP,
          width: PANE_W,
          height: TERM_H,
          border: `2px solid ${T.rule}`,
          background: T.panel,
          overflow: 'hidden',
          opacity,
        }}
      >
        {current.map((b) => {
          const cmdIn = ramp(frame, b.cmd);
          const exitIn = b.exit ? ramp(frame, b.exit.at) : 0;
          return (
            <div key={b.command + b.cmd[0]} style={{position: 'absolute', left: PANE_PAD, top: PANE_PAD, right: PANE_PAD}}>
              <div
                style={{
                  fontFamily: MONO,
                  fontSize: TERM_FONT,
                  lineHeight: `${TERM_LINE}px`,
                  color: T.ink,
                  opacity: cmdIn,
                  whiteSpace: 'pre',
                  marginBottom: TERM_LINE / 2,
                  ...STABLE,
                }}
              >
                <span style={{color: T.muted}}>$ </span>
                {b.command}
                {b.exit && (
                  <span style={{color: b.exit.code === 0 ? T.muted : T.accent, opacity: exitIn}}>
                    {`   → exit ${b.exit.code}`}
                  </span>
                )}
              </div>
              {b.lines.map((l, i) => (
                <div
                  key={i}
                  style={{
                    position: 'relative',
                    fontFamily: MONO,
                    fontSize: TERM_FONT,
                    lineHeight: `${TERM_LINE}px`,
                    whiteSpace: l.wrap ? 'pre-wrap' : 'pre',
                    color: l.tone === 'accent' ? T.accent : l.tone === 'muted' ? T.muted : T.ink,
                    opacity: lineIn(frame, b.out, i, b.lines.length),
                    ...STABLE,
                  }}
                >
                  {l.soft && (
                    <div
                      style={{
                        position: 'absolute',
                        left: -8,
                        right: -8,
                        top: 0,
                        bottom: 0,
                        borderRadius: 4,
                        background: T.accentSoft,
                      }}
                    />
                  )}
                  <span style={{position: 'relative'}}>{l.text}</span>
                </div>
              ))}
            </div>
          );
        })}
      </div>
    </>
  );
};

// -------------------------------------------------------------- spotlight

type Box = {x: number; y: number; w: number; h: number};

/**
 * The frame dims to one box, outlined in accent, with a caption beside it.
 * The dimming is four paper rectangles around the box, so the box itself is
 * untouched pixels of the film.
 */
const Spotlight: React.FC<{box: Box; caption: string; below: boolean; opacity: number}> = ({box, caption, below, opacity}) => {
  const dim = 0.62 * opacity;
  const pad = 10;
  const bx = box.x - pad;
  const by = box.y - pad;
  const bw = box.w + 2 * pad;
  const bh = box.h + 2 * pad;
  const capH = 56;
  const capY = below ? by + bh + 18 : by - 18 - capH;
  return (
    <>
      <div style={{position: 'absolute', left: 0, top: 0, width: WIDTH, height: by, background: T.paper, opacity: dim}} />
      <div style={{position: 'absolute', left: 0, top: by + bh, width: WIDTH, height: HEIGHT - by - bh, background: T.paper, opacity: dim}} />
      <div style={{position: 'absolute', left: 0, top: by, width: bx, height: bh, background: T.paper, opacity: dim}} />
      <div style={{position: 'absolute', left: bx + bw, top: by, width: WIDTH - bx - bw, height: bh, background: T.paper, opacity: dim}} />
      <div
        style={{
          position: 'absolute',
          left: bx,
          top: by,
          width: bw,
          height: bh,
          boxSizing: 'border-box',
          border: `2px solid ${T.accent}`,
          borderRadius: 8,
          opacity,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: bx,
          top: capY,
          height: capH,
          padding: '0 22px',
          display: 'flex',
          alignItems: 'center',
          background: T.paper,
          borderLeft: `4px solid ${T.accent}`,
          borderRadius: 6,
          boxShadow: `0 2px 12px rgba(28, 27, 24, 0.12)`,
          fontFamily: SERIF,
          fontSize: 30,
          color: T.ink,
          whiteSpace: 'nowrap',
          opacity,
          ...STABLE,
        }}
      >
        {caption}
      </div>
    </>
  );
};

// ------------------------------------------------------------------ story

const BLOCKS: Block[] = [
  {
    command: 'claims-ledger status',
    lines: statusLines(CAPTURES.statusBefore.text, []),
    cmd: MOVES.status1Cmd,
    out: MOVES.status1Out,
    until: MOVES.check1Cmd[0],
  },
  {
    command: 'claims-ledger check',
    lines: outputLines(CAPTURES.checkBefore.text),
    cmd: MOVES.check1Cmd,
    out: MOVES.check1Out,
    exit: {code: CAPTURES.checkBefore.exit, at: MOVES.check1Exit},
    until: MOVES.status2Cmd[0],
  },
  {
    command: 'claims-ledger status',
    lines: statusLines(CAPTURES.statusAfterVerdict.text, ['R0001']),
    cmd: MOVES.status2Cmd,
    out: MOVES.status2Out,
    until: MOVES.check2Cmd[0],
  },
  {
    command: 'claims-ledger check',
    lines: outputLines(CAPTURES.checkAfterVerdict.text),
    cmd: MOVES.check2Cmd,
    out: MOVES.check2Out,
    exit: {code: CAPTURES.checkAfterVerdict.exit, at: MOVES.check2Exit},
    until: MOVES.propCmd[0],
  },
  {
    command: 'claims-ledger propagate --write',
    lines: outputLines(CAPTURES.propagate.text),
    cmd: MOVES.propCmd,
    out: MOVES.propOut,
    until: MOVES.status3Cmd[0],
  },
  {
    command: 'claims-ledger status',
    lines: statusLines(CAPTURES.statusAfterPropagate.text, ['R0002', 'R0003']),
    cmd: MOVES.status3Cmd,
    out: MOVES.status3Out,
    until: MOVES.commitCmd[0],
  },
  {
    command: 'git commit -m "refute R0001"',
    lines: outputLines(CAPTURES.commit.text),
    cmd: MOVES.commitCmd,
    out: MOVES.hookOut,
    exit: {code: CAPTURES.commit.exit, at: MOVES.commitExit},
    until: BEATS[BEATS.length - 1].end,
  },
];

/** The terminal's line i, in frame coordinates, for the block on screen at `frame`. */
const termLineBox = (frame: number, from: number, count: number): Box => {
  const block = BLOCKS.find((b) => frame >= b.cmd[0] && frame < b.until) ?? BLOCKS[0];
  // Lines before `from` may wrap; count the rows they occupy at the pane's width.
  const cols = Math.floor((PANE_W - 2 * PANE_PAD) / (TERM_FONT * MONO_ADVANCE));
  const rowsOf = (l: Line) => (l.wrap ? Math.max(1, Math.ceil(l.text.length / cols)) : 1);
  const before = block.lines.slice(0, from).reduce((n, l) => n + rowsOf(l), 0);
  const span = block.lines.slice(from, from + count).reduce((n, l) => n + rowsOf(l), 0);
  const longest = Math.max(...block.lines.slice(from, from + count).map((l) => Math.min(l.text.length, cols)));
  return {
    x: PANE_X + PANE_PAD,
    y: TERM_TOP + PANE_PAD + TERM_LINE * 1.5 + before * TERM_LINE,
    w: Math.min(PANE_W - 2 * PANE_PAD, longest * TERM_FONT * MONO_ADVANCE + 8),
    h: span * TERM_LINE,
  };
};

const termCommandBox = (frame: number): Box => {
  const block = BLOCKS.find((b) => frame >= b.cmd[0] && frame < b.until) ?? BLOCKS[0];
  const chars = 2 + block.command.length + (block.exit ? 12 : 0);
  return {x: PANE_X + PANE_PAD, y: TERM_TOP + PANE_PAD, w: chars * TERM_FONT * MONO_ADVANCE + 8, h: TERM_LINE};
};

const fileRowsBox = (first: number, count: number, lines: string[], scrollPx: number): Box => {
  const longest = Math.max(...lines.slice(first, first + count).map((l) => l.length));
  return {
    x: PANE_X + PANE_PAD,
    y: FILE_TOP + PANE_PAD + first * FILE_LINE - scrollPx,
    w: longest * FILE_FONT * MONO_ADVANCE + 8,
    h: count * FILE_LINE,
  };
};

const Story: React.FC = () => {
  const frame = useCurrentFrame();
  const fileIn = ramp(frame, MOVES.fileIn);
  const beforeCut = frame < MOVES.fileCut[0];

  // R0001, before and after the human's verdict: the same file, the row appended.
  const verdictLanded = frame >= MOVES.verdictLands[0];
  const lines = beforeCut ? (verdictLanded ? ENTRY_AFTER : ENTRY_BEFORE) : DEPENDENT;
  const appendIndex = beforeCut ? APPEND_INDEX : DEPENDENT_APPEND_INDEX;
  const scroll = beforeCut ? fileScrollPx(frame, appendIndex) : (appendIndex - 1) * FILE_LINE;

  const lineOpacity = (i: number): number => {
    if (!beforeCut) {
      return i > DEPENDENT_APPEND_INDEX + 2 && i <= DEPENDENT_APPEND_INDEX + 2 + 3
        ? lineIn(frame, MOVES.dependentLands, i - DEPENDENT_APPEND_INDEX - 3, 3)
        : 1;
    }
    if (verdictLanded && i > APPEND_INDEX + 2 && i <= APPEND_INDEX + 2 + VERDICT_LINES.length) {
      return lineIn(frame, MOVES.verdictLands, i - APPEND_INDEX - 3, VERDICT_LINES.length);
    }
    return lineIn(frame, MOVES.fileIn, Math.min(i, 24), 25);
  };
  const soft = (i: number): number => {
    if (!beforeCut) {
      const isNew = i > DEPENDENT_APPEND_INDEX + 2 && i <= DEPENDENT_APPEND_INDEX + 2 + 3;
      return isNew ? ramp(frame, MOVES.dependentLands) * (1 - ramp(frame, MOVES.dependentSettles)) : 0;
    }
    const isNew = verdictLanded && i > APPEND_INDEX + 2 && i <= APPEND_INDEX + 2 + VERDICT_LINES.length;
    return isNew ? ramp(frame, MOVES.verdictLands) * (1 - ramp(frame, MOVES.verdictSettles)) : 0;
  };

  // The spotlight up at this frame, if any, and its box in frame coordinates.
  const spot = SPOTS.find((s) => frame >= s.on[0] - SPOT_FADE && frame < s.on[1] + SPOT_FADE);
  let spotBox: Box | null = null;
  let spotOpacity = 0;
  if (spot) {
    spotOpacity = Math.min(ramp(frame, [spot.on[0] - SPOT_FADE, spot.on[0]]), 1 - ramp(frame, [spot.on[1], spot.on[1] + SPOT_FADE]));
    const t = spot.target;
    if (t.kind === 'fileRows') {
      const first = t.anchor === 'grounds' ? GROUNDS_INDEX + 2 : t.anchor === 'verdict' ? APPEND_INDEX + 4 : DEPENDENT_APPEND_INDEX + 4;
      const count = t.anchor === 'grounds' ? 2 : 3;
      spotBox = fileRowsBox(first, count, lines, scroll);
    } else if (t.kind === 'termLines') {
      spotBox = termLineBox(frame, t.from, t.count);
    } else {
      spotBox = termCommandBox(frame);
    }
  }

  return (
    <AbsoluteFill style={{backgroundColor: T.paper, ...STABLE}}>
      <StepStrip opacity={fileIn} />
      <FilePane
        path={beforeCut ? ENTRY_PATH : DEPENDENT_PATH}
        lines={lines}
        scrollPx={scroll}
        opacity={fileIn}
        lineOpacity={lineOpacity}
        soft={soft}
      />
      <Terminal blocks={BLOCKS} opacity={fileIn} />
      {spot && spotBox && <Spotlight box={spotBox} caption={spot.caption} below={spot.below} opacity={spotOpacity} />}
    </AbsoluteFill>
  );
};

const Thesis: React.FC = () => {
  const local = useCurrentFrame();
  const t0 = BEATS[BEATS.length - 1].start;
  const storyOut = ramp(local + t0, MOVES.storyOut);
  const thesisIn = ramp(local + t0, MOVES.thesisIn);
  return (
    <AbsoluteFill style={{backgroundColor: T.paper, opacity: storyOut, ...STABLE}}>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: HEIGHT / 2 - 60,
          textAlign: 'center',
          fontFamily: SERIF,
          fontSize: 64,
          color: T.ink,
          opacity: thesisIn,
        }}
      >
        {COPY.thesis}
      </div>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: HEIGHT / 2 + 40,
          textAlign: 'center',
          fontFamily: MONO,
          fontSize: 24,
          color: T.muted,
          opacity: thesisIn,
        }}
      >
        {COPY.signature}
      </div>
    </AbsoluteFill>
  );
};

export const Film: React.FC = () => {
  const thesis = BEATS[BEATS.length - 1];
  return (
    <AbsoluteFill style={{backgroundColor: T.paper}}>
      <Sequence name="story" from={0} durationInFrames={MOVES.storyOut[1]}>
        <Story />
      </Sequence>
      <Sequence name="thesis" from={thesis.start} durationInFrames={thesis.end - thesis.start}>
        <Thesis />
      </Sequence>
    </AbsoluteFill>
  );
};

/**
 * The track matte: the APPEND marker's row alone, white on black, as it
 * scrolls. tools/track-centroid.py measures its centroid per frame and checks
 * it against `fileScrollPx`, the function the film scrolls the pane with.
 */
export const TrackMatte: React.FC = () => {
  const frame = useCurrentFrame();
  const y = FILE_TOP + PANE_PAD + APPEND_INDEX * FILE_LINE - fileScrollPx(frame, APPEND_INDEX);
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <div style={{position: 'absolute', left: PANE_X, top: y, width: PANE_W, height: FILE_LINE, background: '#fff'}} />
    </AbsoluteFill>
  );
};

export const APPEND_LINE_INDEX = APPEND_INDEX;
