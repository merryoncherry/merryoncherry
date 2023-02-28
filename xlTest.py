import argparse
import io
import json
import os
import sys
import time
import xlAutomation.xlDo
import xlAutomation.fseqFile
import xlAutomation.xsqFile
import xlAutomation.compareFseqCRCs

# python ./xlTest.py --start_xlights -R -d M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ShowFolders\EffectsOnStars -s EffectsOnStars.xsq
# python ./xlTest.py --start_xlights -R -C -d M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ShowFolders\EffectsOnStars -s EffectsOnStars.xsq
# python ./xlTest.py --start_xlights -R -C -D -d M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ShowFolders\EffectsOnStars -s EffectsOnStars.xsq --summary_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\TempResults\EffectsOnStars --summary_expected=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ExpectedOutput\EffectsOnStars --report_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ReportResults\EffectsOnStars
# python ./xlTest.py --start_xlights -R -C -D -P -d M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ShowFolders\EffectsOnStars -s EffectsOnStars.xsq --summary_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\TempResults\EffectsOnStars --summary_expected=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ExpectedOutput\EffectsOnStars --report_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ReportResults\EffectsOnStars --perf_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\PerfReport\EffectsOnStars
# python ./xlTest.py --start_xlights -R -C -D -P --suite M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ShowFolders\EffectsOnStars --summary_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\TempResults\EffectsOnStars --summary_expected=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ExpectedOutput\EffectsOnStars --report_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ReportResults\EffectsOnStars --perf_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\PerfReport\EffectsOnStars

# python ./xlTest.py --start_xlights --timing_models -R -C -P --suite M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ShowFolders\SCTS --summary_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\TempResults\SCTS --summary_expected=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ExpectedOutput\SCTS --report_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ReportResults\SCTS --perf_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\PerfReport\SCTS
# python ./xlTest.py --start_xlights --timing_models -R -C -D -P --suite M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ShowFolders\SCTS --summary_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\TempResults\SCTS --summary_expected=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ExpectedOutput\SCTS --report_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ReportResults\SCTS --perf_target=M:\Users\Chuck\Source\Repos\merryoncherry\xLTS\PerfReport\SCTS

# python ./xlTest.py --start_xlights -R -C -P --suite C:\Users\Chuck\Documents\xlightsShows\2022_Xmas_Sample --summary_target=C:\Users\Chuck\Documents\xlightsShows\2022_Xmas_TempResults --summary_expected=C:\Users\Chuck\Documents\xlightsShows\2022_Xmas_AcceptedResults --report_target=C:\Users\Chuck\Documents\xlightsShows\2022_Xmas_Diff --perf_target=C:\Users\Chuck\Documents\xlightsShows\2022_Xmas_Perf_2022_26

# python ./xlTest.py --start_xlights -R -C -P --suite=M:\xL_Test_2021\2021_Aspirational --summary_target=M:\xL_Test_2021\2021_Aspirational_TempResults_2021_39 --summary_expected=M:\xL_Test_2021\2021_Aspirational_AcceptedResults --report_target=M:\xL_Test_2021\2021_Aspirational_Diff --perf_target=M:\xL_Test_2021\2021_Aspirational_Perf_2021_39
# python ./xlTest.py --start_xlights -R -C -P --suite=M:\xL_Test_2021\2021_Aspirational --summary_target=M:\xL_Test_2021\2021_Aspirational_TempResults_2022_07 --summary_expected=M:\xL_Test_2021\2021_Aspirational_AcceptedResults --report_target=M:\xL_Test_2021\2021_Aspirational_Diff --perf_target=M:\xL_Test_2021\2021_Aspirational_Perf_2022_07
# python ./xlTest.py --start_xlights -R -C -P --suite=M:\xL_Test_2021\2021_Aspirational --summary_target=M:\xL_Test_2021\2021_Aspirational_TempResults_2022_13 --summary_expected=M:\xL_Test_2021\2021_Aspirational_AcceptedResults --report_target=M:\xL_Test_2021\2021_Aspirational_Diff --perf_target=M:\xL_Test_2021\2021_Aspirational_Perf_2022_13
# python ./xlTest.py --start_xlights -R -C -P --suite=M:\xL_Test_2021\2021_Aspirational --summary_target=M:\xL_Test_2021\2021_Aspirational_TempResults_2022_20 --summary_expected=M:\xL_Test_2021\2021_Aspirational_AcceptedResults --report_target=M:\xL_Test_2021\2021_Aspirational_Diff --perf_target=M:\xL_Test_2021\2021_Aspirational_Perf_2022_20
# python ./xlTest.py --start_xlights -R -C -P --suite=M:\xL_Test_2021\2021_Aspirational --summary_target=M:\xL_Test_2021\2021_Aspirational_TempResults_2022_26 --summary_expected=M:\xL_Test_2021\2021_Aspirational_AcceptedResults --report_target=M:\xL_Test_2021\2021_Aspirational_Diff --perf_target=M:\xL_Test_2021\2021_Aspirational_Perf_2022_26

