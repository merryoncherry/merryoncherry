import argparse
import io
import json
import os
import sys
import time
import xlAutomation.xlDo
import xlAutomation.fseqFile
import xlAutomation.compareFseqCRCs

# python ./xlTest.py --start_xlights -R -d M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ShowFolders\EffectsOnStars -s EffectsOnStars.xsq
# python ./xlTest.py --start_xlights -R -C -d M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ShowFolders\EffectsOnStars -s EffectsOnStars.xsq
# python ./xlTest.py --start_xlights -R -C -D -d M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ShowFolders\EffectsOnStars -s EffectsOnStars.xsq --summary_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\TempResults\EffectsOnStars --summary_expected=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ExpectedOutput\EffectsOnStars --report_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ReportResults\EffectsOnStars
# python ./xlTest.py --start_xlights -R -C -D -P -d M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ShowFolders\EffectsOnStars -s EffectsOnStars.xsq --summary_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\TempResults\EffectsOnStars --summary_expected=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ExpectedOutput\EffectsOnStars --report_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ReportResults\EffectsOnStars --perf_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\PerfReport\EffectsOnStars

# TODO:
# Implement dir scan
# try to get the model type
# Some kind of perf comparison report

def renderSequence(xlenv, args, perf):
    seqbase = args.sequence[:-4] if args.sequence[-4:] == '.xsq' else args.sequence        
    
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
            'seq_name': seqbase,
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
            'seq_name': seqbase,
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
    fseqbase = args.sequence[:-4] if args.sequence[-4:] == '.xsq' else args.sequence
    fseqn = os.path.join(args.datadir, fseqbase+'.fseq')
    hjson = xlAutomation.fseqFile.calculateFSEQSummary(fseqn, controllers, ctrlbyname, models, smodels, ttracks)
    #print(json.dumps(hjson, indent=2))
    crc_end = time.time()

    if args.summary_target:
        os.makedirs(args.summary_target, mode = 0o777, exist_ok = True)
        with open(os.path.join(args.summary_target, fseqbase+'.crc'), 'w') as fh:
            fh.write(json.dumps(hjson, indent=2))

    if "crc" not in perf:
        perf['crc']=[]
    perf['crc'].append({'suite':args.suite, 'seq_name':fseqbase, 'crc_start':crc_start, 'crc_end':crc_end})
    return hjson

def compareSequenceSummary(args, perf, hjson):
    cmp_start = time.time()
    seqbase = args.sequence[:-4] if args.sequence[-4:] == '.xsq' else args.sequence
    if not hjson:
        # Maybe we were supposed to load it?
        raise Exception("Not provided enough info to get test CRCs for diff")
    if not args.summary_expected:
        raise Exception("Not provided enough info to get baseline CRCs for diff")
    with open(os.path.join(args.summary_expected,seqbase+'.crc'), 'r') as fh:
        baseline = json.load(fh)
    tgt = sys.stdout
    if args.report_target:
        tgt = io.StringIO()

    cargs = xlAutomation.compareFseqCRCs.Args()
    cargs.channels = True
    cargs.frames = False
    cargs.globalcrc = True
    cargs.models = True
    cargs.timings = True

    diff = xlAutomation.compareFseqCRCs.compareSummaries(baseline, hjson, cargs, tgt)

    if diff and args.report_target:
        os.makedirs(args.report_target, mode = 0o777, exist_ok = True)
        with open(os.path.join(args.report_target,seqbase+'.rpt'), 'w') as fh:
            fh.write(tstr.getvalue())

    cmp_end = time.time()

    if "cmp" not in perf:
        perf['cmp']=[]
    perf['cmp'].append({'suite':args.suite, 'seq_name':seqbase, 'cmp_start':cmp_start, 'cmp_end':cmp_end})

    return diff


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
    parser.add_argument('-D', '--diff_summary', action='store_true', help='Diff the CRC summary to expected')
    parser.add_argument('-P', '--perf_summary', action='store_true', help='Report the performance summary')

    # Lower case for paths
    parser.add_argument('-b', '--bindir',  help="Path to xLights binaries")
    parser.add_argument('-c', '--crcdir', help="Path to CRC summaries of .fseq files")
    parser.add_argument('-d', '--datadir', help="Path to xlights data dir (show folder)")    
    parser.add_argument('-w', '--summary_target', help="Path to write fseq summary")
    parser.add_argument('-e', '--summary_expected', help="Path to read fseq expected summary for compare")
    parser.add_argument('-r', '--report_target', help="Path to write comparison report")
    parser.add_argument('-p', '--perf_target', help="Path to write performance report")
    parser.add_argument('-s', '--sequence', help="Name of effect sequence .xsq file")
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
        seqbase = args.sequence[:-4] if args.sequence[-4:] == '.xsq' else args.sequence
        if args.do_render:
            switchAndRender(xlenv, args, perf)
        if args.calc_crcs:
            hjson = calcSequenceCRC(args, perf)
        else:
            hjson = None
        if args.diff_summary:
            compareSequenceSummary(args, perf, hjson)

    if stopXlights:
        perf['stop_xLights_start'] = time.time()
        xlenv.stopXLights()
        perf['stop_xLights_end'] = time.time()

    if args.perf_summary:
        if args.perf_target:
            os.makedirs(args.perf_target, mode = 0o777, exist_ok = True)
            with open(os.path.join(args.perf_target, 'perf_report.json'), 'w') as fh:
                fh.write(json.dumps(perf, indent=2))
            pass
        else:
            print(json.dumps(perf, indent=2))
