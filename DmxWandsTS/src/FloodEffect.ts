// Change-point planning and effect emission for the wands / floods.
// Ported from DmxWands/GenerateFloodEffect.py (the main program's planning loop).
//
// Two modes:
//   planWandChanges()          - event driven: brightness jumps/drops, color jumps, timing marks,
//                                "off on drop"; each change gets a color plus a transmitter pulse.
//   averagedColorsOverTiming() - one popular-color set per timing-track interval (beats, bars, sections).

import { hsvToRgb, RGB } from './ColorUtil';
import { CChoice, ChoiceDiffArgs, FrameInfo, NUM_CHOICES } from './ColorSummary';
import { TimingRec } from './XsqTiming';
import { XsqWriter } from './XsqWriter';

export interface WandArgs extends ChoiceDiffArgs {
    /** Milliseconds to advance the control strobe (in case of delay between strobe and wand action). */
    controladvance: number;
    /** Milliseconds to advance the color change before the strobe. */
    coloradvance: number;
    /** Milliseconds to hold the control signal. */
    controlwidth: number;
    /** Minimum milliseconds of gap between control pulses. */
    controlgap: number;
    /** Apply the timing track last (spaced against detected events) rather than first (overriding). */
    ttracklast: boolean;
    /** Minimum popularity of a color, in tenths of a percent of the lit pixels, for it to be considered. */
    minpopularity: number;
    /** Number of colors to cycle between as the (numbered) beats progress. */
    ncolors: number;
    /** Try to change color when there is an event. */
    changecolor: boolean;
    /** Brightness jump event: if average brightness jumps by this much, count it as an event. */
    brightjumpamt: number;
    /** Brightness jump event: at least this percent must be lit. */
    brightjumparea: number;
    /** Brightness drop event: if average brightness drops by this much, count it as an event. */
    brightdropamt: number;
    /** Brightness drop event: at least this percent must have been lit. */
    brightdroparea: number;
    /** Turn off when brightness drops by this percent from the last change (0 disables). */
    offondrop: number;
    /** Color jump event: a color becomes most popular and gains this many percentage points. */
    colorjumpamt: number;
    /** Color jump event: the color must cover this percent of all pixels. */
    colorjumparea: number;
}

export const DEFAULT_WAND_ARGS: WandArgs = {
    controladvance: 0,
    coloradvance: 0,
    controlwidth: 75,
    controlgap: 50,
    ttracklast: true,
    minpopularity: 10,
    ncolors: 1,
    changecolor: false,
    brightjumpamt: 50,
    brightjumparea: 50,
    brightdropamt: 50,
    brightdroparea: 50,
    offondrop: 50,
    colorjumpamt: 25,
    colorjumparea: 50,
    similarityh: 6,
    similaritys: 10,
    similarityv: 20,
};

class SeqEnt {
    ms: number;
    event = false;          // A trigger event vs just a fill - we want a color change here
    colorFidelity = false;  // Hint that we ought to take the popular color, not just change
    tn = 0;                 // Timing number (from a numeric timing label)

    constructor(readonly frame: FrameInfo) {
        this.ms = frame.ms;
    }
}

/** Sorted set of change points keyed by ms. */
class SparseSeq {
    times: number[] = [];
    frames = new Map<number, SeqEnt>();

    private lowerBound(value: number): number {
        let low = 0;
        let high = this.times.length;
        while (low < high) {
            const mid = (low + high) >> 1;
            if (this.times[mid] < value) low = mid + 1;
            else high = mid;
        }
        return low;
    }

    private closest(ms: number): [SeqEnt | undefined, SeqEnt | undefined] {
        const idx = this.lowerBound(ms);
        const left = idx > 0 ? this.frames.get(this.times[idx - 1]) : undefined;
        const right = idx < this.times.length ? this.frames.get(this.times[idx]) : undefined;
        return [left, right];
    }

    insert(ent: SeqEnt): void {
        if (!this.frames.has(ent.ms)) {
            this.times.splice(this.lowerBound(ent.ms), 0, ent.ms);
        }
        this.frames.set(ent.ms, ent);
    }

