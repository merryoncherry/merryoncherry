import subprocess

import sys
sys.path.append('../merryoncherry')

import xlAutomation.xlDo

srcnet="c:\\users\\chuck\\documents\\xlightsShows\\2023_Base\\xlights_networks.xml"
intnet="c:\\users\\chuck\\documents\\xlightsShows\\2023_Xmas\\xlights_networks.xml"
dstnet="\\\\192.168.1.133\\users\\chuck\\documents\\xlightsShows\\2023_Xmas\\xlights_networks.xml"

srcrgb="c:\\users\\chuck\\documents\\xlightsShows\\2023_Base\\xlights_rgbeffects.xml"
intrgb="c:\\users\\chuck\\documents\\xlightsShows\\2023_Xmas\\xlights_rgbeffects.xml"
dstrgb="\\\\192.168.1.133\\users\\chuck\\documents\\xlightsShows\\2023_Xmas\\xlights_rgbeffects.xml"

xlenv = xlAutomation.xlDo.XLEnv()
xlenv.data = 'c:\\Users\\Chuck\\Documents\\xlightsShows\\2023_Xmas'

wasRunning = xlenv.isXLightsRunning(True)

if not wasRunning:
    xlenv.startXLights()

xlenv.changeShowFolder()

doall = False
doall = True

if doall and False:
    msg = xlenv.batchRenderSeqList([
    "BlessTheUSA.xsq",
    "GBTUSA_AFM.xsq",
    "MyHero.xsq",
    "ROCKInTheUSA.xsq",
    "PartyInTheUSA.xsq",
    "VetsBG.xsq",
    ])
    print (msg)

if doall or True:
    msg = xlenv.batchRenderSeqList([
    #"BackgroundPleaseParkWings.xsq",
    #"BackgroundTuneToEndOfStreet.xsq",
    #"BackgroundTuneToParking.xsq",
    #"BackgroundTuneToParkingWings.xsq",
    #"BackgroundTuneToParkingWingsVary.xsq",
    "StaticSeq.xsq",
    #"SB-BusyToday.xsq",
    #"SB-WhereShouldPeoplePark.xsq",
    #"SB-KeepRight.xsq",
    #"SB-ParkAndTune.xsq",
    #"SB-TakePhotos.xsq",
    "XmasBG_V1.xsq",
    ])
    print (msg)

if doall or False:
    msg = xlenv.batchRenderSeqList([
    #"12Days_McKenzie_FPD.xsq",
    #"12Days_SNC_PPD.xsq",
    "AllIReallyWantForChristmas.xsq",
    "BecauseImSanta.xsq",
    "BlueChristmas_SSS.xsq",
    "CarolOfTheBells_Barlowgirl.xsq",
    #"CarolOfTheBells_Epic_SeqSol.xsq",
    #"CarolOfTheBells_LS_RGBSeq.xsq",
    #"ChildrenChristmasMix_xS.xsq",
    #"ChristmasCanCan_MLS.xsq",
    "ChristmasCanon_SSS.xsq",
    "ChristmasDontBeLate.xsq",
    "ChristmasEve_PPD.xsq",
    "ChristmasInParadise.xsq",
    #"ChristmasNutchracker_PPD.xsq",
    "ChristmasRickRoll.xsq",
    #"ChristmasTreat_Showstopper.xsq",
    "ChristmasTreeFarm_PPD.xsq",
    #"ChristmasTwist_Showstopper.xsq",
    #"ChristmasWithoutYou_AvaMax_RGBSeq.xsq",
    "ChristmasWithoutYou_SSS.xsq",
    "ComeOnChristmas_SSS.xsq",
    "CountOnChristmas_PPD.xsq",
    "CozyLittleChristmas_SSS.xsq",
    "CozyLittleChristmasTreeFarm_PPD.xsq",
    "ClarkIntro.xsq",
    ])
    print (msg)

