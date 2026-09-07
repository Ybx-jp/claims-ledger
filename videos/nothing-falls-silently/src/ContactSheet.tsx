import React from 'react';
import {AbsoluteFill, Freeze} from 'remotion';
import {Film} from './Film';
import {DIAGNOSTIC_FRAMES, DURATION_IN_FRAMES, FPS, HEIGHT, WIDTH} from './timing';

/**
 * Every tile freezes the real film at one diagnostic frame, so the sheet cannot
 * drift from the film. The frame list is derived in timing.ts from the moves
 * and beats, so a move cannot leave the diagnostics by being forgotten.
 */

const COLS = 5;
const TILE_SCALE = 0.19;
const TILE_W = Math.round(WIDTH * TILE_SCALE);
const TILE_H = Math.round(HEIGHT * TILE_SCALE);
const GAP = 16;
const LABEL_H = 26;
const PAD = 24;
const HEADER = 44;

export const SHEET_WIDTH = PAD * 2 + COLS * TILE_W + (COLS - 1) * GAP;
const ROWS = Math.ceil(DIAGNOSTIC_FRAMES.length / COLS);
export const SHEET_HEIGHT = PAD * 2 + HEADER + ROWS * (TILE_H + LABEL_H + GAP);
/** Freeze clamps to the host's duration, so the sheet must be at least as long as the film. */
export const SHEET_DURATION = DURATION_IN_FRAMES;

const Tile: React.FC<{frame: number; label: string}> = ({frame, label}) => (
  <div style={{display: 'flex', flexDirection: 'column', gap: 4}}>
    <div style={{fontFamily: 'monospace', fontSize: 15, color: '#a9b4bf', height: LABEL_H - 4}}>
      {`f${String(frame).padStart(3, '0')}  ${(frame / FPS).toFixed(2)}s  ${label}`}
    </div>
    <div style={{width: TILE_W, height: TILE_H, overflow: 'hidden', position: 'relative', outline: '1px solid #2a323c'}}>
      <div style={{width: WIDTH, height: HEIGHT, transform: `scale(${TILE_SCALE})`, transformOrigin: 'top left'}}>
        <Freeze frame={frame}>
          <Film />
        </Freeze>
      </div>
    </div>
  </div>
);

export const ContactSheet: React.FC = () => (
  <AbsoluteFill style={{backgroundColor: '#07090b', padding: PAD}}>
    <div style={{fontFamily: 'monospace', fontSize: 20, color: '#d8dee4', height: HEADER}}>
      {`nothing-falls-silently · ${WIDTH}×${HEIGHT} · ${FPS} fps · ${DURATION_IN_FRAMES} frames · silent H.264 · ${DIAGNOSTIC_FRAMES.length} diagnostic frames`}
    </div>
    <div style={{display: 'grid', gridTemplateColumns: `repeat(${COLS}, ${TILE_W}px)`, columnGap: GAP, rowGap: GAP}}>
      {DIAGNOSTIC_FRAMES.map((d) => (
        <Tile key={d.frame} {...d} />
      ))}
    </div>
  </AbsoluteFill>
);

/**
 * The storyboard: one tile per beat, at a size the words can be read at, for
 * approval before a render. Same instrument as the contact sheet.
 */
export const STORYBOARD_FRAMES: {frame: number; label: string}[] = [
  {frame: 160, label: 'entry · Grounds'},
  {frame: 280, label: 'entry · status open'},
  {frame: 445, label: 'check · clean'},
  {frame: 610, label: 'verdict · nothing yet'},
  {frame: 740, label: 'verdict · the decision, landing'},
  {frame: 850, label: 'verdict · appended'},
  {frame: 1000, label: 'verdict · status refuted'},
  {frame: 1225, label: 'fail · four cite it live'},
  {frame: 1415, label: 'propagate · flagged'},
  {frame: 1580, label: 'propagate · the cause'},
  {frame: 1745, label: 'propagate · contested'},
  {frame: 1950, label: 'gate · refused'},
  {frame: 2120, label: 'thesis'},
];
const SB_COLS = 2;
const SB_SCALE = 0.46;
const SB_W = Math.round(WIDTH * SB_SCALE);
const SB_H = Math.round(HEIGHT * SB_SCALE);
export const STORYBOARD_WIDTH = PAD * 2 + SB_COLS * SB_W + (SB_COLS - 1) * GAP;
export const STORYBOARD_HEIGHT =
  PAD * 2 + HEADER + Math.ceil(STORYBOARD_FRAMES.length / SB_COLS) * (SB_H + LABEL_H + GAP);

export const Storyboard: React.FC = () => (
  <AbsoluteFill style={{backgroundColor: '#07090b', padding: PAD}}>
    <div style={{fontFamily: 'monospace', fontSize: 20, color: '#d8dee4', height: HEADER}}>
      {`nothing-falls-silently · storyboard · ${STORYBOARD_FRAMES.length} beats`}
    </div>
    <div style={{display: 'grid', gridTemplateColumns: `repeat(${SB_COLS}, ${SB_W}px)`, columnGap: GAP, rowGap: GAP}}>
      {STORYBOARD_FRAMES.map((d) => (
        <div key={d.frame} style={{display: 'flex', flexDirection: 'column', gap: 4}}>
          <div style={{fontFamily: 'monospace', fontSize: 16, color: '#a9b4bf', height: LABEL_H - 4}}>
            {`f${String(d.frame).padStart(3, '0')}  ${(d.frame / FPS).toFixed(2)}s  ${d.label}`}
          </div>
          <div style={{width: SB_W, height: SB_H, overflow: 'hidden', position: 'relative', outline: '1px solid #2a323c'}}>
            <div style={{width: WIDTH, height: HEIGHT, transform: `scale(${SB_SCALE})`, transformOrigin: 'top left'}}>
              <Freeze frame={d.frame}>
                <Film />
              </Freeze>
            </div>
          </div>
        </div>
      ))}
    </div>
  </AbsoluteFill>
);
