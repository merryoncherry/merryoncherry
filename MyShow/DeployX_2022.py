import subprocess
import xlAutomation.xlDo

srcnet="c:\\users\\chuck\\documents\\xlightsShows\\2022_Base\\xlights_networks.xml"
intnet="c:\\users\\chuck\\documents\\xlightsShows\\2022_Xmas\\xlights_networks.xml"
dstnet="\\\\desktop-kara3a2\\users\\chuck\\documents\\xlightsShows\\2022_Xmas\\xlights_networks.xml"

srcrgb="c:\\users\\chuck\\documents\\xlightsShows\\2022_Base\\xlights_rgbeffects.xml"
intrgb="c:\\users\\chuck\\documents\\xlightsShows\\2022_Xmas\\xlights_rgbeffects.xml"
dstrgb="\\\\desktop-kara3a2\\users\\chuck\\documents\\xlightsShows\\2022_Xmas\\xlights_rgbeffects.xml"

#    "--edit=InGroup=OnlyForHalloween:Delete:true;InGroup=OnlyForFuture:Delete:true;Type=Obj:Brighten:30;Obj=.*_Halloween:Active:false;Model=.*:dimcurveall:0,2.3;Model=TreeFence:dimcurvergb:-14,2.5,0,2.5,0,2.5;Model=MainMatrix:dimcurveall:-60,2.2;Model=Arch Hedge.*:dimcurveall:-60,2.2;Model=PPD GE Baby Grand.*:dimcurveall:-30,2.2;Model=Icicles.*:dimcurveall:-30,2.2;Model=PPD EFlake.*:dimcurveall:-30,2.2;;Model=MatrixPost.*:dimcurveall:-30,2.2;Model=MatrixFPorch.*:dimcurveall:-30,2.2",


subprocess.run([
    "python",
    "LayoutUtils/pyLayout.py", 
    "--layout="+srcrgb,
    "--outlayout="+intrgb,
    "--edit=InGroup=OnlyForHalloween:Delete:true;InGroup=OnlyForFuture:Delete:true;Type=Obj:Brighten:30;Obj=.*_Halloween:Active:false;Model=.*:dimcurveall:0,2.3;Model=TreeFence:dimcurvergb:-14,2.5,0,2.5,0,2.5;Model=MainMatrix:dimcurveall:-60,2.2;Model=Arch Hedge.*:dimcurveall:-60,2.3;Model=PPD GE Baby Grand.*:dimcurveall:-30,2.2;Model=GE Priem.*:dimcurveall:-30,2.2;Model=HohohoBushBase:dimcurveall:-60,2.2",
    "--transform=translate:0,0,-300;roty:30"
    ], shell=True, check=True)

subprocess.run([
    "copy", "/Y",
    srcnet,
    intnet], shell=True, check=True)

subprocess.run([
    "copy", "/Y",
    intnet,
    dstnet], shell=True, check=True)

subprocess.run([
    "copy","/Y",
    intrgb,
    dstrgb], shell=True, check=True)

