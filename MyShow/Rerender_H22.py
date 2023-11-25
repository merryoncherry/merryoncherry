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

if False:
    msg = xlenv.batchRenderSeqList([
    "30 Second Jeopardy Spooky.xsq",
    "30 Second Timer With Jeopardy Thinking Music.xsq",
    "AddamsFamily_RGBSeq_V0.xsq",
    "BackgroundTuneTo.xsq",
    "BackgroundTuneToParkOnRight.xsq",
    "BlueMoon.xsq",
    "BringMeToLife_Vivid_V0.xsq",
    "Bruno_RGBSeq_V1.xsq",
    "CameraWarmup.xsq",
    "Casper the Friendly Ghost 1950   Intro Opening Lilly.xsq",
    "DevilWentDownToGeorgia",
    "DisneyVillainsV0.xsq",
    "DuHast_V2.xsq",
    "EnterSandman_MLS.xsq",
    "evilintro.xsq",
    "FriendLikeMe_Visionary_V0.xsq",
    "GhostBustersIntro.xsq",
    "GhostbustersPPDV2.xsq",
    "HalloweenHorrorLights_2020_V0.xsq",
    "HalloweenHorrorLights_2021_V0.xsq",
    "HalloweenHorrorLights_2022_V1.xsq",
    ])
    print (msg)

if False:
    msg = xlenv.batchRenderSeqList([
    "HauntedHeart.xsq",
    "IPutASpellOnYou_HocusPocus_RGBSeq_V0.xsq",
    "MadWorld_V0.xsq",
    "MasterOfPuppets_Visionary_V1.xsq",
    "MJ_Mix_MLS.xsq",
    "Monster_PixelPerfectSeq_V1.xsq",
    "MonsterMash_xS_V7.xsq",
    "PurplePeopleEaterPPDV0.xsq",
    "SeparateWays_StrangerThings_Vivid_V0.xsq",
    "SeletonSam_BF.xsq",
    "SmellsLikeTeenSpirit.xsq",
    "SmoothCriminal_RGBSeq_V0.xsq",
    "SomebodyWatchingMe.xsq",
    "ThisIsHalloween_MLS.xsq",
    "Thriller_V0.xsq",
    "WhereEvilGrows.xsq",
    "WitchDoctorV0.xsq",
    "Youngblood_Visionary_V1.xsq",
    "ZombiePPD.xsq",
    ])
    print (msg)

if True:
    msg = xlenv.batchRenderSeqList([
        "SBSpooky_YouRang_Faster.xsq",
        "SBSpooky_YouRang_V1.xsq",
        "SBSpooky_UnderThatStone.xsq",
        "SBSpooky_ThatTickles.xsq",
        "SBSpooky_AsFunAsWatchingYouSleep.xsq",
        "SBSpooky_KeepWalkingThisWay.xsq",
        "SBSpooky_IAmWarningYou.xsq",
        "SBSpooky_HeyScram.xsq",
        "SBSpooky_HaveAHappyHalloweenHaHa.xsq",
        "SBSpooky_TheyAreWatchingYou.xsq",
        "SBSpooky_KaChow.xsq",
        "SBSpooky_SkeletonInsideYou.xsq",
        "SBSpooky_MonsterMash.xsq",
        "SBSpooky_GhostJoke.xsq",
    ])
    print (msg)

if not wasRunning:
   xlenv.stopXLights()

subprocess.run([
    "copy", "/Y",
    "c:\\users\\chuck\\documents\\xlightsShows\\2022_Halloween\\*.fseq",
    "\\\\desktop-kara3a2\\users\\chuck\\documents\\xlightsShows\\2022_Halloween"], shell=True, check=True)

