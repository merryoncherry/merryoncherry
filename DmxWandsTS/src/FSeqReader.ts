// FSEQ / ESEQ reader. Ported from xlAutomation/fseqFile.py and DmxWands/GenerateFloodEffect.py.
// Format reference: https://github.com/FalconChristmas/fpp/blob/master/docs/FSEQ_Sequence_File_Format.txt
//
// Channel numbering: everything in this module is 0-BASED once parsed.
//   - FSEQ v2 sparse ranges are stored 0-based in the file (xLights writes modelStart - 1).
//   - ESEQ stores a 1-based model start channel; it is converted to 0-based here.
//   - Model start channels from the layout are 1-based; use modelChannelBytes() which converts.

import { promises as fs } from 'fs';
import * as zlib from 'zlib';
import { ZSTDDecoder } from 'zstddec';

export interface FSeqCompBlock {
    frameNum: number;
    blockSize: number;
}

/** A contiguous channel range present in the file. `start` is 0-based. */
export interface FSeqChannelRange {
    start: number;
    count: number;
}

export interface FSeqHeader {
    tag: 'PSEQ' | 'FSEQ' | 'ESEQ';
    majver: number;
    minver: number;
    /** Byte offset of the first frame's channel data. */
    chdataOffset: number;
    /** Channel count per frame (as declared). */
    channels: number;
    /** Bytes per frame in the (decompressed) data. */
    stepSize: number;
    frames: number;
    msPerFrame: number;
    /** 0 = none, 1 = zstd, 2 = zlib */
    compression: number;
    blocks: FSeqCompBlock[];
    /** Sparse ranges (0-based). When the file is not sparse this is one range covering everything. */
    ranges: FSeqChannelRange[];
    /** Variable headers, keyed by their 2-char code ("mf" = media file, "sp" = producer, ...). */
    headers: Record<string, string>;
    // ESEQ only
    modelCount: number;
    modelStart: number; // 1-based, as stored
    modelSize: number;
}

export interface FSeqFrame {
    /** Channel data for this frame, laid out per `header.ranges` (ranges concatenated in order). */
    data: Uint8Array;
    frameNum: number;
    timeMs: number;
}

function u16(b: Buffer, o: number): number { return b[o] + b[o + 1] * 256; }
function u24(b: Buffer, o: number): number { return b[o] + b[o + 1] * 256 + b[o + 2] * 65536; }
function u32(b: Buffer, o: number): number { return b[o] + b[o + 1] * 256 + b[o + 2] * 65536 + b[o + 3] * 16777216; }

export class FSeqReader {
    private fd?: fs.FileHandle;
    header?: FSeqHeader;

    constructor(readonly filename: string) {}

    async open(): Promise<void> {
        if (this.fd) throw new Error('Already open');
        this.fd = await fs.open(this.filename, 'r');
    }

    async close(): Promise<void> {
        try {
            await this.fd?.close();
        } catch {
            // ignore
        }
        this.fd = undefined;
    }

    private async readAt(n: number, at: number): Promise<Buffer> {
        if (!this.fd) throw new Error('Not open');
        const buffer = Buffer.alloc(n);
        const { bytesRead } = await this.fd.read(buffer, 0, n, at);
        if (bytesRead !== n) {
            throw new Error(`Short read at ${at}: wanted ${n}, got ${bytesRead}`);
        }
        return buffer;
    }

    async readHeader(): Promise<FSeqHeader> {
        if (!this.fd) throw new Error('Not open');
        const fileSize = (await this.fd.stat()).size;
        const b0 = await this.readAt(Math.min(32, fileSize), 0);
        const tag = b0.toString('latin1', 0, 4);
        if (tag !== 'PSEQ' && tag !== 'FSEQ' && tag !== 'ESEQ') {
            throw new Error(`Not an FSEQ file (tag "${tag}")`);
        }

        const hdr: FSeqHeader = {
            tag,
            majver: 0, minver: 0,
            chdataOffset: 0, channels: 0, stepSize: 0, frames: 0, msPerFrame: 50,
            compression: 0, blocks: [], ranges: [], headers: {},
            modelCount: 0, modelStart: 0, modelSize: 0,
        };

        if (tag === 'ESEQ') {
            // Uncompressed V2 with a custom 20-byte header; no frame count or timing stored.
            hdr.majver = 2;
            hdr.minver = 0;
            hdr.chdataOffset = 20;
            hdr.modelCount = u32(b0, 4);
            hdr.stepSize = u32(b0, 8);
            hdr.modelStart = u32(b0, 12);
            hdr.modelSize = u32(b0, 16);
            hdr.channels = hdr.stepSize;
            if (hdr.stepSize === 0) throw new Error('Invalid ESEQ: zero step size');
            hdr.frames = Math.floor((fileSize - hdr.chdataOffset) / hdr.stepSize);
            hdr.blocks.push({ frameNum: 0, blockSize: hdr.frames * hdr.stepSize });
            // ESEQ files use 1-based start channels; offset to 0-based (matches the FPP/xLights readers).
            hdr.ranges.push({ start: hdr.modelStart > 0 ? hdr.modelStart - 1 : 0, count: hdr.modelSize });
            this.header = hdr;
            return hdr;
        }

        hdr.chdataOffset = u16(b0, 4);
        hdr.minver = b0[6];
        hdr.majver = b0[7];
        const fixedHeaderLen = u16(b0, 8);
        hdr.channels = u32(b0, 10);
        hdr.stepSize = Math.floor((hdr.channels + 3) / 4) * 4;
        hdr.frames = u32(b0, 14);
        hdr.msPerFrame = b0[18];

        const full = await this.readAt(hdr.chdataOffset, 0);

        if (hdr.majver === 1) {
            // V1: no compression, no sparse ranges; data is one big block.
            hdr.blocks.push({ frameNum: 0, blockSize: hdr.frames * hdr.stepSize });
            hdr.ranges.push({ start: 0, count: hdr.channels });
        } else {
            const compAndBlocks = full[20];
            hdr.compression = compAndBlocks & 15;
            let nblocks = (compAndBlocks & 240) * 16;
            nblocks += full[21];
            const nranges = full[22];

            let p = 32;
            let seenEmpty = false;
            for (let i = 0; i < nblocks; ++i) {
                const frameNum = u32(full, p);
                const blockSize = u32(full, p + 4);
                p += 8;
                if (!blockSize) {
                    seenEmpty = true;
                    if (frameNum) {
                        throw new Error(`Empty block (${i}) with frame number (${frameNum}) assigned`);
                    }
                    continue;
                }
                if (seenEmpty) {
                    throw new Error(`Empty blocks followed by nonempty block ${i}`);
                }
                hdr.blocks.push({ frameNum, blockSize });
            }
            for (let i = 0; i < nranges; ++i) {
                hdr.ranges.push({ start: u24(full, p), count: u24(full, p + 3) });
                p += 6;
            }
            if (!hdr.ranges.length) {
                hdr.ranges.push({ start: 0, count: hdr.channels });
            }
            if (!hdr.blocks.length) {
                if (hdr.compression !== 0) {
                    throw new Error('Compressed FSEQ with no compression blocks');
                }
                hdr.blocks.push({ frameNum: 0, blockSize: hdr.frames * hdr.stepSize });
            }

            // Variable-length headers: u16 length (including these 4 bytes), 2-char code, value.
            p = Math.max(p, fixedHeaderLen);
            while (p + 4 <= hdr.chdataOffset) {
                const hlen = u16(full, p) - 4;
                if (hlen < 0 || p + 4 + hlen > hdr.chdataOffset) break;
                const code = full.toString('latin1', p + 2, p + 4);
                let val = full.toString('utf8', p + 4, p + 4 + hlen);
                while (val.length && val.charCodeAt(val.length - 1) === 0) val = val.slice(0, -1);
                hdr.headers[code] = val;
                p += 4 + hlen;
            }
        }

        this.header = hdr;
        return hdr;
    }

