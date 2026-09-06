// Per-frame color summary of an .fseq: HSV histograms, the 4 most popular
// colors per frame, and brightness/coverage statistics.
// Ported from DmxWands/GenerateFloodEffect.py (Histogram, CChoice, FrameInfo, calculateFSEQColorSummary).

import { makeInverseDimmingLut } from './ColorUtil';
import { FSeqHeader, FSeqReader, modelChannelBytes } from './FSeqReader';

/** An RGB pixel model we can read colors from. */
export interface ColorSourceModel {
    name: string;
    /** 1-based absolute start channel. */
    startChannel: number;
    channelCount: number;
    /** Byte offsets of R, G, B within each 3-channel node (color order). */
    rOff: number;
    gOff: number;
    bOff: number;
    gamma: number;
    brightness: number;
}

export interface HistogramArgs {
    /** Value threshold: a pixel with all raw channels <= this is "black". */
    thresholdv: number;
    /** Hue similarity, in 2-degree histogram bins. */
    similarityh: number;
    /** Saturation similarity (percent). */
    similaritys: number;
    /** Value similarity (percent). */
    similarityv: number;
}

export type ChoiceDiffArgs = Pick<HistogramArgs, 'similarityh' | 'similaritys' | 'similarityv'>;

const H_BINS = 180;
const S_BINS = 101;

export class Histogram {
    minV = 1;
    maxV = 0; // 0..100
    nNonBlack = 0;
    nSamples = 0;
    GHist = new Int32Array(101);              // Grayscale (S == 0) pixels, by V
    VHist = new Int32Array(101);              // All non-black pixels, by V
    HSHist = new Int32Array(H_BINS * S_BINS); // Hue (2 degree bins) x Saturation (percent); grays are in GHist instead

    private static lutCache = new Map<string, Float32Array>();

    static lutFor(model: ColorSourceModel): Float32Array {
        const key = `${model.gamma}|${model.brightness}`;
        let lut = Histogram.lutCache.get(key);
        if (!lut) {
            lut = makeInverseDimmingLut(model.gamma, model.brightness);
            Histogram.lutCache.set(key, lut);
        }
        return lut;
    }

    update(model: ColorSourceModel, raw: Uint8Array, args: HistogramArgs): void {
        const lut = Histogram.lutFor(model);
        const ro = model.rOff, go = model.gOff, bo = model.bOff;
        const thr = args.thresholdv;
        const l = raw.length;
        const GHist = this.GHist, VHist = this.VHist, HSHist = this.HSHist;
        let minV = this.minV, maxV = this.maxV, nNonBlack = this.nNonBlack, nSamples = this.nSamples;

        for (let rp = 0; rp + 2 < l; rp += 3) {
            const rr = raw[rp + ro];
            const gg = raw[rp + go];
            const bb = raw[rp + bo];
            ++nSamples;

            const r = lut[rr], g = lut[gg], b = lut[bb];
            const M = r > g ? (r > b ? r : b) : (g > b ? g : b);
            const m = r < g ? (r < b ? r : b) : (g < b ? g : b);
            const C = M - m;
            let h = 0;
            if (C !== 0) {
                if (M === r) h = (60 * ((g - b) / C) + 360) % 360;
                else if (M === g) h = (60 * ((b - r) / C) + 120) % 360;
                else h = (60 * ((r - g) / C) + 240) % 360;
            }
            const s = M === 0 ? 0 : C / M;
            const v = M;

            if (v < minV) minV = v;
            if (v * 100 > maxV) maxV = v * 100;
            if (rr <= thr && gg <= thr && bb <= thr) continue;

            ++nNonBlack;
            const vi = Math.floor(v * 100);
            VHist[vi]++;
            if (s === 0) {
                GHist[vi]++;
            } else {
                HSHist[Math.floor(h / 2) * S_BINS + Math.floor(s * 100)]++;
            }
        }

        this.minV = minV;
        this.maxV = maxV;
        this.nNonBlack = nNonBlack;
        this.nSamples = nSamples;
    }
}

/** One candidate color for a frame: hue, saturation, typical value, and how many pixels backed it. */
export class CChoice {
    H = 0;      // 0..360
    S = 0;      // 0..100
    VTyp = 0;   // 0..100; for colored choices this is 100 (the real V comes from the frame's vMax)
    popularity = 0;

    setBlack(): void {
        this.H = 0;
        this.S = 0;
        this.VTyp = 0;
    }

    valid(): boolean {
        return this.VTyp > 0;
    }

    invalidate(): void {
        this.VTyp = 0;
        this.H = 0;
        this.S = 0;
        this.popularity = 0;
    }

    clone(): CChoice {
        const c = new CChoice();
        c.H = this.H;
        c.S = this.S;
        c.VTyp = this.VTyp;
        c.popularity = this.popularity;
        return c;
    }

    isDifferent(other: CChoice | undefined, args: ChoiceDiffArgs): boolean {
        if (!other) return true;
        const hdiff = Math.abs(this.H - other.H);
        if (hdiff > args.similarityh && hdiff < 360 - args.similarityh) return true;
        if (Math.abs(this.S - other.S) > args.similaritys) return true;
        if (Math.abs(this.VTyp - other.VTyp) > args.similarityv) return true;
        return false;
    }
}

