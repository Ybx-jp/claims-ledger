import {CAPTURES} from './captures';
import type {Beat, Block, FileState, Interval, Line, Spot, Timeline} from './timeline';

/**
 * The two films, as timelines built from the captured surfaces. Frames are
 * laid down by a cursor so a hold is a number in one place, not a constant
 * repeated in twelve.
 */

export type ScenarioId = 'refuted' | 'superseded';

const APPEND = '<!-- APPEND BELOW THIS LINE ONLY -->';

/** The status table cropped to the entries in the story; the elided rows are counted. */
const cropStatus = (text: string, cast: string[]): string[] => {
  const lines = text.split('\n');
  const rows = lines.filter((l) => cast.some((id) => l.startsWith(id)));
  const footer = lines[lines.length - 1];
  const elided = lines.filter((l) => /^R\d{4}/.test(l)).length - rows.length;
  return [...rows, `  ⋮ ${elided} more`, '', footer];
};

const statusLines = (text: string, cast: string[], changed: string[]): Line[] =>
  cropStatus(text, cast).map((l) => {
    const id = l.slice(0, 5);
    const hot = changed.includes(id);
    return {text: l, tone: cast.includes(id) ? (hot ? 'accent' : 'ink') : 'muted', soft: hot};
  });

const outputLines = (text: string): Line[] =>
  text.split('\n').map((l) => ({
    text: l,
    tone: l.startsWith('FAIL') || l.startsWith('FLAG') ? 'accent' : 'ink',
    wrap: true,
  }));

/** A cursor that lays intervals down in order. */
class Cursor {
  t = 0;
  at(n: number): Interval {
    const s = this.t;
    this.t += n;
    return [s, this.t];
  }
  hold(n: number): number {
    this.t += n;
    return this.t;
  }
}

type Shared = {
  cast: string[];
  newSpotRows: (newLines: string[]) => {first: number; count: number};
  newCaption: string;
  verdictCaption: string;
  statusCaption: string;
  openCaption: string;
  thesis: string;
  title: string;
};

const buildStory = (id: ScenarioId, c: (typeof CAPTURES)['refuted'] | (typeof CAPTURES)['superseded'], s: Shared): Timeline => {
  const before = c.entryBefore.split('\n');
  const after = c.entryAfter.split('\n');
  const newLines = c.newText.split('\n');
  const appendIndex = after.indexOf(APPEND);
  const groundsIndex = before.indexOf('## Grounds');
  const verdictRows = c.verdictRow.trimEnd().split('\n').length;

  const files: FileState[] = [];
  const blocks: Block[] = [];
  const spots: Spot[] = [];
  const beats: Beat[] = [];
  const k = new Cursor();

  // 1 · a claim
  const b1 = k.t;
  files.push({from: 0, path: c.entryPath, lines: before, firstRow: 12, fadeIn: k.at(40)});
  const status1 = {cmd: k.at(10), out: (k.hold(5), k.at(30))};
  k.hold(15);
  spots.push({id: 'grounds', on: k.at(120), target: {kind: 'fileRows', first: groundsIndex + 2, count: before[groundsIndex + 3]?.startsWith('- ') ? 2 : 1}, caption: 'Grounds: the evidence this claim rests on.', below: true});
  k.hold(15);
  spots.push({id: 'open', on: k.at(90), target: {kind: 'termLines', from: s.cast.indexOf(c.entryId.slice(0, 5)), count: 1}, caption: s.openCaption, below: true});
  k.hold(5);
  beats.push({id: 'entry', step: '1 · a claim', start: b1, end: k.t, understanding: 'a claim file, with its evidence, and its status'});
  blocks.push({command: 'claims-ledger status', lines: statusLines(c.statusBefore.text, s.cast, []), ...status1, until: k.t});

  // 2 · check
  const b2 = k.t;
  const check1 = {cmd: k.at(10), out: (k.hold(5), k.at(30)), exit: {code: c.checkBefore.exit, at: (k.hold(5), k.at(10))}};
  k.hold(5);
  spots.push({id: 'clean', on: k.at(100), target: {kind: 'termLines', from: 0, count: 5}, caption: 'Five checkers. A clean run exits 0.', below: true});
  k.hold(5);
  beats.push({id: 'check', step: '2 · check', start: b2, end: k.t, understanding: 'five checkers, all clean'});
  blocks.push({command: 'claims-ledger check', lines: outputLines(c.checkBefore.text), ...check1, until: k.t});

  // 3 · a new claim
  const b3 = k.t;
  files.push({from: k.t, path: c.newPath, lines: newLines, firstRow: 0, fadeIn: k.at(30)});
  k.hold(15);
  spots.push({id: 'new', on: k.at(120), target: {kind: 'fileRows', ...s.newSpotRows(newLines)}, caption: s.newCaption, below: true});
  k.hold(15);
  const back = k.t;
  const landing = {first: appendIndex + 4, count: verdictRows, at: [back + 60, back + 90] as Interval, settle: [back + 100, back + 140] as Interval};
  files.push({from: back, path: c.entryPath, lines: after, firstRow: appendIndex - 1, fadeIn: k.at(20), landing});
  k.hold(15);
  spots.push({id: 'verdict', on: k.at(145), target: {kind: 'fileRows', first: landing.first, count: landing.count}, caption: s.verdictCaption, below: true});
  k.hold(15);
  const status2 = {cmd: k.at(10), out: (k.hold(5), k.at(25))};
  k.hold(10);
  spots.push({id: 'status', on: k.at(80), target: {kind: 'termLines', from: s.cast.indexOf(c.entryId.slice(0, 5)), count: 1}, caption: s.statusCaption, below: true});
  k.hold(10);
  beats.push({id: 'new', step: id === 'refuted' ? '3 · a new claim' : '3 · a successor', start: b3, end: k.t, understanding: 'a new claim is written; the old one gets a verdict naming it; the status follows'});
  blocks.push({command: 'claims-ledger status', lines: statusLines(c.statusAfterVerdict.text, s.cast, [c.entryId.slice(0, 5)]), ...status2, until: k.t});

  return {id, title: s.title, durationInFrames: 0, beats, files, blocks, spots, thesis: s.thesis, storyOut: [0, 0], thesisIn: [0, 0]};
};

