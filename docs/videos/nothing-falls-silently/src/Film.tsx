import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {MONO, SERIF} from './fonts';
import {SCENARIOS, type ScenarioId} from './scenarios';
import {
  FILE_FONT,
  FILE_H,
  FILE_LINE,
  FILE_TOP,
  HEIGHT,
  LABEL_OFFSET,
  MONO_ADVANCE,
  PANE_PAD,
  PANE_W,
  PANE_X,
  SPOT_FADE,
  STEP_Y,
  T,
  TERM_FONT,
  TERM_H,
  TERM_LINE,
  TERM_TOP,
  WIDTH,
  lineIn,
  ramp,
  type Block,
  type FileState,
  type Line,
  type Timeline,
} from './timeline';

/**
 * Two surfaces the product actually has: a file and a shell. Every line drawn
 * is a line tools/capture.py captured from a fresh materialization of the
 * example portfolio. Nothing on screen is invented; what a film adds is order,
 * emphasis and time, and all three come from its timeline in scenarios.ts.
 *
 * Emphasis: the terminal's own tokens FAIL and FLAG carry the accent, the way
 * a colouring shell would show them; a status that has just changed and a
 * verdict row that has just landed sit on accent-soft while they are new; a
 * spotlight dims the frame to one region and names it in the product's own
 * words; a step strip across the top says which moment this is.
 */

const APPEND = '<!-- APPEND BELOW THIS LINE ONLY -->';

/**
 * Grayscale antialiasing and an explicit compositor layer for everything that
 * fades. Chrome turns LCD text antialiasing off when an element is promoted to
 * its own layer, and promotion of an element whose opacity changes every frame
 * is timing-dependent — measured as frames that differ between renders of the
 * same source. Pinning both removes the choice. The two panes clip their
 * children and have square corners: an antialiased rounded corner on a
 * clipping layer rasterized ±1 level differently between renders.
 */
const STABLE: React.CSSProperties = {WebkitFontSmoothing: 'antialiased', willChange: 'opacity'};

export type FilmProps = {scenario: ScenarioId};

// --------------------------------------------------------------- surfaces

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
      ...STABLE,
    }}
  >
    {text}
  </div>
);

const StepStrip: React.FC<{tl: Timeline; opacity: number}> = ({tl, opacity}) => {
  const frame = useCurrentFrame();
  const steps = tl.beats.filter((b) => b.step);
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
        ...STABLE,
      }}
    >
      {steps.map((b) => (
        <span key={b.id} style={{color: b.id === current ? T.ink : T.muted}}>
          {b.step}
        </span>
      ))}
    </div>
  );
};