# python ./xlTest.py --start_xlights -D --suite=M:\xL_Test_2021\2021_Aspirational --summary_target=M:\xL_Test_2021\2021_Aspirational_TempResults_2022_26 --summary_expected=M:\xL_Test_2021\2021_Aspirational_AcceptedResults --report_target=M:\xL_Test_2021\2021_Aspirational_Diff

# python ./xlTest.py --start_xlights -D --suite=M:\xL_Test_2021\2021_Aspirational --summary_expected=M:\xL_Test_2021\2021_Aspirational_TempResults_2021_39 --summary_target=M:\xL_Test_2021\2021_Aspirational_TempResults_2022_13 --report_target=M:\xL_Test_2021\2021_Aspirational_Diff

# Just generate
# python ./xlTest.py --start_xlights -R -C -P --suite=M:\xL_Test_2021\2021_Stabilized --summary_target=M:\xL_Test_2021\2021_Stabilized_TempResults_2022_13 --perf_target=M:\xL_Test_2021\2021_Stabilized_Perf_2022_13
# python ./xlTest.py --start_xlights -R -C -P --suite=M:\xL_Test_2021\2021_Stabilized --summary_target=M:\xL_Test_2021\2021_Stabilized_TempResults_2022_26 --perf_target=M:\xL_Test_2021\2021_Stabilized_Perf_2022_26
# python ./xlTest.py -R -C -P --timing_models --suite=M:\xL_Test_2021\2021_Stabilized_Unstable --summary_target=M:\xL_Test_2021\2021_UnstableRes_1 --perf_target=M:\xL_Test_2021\2021_UnstablePerf_1
# python ./xlTest.py -R -C -P --timing_models --suite=M:\xL_Test_2021\2021_Stabilized_Unstable --summary_target=M:\xL_Test_2021\2021_UnstableRes_2 --perf_target=M:\xL_Test_2021\2021_UnstablePerf_2
# Generate and compare
# python ./xlTest.py --start_xlights -R -C -P -D --suite=M:\xL_Test_2021\2021_Stabilized --summary_target=M:\xL_Test_2021\2021_Stabilized_TempResults_2022_26 --summary_expected=M:\xL_Test_2021\2021_Stabilized_AcceptedResults --report_target=M:\xL_Test_2021\2021_Stabilized_Diff --perf_target=M:\xL_Test_2021\2021_Stabilized_Perf_2022_26
# Just diff
# python ./xlTest.py -D --suite=M:\xL_Test_2021\2021_Stabilized --summary_expected=M:\xL_Test_2021\2021_Stabilized_TempResults_2021_39 --summary_target=M:\xL_Test_2021\2021_Stabilized_TempResults_2022_26 --report_target=M:\xL_Test_2021\2021_Stabilized_Diff
# python ./xlTest.py -D --timing_models --suite=M:\xL_Test_2021\2021_Stabilized_Unstable --summary_expected=M:\xL_Test_2021\2021_UnstableRes_1 --summary_target=M:\xL_Test_2021\2021_UnstableRes_2 --report_target=M:\xL_Test_2021\2021_Unstable_Diff
# python ./xlTest.py -D --timing_models --suite=M:\xL_Test_2021\2021_Stabilized --summary_expected=M:\xL_Test_2021\2021_UnstableRes_1 --summary_target=M:\xL_Test_2021\2021_UnstableRes_2 --report_target=M:\xL_Test_2021\2021_Unstable_Diff
# For perf, see other script

# 2023 Perf
# python ./xlTest.py -R -C -P --suite=M:\xL_Test_2021\2022_Xmas --summary_target=M:\xL_Test_2022\2022_TempResults_branch --perf_target=M:\xL_Test_2022\2022_Perf_branch
# python ./xlTest.py -R -C -P --suite=M:\xL_Test_2021\2022_Xmas --summary_target=M:\xL_Test_2022\2022_TempResults_master --perf_target=M:\xL_Test_2022\2022_Perf_master


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
        #xlenv.changeShowFolder()
        xlenv.changeShowFolderHttpGet()
        end = time.time()
        if "switch_folder" not in perf:
            perf['switch_folder'] = []
        perf['switch_folder'].append({'start': start, 'end': end, 'folder': args.datadir})

