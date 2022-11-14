import subprocess
import xlAutomation.xlDo

srcnet="c:\\users\\chuck\\documents\\xlightsShows\\2022_Base\\xlights_networks.xml"
intnet="c:\\users\\chuck\\documents\\xlightsShows\\2022_Halloween\\xlights_networks.xml"
dstnet="\\\\desktop-kara3a2\\users\\chuck\\documents\\xlightsShows\\2022_Halloween\\xlights_networks.xml"

srcrgb="c:\\users\\chuck\\documents\\xlightsShows\\2022_Base\\xlights_rgbeffects.xml"
intrgb="c:\\users\\chuck\\documents\\xlightsShows\\2022_Halloween\\xlights_rgbeffects.xml"
dstrgb="\\\\desktop-kara3a2\\users\\chuck\\documents\\xlightsShows\\2022_Halloween\\xlights_rgbeffects.xml"

subprocess.run([
    "python",
    "LayoutUtils/pyLayout.py", 
    "--layout="+srcrgb,
    "--outlayout="+intrgb,
    "--edit=InGroup=OnlyForXmas:Delete:true;InGroup=OnlyForFuture:Delete:true;Type=Obj:Brighten:30;Obj=.*_Xmas:Active:false;Model=.*:dimcurveall:0,2.3;Model=TreeFence:dimcurvergb:-14,2.5,0,2.5,0,2.5;Model=MainMatrix:dimcurveall:-60,2.5;Model=Arch Hedge.*:dimcurveall:-60,2.3;Model=PPD GE Baby Grand.*:dimcurveall:-30,2.2",
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

