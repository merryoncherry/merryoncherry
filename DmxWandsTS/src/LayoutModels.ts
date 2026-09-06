// Layout access. All channel / color-order / dimming work is delegated to
// xlLayoutCalcs, which reads both the legacy and current xLights layout
// formats natively and resolves every StartChannel form (!controller, #universe, >model, @model).

import * as fs from 'fs';
import * as path from 'path';
import { DOMParser } from '@xmldom/xmldom';
import { getControllersAndModelChannels, type ControllersAndModelChannels, type XlModelChannelInfo } from 'xllayoutcalcs';
import { ColorSourceModel } from './ColorSummary';

export interface ShowLayout {
    showDir: string;
    channels: ControllersAndModelChannels;
    byName: Map<string, XlModelChannelInfo>;
    /** Model group name -> member names (models, "Model/Submodel", or other groups), as written in the layout. */
    groups: Map<string, string[]>;
}

export function loadXmlFile(filePath: string): Document {
    const text = fs.readFileSync(filePath, 'utf8');
    return new DOMParser().parseFromString(text, 'text/xml') as unknown as Document;
}

function childElements(el: Element | Document, tag: string): Element[] {
    const out: Element[] = [];
    const kids = el.childNodes;
    for (let i = 0; i < kids.length; ++i) {
        const k = kids[i];
        if (k.nodeType === 1 && (k as Element).tagName === tag) out.push(k as Element);
    }
    return out;
}

function readModelGroups(rgb: Document): Map<string, string[]> {
    const groups = new Map<string, string[]>();
    const root = rgb.documentElement;
    if (!root) return groups;
    for (const mgs of childElements(root, 'modelGroups')) {
        for (const mg of childElements(mgs, 'modelGroup')) {
            const name = mg.getAttribute('name') ?? '';
            if (!name) continue;
            const models = (mg.getAttribute('models') ?? '').split(',').map((s) => s.trim()).filter((s) => s.length);
            groups.set(name, models);
        }
    }
    return groups;
}

export function loadShowLayout(showDir: string, log: (msg: string) => void = () => {}): ShowLayout {
    const rgbPath = path.join(showDir, 'xlights_rgbeffects.xml');
    const netPath = path.join(showDir, 'xlights_networks.xml');
    if (!fs.existsSync(rgbPath)) throw new Error(`Missing ${rgbPath}`);
    if (!fs.existsSync(netPath)) throw new Error(`Missing ${netPath}`);
    const rgb = loadXmlFile(rgbPath);
    const net = loadXmlFile(netPath);
    const channels = getControllersAndModelChannels(rgb, net, { logger: log });
    const byName = new Map<string, XlModelChannelInfo>();
    for (const m of channels.models) byName.set(m.name, m);
    return { showDir, channels, byName, groups: readModelGroups(rgb) };
}

/** True when the model is a plain 3-channel RGB-order pixel model we can read colors from. */
export function isColorSource(m: XlModelChannelInfo): boolean {
    return m.simple && m.channelCount >= 3;
}

export function toColorSourceModel(m: XlModelChannelInfo): ColorSourceModel {
    return {
        name: m.name,
        startChannel: m.startChannel,
        channelCount: m.channelCount,
        rOff: m.rgbOffsets.r,
        gOff: m.rgbOffsets.g,
        bOff: m.rgbOffsets.b,
        gamma: m.gamma,
        brightness: m.brightness,
    };
}

export interface SourceResolution {
    models: ColorSourceModel[];
    /** Names that are neither a model nor a group. */
    missing: string[];
    /** Models that were named (directly or via a group) but are not RGB pixel models. */
    notRgb: string[];
}

/**
 * Turn a user list of names into color source models. Names may be models,
 * model groups (expanded recursively), or "Model/Submodel" (the whole model is used).
 */
export function resolveSourceModels(names: string[], layout: ShowLayout): SourceResolution {
    const picked = new Map<string, ColorSourceModel>();
    const missing: string[] = [];
    const notRgb: string[] = [];
    const seenGroups = new Set<string>();

    const visit = (rawName: string): void => {
        const name = rawName.trim();
        if (!name) return;
        const base = name.includes('/') ? name.slice(0, name.indexOf('/')) : name;
        const m = layout.byName.get(base);
        if (m) {
            if (isColorSource(m)) {
                if (!picked.has(m.name)) picked.set(m.name, toColorSourceModel(m));
            } else if (!notRgb.includes(m.name)) {
                notRgb.push(m.name);
            }
            return;
        }
        const grp = layout.groups.get(name);
        if (grp) {
            if (seenGroups.has(name)) return;
            seenGroups.add(name);
            for (const member of grp) visit(member);
            return;
        }
        missing.push(name);
    };
    for (const n of names) visit(n);
    return { models: [...picked.values()], missing, notRgb };
}

/** Every RGB pixel model in the layout except the excluded names. */
export function defaultSourceModels(layout: ShowLayout, exclude: Iterable<string> = []): ColorSourceModel[] {
    const ex = new Set(exclude);
    return layout.channels.models.filter((m) => isColorSource(m) && !ex.has(m.name)).map(toColorSourceModel);
}
