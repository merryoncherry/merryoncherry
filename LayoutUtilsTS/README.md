# LayoutUtilsTS

Bulk editing, 3D transforms, and format conversion for an xLights layout
(`xlights_rgbeffects.xml`), for the things that are tough to do inside xLights:
keep one base layout and derive the Halloween / Christmas / next-year variants
from it, move or rotate the whole display, apply dimming curves in bulk, and
write the result for old or new xLights versions.

This is the TypeScript revamp of `../LayoutUtils/pyLayout.py`. The selector and
edit language is unchanged; the placement math and the format conversion come
from [xlLayoutCalcs](https://github.com/ezsequence/xlLayoutCalcs), so every
model type is handled the way xLights itself lays it out.

## Requirements

- Node 18+ and pnpm.
- The xlLayoutCalcs bundle is vendored as `libs/xllayoutcalcs-<version>.tgz` (a
  `pnpm pack` of that package) and referenced from `package.json` with `file:`.

```sh
cd LayoutUtilsTS
pnpm install
pnpm build
```

## Usage

```sh
node dist/cli.js --layout <in.xml> [--outlayout <out.xml>] [--transform <steps>] [--edit <edits>] [--outformat <fmt>]
```

Order of operations: read, whole-layout `--transform`, `--edit` selections in
order, `--outformat` conversion, write. Without `--outlayout` nothing is
written (a dry run that still reports what would change). Group and view
members that do not exist are always reported.

```sh
# Derive a Halloween layout: drop the Christmas-only stuff, dim the arches, move the whole thing back and turn it
node dist/cli.js --layout 2026_Base/xlights_rgbeffects.xml --outlayout 2026_Halloween/xlights_rgbeffects.xml \
    --edit "InGroup=OnlyForXmas:Delete:true;Type=Obj:Brighten:30;Model=Arch Hedge.*:dimcurveall:-60,2.2" \
    --transform "translate:0,0,-300;roty:30"

# Write a layout an older xLights can read (effect presets go back into the XML)
node dist/cli.js --layout new/xlights_rgbeffects.xml --outlayout old/xlights_rgbeffects.xml --outformat x2026_2

# Or the other way (effect presets come out as xlights_effectpresets.json next to the output)
node dist/cli.js --layout old/xlights_rgbeffects.xml --outlayout new/xlights_rgbeffects.xml --outformat x2026_3

# Move just some models
node dist/cli.js --layout a.xml --outlayout b.xml --edit "Model=Arch.*:translate:0,0,-50;Group=Roof:roty:15"
```

`../MyShow/DeployH_TS.py` is the Halloween deploy script using this tool.

### Transform steps

Semicolon-separated, applied in order, each about the world origin:

| Step | Meaning |
| --- | --- |
| `translate:<x,y,z>` | Move |
| `scale:<x,y,z>` | Scale (uniform values keep every model exact; see notes for non-uniform) |
| `rotx:<deg>`, `roty:<deg>`, `rotz:<deg>` | Rotate about the X / Y / Z axis (right-handed; `roty:30` turns the display about the vertical axis) |

Gridlines view objects stay put unless `--gridlines` is given. Locked models
move too unless `--respectlocked` is given.

### Edits

Semicolon-separated `<selection>:<action>:<arguments>`.

Selections (regular expressions match at the start of the name, like Python's `re.match`):

| Selection | Selects |
| --- | --- |
| `Model=<regex>` | Models by name |
| `Group=<regex>` | Model groups by name |
| `InGroup=<regex>` | Everything inside the matching groups, following nested groups |
| `Obj=<regex>` | View objects (images, meshes, terrain, ...) by name |
| `Type=Model`, `Type=Group`, `Type=Obj` | All of that kind |
| `Type=<DisplayAs>` | Models / objects of a type: `Arches`, `Tree 360`, `Tree`, `Matrix`, `Image`, ... (old and new names both work) |
| `TagColour=<value>` | Models and groups with that tag colour |
| `InactiveModel`, `InactiveObj` | Things with Active="0" |

Actions:

| Action | Effect |
| --- | --- |
| `active:<true/false>` | Set the Active checkbox on models and objects |
| `brighten:<pct>` / `darken:<pct>` | Appearance brightness (objects: `Brightness` x pct; models: `ModelBrightness` on the 100% scale). Not what is sent to the controller |
| `setbrightness:<value>` | Set the appearance brightness directly |
| `dimcurveall:<brightness,gamma>` | Dimming curve for all colours (brightness -100..100). This does change what is sent |
| `dimcurvergb:<rb,rg,gb,gg,bb,bg>` | Per-colour dimming curve |
| `delete:true` | Remove the selection, and every reference to it from groups and views |
| `translate:<x,y,z>`, `scale:<x,y,z>`, `rotx:<deg>`, `roty:<deg>`, `rotz:<deg>` | Transform only the selection (about the world origin) |
| `transform:<step\|step...>` | Several transform steps for the selection, separated by `\|` |

### Output format

| `--outformat` | Writes |
| --- | --- |
| `keep` (default) | Whatever format the input was in |
| `x2026_2` | The pre-2026.3 schema (`parm1/2/3`, `Tree 360`, `Horiz Matrix`, effect presets inside the XML). Reads `xlights_effectpresets.json` next to the input, or `--presets`, to embed the presets |
| `x2026_3` | The 2026.3+ schema (named attributes, `Tree` + `TreeDegrees`, `Matrix` + `Vertical`); effect presets are written to `xlights_effectpresets.json` next to the output |
| `x2026_15` | As `x2026_3`, keeping the 2026.15-only `Controller` view objects |

The input may be in either format regardless of the output.

## Notes on transforms

The transform rewrites each model's placement the way xLights stores it:

- Boxed models (custom, star, tree, matrix, cube, circle, sphere, spinner,
  wreath, window frame, image, DMX) get a new position, scale, and RotateX/Y/Z,
  extracted the same way xLights does when you rotate in the UI.
- Single lines and channel blocks: both endpoints move.
- Arches, candy canes, and icicles: both endpoints move, and `RotateX` is
  recomputed so the model keeps its orientation (the xLights rotate tool
  leaves it alone, so arches can tip over there). `Height` is kept as a ratio.
- Poly lines: every point and curve control point moves; scale is kept (or,
  for a non-uniform scale under a rotation, baked into the points).

Limits inherited from xLights: a non-uniform `scale` on a rotated boxed model
cannot be represented (it would shear; a warning is printed and the closest
rotation is used); poly line icicle drops always hang straight down, so they
follow rotations about Y but not about X or Z; a line within 0.8 degrees of
the X axis is drawn exactly axis-aligned by xLights, so its tiny tilt appears
once a rotation moves it out of that zone.

Viewpoints and model group positions are left alone, as before.

## Layout

| File | Purpose |
| --- | --- |
| `src/cli.ts` | Command line and pipeline |
| `src/LayoutDoc.ts` | Load / pretty-print / save; reference checks |
| `src/Selection.ts` | The selector language |
| `src/Edits.ts` | The edit actions, including delete with reference pruning |
| `src/Transform.ts` | Transform step parsing |