export class FrameInfo {
    /** Always 4 entries, most popular first; unused entries are invalid (black). */
    choices: CChoice[] = [];
    nLit = 0;
    nPixels = 0;
    pctLit = 0;
    pctBright = 0;
    /** Average V among lit pixels (0..100); scale by pctLit for the overall level. */
    vAvg = 0;
    /** Maximum V over all pixels (0..100). */
    vMax = 0;
    ms = 0;

    setBlack(): void {
        this.vAvg = 0;
        this.vMax = 0;
        this.pctLit = 0;
        this.pctBright = 0;
        this.nLit = 0;
        for (const cc of this.choices) cc.setBlack();
    }
}

export const NUM_CHOICES = 4;

/** Extract the 4 most popular colors (with neighborhood knock-out) and the brightness stats. */
export function analyzeHistogram(hist: Histogram, finfo: FrameInfo, args: HistogramArgs): void {
    for (let i = 0; i < NUM_CHOICES; ++i) {
        let gpop = 0;
        let bg = 0;
        for (let v = 0; v < hist.GHist.length; ++v) {
            if (hist.GHist[v] > gpop) {
                bg = v;
                gpop = hist.GHist[v];
            }
        }

        let bc = 0;
        let bh = 0;
        let bs = 0;
        for (let h = 0; h < H_BINS; ++h) {
            const row = h * S_BINS;
            for (let s = 0; s < S_BINS; ++s) {
                if (hist.HSHist[row + s] > bc) {
                    bc = hist.HSHist[row + s];
                    bh = h;
                    bs = s;
                }
            }
        }

        const cc = new CChoice();
        finfo.choices.push(cc);

        if (bc === 0 && gpop === 0) {
            continue; // There simply is not any (more) color
        }

        if (gpop > bc) {
            // Gray: sweep up the neighborhood in V
            for (let v = bg - 5; v <= bg + 5; ++v) {
                if (v > 0 && v <= 100) {
                    cc.popularity += hist.GHist[v];
                    hist.GHist[v] = 0;
                }
            }
            cc.H = 0;
            cc.S = 0;
            cc.VTyp = bg;
        } else {
            // Color: sweep up the neighborhood in H (wrapping) and S
            for (let h = bh - args.similarityh; h <= bh + args.similarityh; ++h) {
                const hw = ((h % H_BINS) + H_BINS) % H_BINS;
                for (let s = bs - args.similaritys; s <= bs + args.similaritys; ++s) {
                    if (s > 0 && s <= 100) {
                        cc.popularity += hist.HSHist[hw * S_BINS + s];
                        hist.HSHist[hw * S_BINS + s] = 0;
                    }
                }
            }
            cc.H = bh * 2;
            cc.S = bs;
            cc.VTyp = 100; // We don't track the V typical of that color; the frame's vMax is used when emitting
        }
    }

    if (hist.nNonBlack) {
        let vtot = 0;
        let btot = 0;
        for (let i = 1; i < hist.VHist.length; ++i) {
            vtot += i * hist.VHist[i];
            if (i >= 50) btot += hist.VHist[i];
        }
        finfo.pctLit = (hist.nNonBlack * 100) / hist.nSamples;
        finfo.pctBright = (btot * 100) / hist.nSamples;
        finfo.vAvg = vtot / hist.nNonBlack;
    }
    finfo.nLit = hist.nNonBlack;
    finfo.nPixels = hist.nSamples;
    finfo.vMax = hist.maxV;
}

export interface ColorSummaryResult {
    header: FSeqHeader;
    frames: FrameInfo[];
    /** Source models whose channels are not stored in the .fseq (sparse file, or rendered from an older layout). */
    missingModels: string[];
}

/** Read every frame of the .fseq and summarize the colors of the given models. */
export async function summarizeFSeqColors(
    fseqFile: string,
    models: ColorSourceModel[],
    args: HistogramArgs,
    onProgress?: (frame: number, total: number) => void,
): Promise<ColorSummaryResult> {
    const reader = new FSeqReader(fseqFile);
    const frames: FrameInfo[] = [];
    const missing = new Set<string>();
    try {
        await reader.open();
        const header = await reader.readHeader();
        await reader.forEachFrame((f) => {
            const hist = new Histogram();
            for (const m of models) {
                const bytes = modelChannelBytes(f.data, header, m.startChannel, m.channelCount);
                if (!bytes) {
                    missing.add(m.name);
                    continue;
                }
                hist.update(m, bytes, args);
            }
            const finfo = new FrameInfo();
            finfo.ms = f.timeMs;
            analyzeHistogram(hist, finfo, args);
            frames.push(finfo);
            if (onProgress && (f.frameNum % 500 === 0 || f.frameNum + 1 === header.frames)) {
                onProgress(f.frameNum + 1, header.frames);
            }
        });
        return { header, frames, missingModels: [...missing] };
    } finally {
        await reader.close();
    }
}
