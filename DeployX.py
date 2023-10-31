import subprocess
import xlAutomation.xlDo

srcnet="c:\\users\\chuck\\documents\\xlightsShows\\2023_Base\\xlights_networks.xml"
intnet="c:\\users\\chuck\\documents\\xlightsShows\\2023_Xmas\\xlights_networks.xml"
dstnet="\\\\192.168.1.133\\users\\chuck\\documents\\xlightsShows\\2023_Xmas\\xlights_networks.xml"

srcrgb="c:\\users\\chuck\\documents\\xlightsShows\\2023_Base\\xlights_rgbeffects.xml"
intrgb="c:\\users\\chuck\\documents\\xlightsShows\\2023_Xmas\\xlights_rgbeffects.xml"
dstrgb="\\\\192.168.1.133\\users\\chuck\\documents\\xlightsShows\\2023_Xmas\\xlights_rgbeffects.xml"

subprocess.run([
    "python",
    "LayoutUtils/pyLayout.py", 
    "--layout="+srcrgb,
    "--outlayout="+intrgb,
    "--edit=InGroup=OnlyForHalloween:Delete:true;InGroup=OnlyForFuture:Delete:true;Type=Obj:Brighten:30;Obj=.*_Halloween:Active:false;Model=.*:dimcurveall:0,2.2;Model=TreeFence:dimcurvergb:-14,2.2,0,2.2,0,2.2;Model=MainMatrix:dimcurveall:-60,2.2;Model=Arch Hedge.*:dimcurveall:-60,2.2;Model=PPD GE Baby Grand.*:dimcurveall:-30,2.2;Model=GE Dragonfly.*:dimcurveall:0,2.5;Model=GE Franken Monster.*:dimcurveall:0,2.5;Model=GE Priem Cube.*:dimcurveall:0,2.5;Model=Matrix KBR Window.*:dimcurveall:0,2.5;Model=MatrixFWall.*:dimcurveall:0,2.5;Model=MatrixPost.*:dimcurveall:0,2.5;Model=MatrixSideDoor.*:dimcurveall:0,2.5;Model=PPD GE Baby Grand Illusion.*:dimcurveall:0,2.5;Model=StarF.*:dimcurveall:0,2.5;Model=GE Triune Tomb.*:dimcurveall:0,2.5;Model=GE Insane.*:dimcurveall:0,1.0;Model=DmxWands:dimcurveall:0,2.2;Model=DmxWandsCtrl:dimcurveall:0,1.0;Model=HohohoBushBase:dimcurveall:-60,2.2",
    "--transform=translate:0,0,-300;roty:30"
    ], shell=True, check=True)

subprocess.run([
    "copy", "/Y",
    srcnet,
    intnet], shell=True, check=True)

if True:
    subprocess.run([
        "copy", "/Y",
        intnet,
        dstnet], shell=True, check=True)

    subprocess.run([
        "copy","/Y",
        intrgb,
        dstrgb], shell=True, check=True)

