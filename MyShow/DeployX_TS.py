# DeployX using the TypeScript layout tool (LayoutUtilsTS) instead of LayoutUtils/pyLayout.py.
#
# Same approach as DeployH_TS.py; the edits are the 2026 DeployH_TS list with the Christmas-specific
# changes carried over from DeployX_2025.py. Build the tool once first:
#     cd LayoutUtilsTS && pnpm install && pnpm build
# then run this from the repo root:  python MyShow/DeployX_TS.py
#
# Differences from DeployX_2025.py:
#   - the copy to the show computer is OFF (set DEPLOY = True to turn it on)
#   - --outformat picks the layout format written: keep (same as the base), x2026_2 (pre-2026.3 xLights),
#     x2026_3 (2026.3+), x2026_15 (2026.15+)
#   - 3D transforms cover every model type (poly lines keep their scale, arches keep their orientation)
#
# Christmas vs Halloween edits (from DeployX_2025.py):
#   - deletes OnlyForHalloween instead of OnlyForXmas, deactivates *_Halloween objects instead of *_Xmas
#   - adds PPD GE Baby Grand.* -30, GE Insane Arch.* 2.2 (overrides GE Insane.* 1.0),
#     Boscoyo ChromaStocking P5 n Matrix 1.1, StarSpiral W .* 1.0
#   - drops the Halloween-only Boscoyo_Megastone_P5 / ChromaGlow_TombStone rules (those models are deleted anyway)
# The 2026 additions shared with Halloween (Eagle_Flying and the P2P_* props) are kept.

import os
import subprocess

DEPLOY = False
OUTFORMAT = "keep"

srcnet="c:\\users\\chuck\\documents\\xlightsShows\\2026_Base\\xlights_networks.xml"
intnet="c:\\users\\chuck\\documents\\xlightsShows\\2026_Xmas\\xlights_networks.xml"
dstnet="\\\\asustuf\\c\\users\\ezrgb\\documents\\xlightsShows\\2026_Xmas\\xlights_networks.xml"

srcrgb="c:\\users\\chuck\\documents\\xlightsShows\\2026_Base\\xlights_rgbeffects.xml"
intrgb="c:\\users\\chuck\\documents\\xlightsShows\\2026_Xmas\\xlights_rgbeffects.xml"
dstrgb="\\\\asustuf\\c\\users\\ezrgb\\documents\\xlightsShows\\2026_Xmas\\xlights_rgbeffects.xml"

os.makedirs(os.path.dirname(intrgb), exist_ok=True)

subprocess.run([
    "node",
    "LayoutUtilsTS/dist/cli.js",
    "--layout="+srcrgb,
    "--outlayout="+intrgb,
    "--outformat="+OUTFORMAT,
    "--edit=InGroup=OnlyForHalloween:Delete:true;InGroup=OnlyForFuture:Delete:true;Type=Obj:Brighten:30;Obj=.*_Halloween:Active:false;Model=.*:dimcurveall:0,2.2;Model=TreeFence:dimcurvergb:-14,2.2,0,2.2,0,2.2;Model=MainMatrix$:dimcurveall:-60,2.2;Model=MainMatrixP5:dimcurveall:0,.8;Model=Arch Hedge.*:dimcurveall:-60,2.2;Model=PPD GE Baby Grand.*:dimcurveall:-30,2.2;Model=GE Dragonfly.*:dimcurveall:0,2.5;Model=GE Dazzler.*:dimcurveall:0,2.5;Model=GE Star Gazer.*:dimcurveall:0,2.5;Model=GE Franken Monster.*:dimcurveall:0,2.5;Model=GE Priem Cube.*:dimcurveall:0,2.5;Model=Matrix KBR Window.*:dimcurveall:0,2.5;Model=MatrixFWall.*:dimcurveall:0,2.5;Model=MatrixPost.*:dimcurveall:0,2.5;Model=MatrixSideDoor.*:dimcurveall:0,2.5;Model=PPD GE Baby Grand Illusion.*:dimcurveall:0,2.5;Model=StarF.*:dimcurveall:0,2.5;Model=GE Triune Tomb.*:dimcurveall:0,2.5;Model=GE Insane.*:dimcurveall:0,1.0;Model=StarInsane.*:dimcurveall:0,1.0;Model=DmxWands:dimcurveall:0,2.2;Model=DmxWandsCtrl:dimcurveall:0,1.0;Model=HohohoBushBase:dimcurveall:-60,2.2;Model=StarMegaMini.*:dimcurveall:0,1.0;Model=StarMiniMega.*:dimcurveall:0,1.0;Model=GE Insane Arch.*:dimcurveall:0,2.2;Model=Boscoyo ChromaStocking P5 . Matrix:dimcurveall:0,1.1;Model=StarSpiral W .*:dimcurveall:0,1.0;Model=Eagle_Flying:dimcurveall:0,1.0;Model=P2P_SingingFirework.*:dimcurveall:0,1.0;Model=P2P_Stamped.Singing.*:dimcurveall:0,1.0;Model=P2P_Stamped.4th.July.Spinner.18.*:dimcurveall:0,1.0;Model=P2P_150.Star.*:dimcurveall:0,1.0;Model=P2P_4th.July.Star.100.*:dimcurveall:0,1.0;",
    "--transform=translate:0,0,-300;roty:30"
    ], shell=True, check=True)

subprocess.run([
    "copy", "/Y",
    srcnet,
    intnet], shell=True, check=True)

if DEPLOY:
    subprocess.run([
        "copy", "/Y",
        intnet,
        dstnet], shell=True, check=True)

    subprocess.run([
        "copy","/Y",
        intrgb,
        dstrgb], shell=True, check=True)