const FilePane: React.FC<{state: FileState; frame: number; opacity: number}> = ({state, frame, opacity}) => {
  const fadeIn = state.fadeIn ? ramp(frame, state.fadeIn) : 1;
  const landing = state.landing;
  const isNew = (i: number) => Boolean(landing && i >= landing.first && i < landing.first + landing.count);
  const lineOpacity = (i: number) => {
    if (landing && isNew(i)) return lineIn(frame, landing.at, i - landing.first, landing.count);
    return state.fadeIn ? lineIn(frame, state.fadeIn, Math.min(Math.max(0, i - state.firstRow), 24), 25) : 1;
  };
  const soft = (i: number) => (landing && isNew(i) ? ramp(frame, landing.at) * (1 - ramp(frame, landing.settle)) : 0);
  return (
    <>
      <Label text={state.path} top={FILE_TOP} opacity={opacity * fadeIn} />
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
        <div style={{position: 'absolute', left: PANE_PAD, top: PANE_PAD - state.firstRow * FILE_LINE, right: PANE_PAD}}>
          {state.lines.map((l, i) => {
            const marker = l === APPEND;
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
                <div style={{position: 'absolute', left: -10, right: -10, top: 0, bottom: 0, borderRadius: 4, background: T.accentSoft, opacity: soft(i)}} />
                <span style={{position: 'relative'}}>{l}</span>
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
};

const Terminal: React.FC<{repo: string; blocks: Block[]; frame: number; opacity: number}> = ({repo, blocks, frame, opacity}) => {
  const current = blocks.filter((b) => frame >= b.cmd[0] && frame < b.until);
  return (
    <>
      <Label text={`${repo} $`} top={TERM_TOP} opacity={opacity} />
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
                  <span style={{color: b.exit.code === 0 ? T.muted : T.accent, opacity: exitIn}}>{`   → exit ${b.exit.code}`}</span>
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
                  {l.soft && <div style={{position: 'absolute', left: -8, right: -8, top: 0, bottom: 0, borderRadius: 4, background: T.accentSoft}} />}
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

const Spotlight: React.FC<{box: Box; dim: number; captions: {text: string; below: boolean; opacity: number}[]}> = ({box, dim, captions}) => {
  const shade = 0.62 * dim;
  const pad = 10;
  const bx = box.x - pad;
  const by = box.y - pad;
  const bw = box.w + 2 * pad;
  const bh = box.h + 2 * pad;
  const capH = 56;
  return (
    <>
      <div style={{position: 'absolute', left: 0, top: 0, width: WIDTH, height: by, background: T.paper, opacity: shade}} />
      <div style={{position: 'absolute', left: 0, top: by + bh, width: WIDTH, height: HEIGHT - by - bh, background: T.paper, opacity: shade}} />
      <div style={{position: 'absolute', left: 0, top: by, width: bx, height: bh, background: T.paper, opacity: shade}} />
      <div style={{position: 'absolute', left: bx + bw, top: by, width: WIDTH - bx - bw, height: bh, background: T.paper, opacity: shade}} />
      <div style={{position: 'absolute', left: bx, top: by, width: bw, height: bh, boxSizing: 'border-box', border: `2px solid ${T.accent}`, borderRadius: 8, opacity: dim}} />
      {captions.map((c) => (
        <div
          key={c.text}
          style={{
            position: 'absolute',
            left: bx,
            top: c.below ? by + bh + 18 : by - 18 - capH,
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
            opacity: c.opacity,
            ...STABLE,
          }}
        >
          {c.text}
        </div>
      ))}
    </>
  );
};

/** The terminal's lines `from .. from+count`, in frame coordinates, for the block on screen at `frame`. */
const termLineBox = (blocks: Block[], frame: number, from: number, count: number): Box => {
  const block = blocks.find((b) => frame >= b.cmd[0] && frame < b.until) ?? blocks[0];
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

const termCommandBox = (blocks: Block[], frame: number): Box => {
  const block = blocks.find((b) => frame >= b.cmd[0] && frame < b.until) ?? blocks[0];
  const chars = 2 + block.command.length + (block.exit ? 12 : 0);
  return {x: PANE_X + PANE_PAD, y: TERM_TOP + PANE_PAD, w: chars * TERM_FONT * MONO_ADVANCE + 8, h: TERM_LINE};
};

const fileRowsBox = (state: FileState, first: number, count: number): Box => {
  const longest = Math.max(...state.lines.slice(first, first + count).map((l) => l.length), 24);
  return {
    x: PANE_X + PANE_PAD,
    y: FILE_TOP + PANE_PAD + (first - state.firstRow) * FILE_LINE,
    w: longest * FILE_FONT * MONO_ADVANCE + 8,
    h: count * FILE_LINE,
  };
};

// ------------------------------------------------------------------ story

const Story: React.FC<{tl: Timeline}> = ({tl}) => {
  const frame = useCurrentFrame();
  const state = [...tl.files].reverse().find((f) => frame >= f.from) ?? tl.files[0];
  const opening = tl.files[0].fadeIn ? ramp(frame, tl.files[0].fadeIn) : 1;

  const active = tl.spots
    .filter((s) => frame >= s.on[0] - SPOT_FADE && frame < s.on[1] + SPOT_FADE)
    .map((s) => {
      const t = s.target;
      const box =
        t.kind === 'fileRows'
          ? fileRowsBox(state, t.first, t.count)
          : t.kind === 'termLines'
            ? termLineBox(tl.blocks, frame, t.from, t.count)
            : termCommandBox(tl.blocks, frame);
      return {spot: s, box, opacity: Math.min(ramp(frame, [s.on[0] - SPOT_FADE, s.on[0]]), 1 - ramp(frame, [s.on[1], s.on[1] + SPOT_FADE]))};
    });

  return (
    <AbsoluteFill style={{backgroundColor: T.paper, ...STABLE}}>
      <StepStrip tl={tl} opacity={opening} />
      <FilePane state={state} frame={frame} opacity={1} />
      <Terminal repo="research-repo" blocks={tl.blocks} frame={frame} opacity={opening} />
      {active.length > 0 && (
        <Spotlight
          box={active[active.length - 1].box}
          dim={Math.max(...active.map((a) => a.opacity))}
          captions={active.map((a) => ({text: a.spot.caption, below: a.spot.below, opacity: a.opacity}))}
        />
      )}
    </AbsoluteFill>
  );
};

const Thesis: React.FC<{tl: Timeline}> = ({tl}) => {
  const local = useCurrentFrame();
  const t0 = tl.storyOut[0];
  const storyOut = ramp(local + t0, tl.storyOut);
  const thesisIn = ramp(local + t0, tl.thesisIn);
  return (
    <AbsoluteFill style={{backgroundColor: T.paper, opacity: storyOut, ...STABLE}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: HEIGHT / 2 - 60, textAlign: 'center', fontFamily: SERIF, fontSize: 64, color: T.ink, opacity: thesisIn}}>
        {tl.thesis}
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: HEIGHT / 2 + 40, textAlign: 'center', fontFamily: MONO, fontSize: 24, color: T.muted, opacity: thesisIn}}>
        claims-ledger
      </div>
    </AbsoluteFill>
  );
};

export const Film: React.FC<FilmProps> = ({scenario}) => {
  const tl = SCENARIOS[scenario]();
  return (
    <AbsoluteFill style={{backgroundColor: T.paper}}>
      <Sequence name="story" from={0} durationInFrames={tl.storyOut[1]}>
        <Story tl={tl} />
      </Sequence>
      <Sequence name="thesis" from={tl.storyOut[0]} durationInFrames={tl.durationInFrames - tl.storyOut[0]}>
        <Thesis tl={tl} />
      </Sequence>
    </AbsoluteFill>
  );
};
