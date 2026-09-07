import React from 'react';
import {Composition} from 'remotion';
import {ContactSheet, SHEET_DURATION, SHEET_HEIGHT, SHEET_WIDTH} from './ContactSheet';
import {ThenAndLater, TrackMatte} from './ThenAndLater';
import {DURATION_IN_FRAMES, FPS, HEIGHT, WIDTH} from './timing';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="ThenAndLater"
      component={ThenAndLater}
      durationInFrames={DURATION_IN_FRAMES}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
    <Composition
      id="ContactSheet"
      component={ContactSheet}
      durationInFrames={SHEET_DURATION}
      fps={FPS}
      width={SHEET_WIDTH}
      height={SHEET_HEIGHT}
    />
    <Composition
      id="TrackMatte"
      component={TrackMatte}
      durationInFrames={DURATION_IN_FRAMES}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  </>
);
