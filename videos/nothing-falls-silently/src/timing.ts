import {Easing} from 'remotion';

/**
 * nothing-falls-silently — the film's timing authority.
 *
 * Every number with a time or a coordinate in it lives here. The film, the
 * contact sheet and the track matte all import from this file, so a diagnostic
 * surface cannot drift from the thing it diagnoses.
 */

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;
export const DURATION_IN_FRAMES = 2160; // 72.000 s

/** The figures' light palette, verbatim from docs/figures/build.py. */
export const T = {
  paper: '#FAF8F3',
  ink: '#1C1B18',
  muted: '#77726A',
  rule: '#D9D4C7',
  panel: '#F0ECE2',
  mark: '#E6E0D2',
  accent: '#B8451F',
  accentSoft: '#F7DED2',
} as const;

export const COPY = {
  thesis: 'Nothing falls silently.',
  signature: 'claims-ledger',
  repo: 'research-repo',
} as const;

// ------------------------------------------------------------------ beats

export const BEATS = [
  {id: 'entry', step: '1 · a claim', start: 0, end: 330, understanding: 'a claim file, with its evidence, and its status'},
  {id: 'check', step: '2 · check', start: 330, end: 500, understanding: 'five checkers, all clean'},
  {id: 'verdict', step: '3 · a verdict', start: 500, end: 1060, understanding: 'a decision is written down as a row; the status follows it'},
  {id: 'fail', step: '4 · what fails', start: 1060, end: 1300, understanding: 'everything that cited it live now fails'},
  {id: 'propagate', step: '5 · propagate', start: 1300, end: 1800, understanding: 'the machine writes the dependents their row'},
  {id: 'gate', step: '6 · the gate', start: 1800, end: 2010, understanding: 'the commit is refused until the citations are fixed'},
  {id: 'thesis', step: '', start: 2010, end: 2160, understanding: 'the sentence'},
] as const;

export type Interval = readonly [number, number];

/** Every motion in the film as a global frame interval. */
export const MOVES = {
  fileIn: [0, 40],
  status1Cmd: [40, 50],
  status1Out: [55, 85],
  check1Cmd: [330, 340],
  check1Out: [345, 375],
  check1Exit: [380, 390],
  fileScroll: [500, 545],
  verdictLands: [730, 760],
  verdictSettles: [770, 810],
  status2Cmd: [905, 915],
  status2Out: [920, 945],
  check2Cmd: [1060, 1070],
  check2Out: [1075, 1150],
  check2Exit: [1155, 1165],
  propCmd: [1300, 1310],
  propOut: [1315, 1360],
  fileCut: [1480, 1480],
  dependentLands: [1485, 1515],
  dependentSettles: [1525, 1565],
  status3Cmd: [1650, 1660],
  status3Out: [1665, 1690],
  commitCmd: [1800, 1810],
  hookOut: [1815, 1880],
  commitExit: [1885, 1895],
  storyOut: [2010, 2040],
  thesisIn: [2035, 2065],
} as const satisfies Record<string, Interval>;

export type MoveName = keyof typeof MOVES;

/**
 * Spotlights: the frame dims to one region and a caption names it in the
 * product's own vocabulary. `on` is the interval the spotlight is fully up;
 * it fades over SPOT_FADE frames on either side. Consecutive spotlights on
 * the same box keep the box and change the caption. Targets are resolved by
 * the film against its own geometry.
 */
export const SPOT_FADE = 10;
export type SpotTarget =
  | {kind: 'fileRows'; anchor: 'grounds' | 'verdictsEmpty' | 'verdict' | 'dependentVerdict'}
  | {kind: 'termLines'; from: number; count: number}
  | {kind: 'termCommand'};

export const SPOTS: {id: string; on: Interval; target: SpotTarget; caption: string; below: boolean}[] = [
  {id: 'grounds', on: [100, 220], target: {kind: 'fileRows', anchor: 'grounds'}, caption: 'Grounds: the evidence this claim rests on.', below: true},
  {id: 'open', on: [235, 325], target: {kind: 'termLines', from: 0, count: 1}, caption: 'Status is derived from its verdicts. None yet: open.', below: true},
  {id: 'clean', on: [395, 495], target: {kind: 'termLines', from: 0, count: 5}, caption: 'Five checkers. A clean run exits 0.', below: true},
  {id: 'verdictsEmpty', on: [555, 665], target: {kind: 'fileRows', anchor: 'verdictsEmpty'}, caption: 'Verdicts: what has happened to the claim since.', below: true},
  {id: 'decision', on: [680, 800], target: {kind: 'fileRows', anchor: 'verdict'}, caption: 'The claim is refuted. The verdict is written here.', below: true},
  {id: 'appended', on: [800, 900], target: {kind: 'fileRows', anchor: 'verdict'}, caption: 'Appended by hand. Nothing above the line changes.', below: true},
  {id: 'refuted', on: [955, 1045], target: {kind: 'termLines', from: 0, count: 1}, caption: 'The status follows the last verdict: refuted.', below: true},
  {id: 'fails', on: [1160, 1290], target: {kind: 'termLines', from: 2, count: 4}, caption: 'Two entries and two documents cite R0001 as live. All four fail.', below: false},
  {id: 'flagged', on: [1365, 1465], target: {kind: 'termLines', from: 2, count: 2}, caption: 'propagate writes the dependents their verdict.', below: true},
  {id: 'cause', on: [1520, 1640], target: {kind: 'fileRows', anchor: 'dependentVerdict'}, caption: 'R0003 rests on R0001. Its row names the cause.', below: true},
  {id: 'contested', on: [1700, 1790], target: {kind: 'termLines', from: 1, count: 2}, caption: 'Both dependents are now contested.', below: true},
  {id: 'refused', on: [1900, 2000], target: {kind: 'termCommand'}, caption: 'The pre-commit hook runs the same check. Refused.', below: true},
];