const finish = (tl: Timeline, k: Cursor): Timeline => {
  const storyOut = k.at(30);
  const thesisIn: Interval = [storyOut[0] + 25, storyOut[0] + 55];
  const end = k.hold(120);
  tl.beats.push({id: 'thesis', step: '', start: storyOut[0], end, understanding: 'the sentence'});
  return {...tl, durationInFrames: end, storyOut, thesisIn};
};

/** The cursor a story left off at is the end of its last beat. */
const resume = (tl: Timeline): Cursor => {
  const k = new Cursor();
  k.t = tl.beats[tl.beats.length - 1].end;
  return k;
};

export const refuted = (): Timeline => {
  const c = CAPTURES.refuted;
  const cast = ['R0001', 'R0002', 'R0003', 'R0013'];
  const tl = buildStory('refuted', c, {
    cast,
    newSpotRows: (lines) => ({first: lines.indexOf('## Assertion') + 2, count: 2}),
    newCaption: 'A new claim is written. It refutes R0001.',
    verdictCaption: 'R0001 is refuted. The verdict names the new claim.',
    statusCaption: 'The status follows the last verdict: refuted.',
    openCaption: 'Its status is open: no verdict has been written.',
    thesis: 'Nothing falls silently.',
    title: 'nothing-falls-silently',
  });
  const k = resume(tl);
  const check2Lines = outputLines(c.checkAfterVerdict.text);
  const firstFail = check2Lines.findIndex((l) => l.text.startsWith('FAIL'));

  // 4 · what fails
  const b4 = k.t;
  const check2 = {cmd: k.at(10), out: (k.hold(5), k.at(75)), exit: {code: c.checkAfterVerdict.exit, at: (k.hold(5), k.at(10))}};
  k.hold(-5);
  tl.spots.push({id: 'fails', on: k.at(130), target: {kind: 'termLines', from: firstFail, count: 4}, caption: 'Two entries and two documents cite R0001 as live. All four fail.', below: false});
  k.hold(10);
  tl.beats.push({id: 'fail', step: '4 · what fails', start: b4, end: k.t, understanding: 'everything that cited it live now fails'});
  tl.blocks.push({command: 'claims-ledger check', lines: check2Lines, ...check2, until: k.t});

  // 5 · propagate
  const b5 = k.t;
  const propLines = outputLines(c.propagate!.text);
  const firstFlag = propLines.findIndex((l) => l.text.startsWith('FLAG'));
  const prop = {cmd: k.at(10), out: (k.hold(5), k.at(45))};
  k.hold(5);
  tl.spots.push({id: 'flagged', on: k.at(100), target: {kind: 'termLines', from: firstFlag, count: 2}, caption: 'propagate writes the dependents their verdict.', below: true});
  k.hold(15);
  const dep = c.dependentAfter!.split('\n');
  const depAppend = dep.indexOf(APPEND);
  const cut = k.t;
  const depLanding = {first: depAppend + 4, count: 3, at: [cut + 5, cut + 35] as Interval, settle: [cut + 45, cut + 85] as Interval};
  tl.files.push({from: cut, path: c.dependentPath!, lines: dep, firstRow: depAppend - 1, fadeIn: k.at(20), landing: depLanding});
  k.hold(20);
  tl.spots.push({id: 'cause', on: k.at(120), target: {kind: 'fileRows', first: depLanding.first, count: 3}, caption: 'R0003 rests on R0001. Its row names the cause.', below: true});
  k.hold(10);
  const status3 = {cmd: k.at(10), out: (k.hold(5), k.at(25))};
  k.hold(10);
  tl.spots.push({id: 'contested', on: k.at(90), target: {kind: 'termLines', from: 1, count: 2}, caption: 'Both dependents are now contested.', below: true});
  k.hold(10);
  tl.beats.push({id: 'propagate', step: '5 · propagate', start: b5, end: k.t, understanding: 'the machine writes the dependents their row'});
  tl.blocks.push({command: 'claims-ledger propagate --write', lines: propLines, ...prop, until: status3.cmd[0]});
  tl.blocks.push({command: 'claims-ledger status', lines: statusLines(c.statusAfterPropagate!.text, cast, ['R0002', 'R0003']), ...status3, until: k.t});

  // 6 · the gate
  const b6 = k.t;
  const commit = {cmd: k.at(10), out: (k.hold(5), k.at(65)), exit: {code: c.commit.exit, at: (k.hold(5), k.at(10))}};
  k.hold(5);
  tl.spots.push({id: 'refused', on: k.at(100), target: {kind: 'termCommand'}, caption: 'The pre-commit hook runs the same check. Refused.', below: true});
  k.hold(10);
  tl.beats.push({id: 'gate', step: '6 · the gate', start: b6, end: k.t, understanding: 'the commit is refused until the citations are fixed'});
  const done = finish(tl, k);
  tl.blocks.push({command: `git commit -m "${c.commit.argv[3]}"`, lines: outputLines(c.commit.text), ...commit, until: done.durationInFrames});
  return done;
};