    /** Iterate every frame in order. The frame's `data` is a view into a per-block buffer; copy it if you keep it. */
    async forEachFrame(visit: (frame: FSeqFrame) => void): Promise<void> {
        if (!this.fd) throw new Error('Not open');
        const hdr = this.header ?? (await this.readHeader());

        let zstd: ZSTDDecoder | undefined;
        if (hdr.compression === 1) {
            zstd = new ZSTDDecoder();
            await zstd.init();
        } else if (hdr.compression !== 0 && hdr.compression !== 2) {
            throw new Error(`Unknown FSEQ compression type ${hdr.compression}`);
        }

        let curFrame = 0;
        let curMs = 0;
        let fileOffset = hdr.chdataOffset;

        for (let bi = 0; bi < hdr.blocks.length; ++bi) {
            const blk = hdr.blocks[bi];
            if (blk.frameNum !== curFrame) {
                throw new Error(`Unexpected start frame ${blk.frameNum} vs ${curFrame} (block ${bi}/${hdr.blocks.length})`);
            }
            const framesInBlock = (bi + 1 < hdr.blocks.length ? hdr.blocks[bi + 1].frameNum : hdr.frames) - curFrame;
            const expectedLen = framesInBlock * hdr.stepSize;

            const raw = await this.readAt(blk.blockSize, fileOffset);
            fileOffset += blk.blockSize;

            let data: Uint8Array;
            if (hdr.compression === 1) {
                data = zstd!.decode(new Uint8Array(raw.buffer, raw.byteOffset, raw.byteLength), expectedLen);
            } else if (hdr.compression === 2) {
                data = zlib.inflateSync(raw);
            } else {
                data = new Uint8Array(raw.buffer, raw.byteOffset, raw.byteLength);
            }

            let off = 0;
            while (off + hdr.stepSize <= data.length && curFrame < hdr.frames) {
                visit({ data: data.subarray(off, off + hdr.stepSize), frameNum: curFrame, timeMs: curMs });
                off += hdr.stepSize;
                ++curFrame;
                curMs += hdr.msPerFrame;
            }
            if (off !== data.length && curFrame < hdr.frames) {
                throw new Error(`Partial frame in block ${bi}: ${data.length - off} leftover bytes`);
            }
        }
        if (curFrame !== hdr.frames) {
            throw new Error(`Frame count mismatch: read ${curFrame}, header says ${hdr.frames}`);
        }
    }
}

/**
 * Slice a model's channels out of a frame. `startChannel` is the layout's
 * 1-based start channel. Returns undefined if the file does not contain the
 * whole model (sparse file without it).
 */
export function modelChannelBytes(frame: Uint8Array, hdr: FSeqHeader, startChannel: number, count: number): Uint8Array | undefined {
    const s0 = startChannel - 1; // 0-based
    const e0 = s0 + count;       // exclusive
    let off = 0;
    for (const rng of hdr.ranges) {
        if (s0 >= rng.start && e0 <= rng.start + rng.count) {
            const from = off + (s0 - rng.start);
            const to = Math.min(from + count, frame.length);
            return frame.subarray(from, to);
        }
        off += rng.count;
    }
    return undefined;
}

/** Just the header, without keeping the file open. */
export async function readFSeqHeader(file: string): Promise<FSeqHeader> {
    const r = new FSeqReader(file);
    try {
        await r.open();
        return await r.readHeader();
    } finally {
        await r.close();
    }
}