    isSpaced(ms: number, gap: number): boolean {
        const [l, r] = this.closest(ms);
        if (l && ms - l.ms < gap) return false;
        if (r && r.ms - ms < gap) return false;
        return true;
    }

    insertIfSpaced(ent: SeqEnt, gap: number): boolean {
        if (!this.isSpaced(ent.ms, gap)) return false;
        this.insert(ent);
        return true;
    }
}

export interface PlannedChange {
    startMs: number;
    endMs: number;
    /** Primary color to send. */
    color: RGB;
    /** A second color (the next most popular different one), for a secondary target. */
    color2: RGB;
    event: boolean;
    tn: number;
}

function timingNumber(label: string): number {
    const n = Number.parseInt(label, 10);
    return Number.isFinite(n) ? n : 0;
}

function choiceToRgb(cc: CChoice, frameVMax: number): RGB {
    if (cc.S > 0) {
        return hsvToRgb(cc.H, cc.S, frameVMax);
    }
    return hsvToRgb(cc.H, cc.S, cc.VTyp);
}

/**
 * Decide when to change the wand color and what color to send.
 * NOTE: mutates `frames` (prunes unpopular choices, blacks out the last frame and "off on drop" frames),
 * exactly as the original did.
 */
export function planWandChanges(frames: FrameInfo[], ttrack: TimingRec | undefined, frameMs: number, args: WandArgs): PlannedChange[] {
    const nframes = frames.length;
    if (!nframes) return [];

    // Prune out the unpopular colors
    for (const f of frames) {
        for (const c of f.choices) {
            if (c.popularity * 1000 < f.nLit * args.minpopularity) {
                c.invalidate();
            }
        }
    }

    const reqgap = args.controlwidth + args.controlgap;
    const ss = new SparseSeq();

    const addTimingEvents = (spaced: boolean): void => {
        if (!ttrack) return;
        for (const te of ttrack.entlist) {
            const sfn = Math.floor(te.startms / frameMs);
            let efn = Math.floor(te.endms / frameMs);
            if (sfn >= nframes) continue;
            if (efn >= nframes) efn = nframes - 1;
            if (efn === sfn) continue;
            const se = new SeqEnt(frames[sfn]);
            se.event = true;
            se.tn = timingNumber(te.label);
            if (spaced) {
                ss.insertIfSpaced(se, reqgap);
            } else {
                // Also mark the end; a following timing mark will simply overwrite it.
                ss.insert(se);
                ss.insert(new SeqEnt(frames[efn]));
            }
        }
    };

    if (!args.ttracklast) addTimingEvents(false);

    // Black at the end
    const seqend = frameMs * nframes;
    frames[nframes - 1].setBlack();
    ss.insert(new SeqEnt(frames[nframes - 1]));

    // Look for brightness / color triggers
    for (let i = 1; i < nframes; ++i) {
        const cf = frames[i];
        const pf = frames[i - 1];
        if (args.brightjumpamt > 0 && cf.pctLit >= args.brightjumparea &&
            cf.vAvg - (pf.vAvg * pf.pctLit) / cf.pctLit >= args.brightjumpamt) {
            const es = new SeqEnt(cf);
            es.event = true;
            es.colorFidelity = true;
            ss.insertIfSpaced(es, reqgap);
        }
        if (args.brightdropamt > 0 && pf.pctLit >= args.brightdroparea &&
            pf.vAvg - (cf.vAvg * cf.pctLit) / pf.pctLit >= args.brightdropamt) {
            const es = new SeqEnt(cf);
            es.event = true;
            ss.insertIfSpaced(es, reqgap);
        }

        if (args.colorjumpamt > 0 && cf.nPixels > 0 && cf.nLit > 0) {
            const top = cf.choices[0];
            const amtpopular = (100 * top.popularity) / cf.nPixels;
            if (amtpopular > args.colorjumparea) {
                const pctpopular = (100 * top.popularity) / cf.nLit;
                let prevpop = 0;
                if (pf.nLit > 0) {
                    for (const c of pf.choices) {
                        if (c.popularity > 0 && !c.isDifferent(top, args)) {
                            prevpop = (100 * c.popularity) / pf.nLit;
                        }
                    }
                }
                if (pctpopular - prevpop >= args.colorjumpamt) {
                    const es = new SeqEnt(cf);
                    es.event = true;
                    es.colorFidelity = true;
                    ss.insertIfSpaced(es, reqgap);
                }
            }
        }
    }

    if (args.ttracklast) addTimingEvents(true);

    // Turn off when the brightness falls well below what it was at the last change
    if (args.offondrop > 0) {
        let lastevt: SeqEnt | undefined;
        for (let i = 0; i < nframes; ++i) {
            const curms = i * frameMs;
            const at = ss.frames.get(curms);
            if (at) {
                lastevt = at;
                continue;
            }
            if (!lastevt || lastevt.frame.vMax === 0) continue;
            if (100 - (100 * frames[i].vMax) / lastevt.frame.vMax > args.offondrop) {
                if (ss.isSpaced(curms, reqgap)) {
                    frames[i].setBlack();
                    const se = new SeqEnt(frames[i]);
                    ss.insertIfSpaced(se, reqgap);
                    lastevt = se;
                }
            }
        }
    }

    // Walk the change points and pick colors
    const plan: PlannedChange[] = [];
    const ncolors = Math.max(1, args.ncolors);
    let lastChoice: CChoice | undefined;
    let i = 0;
    while (i < ss.times.length) {
        const stime = ss.times[i];
        let etime = seqend;
        for (;;) {
            ++i;
            etime = i < ss.times.length ? ss.times[i] : seqend;
            if (etime - stime >= reqgap || i >= ss.times.length) break;
        }

        const cframe = ss.frames.get(stime)!;
        const choices = cframe.frame.choices;
        let chosen = 0;
        let cc = choices[chosen];

        if (cframe.event) {
            if (ncolors > 1) {
                chosen = (((cframe.tn - 1) % ncolors) + ncolors) % ncolors % NUM_CHOICES;
                cc = choices[chosen];
            }
            if (args.changecolor && !cframe.colorFidelity) {
                for (let ccc = 0; ccc < NUM_CHOICES; ++ccc) {
                    const cand = choices[(chosen + ccc) % NUM_CHOICES];
                    if (cand.isDifferent(lastChoice, args)) {
                        cc = cand;
                        break;
                    }
                }
            }
        }

        // Secondary color: the next most popular choice that differs from the primary
        let cc2 = cc;
        for (let ccc = 0; ccc < NUM_CHOICES; ++ccc) {
            const cand = choices[ccc];
            if (cand.popularity > 0 && cand.valid() && cand.isDifferent(cc, args)) {
                cc2 = cand;
                break;
            }
        }

        lastChoice = cc;
        plan.push({
            startMs: stime,
            endMs: etime,
            color: choiceToRgb(cc, cframe.frame.vMax),
            color2: choiceToRgb(cc2, cframe.frame.vMax),
            event: cframe.event,
            tn: cframe.tn,
        });
    }
    return plan;
}