def switchAndRender(xlenv, args, perf):
    switchFolder(xlenv, args, perf)
    renderSequence(xlenv, args, perf)

def switchAndRenderSequences(xlenv, args, perf, seqs):
    switchFolder(xlenv, args, perf)
    oseq = args.sequence
    for seq in seqs:
        args.sequence = seq
        renderSequence(xlenv, args, perf)
    args.sequence = oseq

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
        xlAutomation.xsqFile.readSequenceTimingTrack(os.path.join(args.datadir, args.sequence), ttracks)

    # Process the CRC and tell us the result
    fseqbase = args.sequence[:-4] if args.sequence[-4:] == '.xsq' else args.sequence
    fseqn = os.path.join(args.datadir, fseqbase+'.fseq')
    hjson = xlAutomation.fseqFile.calculateFSEQSummary(fseqn, controllers, ctrlbyname, models, smodels, ttracks, args.timing_models)
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
    if not hjson and args.summary_target:
        # We are supposed to load it
        with open(os.path.join(args.summary_target,seqbase+'.crc'), 'r') as fh:
            hjson = json.load(fh)
    if not hjson:
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
    cargs.versions = False
    cargs.frames = False
    cargs.globalcrc = True
    cargs.models = True
    cargs.timings = True
    cargs.timing_models = args.timing_models

    diff = xlAutomation.compareFseqCRCs.compareSummaries(baseline, hjson, cargs, tgt)

    if diff and args.report_target:
        os.makedirs(args.report_target, mode = 0o777, exist_ok = True)
        with open(os.path.join(args.report_target,seqbase+'.rpt'), 'w') as fh:
            fh.write(tgt.getvalue())

    cmp_end = time.time()

    if "cmp" not in perf:
        perf['cmp']=[]
    perf['cmp'].append({'suite':args.suite, 'seq_name':seqbase, 'cmp_start':cmp_start, 'cmp_end':cmp_end})

    return diff


def testSequence(xlenv, args, perf):
    #seqbase = args.sequence[:-4] if args.sequence[-4:] == '.xsq' else args.sequence
    diff = False
    if args.do_render:
        switchAndRender(xlenv, args, perf)
    if args.calc_crcs:
        hjson = calcSequenceCRC(args, perf)
    else:
        hjson = None
    if args.diff_summary:
        diff = compareSequenceSummary(args, perf, hjson)
    return diff

def testSequences(xlenv, args, perf, seqs):
    if args.do_render:
        switchAndRenderSequences(xlenv, args, perf, seqs)

    oseq = args.sequence
    diff = False
    for seq in seqs:
        print(seq)
        args.sequence = seq

        if args.calc_crcs:
            hjson = calcSequenceCRC(args, perf)
        else:
            hjson = None
        if args.diff_summary:
            if compareSequenceSummary(args, perf, hjson):
                diff = True

    args.sequence = oseq
    return diff

def testSuiteFolder(xlenv, args, perf, pth):
    flist = os.listdir(pth)
    slist = []
    for x in flist:
        if x.endswith('.xsq'):
            slist.append(x)

    oddir = args.datadir
    args.datadir = pth
    testSequences(xlenv, args, perf, slist)
    args.datadir = oddir

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
    parser.add_argument('-l', '--timing_models', action='store_true', help='Keep model info within timing sections')

    # Lower case for paths
    parser.add_argument('-b', '--bindir',  help="Path to xLights binaries")
    parser.add_argument('-d', '--datadir', help="Path to xlights data dir (show folder)")    
    parser.add_argument('-w', '--summary_target', help="Path to write fseq summary")
    parser.add_argument('-e', '--summary_expected', help="Path to read fseq expected summary for compare")
    parser.add_argument('-r', '--report_target', help="Path to write comparison report")
    parser.add_argument('-p', '--perf_target', help="Path to write performance report")
    parser.add_argument('-s', '--sequence', help="Name of effect sequence .xsq file")
    parser.add_argument('-u', '--suite', help="Test suite directory; will run all .xsq in suite")

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
        testSequence(xlenv, args, perf)

    if args.suite:
        testSuiteFolder(xlenv, args, perf, args.suite)

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
