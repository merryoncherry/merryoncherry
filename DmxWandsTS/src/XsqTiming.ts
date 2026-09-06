// Reading bits of an existing .xsq: the head and the timing tracks.
// Ported from xlAutomation/xsqFile.py (readSequenceTimingTrack).

export class TimingEnt {
    constructor(public label: string, public startms: number, public endms: number) {}
}

export class TimingRec {
    /** Primary (first layer) entries. */
    entlist: TimingEnt[] = [];
    /** All layers (e.g. a vocal track with phrases / words / phonemes). */
    subentlists: TimingEnt[][] = [];
    constructor(public name: string) {}
}

export interface XsqHeadInfo {
    version: string;
    author: string;
    song: string;
    artist: string;
    album: string;
    sequenceType: string;
    frameMs: number;
    durationSec: number;
    mediaFile: string;
}

function elementChildren(n: Node): Element[] {
    const out: Element[] = [];
    for (let i = 0; i < n.childNodes.length; ++i) {
        const k = n.childNodes[i];
        if (k.nodeType === 1) out.push(k as Element);
    }
    return out;
}

export function readXsqHead(doc: Document): XsqHeadInfo {
    const info: XsqHeadInfo = {
        version: '', author: '', song: '', artist: '', album: '',
        sequenceType: '', frameMs: 0, durationSec: 0, mediaFile: '',
    };
    const root = doc.documentElement;
    if (!root) return info;
    for (const section of elementChildren(root)) {
        if (section.tagName !== 'head') continue;
        for (const field of elementChildren(section)) {
            const text = field.textContent ?? '';
            switch (field.tagName) {
                case 'version': info.version = text.trim(); break;
                case 'author': info.author = text; break;
                case 'song': info.song = text; break;
                case 'artist': info.artist = text; break;
                case 'album': info.album = text; break;
                case 'sequenceType': info.sequenceType = text; break;
                case 'sequenceTiming': info.frameMs = Number.parseInt(text) || 0; break;
                case 'sequenceDuration': info.durationSec = Number.parseFloat(text) || 0; break;
                case 'mediaFile': info.mediaFile = text; break;
            }
        }
    }
    return info;
}

export function readTimingTracks(doc: Document): TimingRec[] {
    const root = doc.documentElement;
    if (!root || root.tagName !== 'xsequence') {
        throw new Error('Root element is not "xsequence"');
    }
    const ttracks: TimingRec[] = [];
    for (const section of elementChildren(root)) {
        if (section.tagName !== 'ElementEffects') continue;
        for (const element of elementChildren(section)) {
            if (element.tagName !== 'Element' || element.getAttribute('type') !== 'timing') continue;
            const tt = readTimingEntries(element);
            if (tt) ttracks.push(tt);
        }
    }
    return ttracks;
}

export function readTimingEntries(element: Element): TimingRec | undefined {
    let trec: TimingRec | undefined;
    for (const tlayer of elementChildren(element)) {
        if (tlayer.tagName !== 'EffectLayer') continue;
        const entlist: TimingEnt[] = [];
        let lastetime = 0;
        for (const effect of elementChildren(tlayer)) {
            if (effect.tagName !== 'Effect') continue;
            const st = Number.parseInt(effect.getAttribute('startTime') ?? '');
            const et = Number.parseInt(effect.getAttribute('endTime') ?? '');
            if (!Number.isFinite(st) || !Number.isFinite(et)) continue;
            if (st === et) continue;       // zero length - skip
            if (st < lastetime) continue;  // overlaps (e.g. polyphonic transcription) - skip
            lastetime = et;
            entlist.push(new TimingEnt(effect.getAttribute('label') ?? '', st, et));
        }
        if (!trec) {
            trec = new TimingRec(element.getAttribute('name') ?? '');
            trec.entlist.push(...entlist);
        }
        trec.subentlists.push(entlist);
    }
    return trec;
}
