#!/usr/bin/env node
// xLights effect generator for floods / DMX wireless wands / bracelets.
//
// Reads a rendered .fseq plus the show layout, works out the dominant colors
// and energy of each frame, decides when a color update is worthwhile, and
// writes a new .xsq with:
//   - an "On" effect in the chosen color on the color target model, and
//   - a short "DMX" pulse on the control target model to strobe the transmitter.
//
// Revamp of DmxWands/GenerateFloodEffect.py in TypeScript. Layout work
// (channel resolution, color order, dimming curves, old/new layout formats) is
// done by xlLayoutCalcs.

import * as fs from 'fs';
import * as path from 'path';
import { Command, InvalidArgumentError } from 'commander';
import { HistogramArgs, summarizeFSeqColors } from './ColorSummary';
import {
    averagedColorsOverTiming,
    DEFAULT_WAND_ARGS,
    emitTimingColorEffects,
    emitWandEffects,
    planWandChanges,
    WandArgs,
    WandTargets,
} from './FloodEffect';
import { defaultSourceModels, isColorSource, loadShowLayout, loadXmlFile, resolveSourceModels } from './LayoutModels';
import { readTimingTracks, readXsqHead, TimingRec } from './XsqTiming';
import { XsqWriter } from './XsqWriter';

function intArg(value: string): number {
    const n = Number.parseInt(value, 10);
    if (!Number.isFinite(n)) throw new InvalidArgumentError('Expected an integer.');
    return n;
}

function intList(value: string): number[] {
    return value.split(',').map((s) => intArg(s.trim()));
}

interface CliOptions {
    showdir: string;
    fseq: string;
    outxsq?: string;
    modelsource?: string;
    targetcontrol: string;
    ch1val: number;
    ch2val: number;
    ctrlvals?: number[];
    targetcolor: string;
    targetcolor2?: string;
    controladvance: number;
    coloradvance: number;
    controlwidth: number;
    controlgap: number;
    inxsq?: string;
    timingtrack?: string;
    ttracklast: number;
    minpopularity: number;
    ncolors: number;
    changecolor: number;
    brightjumpamt: number;
    brightjumparea: number;
    brightdropamt: number;
    brightdroparea: number;
    offondrop: number;
    colorjumpamt: number;
    colorjumparea: number;
    similarityh: number;
    similaritys: number;
    similarityv: number;
    thresholdv: number;
    mode: string;
    permodel: boolean;
    nomedia: boolean;
    notiming: boolean;
    dumpplan?: string;
    listmodels: boolean;
    listtracks: boolean;
    quiet: boolean;
}

