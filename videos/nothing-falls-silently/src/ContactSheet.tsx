import React from 'react';
import {AbsoluteFill, Freeze} from 'remotion';
import {Film} from './Film';
import {SCENARIOS, type ScenarioId} from './scenarios';
import {diagnosticFrames, FPS, HEIGHT, storyboardFrames, WIDTH} from './timeline';

/**
 * Every tile freezes the real film at one frame, so a sheet cannot drift from
 * the film. The frame lists are derived from the timeline in timeline.ts, so
 * a move cannot leave the diagnostics by being forgotten. The host's duration
 * must cover the highest frozen frame: Freeze clamps to it.
 */

const GAP = 16;
const LABEL_H = 26;
const PAD = 24;
const HEADER = 44;

type SheetSpec = {cols: number; scale: number; frames: (id: ScenarioId) => {frame: number; label: string}[]; title: string};

const CONTACT: SheetSpec = {cols: 5, scale: 0.19, frames: (id) => diagnosticFrames(SCENARIOS[id]()), title: 'contact sheet'};
const STORYBOARD: SheetSpec = {cols: 2, scale: 0.46, frames: (id) => storyboardFrames(SCENARIOS[id]()), title: 'storyboard'};

export const sheetSize = (spec: SheetSpec, id: ScenarioId) => {
  const tw = Math.round(WIDTH * spec.scale);
  const th = Math.round(HEIGHT * spec.scale);
  const n = spec.frames(id).length;
  const rows = Math.ceil(n / spec.cols);
  return {width: PAD * 2 + spec.cols * tw + (spec.cols - 1) * GAP, height: PAD * 2 + HEADER + rows * (th + LABEL_H + GAP)};
};

const Sheet: React.FC<{spec: SheetSpec; scenario: ScenarioId}> = ({spec, scenario}) => {
  const tl = SCENARIOS[scenario]();
  const tw = Math.round(WIDTH * spec.scale);
  const th = Math.round(HEIGHT * spec.scale);
  const frames = spec.frames(scenario);
  return (
    <AbsoluteFill style={{backgroundColor: '#07090b', padding: PAD}}>
      <div style={{fontFamily: 'monospace', fontSize: 20, color: '#d8dee4', height: HEADER}}>
        {`${tl.title} · ${spec.title} · ${WIDTH}×${HEIGHT} · ${FPS} fps · ${tl.durationInFrames} frames · silent H.264 · ${frames.length} frames shown`}
      </div>
      <div style={{display: 'grid', gridTemplateColumns: `repeat(${spec.cols}, ${tw}px)`, columnGap: GAP, rowGap: GAP}}>
        {frames.map((d) => (
          <div key={d.frame} style={{display: 'flex', flexDirection: 'column', gap: 4}}>
            <div style={{fontFamily: 'monospace', fontSize: 15, color: '#a9b4bf', height: LABEL_H - 4}}>
              {`f${String(d.frame).padStart(4, '0')}  ${(d.frame / FPS).toFixed(2)}s  ${d.label}`}
            </div>
            <div style={{width: tw, height: th, overflow: 'hidden', position: 'relative', outline: '1px solid #2a323c'}}>
              <div style={{width: WIDTH, height: HEIGHT, transform: `scale(${spec.scale})`, transformOrigin: 'top left'}}>
                <Freeze frame={d.frame}>
                  <Film scenario={scenario} />
                </Freeze>
              </div>
            </div>
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

export const ContactSheet: React.FC<{scenario: ScenarioId}> = ({scenario}) => <Sheet spec={CONTACT} scenario={scenario} />;
export const Storyboard: React.FC<{scenario: ScenarioId}> = ({scenario}) => <Sheet spec={STORYBOARD} scenario={scenario} />;
export const contactSize = (id: ScenarioId) => sheetSize(CONTACT, id);
export const storyboardSize = (id: ScenarioId) => sheetSize(STORYBOARD, id);
