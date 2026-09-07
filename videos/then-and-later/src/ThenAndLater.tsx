import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {MONO, SERIF} from './fonts';
import {
  BEATS,
  COLUMN_LABEL_Y,
  COPY,
  HEIGHT,
  LEFT_X,
  MOVES,
  P,
  PANEL_W,
  PANEL_Y,
  RIGHT_X,
  T,
  TETHER,
  TIME_RULE,
  WIDTH,
  panelX,
  ramp,
} from './timing';

/**
 * then-and-later. One sentence, one source, two worlds.
 *
 * Everything is derived from the current frame through `ramp()` over the
 * intervals in timing.ts. The one tracked move — the panel's slide at the
 * split — is the only place a non-linear easing appears, and it is the
 * quadratic slow-in/slow-out Dragicevic et al. measured; every other change is
 * a linear, monotonic fade of a thing that is not moving.
 */

type World = 'prose' | 'ledger';

/** The digits in the source line, cross-faded in the same mono cells. */
const Digits: React.FC<{flip: number}> = ({flip}) => (
  <span style={{position: 'relative', display: 'inline-block'}}>
    <span style={{opacity: 1 - flip}}>{COPY.before}</span>
    <span style={{position: 'absolute', left: 0, top: 0, opacity: flip}}>{COPY.after}</span>
  </span>
);

const Greek: React.FC<{y: number; w: number}> = ({y, w}) => (
  <div
    style={{
      position: 'absolute',
      left: P.cardPad,
      top: y,
      width: w,
      height: 12,
      borderRadius: 6,
      background: T.rule,
    }}
  />
);

const Chip: React.FC<{text: string; color: string; opacity: number}> = ({text, color, opacity}) => (
  <div
    style={{
      position: 'absolute',
      right: 0,
      top: P.chipY,
      height: P.chipH,
      padding: '0 18px',
      borderRadius: P.chipH / 2,
      border: `2px solid ${color}`,
      color,
      fontFamily: MONO,
      fontSize: 22,
      lineHeight: `${P.chipH - 4}px`,
      opacity,
    }}
  >
    {text}
  </div>
);

/**
 * One world. `x` is the panel's left edge; everything else is a function of
 * the frame and which world this is.
 */
