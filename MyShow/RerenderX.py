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
#doall = True

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

if doall or False:
    msg = xlenv.batchRenderSeqList([
    #"BackgroundPleaseParkWings.xsq",
    #"BackgroundTuneToEndOfStreet.xsq",
    #"BackgroundTuneToParking.xsq",
    #"BackgroundTuneToParkingWings.xsq",
    #"BackgroundTuneToParkingWingsVary.xsq",
    "StaticSeq.xsq",
    "StaticSeq_Short.xsq",
    "XmasBG_V1.xsq",
    ])
    print (msg)

if doall or False:
    msg = xlenv.batchRenderSeqList([
    "12Days_SNC_PPD.xsq",
    "AllIReallyWantForChristmas.xsq",
    "AllIWantForChristmas_RGBS.xsq",
    "BecauseImSanta.xsq",
    "BlueChristmas_SSS.xsq",
    "CarolOfTheBells_Barlowgirl.xsq",
    "CarolOfTheBells_Epic_SeqSol.xsq",
    "CarolOfTheBells_LS_RGBSeq.xsq",
    "ChildrenChristmasMix_xS.xsq",
    "ChristmasCanCan_MLS.xsq",
    "ChristmasCanon_SSS.xsq",
    "ChristmasDontBeLate.xsq",
    "ChristmasEve_PPD.xsq",
    "ChristmasEveryDay_xS.xsq",
    "ChristmasInParadise.xsq",
    "ChristmasInTheSand_PPD.xsq",
    "ChristmasMedleyVoctave_PPS.xsq",
    "ChristmasNutchracker_PPD.xsq",
    "ChristmasOfLove_PPD.xsq",
    "ChristmasParadise_Vivid.xsq",
    "ChristmasRickRoll.xsq",
    "ChristmasTreat_SSS.xsq",
    "ChristmasTreeFarm_PPD.xsq",
    "ChristmasTwist_SSS.xsq",
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
    "Crystallize_LS_SeqSol.xsq",
    "Crystallize_xS.xsq",
    "DanceofTheSugarPlum_FPD.xsq",
    "DarleneLoveBabyPleaseComeHome.xsq",
    "DiddlySquat_Vivid.xsq",
    "DiscoSanta_NOEL_PPD.xsq",
    "Dominick_PPD.xsq",
    "DominickToItalian.xsq",
    "DontBeAJerk_Spongebob_PPD.xsq",
    "DontStopTheSantaMan.xsq",
    "DubstepSnowman_VLS.xsq",
    "EverybodyLovesXmas_xS.xsq",
    "FavoriteTimeOfYear_PPD.xsq",
    "FeelsLikeChristmas.xsq",
    "FelizNavidad_SSS.xsq",
    "FrostyTheSnowman.xsq",
    "GoTellSantaBaby_PPD.xsq",
    "GrandmaGotRunOver_PPD.xsq",
    "GrinchClassic_xS.xsq",
    "HappyHolidays_PPD.xsq",
    "HaveYourselfAMerryLittleChristmas_DW_PPD.xsq",
    "HaveYourselfAMerryLittleXmas_SSS.xsq",
    "HereComesSantaClaus_Bing_PPD.xsq",
    "HereComesSantaClaus_Bing_xS.xsq",
    "HolidayRoad_SSS.xsq",
    "HollyJollyChristmas_Buble_PPD.xsq",
     ])
    print (msg)

if doall or False:
    msg = xlenv.batchRenderSeqList([
    "HollyJollyChristmas_Ives_xS.xsq",
    "HollyJollyChristmas_SSS.xsq",
    "HomeForTheHolidays_PerryComo_PPD.xsq",
    "IceStorm_Vivid.xsq",
    "ImGonnaBeWarm.xsq",
    "ItMustBeSanta_PPD.xsq",
    "ItsTheMostWonderfulTimeOfTheYear_SSS.xsq",
    "IBTLALLC_SSS.xsq",
    "IWantYouForXmas_xS.xsq",
    "JingleBellRock_SSS.xsq",
    "JingleBellsBingAndrewsSistersPPD.xsq",
    "JingleBells_Denver_PPD.xsq",
    "JingleBells_Glee_PPD.xsq",
    "JingleJingleJingle_PPD.xsq",
    "JoyToTheWorld_BobRivers_PPD.xsq",
    "JoyToTheWorld_LS_PPD.xsq",
    "KidOnChristmas_PPD.xsq",
    "LetItSnow_RLLS_PPD.xsq",
    "LittleStNick_PPD.xsq",
    "MarshmallowWorld_FB_PPD.xsq",
    ])
    print (msg)

