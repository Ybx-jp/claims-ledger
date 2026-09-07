import {cancelRender, continueRender, delayRender, staticFile} from 'remotion';

/**
 * The faces are committed under public/fonts and loaded from staticFile(), so
 * the same source renders the same pixels and a missing face stalls the render
 * instead of substituting. IBM Plex Serif and Mono stand in for the figures'
 * Charter/system-mono stacks, which are not freely redistributable.
 *
 * Source: @fontsource/ibm-plex-serif@5.2.6 and @fontsource/ibm-plex-mono (the
 * upstream project is IBM/plex). Licence: SIL Open Font License 1.1, in
 * public/fonts/OFL.txt.
 */

export const SERIF = 'IBM Plex Serif';
export const MONO = 'IBM Plex Mono';

export const FACES = [
  {family: SERIF, weight: '400', file: 'fonts/ibm-plex-serif-latin-400-normal.woff2'},
  {family: MONO, weight: '400', file: 'fonts/ibm-plex-mono-latin-400-normal.woff2'},
] as const;

/** A canvas advance width for one string in one family, at 100 px. */
export const advance = (family: string, text: string): number => {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('no 2d context to measure type with');
  ctx.font = `400 100px "${family}"`;
  return ctx.measureText(text).width;
};

/**
 * A face that did not load substitutes silently, so loading is verified by
 * measurement: the string's advance in the face must differ from its advance in
 * a family that cannot resolve. Identical widths mean the fallback drew.
 */
export const verifyFaces = (): {family: string; ok: boolean; width: number; fallback: number}[] =>
  FACES.map(({family, weight}) => {
    const width = advance(family, 'Scores at or above 0.72');
    const fallback = advance('__no_such_face__', 'Scores at or above 0.72');
    const checked = document.fonts.check(`${weight} 100px "${family}"`);
    return {family, ok: checked && width !== fallback, width, fallback};
  });

let loaded: Promise<void> | null = null;

export const loadFonts = (): Promise<void> => {
  if (loaded) return loaded;
  const handle = delayRender(`Loading ${FACES.length} IBM Plex faces`);
  loaded = Promise.all(
    FACES.map(async ({family, weight, file}) => {
      const face = new FontFace(family, `url(${staticFile(file)}) format('woff2')`, {weight});
      await face.load();
      document.fonts.add(face);
    }),
  )
    .then(() => {
      const bad = verifyFaces().filter((r) => !r.ok);
      if (bad.length) {
        throw new Error(`faces substituted: ${bad.map((b) => b.family).join(', ')}`);
      }
      continueRender(handle);
    })
    .catch((err) => cancelRender(err));
  return loaded;
};

loadFonts();