if doall or False:
    msg = xlenv.batchRenderSeqList([
    #"Crystallize_LS_SeqSol.xsq",
    #"DanceofTheSugarPlum_FPD.xsq",
    #"DarleneLoveBabyPleaseComeHome.xsq",
    #"DiddlySquat_Vivid.xsq",
    #"DiscoSanta_NOEL_PPD.xsq",
    "Dominick_PPD.xsq",
    "DominickToItalian.xsq",
    #"DontBeAJerk_Spongebob_PPD.xsq",
    #"DontStopTheSantaMan.xsq",
    #"FavoriteTimeOfYear_PPD.xsq",
    "FeelsLikeChristmas.xsq",
    "FelizNavidad_SSS.xsq",
    "FrostyTheSnowman.xsq",
    "GoTellSantaBaby_PPD.xsq",
    "GrandmaGotRunOver_PPD.xsq",
    #"GrinchClassic_xS.xsq",
    "HappyHolidays_PPD.xsq",
    #"HaveYourselfAMerryLittleChristmas_DW_PPD.xsq",
    "HaveYourselfAMerryLittleXmas_SSS.xsq",
    #"HereComesSantaClaus_Bing_PPD.xsq",
    #"HereComesSantaClaus_Bing_xS.xsq",
    "HolidayRoad_SSS.xsq",
    "HollyJollyChristmas_Buble_PPD.xsq",
    #"HollyJollyChristmas_Ives_xS.xsq",
    "HollyJollyChristmas_SSS.xsq",
    #"HomeForTheHolidays_PerryComo_PPD.xsq",
    #"IceStorm_Vivid.xsq",
    "ImGonnaBeWarm.xsq",
    #"ItMustBeSanta_PPD.xsq",
    "ItsTheMostWonderfulTimeOfTheYear_SSS.xsq",
    "IBTLALLC_SSS.xsq",
    #"JingALing_JJ.xsq",
    "JingleBellRock_SSS.xsq",
    #"JingleBellsBingAndrewsSistersPPD.xsq",
    "JingleBells_Denver_PPD.xsq",
    #"JingleJingleJingle_PPD.xsq",
    #"JoyToTheWorld_BobRivers_PPD.xsq",
    #"LetItSnow_Buble_MLS.xsq",
    "LetItSnow_RLLS_PPD.xsq",
    #"LightOfChristmas_PPD.xsq",
    #"LightOfChristmas_PPD_V2.xsq",
    #"LittleStNick_PPD.xsq",
    #"MarshmallowWorld_FB_PPD.xsq",
    ])
    print (msg)

if doall or False:
    msg = xlenv.batchRenderSeqList([
    "MeleKalikimaka_SSS.xsq",
    #"Mistletoe_Bieber_xS.xsq",
    #"MrSanta_PPD.xsq",
    "MyFavoriteThings_SSS.xsq",
    #"NutcrackerDubstep_xS.xsq",
    "Nutrocker_PPD.xsq",
    "OComeEmmanuel_SSS.xsq",
    #"QueenOfTheWinterNight_TSO_PPD.xsq",
    "RockinAround_Duffield_PPD.xsq",
    #"RockinAround_Newsong_PPD.xsq",
    "RockinAroundTheChristmasTree_SSS.xsq",
    "RudolphTRNRD_SSS.xsq",
    #"SantaBringMyBabyBack_Train_PPD.xsq",
    "SantaCantYouHearMe_PPD.xsq",
    #"SantaClaus_Panama_PPD.xsq",
    "SantaSings_BS.xsq",
    "SantaTellMe_SSS.xsq",
    "Sarajevo_SSS.xsq",
    "SB-ChuckBLilJohnWet.xsq",
    #"SeasonsUponUs.xsq",
    "SiberianSleighRide.xsq",
    #"SilverBells_xS.xsq",
    #"SkinnySanta_PPD.xsq",
    #"SleighRide_101Strings_MLS.xsq",
    #"SleighRide_Mathis_xS.xsq",
    #"SleighRide_Ptx_PPD.xsq",
    "SleighRide_Ptx_SSS.xsq",
    #"SnoopysChristmas_SSol.xsq",
    #"SnowMiserHeatMiser_SeqSol.xsq",
    #"SnowWaltz_EFL.xsq",
    "SomedayAtChristmas_PPD.xsq",
    #"StepIntoChristmas_PPD.xsq",
    #"SugarAndBooze_PPD.xsq",
    #"TakinCareOfChristmas_xS.xsq",
    "ThatTimeOfYear.xsq",
    #"TheChristmasSong_EFL.xsq",
    #"TheChristmasSong_xS.xsq",
    #"ToySack_BobRivers_xS.xsq",
    #"TSOChistmasMedley_xS.xsq",
    #"TSO_Sarajevo_MLS.xsq",
    ])
    print (msg)

