import subprocess
import xlAutomation.xlDo

srcnet="c:\\users\\chuck\\documents\\xlightsShows\\2023_Base\\xlights_networks.xml"
intnet="c:\\users\\chuck\\documents\\xlightsShows\\2023_Halloween\\xlights_networks.xml"
dstnet="\\\\192.168.1.133\\users\\chuck\\documents\\xlightsShows\\2023_Halloween\\xlights_networks.xml"

srcrgb="c:\\users\\chuck\\documents\\xlightsShows\\2023_Base\\xlights_rgbeffects.xml"
intrgb="c:\\users\\chuck\\documents\\xlightsShows\\2023_Halloween\\xlights_rgbeffects.xml"
dstrgb="\\\\192.168.1.133\\users\\chuck\\documents\\xlightsShows\\2023_Halloween\\xlights_rgbeffects.xml"

xlenv = xlAutomation.xlDo.XLEnv()
xlenv.data = 'c:\\Users\\Chuck\\Documents\\xlightsShows\\2023_Halloween'

wasRunning = xlenv.isXLightsRunning(True)

if not wasRunning:
    xlenv.startXLights()

print("xLights now running.")

xlenv.changeShowFolder()

doall = False

if doall or False:
    msg = xlenv.batchRenderSeqList([
    #"30 Second Jeopardy Spooky.xsq",
    #"30 Second Timer With Jeopardy Thinking Music.xsq",
    "AddamsFamily.xsq",
    "BackgroundTuneTo.xsq",
    "BackgroundTuneToParkOnRight.xsq",
    "Bang.xsq",
    "BarbieGirl.xsq",
    "Beggin.xsq",
    #"BlueMoon.xsq",
    "Bones.xsq",
    "BringMeToLife.xsq",
    "Bruno.xsq",
    #"CameraWarmup.xsq",
    #"Casper the Friendly Ghost 1950   Intro Opening Lilly.xsq",
    "DevilInside.xsq",
    ])
    print (msg)

if doall or False:
    msg = xlenv.batchRenderSeqList([
    #"DevilWentDownToGeorgia.xsq",
    "Dragula.xsq",
    "DuHast.xsq",
    "Dynamite.xsq",
    "EnterSandman.xsq",
    #"evilintro.xsq",
    "ET.xsq",
    "Everlong.xsq",
    #"FriendLikeMe_Visionary_V0.xsq",
    "GhostBustersIntro.xsq",
    "Ghostbusters.xsq",
    #"HalloweenHorrorLights_2020_V0.xsq",
    #"HalloweenHorrorLights_2022_V1.xsq",
    ])
    print (msg)

if doall or False:
    msg = xlenv.batchRenderSeqList([
    "HauntedHeart.xsq",
    "InfernoOfScarySkeletons.xsq",
    "IPutASpellOnYou.xsq",
    "Kashmir.xsq",
    "LightEmUp.xsq",
    "LivinOnAPrayer.xsq",
    #"MadWorld_V0.xsq",
    "Mambo5.xsq",
    #"MasterOfPuppets_Visionary_V1.xsq",
    "MJMix.xsq",
    #"Monster_PixelPerfectSeq_V1.xsq",
    #"MonsterMash_xS_V7.xsq",
    "OogieBoogie.xsq",
    "PurplePeopleEater.xsq",
    "Rasputin.xsq",
    "Roar.xsq",
    #"SeparateWays_StrangerThings_Vivid_V0.xsq",
    #"SeletonSam_BF.xsq",
    #"SmellsLikeTeenSpirit.xsq",
    ])
    print (msg)

if doall or True:
    msg = xlenv.batchRenderSeqList([
    "SmoothCriminal.xsq",
    "SomebodysWatchingMe.xsq",
    #"ThisIsHalloween_MLS.xsq",
    #"Thriller_V0.xsq",
    "ToxicRemix.xsq",
    "Villains.xsq",
    "WhenTheLightsComeOn.xsq",
    "WhereEvilGrows.xsq",
    "WitchDoctor.xsq",
    #"Youngblood_Visionary_V1.xsq",
    "YouMakeMeFeelLikeItsHalloween.xsq",
    "YouShookMeAllNightLong.xsq",
    "Zombie.xsq",
    ])
    print (msg)

if doall or False:
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
    "c:\\users\\chuck\\documents\\xlightsShows\\2023_Halloween\\*.fseq",
    "\\\\192.168.1.133\\users\\chuck\\documents\\xlightsShows\\2023_Halloween"], shell=True, check=True)

