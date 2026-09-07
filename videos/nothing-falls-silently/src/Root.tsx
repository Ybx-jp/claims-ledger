import React from 'react';
import {Composition} from 'remotion';
import {ContactSheet, SHEET_DURATION, SHEET_HEIGHT, SHEET_WIDTH, STORYBOARD_HEIGHT, STORYBOARD_WIDTH, Storyboard} from './ContactSheet';
import {Film, TrackMatte} from './Film';
import {DURATION_IN_FRAMES, FPS, HEIGHT, WIDTH} from './timing';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="NothingFallsSilently"
      component={Film}
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
    <Composition
      id="Storyboard"
      component={Storyboard}
      durationInFrames={SHEET_DURATION}
      fps={FPS}
      width={STORYBOARD_WIDTH}
      height={STORYBOARD_HEIGHT}
    />
  </>
);
