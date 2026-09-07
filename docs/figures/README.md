# Figures

Diagrams for the README and `docs/`, hand-authored as SVG so they diff, with a dark
variant derived from each light source by `build.py`. Every file here is a design
artifact: nothing in it is imported by the package.

```console
$ python3 docs/figures/build.py            # regenerate the -dark variants
$ python3 docs/figures/build.py --png /tmp # also rasterize both for review
```

The light file is the source of truth. Edit it, run the build, commit both.

## The figures

| file | explains | intended home |
|---|---|---|
| `four-roles.svg` | One frozen statement against Assertion · Grounds · Warrant · Backing, with the quotation resolved against the source bytes | README, under *Why* |
| `entry-anatomy.svg` | An entry file annotated part by part; the frozen region, the APPEND seam, the append-only tail | README after the example entry, or SCHEMA.md *The entry* |
| `status-derivation.svg` | The verdict list, the derived status, and the state diagram with the terminal set and the one reinstatement exception | SCHEMA.md *Statuses*; examples/FEATURES.md §6 |
| `five-checks.svg` | What each checker reads, what it holds, which two write | README *The five checks* |
| `resolution.svg` | The quote grammar — spans resolved in order against the stored bytes, elisions marked — and the `verbatim_sha` fingerprint over normalized Scope and sorted Backing | SCHEMA.md before *Immutability* |
| `freshness.svg` | The pin on a git timeline against the tree this run reads; the five findings with exit and discharge | FRESHNESS.md *The findings*; SCHEMA.md after *Freshness* |
| `propagation.svg` | The one machine-written verdict shape from its two causes, a challenge and a fallen dependency; why the dependent cannot climb back | SCHEMA.md after *Propagation* |

## Embedding

GitHub picks the variant from the viewer's colour scheme through `<picture>`; a
Markdown renderer that ignores the `<source>` falls back to the light file.

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/figures/four-roles-dark.svg">
  <img alt="A single frozen statement, where a faithful quotation runs into unsourced inference, against an entry whose Assertion, Grounds, Warrant and Backing each sit on their own line and whose quotation is resolved against the stored source bytes." src="docs/figures/four-roles.svg" width="960">
</picture>
```

Paths are relative to the document, so from inside `docs/` they are `figures/…` and from `examples/` they are `../docs/figures/…`. Each
SVG carries its own `<title>` and `<desc>`; the `alt` above repeats the description
because an `<img>` does not expose the SVG's own text to a screen reader.

## The system

One family, so the figures read as one document rather than four.

| token | light | dark | used for |
|---|---|---|---|
| paper | `#FAF8F3` | `#161513` | the ground |
| ink | `#1C1B18` | `#ECE8DF` | text, edges, nodes |
| muted | `#77726A` | `#9C968B` | annotations, headings, section markers |
| rule | `#D9D4C7` | `#3A3732` | hairlines, cell borders, empty dots |
| panel | `#F0ECE2` | `#201E1B` | the frozen region, stored bytes, terminal nodes |
| mark | `#E6E0D2` | `#2E2B26` | a faithful quotation |
| accent | `#B8451F` | `#F0855A` | the one thing a check catches: the seam, the marker, `--write`, the exception |
| accent-soft | `#F7DED2` | `#41251A` | the matched span, the deriving verdict |

- Titles and annotations are set in a serif (Charter → Iowan Old Style → Palatino →
  Georgia); ledger content is monospace (system stack). No web fonts: an SVG served
  through GitHub's image proxy cannot fetch any.
- Mono metrics are assumed at 0.6 em per character for span highlights, which holds
  for every font in the stack to within a pixel at 12 px.
- Leading indents inside mono lines are non-breaking spaces, because renderers
  collapse ordinary leading whitespace in SVG text.
- Contrast: ink on paper is 15.6:1 light and 14.3:1 dark; muted on paper 4.6:1 and
  5.6:1; accent on paper 5.0:1 and 7.0:1. Accent is never the only carrier of meaning —
  every accent element also has a label.
- Canvas is 960 wide; the `<img width="960">` above keeps GitHub from upscaling it.