export interface WandTargets {
    /** Model that receives the transmitter control pulses (DMX effect). */
    control?: string;
    /** Model that receives the color (On effect). */
    color?: string;
    /** Optional model that receives the secondary color. */
    color2?: string;
}

export interface EmitOptions {
    /** DMX channel values for the control pulse, channel 1 first. */
    controlValues: number[];
    /** Render per model (for targets that are model groups). */
    perModel: boolean;
}

/** Emit the planned changes as On + DMX effects. Returns the number of effects written. */
export function emitWandEffects(w: XsqWriter, plan: PlannedChange[], targets: WandTargets, args: WandArgs, opts: EmitOptions): number {
    const ctrlLayer = targets.control ? w.addEffectLayer(targets.control) : undefined;
    const clrLayer = targets.color ? w.addEffectLayer(targets.color) : undefined;
    const clrLayer2 = targets.color2 ? w.addEffectLayer(targets.color2) : undefined;
    const before = w.effectCount;

    for (const ch of plan) {
        const ctrlstime = Math.max(ch.startMs - args.controladvance, 0);
        const ctrletime = Math.max(ch.startMs - args.controladvance + args.controlwidth, 0);
        const clrstime = Math.max(ch.startMs - args.coloradvance, 0);
        const clretime = Math.max(ch.endMs - args.coloradvance, 0);
        if (clretime <= clrstime) continue;

        if (clrLayer) w.addOnEffect(clrLayer, clrstime, clretime, ch.color, opts.perModel);
        if (clrLayer2) w.addOnEffect(clrLayer2, clrstime, clretime, ch.color2, opts.perModel);
        if (ctrlLayer && ctrletime > ctrlstime) w.addDmxEffect(ctrlLayer, ctrlstime, ctrletime, opts.controlValues, opts.perModel);
    }
    return w.effectCount - before;
}

