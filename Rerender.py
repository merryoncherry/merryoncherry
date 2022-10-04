import subprocess
import xlAutomation.xlDo

srcnet="c:\\users\\chuck\\documents\\xlightsShows\\2022_Base\\xlights_networks.xml"
intnet="c:\\users\\chuck\\documents\\xlightsShows\\2022_Halloween\\xlights_networks.xml"
dstnet="\\\\desktop-kara3a2\\users\\chuck\\documents\\xlightsShows\\2022_Halloween\\xlights_networks.xml"

srcrgb="c:\\users\\chuck\\documents\\xlightsShows\\2022_Base\\xlights_rgbeffects.xml"
intrgb="c:\\users\\chuck\\documents\\xlightsShows\\2022_Halloween\\xlights_rgbeffects.xml"
dstrgb="\\\\desktop-kara3a2\\users\\chuck\\documents\\xlightsShows\\2022_Halloween\\xlights_rgbeffects.xml"

xlenv = xlAutomation.xlDo.XLEnv()
xlenv.data = 'c:\\Users\\Chuck\\Documents\\xlightsShows\\2022_Halloween'

wasRunning = xlenv.isXLightsRunning(True)

if not wasRunning:
    xlenv.startXLights()

xlenv.changeShowFolder()

msg = xlenv.batchRenderSeqList([
    "30 Second Timer With Jeopardy Thinking Music.xsq",
    "AddamsFamily_RGBSeq_V0.xsq",
    "BlueMoon.xsq",
    "BringMeToLife_Vivid_V0.xsq",
    "Casper the Friendly Ghost 1950   Intro Opening Lilly.xsq",
    "DisneyVillainsV0.xsq",
    "DuHast_V2.xsq",
    "evilintro.xsq",
    "GhostBustersIntro.xsq",
    "GhostbustersPPDV2.xsq",
    "IPutASpellOnYou_HocusPocus_RGBSeq_V0.xsq",
    "MadWorld_V0.xsq",
    "MJ_Mix_MLS.xsq",
    "Monster_PixelPerfectSeq_V1.xsq",
    "MonsterMash_xS_V7.xsq",
    "PurplePeopleEaterPPDV0.xsq",
    "SeparateWays_StrangerThings_Vivid_V0.xsq",
    "SmoothCriminal_RGBSeq_V0.xsq",
    "ThisIsHalloween_MLS.xsq",
    "WitchDoctorV0.xsq"
    ])

print (msg)

if not wasRunning:
   xlenv.stopXLights()

subprocess.run([
    "copy", "/Y",
    "c:\\users\\chuck\\documents\\xlightsShows\\2022_Halloween\\*.fseq",
    "\\\\desktop-kara3a2\\users\\chuck\\documents\\xlightsShows\\2022_Halloween"], shell=True, check=True)

