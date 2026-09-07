import React from 'react';
import {Composition} from 'remotion';
import {ContactSheet, contactSize, Storyboard, storyboardSize} from './ContactSheet';
import {Film} from './Film';
import {SCENARIOS, type ScenarioId} from './scenarios';
import {FPS, HEIGHT, WIDTH} from './timeline';

const FILMS: {id: string; scenario: ScenarioId}[] = [
  {id: 'NothingFallsSilently', scenario: 'refuted'},
  {id: 'ReplacedNeverEdited', scenario: 'superseded'},
];

export const RemotionRoot: React.FC = () => (
  <>
    {FILMS.map(({id, scenario}) => {
      const tl = SCENARIOS[scenario]();
      const contact = contactSize(scenario);
      const board = storyboardSize(scenario);
      return (
        <React.Fragment key={id}>
          <Composition id={id} component={Film} durationInFrames={tl.durationInFrames} fps={FPS} width={WIDTH} height={HEIGHT} defaultProps={{scenario}} />
          <Composition id={`${id}-ContactSheet`} component={ContactSheet} durationInFrames={tl.durationInFrames} fps={FPS} width={contact.width} height={contact.height} defaultProps={{scenario}} />
          <Composition id={`${id}-Storyboard`} component={Storyboard} durationInFrames={tl.durationInFrames} fps={FPS} width={board.width} height={board.height} defaultProps={{scenario}} />
        </React.Fragment>
      );
    })}
  </>
);
