// Writes a v2 sparse FSEQ the way xLights "Export Model -> FPP Compressed Sub sequence" does:
// one zstd-compressed block, one sparse range, channel count == range length (no padding to 4).
// Usage: node make-sparse-fseq.js <out.fseq> [channels=150] [frames=200] [startChannel1Based=5001]
// Needs Node >= 22.15 (built-in zstd).
const fs = require('fs');
const zlib = require('zlib');

const [out, chArg, frArg, stArg] = process.argv.slice(2);
if (!out) { console.error('usage: node make-sparse-fseq.js <out.fseq> [channels] [frames] [startChannel]'); process.exit(1); }
const channels = Number(chArg ?? 150);      // NOT a multiple of 4 -> triggers the bug
const frames = Number(frArg ?? 200);
const start0 = Number(stArg ?? 5001) - 1;   // stored 0-based

// Frame data: channel i of frame f = (f + i) & 255, so misalignment is visible.
const raw = Buffer.alloc(channels * frames);
for (let f = 0; f < frames; ++f)
    for (let i = 0; i < channels; ++i) raw[f * channels + i] = (f + i) & 255;
const block = zlib.zstdCompressSync(raw);

const fixedLen = 32;
const nblocks = 1, nranges = 1;
let hdrLen = fixedLen + nblocks * 8 + nranges * 6;
const chdata = Math.ceil(hdrLen / 4) * 4;
const h = Buffer.alloc(chdata);
h.write('PSEQ', 0, 'latin1');
h.writeUInt16LE(chdata, 4);
h[6] = 0; h[7] = 2;                 // v2.0
h.writeUInt16LE(fixedLen, 8);
h.writeUInt32LE(channels, 10);      // sum of sparse range lengths, exactly as FPP/xLights write it
h.writeUInt32LE(frames, 14);
h[18] = 50;                         // ms per frame
h[20] = 1;                          // zstd, high bits of block count = 0
h[21] = nblocks;
h[22] = nranges;
let p = 32;
h.writeUInt32LE(0, p); h.writeUInt32LE(block.length, p + 4); p += 8;
h.writeUIntLE(start0, p, 3); h.writeUIntLE(channels, p + 3, 3);
fs.writeFileSync(out, Buffer.concat([h, block]));
console.log(`wrote ${out}: ${channels} channels @ start ${start0 + 1}, ${frames} frames, zstd block ${block.length} bytes`);
