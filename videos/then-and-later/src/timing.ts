import {Easing} from 'remotion';

/**
 * then-and-later — the film's timing authority.
 *
 * Every number with a time or a coordinate in it lives here. The film, the
 * contact sheet and the track matte all import from this file, so a diagnostic
 * surface cannot drift from the thing it diagnoses.
 */

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;
export const DURATION_IN_FRAMES = 720; // 24.000 s

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

/**
 * The words. The claim is the Nimbus portfolio's threshold claim and the
 * source is its API contract; the change is the one examples/ is built around.
 */
export const COPY = {
  assertion: 'Scores at or above 0.72 go to review.',
  quotePrefix: 'Scores greater than or equal to ',
  quoteSuffix: ' require review.',
  before: '0.72',
  after: '0.75',
  sourceName: 'backend-service · openapi.yaml',
  shaBefore: 'sha256 · 3f9a2c…',
  shaAfter: 'sha256 · c71e08…',
  corroborated: 'corroborated',
  contested: 'contested',
  nothing: 'nothing happens',
  caught: 'caught',
  whenWritten: 'WHEN WRITTEN',
  later: 'LATER',
  prose: 'PROSE',
  ledger: 'LEDGER',
  thesis: 'A sentence outlives what made it true.',
  signature: 'claims-ledger',
} as const;

// ------------------------------------------------------------------ beats

export const BEATS = [
  {id: 'establish', start: 0, end: 75, understanding: 'here is a sentence someone wrote'},
  {id: 'source', start: 75, end: 165, understanding: 'the sentence quotes this line'},
  {id: 'split', start: 165, end: 225, understanding: 'two worlds, same starting point'},
  {id: 'bind', start: 225, end: 315, understanding: 'the ledger keeps the link'},
  {id: 'time', start: 315, end: 405, understanding: 'the world moved under the sentence'},
  {id: 'outcome', start: 405, end: 495, understanding: 'one world noticed'},
  {id: 'hold', start: 495, end: 600, understanding: 'compare at leisure'},
  {id: 'thesis', start: 600, end: 720, understanding: 'the title, earned'},
] as const;

export type Interval = readonly [number, number];

/** Every motion in the film as a global frame interval. */
export const MOVES = {
  sentenceIn: [0, 20],
  cardRise: [75, 99],
  matchIn: [105, 120],
  panelSlide: [165, 195],
  copyIn: [190, 215],
  labelsIn: [205, 225],
  proseForgets: [225, 255],
  tetherDraw: [225, 255],
  shaIn: [255, 270],
  chipIn: [270, 285],
  timeSweep: [315, 375],
  laterIn: [370, 385],
  digitsFlip: [385, 405],
  tetherAccent: [410, 440],
  ghostIn: [410, 440],
  shaFlip: [425, 440],
  chipFlip: [440, 455],
  captionsIn: [460, 480],
  worldsOut: [600, 630],
  thesisIn: [625, 655],
} as const satisfies Record<string, Interval>;

export type MoveName = keyof typeof MOVES;

// ---------------------------------------------------------------- easings

/**
 * Dragicevic et al., CHI 2011: slow-in/slow-out as a quadratic transformation
 * of linear pacing had the lowest object-tracking error of the four pacings
 * measured. It is used on the one move in this film that asks the viewer to
 * track an object it already knows — the panel's slide at the split.
 */
export const slowInSlowOutQuad = (t: number): number =>
  t <= 0.5 ? 2 * t * t : 1 - 2 * (1 - t) * (1 - t);

/** Fades are not tracked moves; they are linear and monotonic. */
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

// ------------------------------------------------------------------ layout

export const PANEL_W = 860;
export const PANEL_Y = 150;
export const PANEL_CENTER_X = (WIDTH - PANEL_W) / 2; // 530
export const LEFT_X = 100;
export const RIGHT_X = WIDTH - 100 - PANEL_W; // 960

/** How far the panel travels at the split: half its own width. */
export const SLIDE_PX = PANEL_CENTER_X - LEFT_X; // 430

/** The panel's x at a frame — the function the track matte is checked against. */
export const panelX = (frame: number): number =>
  PANEL_CENTER_X - SLIDE_PX * ramp(frame, MOVES.panelSlide, slowInSlowOutQuad);

/** Positions inside a panel. */
export const P = {
  chipY: 0,
  chipH: 36,
  assertionY: 50,
  assertionSize: 46,
  quoteY: 120,
  quoteH: 48,
  quoteSize: 24,
  cardY: 300,
  cardH: 340,
  cardHeaderY: 24,
  cardLineY: 160,
  cardLineSize: 24,
  cardPad: 32,
  greekAbove: [
    {y: 80, w: 560},
    {y: 110, w: 640},
  ],
  greekBelow: [
    {y: 220, w: 600},
    {y: 250, w: 700},
    {y: 280, w: 420},
  ],
  shaY: 664,
  shaSize: 20,
  captionY: 712,
  captionSize: 28,
} as const;

/** The mono advance at the sizes used, measured for IBM Plex Mono (0.6 em). */
export const MONO_ADVANCE = 0.6;

/** The tether, in panel coordinates: from under the quotation to the top of the span. */
export const TETHER = (() => {
  const quoteChars = COPY.quotePrefix.length + COPY.before.length + COPY.quoteSuffix.length + 2;
  const quoteW = quoteChars * P.quoteSize * MONO_ADVANCE + 32;
  const lineChars = COPY.quotePrefix.length + COPY.before.length + COPY.quoteSuffix.length;
  const lineW = lineChars * P.cardLineSize * MONO_ADVANCE;
  const from = {x: quoteW / 2, y: P.quoteY + P.quoteH + 2};
  const to = {x: P.cardPad + lineW / 2, y: P.cardY + P.cardLineY - 8};
  const c1 = {x: from.x, y: from.y + 90};
  const c2 = {x: to.x, y: to.y - 60};
  return {
    quoteW,
    lineW,
    from,
    to,
    d: `M ${from.x} ${from.y} C ${c1.x} ${c1.y} ${c2.x} ${c2.y} ${to.x} ${to.y}`,
    dReversed: `M ${to.x} ${to.y} C ${c2.x} ${c2.y} ${c1.x} ${c1.y} ${from.x} ${from.y}`,
  };
})();

export const TIME_RULE = {y: 60, x0: 60, x1: WIDTH - 60};
export const COLUMN_LABEL_Y = 118;

// ------------------------------------------------------------ diagnostics

/**
 * The frames the contact sheet renders: start, midpoint and end of every move,
 * the midpoint of every hold between beats, the first and last frame.
 */
export const DIAGNOSTIC_FRAMES: {frame: number; label: string}[] = (() => {
  const out = new Map<number, string>();
  const put = (f: number, label: string) => {
    const clamped = Math.max(0, Math.min(DURATION_IN_FRAMES - 1, f));
    if (!out.has(clamped)) out.set(clamped, label);
  };
  put(0, 'first');
  for (const [name, [s, e]] of Object.entries(MOVES) as [MoveName, Interval][]) {
    put(s, `${name} · start`);
    put(Math.floor((s + e) / 2), `${name} · mid`);
    put(e, `${name} · end`);
  }
  for (const b of BEATS) put(Math.floor((b.start + b.end) / 2), `${b.id} · hold mid`);
  put(DURATION_IN_FRAMES - 1, 'last');
  return [...out.entries()].sort((a, b) => a[0] - b[0]).map(([frame, label]) => ({frame, label}));
})();
