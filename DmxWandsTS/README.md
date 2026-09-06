# DmxWandsTS

Generates an xLights sequence (`.xsq`) that drives "just one color" targets such as
DMX wireless wands / bracelets or a flood light, from an already rendered `.fseq`.

This is the TypeScript revamp of `../DmxWands/GenerateFloodEffect.py`. The wand
logic is a straight port; the layout work (start channels, color order, dimming
curves, old and new `xlights_rgbeffects.xml` formats) is done by
[xlLayoutCalcs](https://github.com/ezsequence/xlLayoutCalcs).

## What it does

1. Loads the show layout (`xlights_rgbeffects.xml` + `xlights_networks.xml`) and
   resolves every RGB pixel model's absolute channel range, color order, and
   dimming curve (gamma / brightness) via xlLayoutCalcs.
2. Reads every frame of the `.fseq`, undoes the dimming curve, and builds HSV
   histograms over the chosen source models. Each frame gets its four most
   popular colors plus brightness / coverage statistics.
3. Decides *when* to update the wands. Wands can only take a few updates per
   second and the transmitter is best strobed briefly, so a change is emitted at:
   - timing-track marks (beats, bars, sections) from an existing `.xsq`,
   - brightness jumps and drops,
   - a color suddenly becoming dominant,
   - a large brightness drop since the last update ("off on drop"),
   - and the end of the sequence (black).
4. Writes a new `.xsq` containing, per change, an `On` effect in the chosen color
   on the color target model and a short `DMX` pulse on the control target model
   (channel 1 = ID, channel 2 = group by default). The timing track and the media
   file / song info are copied in so the result opens ready to review in xLights.

## Requirements

- Node 18+ and pnpm.
- The xlLayoutCalcs bundle is vendored as `libs/xllayoutcalcs-<version>.tgz` (a `pnpm pack` of that
  package) and referenced from `package.json` with `file:`. To upgrade, drop in a new tarball and
  update the version in both places.

```sh
cd DmxWandsTS
pnpm install
pnpm build
```

## Usage

```sh
node dist/cli.js --showdir <showFolder> --fseq <rendered.fseq> --outxsq <out.xsq> [options]
```

Typical runs:

```sh
# Every RGB model in the layout, event-driven changes only
node dist/cli.js --showdir C:/shows/2026_Xmas --fseq "C:/shows/2026_Xmas/Song.fseq" --outxsq Song_wands.xsq

# Use the beat track of the original sequence as the main trigger
node dist/cli.js --showdir C:/shows/2026_Xmas --fseq "C:/shows/2026_Xmas/Song.fseq" \
    --inxsq "C:/shows/2026_Xmas/Song.xsq" --timingtrack "Beat Count" --outxsq Song_wands.xsq

# Only look at some models / groups, cycle through 2 colors on numbered beats, send a 2nd color too
node dist/cli.js ... --modelsource "All Arches,All Trees Mini" --ncolors 2 --changecolor 1 --targetcolor2 DmxWands5Ch

# One popular color per bar (no event detection)
node dist/cli.js ... --inxsq Song.xsq --timingtrack Bars --mode timing

# Helpers
node dist/cli.js --showdir <showFolder> --fseq x --listmodels
node dist/cli.js --showdir <showFolder> --fseq x --inxsq Song.xsq --listtracks
```

`pnpm example` runs it against `../xLTS/ShowFolders/EffectsOnStars`.

### Options

Inputs / outputs

| Option | Default | Meaning |
| --- | --- | --- |
| `--showdir <dir>` | required | Show folder with `xlights_rgbeffects.xml` and `xlights_networks.xml` |
| `--fseq <file>` | required | Rendered `.fseq` (or `.eseq`) to read colors from |
| `--outxsq <file>` | required | Generated `.xsq` |
| `--modelsource <names>` | all RGB models | Comma-separated models and/or model groups (groups expand recursively) |
| `--inxsq <file>` | | Existing `.xsq`: source of the timing track and media / song info |
| `--timingtrack <name>` | | Timing track in `--inxsq` whose marks trigger updates |
| `--mode wands\|timing` | `wands` | `wands`: event driven; `timing`: one popular color per timing interval |
| `--dumpplan <file>` | | Also write the planned changes as CSV, handy for tuning |
| `--nomedia`, `--notiming` | | Do not copy media info / the timing track into the output |
| `--listmodels`, `--listtracks` | | Print what is available and exit |

Targets and transmitter control

| Option | Default | Meaning |
| --- | --- | --- |
| `--targetcontrol <name>` | `DmxWandsCtrl` | Model that gets the DMX control pulses |
| `--targetcolor <name>` | `DmxWands` | Model that gets the color |
| `--targetcolor2 <name>` | | Optional model that gets the second most popular color |
| `--ch1val`, `--ch2val` | 85, 0 | Control channel 1 (ID) and 2 (group) values |
| `--ctrlvals <list>` | | Full list of control channel values, e.g. `85,0,0` (overrides ch1/ch2) |
| `--controlwidth <ms>` | 75 | How long to hold the control pulse (75-100 ms works well) |
| `--controlgap <ms>` | 50 | Minimum gap between pulses |
| `--controladvance <ms>` | 0 | Send the pulse this much early (transmitter latency) |
| `--coloradvance <ms>` | 0 | Send the color this much early |
| `--permodel` | off | Render the effects per model (targets that are groups) |

Change detection

| Option | Default | Meaning |
| --- | --- | --- |
| `--ttracklast 0\|1` | 1 | 1: timing marks are added last and spaced against detected events; 0: they go first and override |
| `--ncolors <n>` | 1 | Cycle between the n most popular colors as numbered beats progress |
| `--changecolor 0\|1` | 0 | On an event, prefer a color different from the last one |
| `--minpopularity <n>` | 10 | Tenths of a percent of lit pixels a color needs to be considered |
| `--brightjumpamt / --brightjumparea` | 50 / 50 | Brightness rises by this much while at least this percent is lit |
| `--brightdropamt / --brightdroparea` | 50 / 50 | Brightness falls by this much while at least this percent was lit |
| `--colorjumpamt / --colorjumparea` | 25 / 50 | A color becomes dominant by this many points while covering this percent |
| `--offondrop <n>` | 50 | Go dark when brightness drops this percent below the last update (0 disables) |
| `--similarityh / --similaritys / --similarityv` | 6 / 10 / 20 | How close two colors must be to count as the same (hue in 2 degree bins, S and V in percent) |
| `--thresholdv <n>` | 5 | Raw channel value at or below which a pixel is black |

## Notes

- Both xLights layout formats are read natively; nothing is migrated on disk.
- The FSEQ reader handles v1, v2 (zstd and zlib compression, sparse ranges) and ESEQ.
  Sparse range starts are 0-based in the file, ESEQ model starts are 1-based, and
  the code converts accordingly (the Python original was off by one on sparse files).
- Models whose channels are not stored in the file (sparse export, or a render made
  from an older layout) are reported and skipped.
- Timing marks placed exactly on effect boundaries can land on a black frame, which
  yields a black update. Use `--dumpplan` to see what was chosen, and consider
  `--ttracklast 0` or `--mode timing` if that happens a lot.
- Only plain 3-channel RGB-order pixel models are used as color sources; DMX,
  single-color, and RGBW models are skipped (`--listmodels` shows which).

## Layout

| File | Purpose |
| --- | --- |
| `src/cli.ts` | Command line, orchestration |
| `src/LayoutModels.ts` | Layout loading through xlLayoutCalcs; model group expansion |
| `src/FSeqReader.ts` | FSEQ / ESEQ header and frame iteration |
| `src/ColorSummary.ts` | HSV histograms and per-frame popular colors |
| `src/FloodEffect.ts` | Change-point planning (wands mode), per-interval colors (timing mode), effect emission |
| `src/XsqTiming.ts` | Timing tracks and head info from an existing `.xsq` |
| `src/XsqWriter.ts` | Builds the output `.xsq` |
| `src/ColorUtil.ts` | RGB / HSV conversions |
