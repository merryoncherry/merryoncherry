import argparse
import json
import os
import time
import xlAutomation.xlDo
import xlAutomation.fseqFile

# python ./xlTest.py --start_xlights -R -d M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ShowFolders\EffectsOnStars -s EffectsOnStars.xsq

# TODO:
# Refactor logic for fseqfile
# Summarize rendered sequence
# Refactor logic for compare
# Compare it
# Implement dir scan
# Save the perf data if asked

#class Args:
#    do_render
#    start_xlights
#    bindir - str
#    datadir - str
#    sequence - str

#    def __init__(self):
#        self.suiteFolder = ""
#        self.summaryFolder = ""
#        self.summaryExpectedFolder = ""
#        self.perfFolder = ""
#        self.perfBaselineFolder = ""
#        self.reportFolder = ""
#        self.performSummary = False
#        self.compareSummary = False
#        self.saveJsonReport = False
#        self.printTxtReport = False
#        self.updateExpectedSummary = False

def renderSequence(xlenv, args, perf):
    if 0:
        start_open = time.time()
        x = xlenv.openSequence(args.sequence)
        print(x)
        end_open = time.time()

        start_render = time.time()
        x = xlenv.renderSequence(args.sequence)
        print(x)
        end_render = time.time()

        start_save = time.time()
        x = xlenv.saveSequence()
        print(x)
        end_save = time.time()

        start_close = time.time()
        x = xlenv.closeSequence()
        print(x)
        end_close = time.time()

        if "render_seq" not in perf:
            perf['render_seq'] = []
        perf['render_seq'].append({
            'suite': args.suite,
            'seq_name': args.sequence,
            'start_open': start_open, 'end_open': end_open,
            'start_render': start_render, 'end_render': end_render,
            'start_save':start_save, 'end_save':end_save,
            'start_close':start_close, 'end_close':end_close})
    else:
        start_batch = time.time()
        xlenv.batchRenderSeqList([args.sequence])
        end_batch = time.time()

        if "render_batch" not in perf:
            perf['render_batch'] = []

        perf['render_batch'].append({
            'suite': args.suite,
            'seq_name': args.sequence,
            'start_batch': start_batch, 'end_batch': end_batch})

def switchFolder(xlenv, args, perf):
    if args.datadir:
        xlenv.data = args.datadir
        start = time.time()
        xlenv.changeShowFolder()
        end = time.time()
        if "switch_folder" not in perf:
            perf['switch_folder'] = []
        perf['switch_folder'].append({'start': start, 'end': end, 'folder': args.datadir})

def switchAndRender(xlenv, args, perf):
    switchFolder(xlenv, args, perf)
    renderSequence(xlenv, args, perf)

def calcSequenceCRC(args, perf):
    crc_start = time.time()

    # Read in the context for it
    controllers = []
    ctrlbyname = {}
    models = []
    smodels = []
    ttracks = []

    if args.datadir:
        xlAutomation.fseqFile.readControllersAndModels(args.datadir, controllers, ctrlbyname, models, smodels)
        xlAutomation.fseqFile.readSequenceTimingTrack(os.path.join(args.datadir, args.sequence), ttracks)

    # Process the CRC and tell us the result

    crc_end = time.time()
    if "crc" not in perf:
        perf['crc']=[]
    perf['crc'].append({'suite':args.suite, 'crc_start':crc_start, 'crc_end':crc_end})

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

    # Upper case for actions
    parser.add_argument('-R', '--do_render', action='store_true',  help="Do rendering of all sequences")
    parser.add_argument('-S', '--start_xlights', action='store_true',  help="Start xLights if not running")
    parser.add_argument('-C', '--calc_crcs', action='store_true', help='Calculate fseq CRC summaries')

    # Lower case for paths
    parser.add_argument('-b', '--bindir',  help="Path to xLights binaries")
    parser.add_argument('-d', '--datadir', help="Path to xlights data dir (show folder)")    
    parser.add_argument('-s', '--sequence', help="Path to or name of effect sequence .xsq file")
    parser.add_argument('-c', '--crcdir', help="Path to CRC summaries of .fseq files")
    parser.add_argument('-u', '--suite', help="Test suite")

    #parser.add_argument('-x', '--xlights',  help="Path to xlights_rgbeffects.xml and xlights_networks.xml")
    #parser.add_argument('-o', '--output',   help="Path to output file")
    #parser.add_argument('flist', nargs=1, help='sequence binary files')

    args = parser.parse_args()

    perf = {}

    xlenv = None
    if args.start_xlights or args.do_render:
        xlenv = xlAutomation.xlDo.XLEnv()
        if args.bindir:
            xlenv.bin = args.bindir
        if args.datadir:
            xlenv.data = args.datadir

    stopXlights = False
    if args.start_xlights:
        wasRunning = xlenv.isXLightsRunning(True)

        if not wasRunning:
            perf['start_xLights_start'] = time.time()
            xlenv.startXLights()
            perf['start_xLights_end'] = time.time()
            stopXlights = True

    if args.sequence:
        if args.do_render:
            switchAndRender(xlenv, args, perf)
        if args.calc_crcs:
            calcSequenceCRC(args, perf)

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