const program = new Command();
program
    .name('dmxwands')
    .description('xLights effect generator for floods / DMX wireless wands / bracelets: one color + transmitter pulse per scene change, derived from a rendered .fseq')
    .requiredOption('--showdir <dir>', 'Show folder with xlights_rgbeffects.xml and xlights_networks.xml')
    .requiredOption('--fseq <file>', '.fseq (or .eseq) input, the rendered sequence to read colors from')
    .option('--outxsq <file>', 'Generated .xsq output')
    .option('--modelsource <names>', 'Comma-separated source models and/or model groups for the RGB colors (default: every RGB pixel model)')
    .option('--targetcontrol <name>', 'Target model for the transmitter control pulses', 'DmxWandsCtrl')
    .option('--ch1val <n>', 'Control channel 1 (ID) value', intArg, 85)
    .option('--ch2val <n>', 'Control channel 2 (Group) value', intArg, 0)
    .option('--ctrlvals <list>', 'Full list of control channel values (overrides --ch1val/--ch2val), e.g. "85,0,0"', intList)
    .option('--targetcolor <name>', 'Target model for the color', 'DmxWands')
    .option('--targetcolor2 <name>', 'Optional second target model, gets the second most popular color')
    .option('--controladvance <ms>', 'Milliseconds to advance the timing of the control strobe', intArg, DEFAULT_WAND_ARGS.controladvance)
    .option('--coloradvance <ms>', 'Milliseconds to advance the timing of the color', intArg, DEFAULT_WAND_ARGS.coloradvance)
    .option('--controlwidth <ms>', 'Milliseconds to hold the control signal (.075-.1 s works well)', intArg, DEFAULT_WAND_ARGS.controlwidth)
    .option('--controlgap <ms>', 'Minimum milliseconds of gap between control pulses', intArg, DEFAULT_WAND_ARGS.controlgap)
    .option('--inxsq <file>', 'Input .xsq: source of the timing track and of the media file / song info')
    .option('--timingtrack <name>', 'Timing track (in --inxsq) whose marks trigger color updates')
    .option('--ttracklast <0|1>', 'Apply the timing track last, spaced against the detected events (1), or first, overriding them (0)', intArg, 1)
    .option('--minpopularity <n>', 'Minimum popularity of a color (tenths of a percent of lit pixels) for it to be considered', intArg, DEFAULT_WAND_ARGS.minpopularity)
    .option('--ncolors <n>', 'Number of colors to cycle between as numbered beats progress', intArg, DEFAULT_WAND_ARGS.ncolors)
    .option('--changecolor <0|1>', 'Try to change color when there is an event', intArg, 0)
    .option('--brightjumpamt <n>', 'Brightness jump event: brightness rises by this amount', intArg, DEFAULT_WAND_ARGS.brightjumpamt)
    .option('--brightjumparea <n>', 'Brightness jump event: at least this percent must be lit', intArg, DEFAULT_WAND_ARGS.brightjumparea)
    .option('--brightdropamt <n>', 'Brightness drop event: brightness falls by this amount', intArg, DEFAULT_WAND_ARGS.brightdropamt)
    .option('--brightdroparea <n>', 'Brightness drop event: at least this percent must have been lit', intArg, DEFAULT_WAND_ARGS.brightdroparea)
    .option('--offondrop <n>', 'Turn off when brightness drops by this percent since the last change (0 disables)', intArg, DEFAULT_WAND_ARGS.offondrop)
    .option('--colorjumpamt <n>', 'Color jump event: a color becomes most popular and gains this many points', intArg, DEFAULT_WAND_ARGS.colorjumpamt)
    .option('--colorjumparea <n>', 'Color jump event: the color must cover this percent of all pixels', intArg, DEFAULT_WAND_ARGS.colorjumparea)
    .option('--similarityh <n>', 'Hue similarity (2-degree bins)', intArg, DEFAULT_WAND_ARGS.similarityh)
    .option('--similaritys <n>', 'Saturation similarity (percent)', intArg, DEFAULT_WAND_ARGS.similaritys)
    .option('--similarityv <n>', 'Value similarity (percent)', intArg, DEFAULT_WAND_ARGS.similarityv)
    .option('--thresholdv <n>', 'Value threshold: pixels at or below this (0-255) are too dark to count', intArg, 5)
    .option('--mode <mode>', '"wands": event-driven changes (default); "timing": one popular color per timing-track interval', 'wands')
    .option('--permodel', 'Render the effects per model (use when the targets are model groups)', false)
    .option('--nomedia', 'Do not carry the media file / song info into the output', false)
    .option('--notiming', 'Do not copy the timing track into the output', false)
    .option('--dumpplan <file>', 'Also write the planned changes as CSV (for tuning)')
    .option('--listmodels', 'List the RGB pixel models and model groups in the layout, then exit', false)
    .option('--listtracks', 'List the timing tracks in --inxsq, then exit', false)
    .option('--quiet', 'Less progress output', false);

