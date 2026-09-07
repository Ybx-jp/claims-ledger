import {Easing} from 'remotion';

/**
 * The films' shared vocabulary: the palette, the layout, the easings, and the
 * timeline types a scenario is built from. Every number with a time or a
 * coordinate in it lives here or in scenarios.ts; the film, the contact sheet
 * and the storyboard all read the same timeline, so a diagnostic surface
 * cannot drift from the thing it diagnoses.
 */

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;

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

export type Interval = readonly [number, number];

// ---------------------------------------------------------------- easings

/**
 * Dragicevic et al., CHI 2011: quadratic slow-in/slow-out had the lowest
 * object-tracking error of the four pacings measured. Kept for any move that
 * asks the viewer to follow text it is already reading.
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

/** Lines arrive one after another: line i fades over `dur` frames, starting `step` after line i-1. */
export const lineIn = (frame: number, [start, end]: Interval, i: number, n: number): number => {
  const dur = 8;
  const step = n <= 1 ? 0 : Math.max(1, (end - start - dur) / (n - 1));
  return ramp(frame, [start + i * step, start + i * step + dur]);
};

// ------------------------------------------------------------------ layout

/**
 * Stacked, not side by side: every real line the films show — a status row of
 * 88 characters, a FAIL line of 150 — fits its pane unwrapped at the size it
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
export const TERM_LINE = 23;
export const PANE_PAD = 28;
export const MONO_ADVANCE = 0.6;

export const SPOT_FADE = 10;

// --------------------------------------------------------------- timeline

export type Line = {text: string; tone: 'ink' | 'muted' | 'accent'; soft?: boolean; wrap?: boolean};

/** What the file pane shows from `from` until the next state's `from`. */
export type FileState = {
  from: number;
  path: string;
  lines: string[];
  /** The row at the top of the pane. */
  firstRow: number;
  fadeIn?: Interval;
  /** Rows that land while this state is up, one after another, on accent-soft until they settle. */
  landing?: {first: number; count: number; at: Interval; settle: Interval};
};

export type Block = {
  command: string;
  lines: Line[];
  cmd: Interval;
  out: Interval;
  exit?: {code: number; at: Interval};
  until: number;
};

export type SpotTarget =
  | {kind: 'fileRows'; first: number; count: number}
  | {kind: 'termLines'; from: number; count: number}
  | {kind: 'termCommand'};

export type Spot = {id: string; on: Interval; target: SpotTarget; caption: string; below: boolean};

export type Beat = {id: string; step: string; start: number; end: number; understanding: string};

export type Timeline = {
  id: string;
  title: string;
  durationInFrames: number;
  beats: Beat[];
  files: FileState[];
  blocks: Block[];
  spots: Spot[];
  thesis: string;
  storyOut: Interval;
  thesisIn: Interval;
};

/** Every motion in a timeline as a named global interval, for the diagnostics. */
export const movesOf = (tl: Timeline): {name: string; at: Interval}[] => {
  const out: {name: string; at: Interval}[] = [];
  tl.files.forEach((f, i) => {
    if (f.fadeIn) out.push({name: `file${i} fadeIn`, at: f.fadeIn});
    if (f.landing) {
      out.push({name: `file${i} landing`, at: f.landing.at});
      out.push({name: `file${i} settle`, at: f.landing.settle});
    }
  });
  tl.blocks.forEach((b, i) => {
    out.push({name: `block${i} cmd`, at: b.cmd});
    out.push({name: `block${i} out`, at: b.out});
    if (b.exit) out.push({name: `block${i} exit`, at: b.exit.at});
  });
  tl.spots.forEach((s) => out.push({name: `spot ${s.id}`, at: s.on}));
  out.push({name: 'storyOut', at: tl.storyOut}, {name: 'thesisIn', at: tl.thesisIn});
  return out;
};

/** Start, midpoint and end of every move, the midpoint of every beat, first and last frame. */
export const diagnosticFrames = (tl: Timeline): {frame: number; label: string}[] => {
  const out = new Map<number, string>();
  const put = (f: number, label: string) => {
    const clamped = Math.max(0, Math.min(tl.durationInFrames - 1, f));
    if (!out.has(clamped)) out.set(clamped, label);
  };
  put(0, 'first');
  for (const {name, at: [s, e]} of movesOf(tl)) {
    put(s, `${name} · start`);
    if (e > s) put(Math.floor((s + e) / 2), `${name} · mid`);
    put(e, `${name} · end`);
  }
  for (const b of tl.beats) put(Math.floor((b.start + b.end) / 2), `${b.id} · hold mid`);
  put(tl.durationInFrames - 1, 'last');
  return [...out.entries()].sort((a, b) => a[0] - b[0]).map(([frame, label]) => ({frame, label}));
};

/** One tile per spotlight, at its midpoint, plus the thesis. */
export const storyboardFrames = (tl: Timeline): {frame: number; label: string}[] => [
  ...tl.spots.map((s) => ({frame: Math.floor((s.on[0] + s.on[1]) / 2), label: s.id})),
  {frame: Math.floor((tl.thesisIn[1] + tl.durationInFrames) / 2), label: 'thesis'},
];