// ---------------------------------------------------------------- easings

/**
 * Dragicevic et al., CHI 2011: quadratic slow-in/slow-out had the lowest
 * object-tracking error of the four pacings measured. It is used on the one
 * move that asks the viewer to follow text it is already reading — the file
 * pane's scroll to the APPEND marker.
 */
export const slowInSlowOutQuad = (t: number): number =>
  t <= 0.5 ? 2 * t * t : 1 - 2 * (1 - t) * (1 - t);

export const linear = Easing.linear;

/** 0 before the interval, 1 after it, eased progress inside it. */
export const ramp = (
  frame: number,
  [start, end]: Interval,
  easing: (t: number) => number = linear,
): number => {
  if (frame <= start) return 0;
  if (frame >= end) return 1;
  return easing((frame - start) / (end - start));
};

/** Lines arrive one after another: line i fades over `dur` frames starting `step` after line i-1. */
export const lineIn = (frame: number, [start, end]: Interval, i: number, n: number): number => {
  const dur = 8;
  const step = n <= 1 ? 0 : Math.max(1, (end - start - dur) / (n - 1));
  return ramp(frame, [start + i * step, start + i * step + dur]);
};

// ------------------------------------------------------------------ layout

/**
 * Stacked, not side by side: every real line the film shows — a status row of
 * 79 characters, a FAIL line of 150 — fits its pane unwrapped at the size it
 * is drawn, so the surface is shown as the shell would show it.
 */
export const MARGIN = 60;
export const PANE_X = MARGIN;
export const PANE_W = WIDTH - 2 * MARGIN; // 1800
export const FILE_TOP = 120;
export const FILE_H = 460;
export const TERM_TOP = FILE_TOP + FILE_H + 60; // 640
export const TERM_H = HEIGHT - TERM_TOP - MARGIN; // 380
export const LABEL_OFFSET = 34;
export const STEP_Y = 34;

export const FILE_FONT = 22;
export const FILE_LINE = 30;
export const TERM_FONT = 18;
export const TERM_LINE = 24;
export const PANE_PAD = 28;

/** The file pane opens on the Assertion, not the frontmatter: the id is in the label. */
export const FILE_FIRST_ROW = 12;
/** The scroll lands the APPEND marker this many rows from the pane's top. */
export const SCROLL_TARGET_ROW = 1;

/** The scroll, in px, at a frame — the function the track matte is checked against. */
export const fileScrollPx = (frame: number, appendLineIndex: number): number => {
  const from = FILE_FIRST_ROW * FILE_LINE;
  const to = (appendLineIndex - SCROLL_TARGET_ROW) * FILE_LINE;
  return from + (to - from) * ramp(frame, MOVES.fileScroll, slowInSlowOutQuad);
};

// ------------------------------------------------------------ diagnostics

export const DIAGNOSTIC_FRAMES: {frame: number; label: string}[] = (() => {
  const out = new Map<number, string>();
  const put = (f: number, label: string) => {
    const clamped = Math.max(0, Math.min(DURATION_IN_FRAMES - 1, f));
    if (!out.has(clamped)) out.set(clamped, label);
  };
  put(0, 'first');
  for (const [name, [s, e]] of Object.entries(MOVES) as [MoveName, Interval][]) {
    put(s, `${name} · start`);
    if (e > s) put(Math.floor((s + e) / 2), `${name} · mid`);
    put(e, `${name} · end`);
  }
  for (const b of BEATS) put(Math.floor((b.start + b.end) / 2), `${b.id} · hold mid`);
  put(DURATION_IN_FRAMES - 1, 'last');
  return [...out.entries()].sort((a, b) => a[0] - b[0]).map(([frame, label]) => ({frame, label}));
})();