async function main(): Promise<number> {
    program.parse(process.argv);
    const opts = program.opts<CliOptions>();
    const say = (msg: string): void => {
        if (!opts.quiet) console.log(msg);
    };
    const warn = (msg: string): void => console.warn(msg);

    // ---- Layout -----------------------------------------------------------
    say(`Loading layout from ${opts.showdir}`);
    const layout = loadShowLayout(opts.showdir, warn);
    say(`  ${layout.channels.controllers.length} controllers, ${layout.channels.models.length} models, ${layout.groups.size} groups`);

    if (opts.listmodels) {
        console.log('RGB pixel models:');
        for (const m of layout.channels.models) {
            if (isColorSource(m)) console.log(`  ${m.name}  [${m.displayAs}] ch ${m.startChannel}+${m.channelCount}, gamma ${m.gamma}, brightness ${m.brightness}`);
        }
        console.log('Other models:');
        for (const m of layout.channels.models) {
            if (!isColorSource(m)) console.log(`  ${m.name}  [${m.displayAs}] ch ${m.startChannel}+${m.channelCount}`);
        }
        console.log('Model groups:');
        for (const [g, members] of layout.groups) console.log(`  ${g}  (${members.length} members)`);
        return 0;
    }

    const targets: WandTargets = {
        control: opts.targetcontrol || undefined,
        color: opts.targetcolor || undefined,
        color2: opts.targetcolor2 || undefined,
    };
    for (const t of [targets.control, targets.color, targets.color2]) {
        if (t && !layout.byName.has(t) && !layout.groups.has(t)) {
            warn(`Warning: target "${t}" is not a model or group in this layout; the output will still reference it`);
        }
    }

    // ---- Source models ----------------------------------------------------
    const excluded = [targets.control, targets.color, targets.color2].filter((x): x is string => !!x);
    let sources = defaultSourceModels(layout, excluded);
    if (opts.modelsource) {
        const res = resolveSourceModels(opts.modelsource.split(','), layout);
        for (const n of res.missing) warn(`Warning: source "${n}" is not a model or group`);
        for (const n of res.notRgb) warn(`Warning: source "${n}" is not an RGB pixel model; skipped`);
        if (res.missing.length && !res.models.length) {
            console.error('ERROR: none of the source models were found');
            return 2;
        }
        sources = res.models;
    }
    if (!sources.length) {
        console.error('ERROR: no RGB pixel models to read colors from');
        return 2;
    }
    const totalPixels = sources.reduce((a, m) => a + Math.floor(m.channelCount / 3), 0);
    say(`  Reading colors from ${sources.length} models (${totalPixels} pixels)`);

    // ---- Timing track / media from the input xsq ---------------------------
    let ttrack: TimingRec | undefined;
    let mediaFile = '';
    let song = '';
    let artist = '';
    let album = '';
    if (opts.inxsq) {
        const xdoc = loadXmlFile(opts.inxsq);
        const head = readXsqHead(xdoc);
        mediaFile = head.mediaFile;
        song = head.song;
        artist = head.artist;
        album = head.album;
        const tracks = readTimingTracks(xdoc);
        if (opts.listtracks) {
            console.log(`Timing tracks in ${opts.inxsq}:`);
            for (const t of tracks) console.log(`  ${t.name}  (${t.entlist.length} marks, ${t.subentlists.length} layers)`);
            return 0;
        }
        if (opts.timingtrack) {
            ttrack = tracks.find((t) => t.name === opts.timingtrack);
            if (!ttrack) {
                console.error(`ERROR: timing track "${opts.timingtrack}" not found. Available: ${tracks.map((t) => t.name).join(', ') || '(none)'}`);
                return 2;
            }
            say(`  Using timing track "${ttrack.name}" with ${ttrack.entlist.length} marks`);
        }
    } else if (opts.listtracks) {
        console.error('ERROR: --listtracks needs --inxsq');
        return 2;
    } else if (opts.timingtrack) {
        console.error('ERROR: --timingtrack needs --inxsq');
        return 2;
    }

    if (!opts.outxsq) {
        console.error('ERROR: --outxsq is required');
        return 2;
    }
    if (opts.mode !== 'wands' && opts.mode !== 'timing') {
        console.error(`ERROR: unknown --mode "${opts.mode}" (use wands or timing)`);
        return 2;
    }
    if (opts.mode === 'timing' && !ttrack) {
        warn('Warning: --mode timing without a timing track: one color for the whole sequence');
    }

    // ---- Color summary of the fseq ----------------------------------------
    const histArgs: HistogramArgs = {
        thresholdv: opts.thresholdv,
        similarityh: opts.similarityh,
        similaritys: opts.similaritys,
        similarityv: opts.similarityv,
    };
    say(`Reading ${opts.fseq}`);
    const t0 = Date.now();
    const summary = await summarizeFSeqColors(opts.fseq, sources, histArgs, (n, total) => {
        if (!opts.quiet) process.stdout.write(`  frame ${n}/${total}\r`);
    });
    const hdr = summary.header;
    say(`  ${hdr.tag} v${hdr.majver}.${hdr.minver}: ${hdr.frames} frames @ ${hdr.msPerFrame} ms, ${hdr.channels} channels, read in ${((Date.now() - t0) / 1000).toFixed(1)} s`);
    if (summary.missingModels.length) {
        warn(`Warning: ${summary.missingModels.length} source models are outside the channel ranges stored in this fseq (sparse file or older render): ${summary.missingModels.slice(0, 10).join(', ')}${summary.missingModels.length > 10 ? ', ...' : ''}`);
    }
    if (!summary.frames.length) {
        console.error('ERROR: the fseq has no frames');
        return 2;
    }

    // ---- Plan and emit ----------------------------------------------------
    const args: WandArgs = {
        controladvance: opts.controladvance,
        coloradvance: opts.coloradvance,
        controlwidth: opts.controlwidth,
        controlgap: opts.controlgap,
        ttracklast: opts.ttracklast !== 0,
        minpopularity: opts.minpopularity,
        ncolors: opts.ncolors,
        changecolor: opts.changecolor !== 0,
        brightjumpamt: opts.brightjumpamt,
        brightjumparea: opts.brightjumparea,
        brightdropamt: opts.brightdropamt,
        brightdroparea: opts.brightdroparea,
        offondrop: opts.offondrop,
        colorjumpamt: opts.colorjumpamt,
        colorjumparea: opts.colorjumparea,
        similarityh: opts.similarityh,
        similaritys: opts.similaritys,
        similarityv: opts.similarityv,
    };
    const emitOpts = {
        controlValues: opts.ctrlvals ?? [opts.ch1val, opts.ch2val],
        perModel: opts.permodel,
    };

    const writer = new XsqWriter(hdr.msPerFrame, hdr.frames);
    writer.setComment(`Generated by DmxWandsTS from ${path.basename(opts.fseq)}`);
    if (!opts.nomedia) {
        const mf = mediaFile || hdr.headers['mf'] || '';
        if (mf) writer.setMedia(mf, song, artist, album);
    }

    let nEffects = 0;
    if (opts.mode === 'timing') {
        const intervals = averagedColorsOverTiming(ttrack, summary.frames, hdr.msPerFrame, args);
        say(`Planned ${intervals.length} timing intervals with color`);
        nEffects = emitTimingColorEffects(writer, intervals, targets, args, emitOpts);
        if (opts.dumpplan) {
            const rows = ['startMs,endMs,H,S,VTyp,popularity,vMax'];
            for (const iv of intervals) {
                const c = iv.choices[0];
                rows.push(`${iv.start},${iv.end},${c.H},${c.S},${c.VTyp},${c.popularity},${iv.vMax.toFixed(1)}`);
            }
            fs.writeFileSync(opts.dumpplan, rows.join('\n') + '\n');
        }
    } else {
        const plan = planWandChanges(summary.frames, ttrack, hdr.msPerFrame, args);
        const nEvents = plan.filter((p) => p.event).length;
        say(`Planned ${plan.length} color changes (${nEvents} at events)`);
        nEffects = emitWandEffects(writer, plan, targets, args, emitOpts);
        if (opts.dumpplan) {
            const rows = ['startMs,endMs,event,tn,r,g,b,r2,g2,b2'];
            for (const p of plan) {
                rows.push(`${p.startMs},${p.endMs},${p.event ? 1 : 0},${p.tn},${p.color.join(',')},${p.color2.join(',')}`);
            }
            fs.writeFileSync(opts.dumpplan, rows.join('\n') + '\n');
        }
    }

    if (ttrack && !opts.notiming) writer.addTimingTrack(ttrack);

    await writer.save(opts.outxsq);
    say(`Wrote ${nEffects} effects to ${opts.outxsq}`);
    return 0;
}

main().then(
    (code) => process.exit(code),
    (err) => {
        console.error(`ERROR: ${err instanceof Error ? err.message : String(err)}`);
        process.exit(1);
    },
);