if doall or False:
    msg = xlenv.batchRenderSeqList([
    #"TwasTheNightBeforeChristmas_xS.xsq",
    #"UpOnTheHouseTop_Ptx.xsq",
    #"WeNeedALittleChristmas_xS.xsq",
    #"WeThreeGentlemen_xS.xsq",
    "WeThreeKings_PPD.xsq",
    #"WeWishYouAMerryChristmas_Weezer_PPD.xsq",
    #"WhatChristmasMeansToMe_SW_PPD.xsq",
    "WhenIAmOlder.xsq",
    "WhenYouBelieve_PPD.xsq",
    "WhereAreYouChristmasFaithHillPPD.xsq",
    #"WhiteChristmas_Drifters_PPD.xsq",
    "WhiteChristmas_SSS.xsq",
    "WinterWonderland_SG_PPD.xsq",
    "WizardsInWinter_SSS.xsq",
    #"WonderfulChristmastime_UsTheDuo_PPD.xsq",
    #"xSClassicMedley.xsq",
    ])
    print (msg)

if doall or False:
    msg = xlenv.batchRenderSeqList([
    #"AWholeNewWorld_RGB.xsq",
    #"AllTheSmallThings_PPD.xsq",
    #"BeOurGuest_SeqSol.xsq",
    #"Beggin_RGB.xsq",
    #"CN_Mashup_MLS.xsq",
    #"CrazyLittleThingCalledLove_PPD.xsq",
    #"DangerZone_BF.xsq",
    #"DisneyPrincesses_MLS.xsq",
    #"DontStop_Showstopper.xsq",
    #"Encanto_PPD.xsq",
    #"FancyLike_Showstopper.xsq",
    #"FinalCountdown_PPD.xsq",
    #"GetThisPartyStarted_Showstopper.xsq",
    #"GoodbyeCorona_PPD.xsq",
    #"GreatestShow_XATW.xsq",
    #"Happy_MLS.xsq",
    #"IceIceBaby_Visionary.xsq",
    #"Levitating_BF.xsq",
    #"LittleMermaidMashup_Visionary.xsq",
    #"LivinOnAPrayer_RGB.xsq",
    #"Memories_PPD.xsq",
    #"NutcrackerRussianDance_Visionary.xsq",
    #"PokerFace_PPD.xsq",
    #"Rasputin_RGB.xsq",
    #"Roar_RGB.xsq",
    #"SWOTRB_2022_xS.xsq",
    #"TakeOnMe_MLS.xsq",
    #"WeDontTalkAboutBruno_RGB.xsq",
    #"WWWDWBH_xS.xsq",
    #"YouveGotAFriendInMe_SeqSol.xsq",
    #"Zero_XATW.xsq",
    ])
    print (msg)

if not wasRunning:
   xlenv.stopXLights()

subprocess.run([
    "copy", "/Y",
    intnet,
    dstnet], shell=True, check=True)

subprocess.run([
    "copy","/Y",
    intrgb,
    dstrgb], shell=True, check=True)

subprocess.run([
    "copy", "/Y",
    "c:\\users\\chuck\\documents\\xlightsShows\\2023_Xmas\\*.fseq",
    "\\\\192.168.1.133\\users\\chuck\\documents\\xlightsShows\\2023_Xmas"], shell=True, check=True)