// ---------------------------------------------------------------------------
// Timing-interval mode

export class ColorForTime {
    constructor(
        /** Merged choices over the interval, most popular first. */
        readonly choices: CChoice[],
        readonly start: number,
        readonly end: number,
        /** Maximum V (0..100) seen in the interval. */
        readonly vMax: number,
    ) {}
}

/**
 * Merge the per-frame color choices over each timing interval (or the whole
 * sequence when no timing track is given), producing the popular colors per interval.
 */
export function averagedColorsOverTiming(timing: TimingRec | undefined, frames: FrameInfo[], frameMs: number, args: ChoiceDiffArgs): ColorForTime[] {
    if (!frames.length) return [];
    if (!timing) {
        timing = new TimingRec('whole');
        timing.entlist.push({ label: '', startms: 0, endms: frames[frames.length - 1].ms + frameMs });
    }

    const res: ColorForTime[] = [];
    for (const te of timing.entlist) {
        const first = Math.max(0, Math.floor(te.startms / frameMs));
        const last = Math.min(frames.length, Math.ceil(te.endms / frameMs));
        if (first >= last) continue;

        const merged: CChoice[] = [];
        let vMax = 0;
        for (let fi = first; fi < last; ++fi) {
            const frame = frames[fi];
            if (frame.vMax > vMax) vMax = frame.vMax;
            for (const c of frame.choices) {
                if (!c.popularity || !c.valid()) continue;
                const existing = merged.find((m) => !c.isDifferent(m, args));
                if (existing) {
                    existing.popularity += c.popularity;
                    existing.VTyp = Math.max(existing.VTyp, c.VTyp);
                } else {
                    merged.push(c.clone());
                }
            }
        }
        if (!merged.length) continue;
        merged.sort((a, b) => b.popularity - a.popularity);
        res.push(new ColorForTime(merged, te.startms, te.endms, vMax));
    }
    return res;
}

/** Emit one color per timing interval (plus a control pulse at each interval start). Returns the number of effects written. */
export function emitTimingColorEffects(w: XsqWriter, intervals: ColorForTime[], targets: WandTargets, args: WandArgs, opts: EmitOptions): number {
    const ctrlLayer = targets.control ? w.addEffectLayer(targets.control) : undefined;
    const clrLayer = targets.color ? w.addEffectLayer(targets.color) : undefined;
    const clrLayer2 = targets.color2 ? w.addEffectLayer(targets.color2) : undefined;
    const before = w.effectCount;

    for (const iv of intervals) {
        const cc = iv.choices[0];
        const cc2 = iv.choices.length > 1 ? iv.choices[1] : cc;
        const ctrlstime = Math.max(iv.start - args.controladvance, 0);
        const ctrletime = Math.max(iv.start - args.controladvance + args.controlwidth, 0);
        const clrstime = Math.max(iv.start - args.coloradvance, 0);
        const clretime = Math.max(iv.end - args.coloradvance, 0);
        if (clretime <= clrstime) continue;

        if (clrLayer) w.addOnEffect(clrLayer, clrstime, clretime, choiceToRgb(cc, iv.vMax), opts.perModel);
        if (clrLayer2) w.addOnEffect(clrLayer2, clrstime, clretime, choiceToRgb(cc2, iv.vMax), opts.perModel);
        if (ctrlLayer && ctrletime > ctrlstime) w.addDmxEffect(ctrlLayer, ctrlstime, ctrletime, opts.controlValues, opts.perModel);
    }
    return w.effectCount - before;
}
