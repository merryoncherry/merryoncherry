import subprocess
import xlAutomation.xlDo

srcnet="c:\\users\\chuck\\documents\\xlightsShows\\2022_Base\\xlights_networks.xml"
intnet="c:\\users\\chuck\\documents\\xlightsShows\\2022_Xmas\\xlights_networks.xml"
dstnet="\\\\desktop-kara3a2\\users\\chuck\\documents\\xlightsShows\\2022_Xmas\\xlights_networks.xml"

srcrgb="c:\\users\\chuck\\documents\\xlightsShows\\2022_Base\\xlights_rgbeffects.xml"
intrgb="c:\\users\\chuck\\documents\\xlightsShows\\2022_Xmas\\xlights_rgbeffects.xml"
dstrgb="\\\\desktop-kara3a2\\users\\chuck\\documents\\xlightsShows\\2022_Xmas\\xlights_rgbeffects.xml"

xlenv = xlAutomation.xlDo.XLEnv()
xlenv.data = 'c:\\Users\\Chuck\\Documents\\xlightsShows\\2022_Xmas'

wasRunning = xlenv.isXLightsRunning(True)

if not wasRunning:
    xlenv.startXLights()

xlenv.changeShowFolder()

if False:
    msg = xlenv.batchRenderSeqList([
    "GodBlessTheUSA.xsq",
    "MyHero.xsq",
    "ROCKInTheUSA.xsq",
    "PartyInTheUSA.xsq",
    "VetsBG.xsq",
    ])
    print (msg)

if True:
    msg = xlenv.batchRenderSeqList([
    "VetsBG.xsq",
    ])
    print (msg)

if False:
    msg = xlenv.batchRenderSeqList([
    ])
    print (msg)

if not wasRunning:
   xlenv.stopXLights()

subprocess.run([
    "copy", "/Y",
    "c:\\users\\chuck\\documents\\xlightsShows\\2022_Xmas\\*.fseq",
    "\\\\desktop-kara3a2\\users\\chuck\\documents\\xlightsShows\\2022_Xmas"], shell=True, check=True)

