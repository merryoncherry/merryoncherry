// Parsing the pyLayout transform language into an affine matrix.
//
//   translate:<x,y,z>   scale:<x,y,z>   rotx:<deg>   roty:<deg>   rotz:<deg>
//
// Steps are separated by ';' (or '|' inside an edit) and applied in the order
// written, each about the world origin.

import { composeTransform, Mat4, TransformStep, Vec3 } from 'xllayoutcalcs';

function vec3(text: string, what: string): Vec3 {
    const parts = text.split(',').map((s) => Number.parseFloat(s.trim()));
    if (parts.length !== 3 || parts.some((n) => !Number.isFinite(n))) {
        throw new Error(`${what} takes x,y,z but found: ${text}`);
    }
    return [parts[0], parts[1], parts[2]];
}

function num(text: string, what: string): number {
    const n = Number.parseFloat(text.trim());
    if (!Number.isFinite(n)) throw new Error(`${what} takes a number but found: ${text}`);
    return n;
}

export function parseTransformSteps(spec: string, separator = ';'): TransformStep[] {
    const steps: TransformStep[] = [];
    for (const raw of spec.split(separator)) {
        const item = raw.trim();
        if (!item) continue;
        const colon = item.indexOf(':');
        if (colon < 0) throw new Error(`transform is a list of command:arguments, but found: ${item}`);
        const cmd = item.slice(0, colon).trim().toLowerCase();
        const arg = item.slice(colon + 1).trim();
        switch (cmd) {
            case 'translate': steps.push({ translate: vec3(arg, 'translate') }); break;
            case 'scale': steps.push({ scale: vec3(arg, 'scale') }); break;
            case 'rotx': steps.push({ rotate: { axis: 'x', degrees: num(arg, 'rotx') } }); break;
            case 'roty': steps.push({ rotate: { axis: 'y', degrees: num(arg, 'roty') } }); break;
            case 'rotz': steps.push({ rotate: { axis: 'z', degrees: num(arg, 'rotz') } }); break;
            default: throw new Error(`Not a valid transform command: ${cmd} (use translate, scale, rotx, roty, rotz)`);
        }
    }
    return steps;
}

export function transformMatrix(spec: string, separator = ';'): Mat4 {
    return composeTransform(parseTransformSteps(spec, separator));
}