if doall or False:
    msg = xlenv.batchRenderSeqList([
    "MeleKalikimaka_SSS.xsq",
    "Misers_SeqSol.xsq",
    "Mistletoe_Bieber_xS.xsq",
    "MrSanta_PPD.xsq",
    "MyFavoriteThings_SSS.xsq",
    "NutcrackerDubstep_xS.xsq",
    "Nutrocker_PPD.xsq",
    "OComeEmmanuel_SSS.xsq",
    "PleaseSantaPlease_PPD.xsq",
    "QueenOfTheWinterNight_TSO_PPD.xsq",
    "RockinAround_Duffield_PPD.xsq",
    "RockinAround_Newsong_PPD.xsq",
    "RockinAroundTheChristmasTree_SSS.xsq",
    "RudolphTRNRD_SSS.xsq",
    "RunRunRudolph_KC_EFL.xsq",
    "RunRunRudolph_KC_PPD.xsq",
    "SantaBringMyBabyBack_Train_PPD.xsq",
    "SantaCantYouHearMe_PPD.xsq",
    "SantaClaus_Panama_PPD.xsq",
    "SantaShark_MLS.xsq",
    "SantaSings_BS.xsq",
    "SantaTellMe_SSS.xsq",
    "Sarajevo_SSS.xsq",
    "SB-ChuckBLilJohnWet.xsq",
    "SeasonsUponUs.xsq",
    ])
    print (msg)

if doall or False:
    msg = xlenv.batchRenderSeqList([
    "ShakeUpChristmas_PPD.xsq",
    "ShelfishElf_xS.xsq",
    "SiberianSleighRide.xsq",
    "SilverBells_xS.xsq",
    "SkinnySanta_PPD.xsq",
    "SleighRide_Mathis_xS.xsq",
    "SleighRide_Ptx_PPD.xsq",
    "SleighRide_Ptx_SSS.xsq",
    "SnoopysChristmas_SSol.xsq",
    "SnowflakeShuffle_PPS.xsq",
    "SnowWaltz_EFL.xsq",
    "SomedayAtChristmas_PPD.xsq",
    "StepIntoChristmas_PPD.xsq",
    "SugarAndBooze_PPD.xsq",
    "TakinCareOfChristmas_xS.xsq",
    "ThatTimeOfYear.xsq",
    "TheChristmasSong_EFL.xsq",
    "TheChristmasSong_xS.xsq",
    "ToySack_BobRivers_xS.xsq",
    "TSOChistmasMedley_xS.xsq",
    ])
    print (msg)

if doall or False:
    msg = xlenv.batchRenderSeqList([
    "TwasTheNightBeforeChristmas_xS.xsq",
    "UpOnTheHouseTop_Ptx_SeqSol.xsq",
    "WeNeedALittleChristmas_xS.xsq",
    "WeThreeGentlemen_xS.xsq",
    "WeThreeKings_PPD.xsq",
    "WeWishYouAMerryChristmas_Weezer_PPD.xsq",
    "WhatChristmasMeansToMe_EFL.xsq",
    "WhatChristmasMeansToMe_SW_PPD.xsq",
    "WhenIAmOlder.xsq",
    "WhenYouBelieve_PPD.xsq",
    "WhereAreYouChristmasFaithHillPPD.xsq",
    "WhiteChristmas_Drifters_PPD.xsq",
    "WhiteChristmas_SSS.xsq",
    "WinterWonderland_SG_PPD.xsq",
    "WizardsInWinter_PPD.xsq",
    "WizardsInWinter_SSS.xsq",
    "WonderfulChristmastime_UsTheDuo_PPD.xsq",
    "xSClassicMedley.xsq",
    ])
    print (msg)

if doall or False:
    msg = xlenv.batchRenderSeqList([
    #"AWholeNewWorld_RGB.xsq",
    "AllTheSmallThings_PPD.xsq",
    "AuldLangSyne_MC_PPD.xsq",
    "BeOurGuest_SeqSol.xsq",
    #"CrazyLittleThingCalledLove_PPD.xsq",
    #"DangerZone_BF.xsq",
    "DisneyPrincesses_MLS.xsq",
    "DontStop_SSS.xsq",
    "FancyLike_SSS.xsq",
    "FinalCountdown_PPD.xsq",
    "Footloose_PPD.xsq",
    "GetThisPartyStarted_SSS.xsq",
    "Happy_MLS.xsq",
    "HowFarIllGo_PPD.xsq",
    "IceIceBaby_VLS.xsq",
    #"Levitating_BF.xsq",
    "LittleMermaidMashup_VLS.xsq",
    #"LivinOnAPrayer_RGB.xsq",
    "Mambo5_PPD.xsq",
    "Memories_PPD.xsq",
    "NutcrackerRussianDance_VLS.xsq",
    "PokerFace_PPD.xsq",
    #"Rasputin_RGB.xsq",
    #"Roar_RGB.xsq",
    "ShutUpAndDance_PPD.xsq",
    "SpaceMan_xS.xsq",
    "SWOTRB_xS.xsq",
    #"TakeOnMe_MLS.xsq",
    "WhatElseCanIDo_PPD.xsq",
    "WWWDWBH_xS.xsq",
    "YouSpinMe_VLS.xsq",
    #"YouveGotAFriendInMe_SeqSol.xsq",
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