const Panel: React.FC<{world: World; x: number; opacity: number}> = ({world, x, opacity}) => {
  const frame = useCurrentFrame();
  const ledger = world === 'ledger';

  const cardRise = ramp(frame, MOVES.cardRise);
  const matchIn = ramp(frame, MOVES.matchIn);
  const forgets = ledger ? 0 : ramp(frame, MOVES.proseForgets);
  const tetherDraw = ledger ? ramp(frame, MOVES.tetherDraw) : 0;
  const shaIn = ledger ? ramp(frame, MOVES.shaIn) : 0;
  const chipIn = ledger ? ramp(frame, MOVES.chipIn) : 0;
  const flip = ramp(frame, MOVES.digitsFlip);
  const tetherAccent = ledger ? ramp(frame, MOVES.tetherAccent) : 0;
  const ghostIn = ledger ? ramp(frame, MOVES.ghostIn) : 0;
  const shaFlip = ledger ? ramp(frame, MOVES.shaFlip) : 0;
  const chipFlip = ledger ? ramp(frame, MOVES.chipFlip) : 0;
  const captionIn = ramp(frame, MOVES.captionsIn);

  // The source-side highlight: lit at the match, forgotten by prose after the
  // split, and in the ledger replaced by the empty dashed place once the bytes
  // no longer contain the span.
  const spanFill = ledger ? T.accentSoft : T.mark;
  const spanOpacity = matchIn * (1 - forgets) * (1 - ghostIn);

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: PANEL_Y,
        width: PANEL_W,
        height: HEIGHT - PANEL_Y,
        opacity,
      }}
    >
      {ledger && (
        <>
          <Chip text={COPY.corroborated} color={T.muted} opacity={chipIn * (1 - chipFlip)} />
          <Chip text={COPY.contested} color={T.accent} opacity={chipFlip} />
        </>
      )}

      <div
        style={{
          position: 'absolute',
          left: 0,
          top: P.assertionY,
          fontFamily: SERIF,
          fontSize: P.assertionSize,
          lineHeight: 1.2,
          color: T.ink,
          whiteSpace: 'nowrap',
        }}
      >
        {COPY.assertion}
      </div>

      <div
        style={{
          position: 'absolute',
          left: 0,
          top: P.quoteY,
          height: P.quoteH,
          padding: '0 16px',
          borderRadius: 6,
          background: ledger ? T.accentSoft : T.mark,
          fontFamily: MONO,
          fontSize: P.quoteSize,
          lineHeight: `${P.quoteH}px`,
          color: T.ink,
          whiteSpace: 'nowrap',
          opacity: matchIn,
        }}
      >
        {`“${COPY.quotePrefix}${COPY.before}${COPY.quoteSuffix}”`}
      </div>

      {/* the source document */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: P.cardY + (1 - cardRise) * 60,
          width: PANEL_W,
          height: P.cardH,
          borderRadius: 8,
          border: `2px solid ${T.rule}`,
          background: T.paper,
          opacity: cardRise,
        }}
      >
        <div
          style={{
            position: 'absolute',
            left: P.cardPad,
            top: P.cardHeaderY,
            fontFamily: MONO,
            fontSize: 20,
            color: T.muted,
          }}
        >
          {COPY.sourceName}
        </div>
        {P.greekAbove.map((g) => (
          <Greek key={g.y} {...g} />
        ))}
        <div
          style={{
            position: 'absolute',
            left: P.cardPad - 8,
            top: P.cardLineY - 8,
            width: TETHER.lineW + 16,
            height: P.cardLineSize * 1.5 + 16,
            borderRadius: 6,
            background: spanFill,
            opacity: spanOpacity,
          }}
        />
        <div
          style={{
            position: 'absolute',
            left: P.cardPad - 8,
            top: P.cardLineY - 8,
            width: TETHER.lineW + 16,
            height: P.cardLineSize * 1.5 + 16,
            borderRadius: 6,
            border: `2px dashed ${T.accent}`,
            boxSizing: 'border-box',
            opacity: ghostIn,
          }}
        />
        <div
          style={{
            position: 'absolute',
            left: P.cardPad,
            top: P.cardLineY,
            fontFamily: MONO,
            fontSize: P.cardLineSize,
            lineHeight: 1.5,
            color: T.ink,
            whiteSpace: 'nowrap',
          }}
        >
          {COPY.quotePrefix}
          <Digits flip={flip} />
          {COPY.quoteSuffix}
        </div>
        {P.greekBelow.map((g) => (
          <Greek key={g.y} {...g} />
        ))}
      </div>

      {/* the tether, ledger only: ink drawn from the quotation down, accent drawn from the bytes up */}
      {ledger && (
        <svg
          width={PANEL_W}
          height={HEIGHT - PANEL_Y}
          style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}
        >
          <path
            d={TETHER.d}
            pathLength={1}
            fill="none"
            stroke={T.ink}
            strokeWidth={2.5}
            strokeDasharray={1}
            strokeDashoffset={1 - tetherDraw}
          />
          <path
            d={TETHER.dReversed}
            pathLength={1}
            fill="none"
            stroke={T.accent}
            strokeWidth={2.5}
            strokeDasharray={1}
            strokeDashoffset={1 - tetherAccent}
          />
          <circle cx={TETHER.from.x} cy={TETHER.from.y} r={5} fill={T.ink} opacity={tetherDraw} />
          <circle cx={TETHER.to.x} cy={TETHER.to.y} r={5} fill={T.ink} opacity={tetherDraw} />
          <circle cx={TETHER.to.x} cy={TETHER.to.y} r={5} fill={T.accent} opacity={tetherAccent} />
        </svg>
      )}

      {ledger && (
        <div
          style={{
            position: 'absolute',
            right: 0,
            top: P.shaY,
            fontFamily: MONO,
            fontSize: P.shaSize,
            whiteSpace: 'nowrap',
          }}
        >
          <span style={{color: T.muted, opacity: shaIn * (1 - shaFlip)}}>{COPY.shaBefore}</span>
          <span style={{position: 'absolute', right: 0, top: 0, color: T.accent, opacity: shaFlip}}>
            {COPY.shaAfter}
          </span>
        </div>
      )}

      <div
        style={{
          position: 'absolute',
          left: 0,
          top: P.captionY,
          fontFamily: SERIF,
          fontSize: P.captionSize,
          color: ledger ? T.accent : T.muted,
          opacity: captionIn,
        }}
      >
        {ledger ? COPY.caught : COPY.nothing}
      </div>
    </div>
  );
};