export const superseded = (): Timeline => {
  const c = CAPTURES.superseded;
  const cast = ['R0005', 'R0006', 'R0013'];
  const tl = buildStory('superseded', c, {
    cast,
    newSpotRows: (lines) => ({first: lines.findIndex((l) => l.startsWith('supersedes:')), count: 1}),
    newCaption: 'A new claim is written. It supersedes R0006.',
    verdictCaption: 'R0006 is superseded. The verdict names its successor.',
    statusCaption: 'The status follows the last verdict: superseded.',
    openCaption: 'Its status is open: no verdict has been written.',
    thesis: 'A claim is replaced, never edited.',
    title: 'replaced-never-edited',
  });
  const k = resume(tl);

  // 4 · check
  const b4 = k.t;
  const check2 = {cmd: k.at(10), out: (k.hold(5), k.at(30)), exit: {code: c.checkAfterVerdict.exit, at: (k.hold(5), k.at(10))}};
  k.hold(5);
  tl.spots.push({id: 'clean2', on: k.at(120), target: {kind: 'termLines', from: 0, count: 5}, caption: 'Successor and predecessor name each other. All clean.', below: true});
  k.hold(10);
  tl.beats.push({id: 'check2', step: '4 · check', start: b4, end: k.t, understanding: 'the succession is recorded both ways, so nothing fails'});
  tl.blocks.push({command: 'claims-ledger check', lines: outputLines(c.checkAfterVerdict.text), ...check2, until: k.t});

  // 5 · the gate
  const b5 = k.t;
  const commit = {cmd: k.at(10), out: (k.hold(5), k.at(35)), exit: {code: c.commit.exit, at: (k.hold(5), k.at(10))}};
  k.hold(5);
  tl.spots.push({id: 'accepted', on: k.at(110), target: {kind: 'termCommand'}, caption: 'The pre-commit hook runs the same check. Accepted.', below: true});
  k.hold(10);
  tl.beats.push({id: 'gate', step: '5 · the gate', start: b5, end: k.t, understanding: 'the commit is accepted'});
  const done = finish(tl, k);
  tl.blocks.push({command: `git commit -m "${c.commit.argv[3]}"`, lines: outputLines(c.commit.text), ...commit, until: done.durationInFrames});
  return done;
};

export const SCENARIOS: Record<ScenarioId, () => Timeline> = {refuted, superseded};
