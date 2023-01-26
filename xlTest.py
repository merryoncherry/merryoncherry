import argparse
import json
import time
import xlAutomation.xlDo

class Args:
    def __init__(self):
        self.xlightsBin = ""
        self.showFolder = ""
        self.suiteFolder = ""
        self.summaryFolder = ""
        self.summaryExpectedFolder = ""
        self.perfFolder = ""
        self.perfBaselineFolder = ""
        self.reportFolder = ""
        self.startXlights = False
        self.performRender = False
        self.performSummary = False
        self.compareSummary = False
        self.saveJsonReport = False
        self.printTxtReport = False
        self.updateExpectedSummary = False

def renderSequence(args):
    pass

def testSequence(args):
    pass

def testSequences(args):
    pass

def testFolder(args):
    pass

def testFolders(args):
    pass

def testSuites(args):
    pass

if __name__ == '__main__':
    # Command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('-S', '--start_xlights', action='store_true',  help="Start xLights if not running")
    parser.add_argument('-R', '--do_render', action='store_true',  help="Do rendering of all sequences")
    #parser.add_argument('-x', '--xlights',  help="Path to xlights_rgbeffects.xml and xlights_networks.xml")
    #parser.add_argument('-s', '--sequence', help="Path to effect sequence .xsq file")
    #parser.add_argument('-o', '--output',   help="Path to output file")
    #parser.add_argument('flist', nargs=1, help='sequence binary files')

    args = parser.parse_args()

    perf = {}

    xlenv = None
    if args.start_xlights or args.do_render:
        xlenv = xlAutomation.xlDo.XLEnv()
        #xlenv.data = 'c:\\Users\\Chuck\\Documents\\xlightsShows\\2022_Halloween'

    stopXlights = False
    if args.start_xlights:
        wasRunning = xlenv.isXLightsRunning(True)

        if not wasRunning:
            perf['start_xLights_start'] = time.time()
            xlenv.startXLights()
            perf['start_xLights_end'] = time.time()
            stopXlights = True

    #xlenv.changeShowFolder()

    if stopXlights:
        perf['stop_xLights_start'] = time.time()
        xlenv.stopXLights()
        perf['stop_xLights_end'] = time.time()

    print(json.dumps(perf, indent=2))

if 0:
    if 1:
        subprocess.run('python fseqFile.py '
            " -s m:\\users\\chuck\\source\\repos\\merryoncherry\\xlts\\showfolders\\effectsonstars\\EffectsOnStars.xsq "
            " -x m:\\users\\chuck\\source\\repos\\merryoncherry\\xlts\\showfolders\\effectsonstars "
            " -o m:\\users\\chuck\\source\\repos\\merryoncherry\\xlts\\expectedoutput\\effectsonstars\\EffectsOnStars.crc.tmp " # Not a good place to put it
            " m:\\users\\chuck\\source\\repos\\merryoncherry\\xlts\\showfolders\\effectsonstars\\EffectsOnStars.fseq "
            , capture_output=False)

    subprocess.run('python compareFseqCRCs.py '
        " -c -f -m -t"
        " m:\\users\\chuck\\source\\repos\\merryoncherry\\xlts\\expectedoutput\\effectsonstars\\EffectsOnStars.crc "
        " m:\\users\\chuck\\source\\repos\\merryoncherry\\xlts\\expectedoutput\\effectsonstars\\EffectsOnStars.crc.tmp "
        , capture_output=False)
