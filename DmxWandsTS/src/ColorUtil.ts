// Color helpers. Ported from DmxWands/GenerateFloodEffect.py (rgb_to_hsv / hsv_to_rgb).

export type RGB = [number, number, number];

/**
 * Per-model lookup table: raw 0-255 channel byte -> 0..1 linear value with the
 * model's dimming curve (brightness, gamma) undone. Building this once per
 * model replaces a Math.pow() per channel per pixel per frame.
 */
export function makeInverseDimmingLut(gamma: number, brightness: number): Float32Array {
    const invgamma = 1.0 / (gamma > 0 ? gamma : 1.0);
    const invbright = 1.0 / (brightness > 0 ? brightness : 1.0);
    const lut = new Float32Array(256);
    for (let i = 0; i < 256; ++i) {
        lut[i] = Math.min(1.0, Math.pow((i * invbright) / 255.0, invgamma));
    }
    return lut;
}

/**
 * H in the range [0, 360), S and V in the range [0, 1].
 * Inverts the gamma/brightness correction as part of the calculation.
 * (Reference implementation; the histogram uses the LUT + inline math for speed.)
 */
export function rgbToHsv(r: number, g: number, b: number, invgamma: number, invbright: number): [number, number, number] {
    r = Math.min(1.0, Math.pow((r * invbright) / 255.0, invgamma));
    g = Math.min(1.0, Math.pow((g * invbright) / 255.0, invgamma));
    b = Math.min(1.0, Math.pow((b * invbright) / 255.0, invgamma));
    return linearRgbToHsv(r, g, b);
}

/** r, g, b already linear 0..1. Returns [H 0..360, S 0..1, V 0..1]. */
export function linearRgbToHsv(r: number, g: number, b: number): [number, number, number] {
    const M = Math.max(r, g, b);
    const m = Math.min(r, g, b);
    const C = M - m;

    let H = 0;
    if (C !== 0) {
        if (M === r) {
            H = (60 * ((g - b) / C) + 360) % 360;
        } else if (M === g) {
            H = (60 * ((b - r) / C) + 120) % 360;
        } else {
            H = (60 * ((r - g) / C) + 240) % 360;
        }
    }
    const S = M === 0 ? 0 : C / M;
    return [H, S, M];
}

/** H 0..360; S and V are 0-100. Returns 0-255 integer RGB. Out-of-range S/V are clamped. */
export function hsvToRgb(h: number, s: number, v: number): RGB {
    s = Math.min(1.0, Math.max(0.0, s / 100.0));
    v = Math.min(1.0, Math.max(0.0, v / 100.0));
    h = ((h % 360) + 360) % 360;

    let r: number, g: number, b: number;
    if (s === 0) {
        r = g = b = v;
    } else {
        h /= 60.0; // sector 0 to 5
        const i = Math.floor(h);
        const f = h - i;
        const p = v * (1 - s);
        const q = v * (1 - s * f);
        const t = v * (1 - s * (1 - f));
        switch (i) {
            case 0: r = v; g = t; b = p; break;
            case 1: r = q; g = v; b = p; break;
            case 2: r = p; g = v; b = t; break;
            case 3: r = p; g = q; b = v; break;
            case 4: r = t; g = p; b = v; break;
            default: r = v; g = p; b = q; break;
        }
    }
    return [Math.floor(r * 255), Math.floor(g * 255), Math.floor(b * 255)];
}

export function toHex2(value: number): string {
    return Math.max(0, Math.min(255, Math.round(value))).toString(16).padStart(2, '0').toUpperCase();
}

export function rgbToHexString(rgb: RGB): string {
    return `#${toHex2(rgb[0])}${toHex2(rgb[1])}${toHex2(rgb[2])}`;
}