const Label: React.FC<{text: string; x: number; y: number; opacity: number; anchor?: 'left' | 'right'}> = ({
  text,
  x,
  y,
  opacity,
  anchor = 'left',
}) => (
  <div
    style={{
      position: 'absolute',
      [anchor]: anchor === 'left' ? x : WIDTH - x,
      top: y,
      fontFamily: SERIF,
      fontSize: 18,
      letterSpacing: '0.16em',
      color: T.muted,
      opacity,
      whiteSpace: 'nowrap',
    }}
  >
    {text}
  </div>
);

const Story: React.FC = () => {
  const frame = useCurrentFrame();
  const sentenceIn = ramp(frame, MOVES.sentenceIn);
  const copyIn = ramp(frame, MOVES.copyIn);
  const labelsIn = ramp(frame, MOVES.labelsIn);
  const sweep = ramp(frame, MOVES.timeSweep);
  const laterIn = ramp(frame, MOVES.laterIn);
  const x = panelX(frame);

  return (
    <AbsoluteFill style={{backgroundColor: T.paper}}>
      {/* the passage of time, across the top */}
      <svg width={WIDTH} height={HEIGHT} style={{position: 'absolute', left: 0, top: 0}}>
        <line
          x1={TIME_RULE.x0}
          y1={TIME_RULE.y}
          x2={TIME_RULE.x1}
          y2={TIME_RULE.y}
          pathLength={1}
          stroke={T.muted}
          strokeWidth={1.5}
          strokeDasharray={1}
          strokeDashoffset={1 - sweep}
        />
      </svg>
      <Label text={COPY.whenWritten} x={TIME_RULE.x0} y={TIME_RULE.y - 30} opacity={labelsIn} />
      <Label text={COPY.later} x={TIME_RULE.x1} y={TIME_RULE.y - 30} opacity={laterIn} anchor="right" />

      <Label text={COPY.prose} x={LEFT_X} y={COLUMN_LABEL_Y} opacity={labelsIn} />
      <Label text={COPY.ledger} x={RIGHT_X} y={COLUMN_LABEL_Y} opacity={labelsIn} />

      {/* the ledger world fades in at its seat; the prose world is the panel that moved */}
      <Panel world="ledger" x={RIGHT_X} opacity={copyIn} />
      <Panel world="prose" x={x} opacity={sentenceIn} />
    </AbsoluteFill>
  );
};

const Thesis: React.FC = () => {
  const local = useCurrentFrame();
  const t0 = BEATS[BEATS.length - 1].start;
  const worldsOut = ramp(local + t0, MOVES.worldsOut);
  const thesisIn = ramp(local + t0, MOVES.thesisIn);
  return (
    <AbsoluteFill style={{backgroundColor: T.paper, opacity: worldsOut}}>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: HEIGHT / 2 - 60,
          textAlign: 'center',
          fontFamily: SERIF,
          fontSize: 60,
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

export const ThenAndLater: React.FC = () => {
  const thesis = BEATS[BEATS.length - 1];
  return (
    <AbsoluteFill style={{backgroundColor: T.paper}}>
      <Sequence name="story" from={0} durationInFrames={thesis.start + (MOVES.worldsOut[1] - MOVES.worldsOut[0])}>
        <Story />
      </Sequence>
      <Sequence name="thesis" from={thesis.start} durationInFrames={thesis.end - thesis.start}>
        <Thesis />
      </Sequence>
    </AbsoluteFill>
  );
};

/**
 * The track matte: the moving panel alone, white on black, nothing else drawn.
 * tools/track-centroid.py measures its centroid per frame and checks it against
 * `panelX`, the function the film positions the panel with.
 */
export const TrackMatte: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <div
        style={{
          position: 'absolute',
          left: panelX(frame),
          top: PANEL_Y,
          width: PANEL_W,
          height: 300,
          background: '#fff',
        }}
      />
    </AbsoluteFill>
  );
};
