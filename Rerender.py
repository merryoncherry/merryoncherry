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
#doall = True

if doall or False:
    msg = xlenv.batchRenderSeqList([
    "Announcement.xsq",
    "BackgroundTuneTo.xsq",
    "BackgroundTuneToParkOnRight.xsq",
    "StaticIntroSeq.xsq",
    ])
    print (msg)

if doall or False:
    msg = xlenv.batchRenderSeqList([
    "1983In3.xsq",
    "30 Second Jeopardy Spooky.xsq",
    "30 Second Timer With Jeopardy Thinking Music.xsq",
    "AddamsFamily.xsq",
    "Astronaut.xsq",
    "Bang.xsq",
    "BarbieGirl.xsq",
    "Beggin.xsq",
    "BlackMagic.xsq",
    "BloodyMary_BF.xsq",
    "Bones.xsq",
    "BooToYou.xsq",
    "BringMeToLife.xsq",
    "Bruno.xsq",
    #"Casper the Friendly Ghost 1950   Intro Opening Lilly.xsq",
    "CryLittleSister.xsq",
    "Degradation.xsq",
    "DevilInside.xsq",
    ])
    print (msg)

if doall or False:
    msg = xlenv.batchRenderSeqList([
    "DevilWentDownToGeorgia_xS.xsq",
    "DontLetMeDown.xsq",
    "Dragula.xsq",
    "DuHast.xsq",
    "Dynamite.xsq",
    "EnterSandman.xsq",
    "evilintro.xsq",
    "ET.xsq",
    "Everlong_Adj.xsq", # Abended once
    "EyeOfTheTiger.xsq",
    #"FriendLikeMe_Visionary_V0.xsq",
    "GhostBustersIntro.xsq",
    "Ghostbusters.xsq",
    "GrimGrinningGhosts.xsq",
    #"HalloweenHorrorLights_2020_V0.xsq",
    #"HalloweenHorrorLights_2022_V1.xsq",
    "HalloweenTheme.xsq",
    ])
    print (msg)

if doall or True:
    msg = xlenv.batchRenderSeqList([
    "HauntedHeart.xsq",
    "InfernoOfScarySkeletons.xsq",
    "IPutASpellOnYou.xsq",
    "IPutASpellOnYou_Hawkins.xsq",
    "IWantCandy.xsq",
    "JokerThief.xsq",
    "Kashmir.xsq", # Abended once
    "LadiesAndGentlemen.xsq",
    "LightEmUp.xsq",
    "LivinOnAPrayer.xsq",
    "MadWorld.xsq",
    "Mambo5.xsq",
    #"MasterOfPuppets_Visionary_V1.xsq",
    "MJMix.xsq",
    #"Monster_PixelPerfectSeq_V1.xsq",
    "MonsterMash_xS.xsq",
    "OneWayOrAnother.xsq",
    "OogieBoogie.xsq",
    "Paradise.xsq", # Abended once
    "ProperEducation.xsq",
    "Psycho.xsq",
    "PurplePeopleEater.xsq",
    "Rasputin.xsq",
    "Roar.xsq",
    "SeparateWays.xsq",
    "SkeletonSam_BF.xsq",
    "SmellsLikeTeenSpirit.xsq",
    ])
    print (msg)

if doall or True:
    msg = xlenv.batchRenderSeqList([
    "SmoothCriminal.xsq",
    "SomebodysWatchingMe.xsq",
    "SomebodysWatchingMeRemix.xsq",
    "SpookyScarySkeletons_MLS.xsq",
    "StrangerThingsRemix.xsq",
    "SweetDreams.xsq",
    "TheSpook.xsq",
    "ThisIsHalloween_MLS.xsq",
    "ThisIsHalloween_xS.xsq",
    "Thriller_xS_TA.xsq",
    "ToxicRemix.xsq",
    "Villains.xsq",
    "WatchingMePortals.xsq",
    "WhereEvilGrows.xsq",
    "WitchDoctor.xsq",
    "WitchesAreBack.xsq",
    #"Youngblood_Visionary_V1.xsq",
    "YouMakeMeFeelLikeItsHalloween.xsq",
    "YouShookMeAllNightLong.xsq",
    "Zombie.xsq", # Abended once
    ])
    print (msg)

if doall or True:
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

