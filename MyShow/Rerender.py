import subprocess
import xlAutomation.xlDo

srcnet="c:\\users\\chuck\\documents\\xlightsShows\\2024_Base\\xlights_networks.xml"
intnet="c:\\users\\chuck\\documents\\xlightsShows\\2024_Halloween\\xlights_networks.xml"
dstnet="\\\\192.168.1.133\\users\\chuck\\documents\\xlightsShows\\2024_Halloween\\xlights_networks.xml"

srcrgb="c:\\users\\chuck\\documents\\xlightsShows\\2024_Base\\xlights_rgbeffects.xml"
intrgb="c:\\users\\chuck\\documents\\xlightsShows\\2024_Halloween\\xlights_rgbeffects.xml"
dstrgb="\\\\192.168.1.133\\users\\chuck\\documents\\xlightsShows\\2024_Halloween\\xlights_rgbeffects.xml"

xlenv = xlAutomation.xlDo.XLEnv()
xlenv.data = 'c:\\Users\\Chuck\\Documents\\xlightsShows\\2024_Halloween'

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
    "AintWorried.xsq",
    "Astronaut.xsq",
    "Bang.xsq",
    "BarbieGirl.xsq",
    "Beetlejuice.xsq",
    "Beggin.xsq",
    "BlackMagic.xsq",
    "BloodyMary_BF.xsq",
    ])
    print (msg)

if doall or True:
    msg = xlenv.batchRenderSeqList([
    "BloodyMary_HHL.xsq",
    "Bluey.xsq", # Abended once
    "Bones.xsq",
    "BooToYou.xsq",
    "BringMeToLife.xsq",
    "Bruno.xsq",
    "CottonEyeJoe.xsq",
    "CryLittleSister.xsq",
    "Degradation.xsq",
    "DevilInside.xsq",
    ])
    print (msg)

if doall or True:
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
    "Everybody.xsq",
    "EyeOfTheTiger.xsq",
    "Frankenstein.xsq",
    "FriendLikeMe.xsq",
    "GhostBustersIntro.xsq",
    "Ghostbusters.xsq",
    "GrimGrinningGhosts.xsq",
    "HalloweenTheme.xsq",
    ])
    print (msg)

if doall or True:
    msg = xlenv.batchRenderSeqList([
    "HauntedHeart.xsq",
    "Heathens.xsq",
    "InfernoOfScarySkeletons.xsq",
    "IPutASpellOnYou.xsq",
    "IPutASpellOnYou_Hawkins.xsq",
    "IWantCandy.xsq",
    "JokerThief.xsq",
    "JohnWilliams.xsq",
    "Kashmir.xsq", # Abended once
    "LadiesAndGentlemen.xsq",
    "LightEmUp.xsq",
    "LivinOnAPrayer.xsq",
    "MadWorld.xsq",
    "Mambo5.xsq",
    "MasterOfPuppets.xsq",
    "MJMix.xsq",
    ])
    print (msg)

if doall or True:
    msg = xlenv.batchRenderSeqList([
    "Monster_PPS.xsq",
    "MonsterMash_xS.xsq",
    "Mony.xsq",
    "OneWayOrAnother.xsq",
    "OogieBoogie.xsq",
    "Paradise.xsq", # Abended once
    "ProperEducation.xsq",
    "Psycho.xsq",
    "PurplePeopleEater.xsq",
    "Rasputin.xsq",
    "RaveInTheGrave.xsq",
    "Roar.xsq",
    "RunningUpThatHill.xsq",
    "Secret.xsq",
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
    "StayinInBlack.xsq",
    "StrangerThingsRemix.xsq",
    "Superstition.xsq",
    "SweetDreams.xsq",
    "TheSpook.xsq",
    "ThisIsHalloween_MLS.xsq",
    "ThisIsHalloween_xS.xsq",
    "Thriller_xS_TA.xsq",
    ])
    print (msg)

if doall or True:
    msg = xlenv.batchRenderSeqList([
    "Tocatta.xsq",
    "ToxicRemix.xsq",
    "Villains.xsq",
    "WatchingMePortals.xsq",
    "WelcomeToMyNightmare.xsq",
    "WhatsThis_Voiceplay.xsq",
    "WhereEvilGrows.xsq",
    "WitchDoctor.xsq",
    "WitchesAreBack.xsq",
    "YoungBlood.xsq",
    "YouMakeMeFeelLikeItsHalloween.xsq",
    "YouShookMeAllNightLong.xsq",
    "Zombie.xsq", # Abended once
    ])
    print (msg)

if doall or True:
    msg = xlenv.batchRenderSeqList([
        "SBSpooky_YouRang_Faster.xsq", #
        "SBSpooky_YouRang_V1.xsq", #
        "SBSpooky_UnderThatStone.xsq", #
        "SBSpooky_ThatTickles.xsq", #
        "SBSpooky_AsFunAsWatchingYouSleep.xsq", #
        "SBSpooky_KeepWalkingThisWay.xsq", #
        "SBSpooky_IAmWarningYou.xsq", #
        "SBSpooky_HeyScram.xsq", #
        "SBSpooky_HaveAHappyHalloweenHaHa.xsq", #
        "SBSpooky_TheyAreWatchingYou.xsq", #
        "SBSpooky_KaChow.xsq", #
        "SBSpooky_SkeletonInsideYou.xsq", #
        "SBSpooky_MonsterMash.xsq", #
        "SBSpooky_GhostJoke.xsq", #

    ])
    print (msg)

if doall or True:
    msg = xlenv.batchRenderSeqList([
        "SBBarbie.xsq", #
        "SBBubbles.xsq", #
        "SBCoffin.xsq",
        "SBGhoulFriend.xsq", #
        "SBLightEmUp.xsq",
        "SBPainInTheNeck.xsq", #
        "SBShopping.xsq", #
        "SBSquash.xsq",
        "SBVampirates.xsq",
        "SBWarts.xsq", #
        "SBWhichWitch.xsq", #
        "SBWitchesGetStitches.xsq", #
    ])
    print (msg)

if not wasRunning:
   xlenv.stopXLights()

subprocess.run([
    "copy", "/Y",
    "c:\\users\\chuck\\documents\\xlightsShows\\2024_Halloween\\*.fseq",
    "\\\\192.168.1.133\\users\\chuck\\documents\\xlightsShows\\2024_Halloween"], shell=True, check=True)

