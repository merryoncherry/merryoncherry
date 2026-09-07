// Loading, saving, and walking an xlights_rgbeffects.xml document.
// Ported from LayoutUtils/pyLayout.py (TextRemover, ValidNameBuilder, GroupMemberChecker, output).

import * as fs from 'fs';
import { DOMParser } from '@xmldom/xmldom';

export function loadLayout(filePath: string): Document {
    const text = fs.readFileSync(filePath, 'utf8');
    const doc = new DOMParser().parseFromString(text, 'text/xml') as unknown as Document;
    if (!doc.documentElement || doc.documentElement.tagName !== 'xrgb') {
        throw new Error(`${filePath}: root element is not <xrgb>`);
    }
    return doc;
}

/** Element children, optionally filtered by tag. */
export function childElements(parent: Node, tag?: string): Element[] {
    const out: Element[] = [];
    for (let i = 0; i < parent.childNodes.length; ++i) {
        const k = parent.childNodes[i];
        if (k.nodeType === 1 && (!tag || (k as Element).tagName === tag)) out.push(k as Element);
    }
    return out;
}

/** First child element with the tag, or undefined. */
export function childElement(parent: Node, tag: string): Element | undefined {
    return childElements(parent, tag)[0];
}

/** Attribute value, or '' when absent (xmldom returns '' or null depending on version). */
export function attr(el: Element, name: string): string {
    return el.getAttribute(name) ?? '';
}

export function numAttr(el: Element, name: string, def: number): number {
    const v = attr(el, name);
    if (!v) return def;
    const n = Number.parseFloat(v);
    return Number.isFinite(n) ? n : def;
}

/** The layout sections, each possibly absent. */
export function sections(doc: Document): { models?: Element; modelGroups?: Element; viewObjects?: Element; views?: Element } {
    const root = doc.documentElement;
    return {
        models: childElement(root, 'models'),
        modelGroups: childElement(root, 'modelGroups'),
        viewObjects: childElement(root, 'view_objects'),
        views: childElement(root, 'views'),
    };
}

export function modelElements(doc: Document): Element[] {
    const s = sections(doc);
    return s.models ? childElements(s.models, 'model') : [];
}

export function groupElements(doc: Document): Element[] {
    const s = sections(doc);
    return s.modelGroups ? childElements(s.modelGroups, 'modelGroup') : [];
}

export function viewObjectElements(doc: Document): Element[] {
    const s = sections(doc);
    return s.viewObjects ? childElements(s.viewObjects, 'view_object') : [];
}

export function viewElements(doc: Document): Element[] {
    const s = sections(doc);
    return s.views ? childElements(s.views, 'view') : [];
}

/** Split a `models="a,b,Model/Sub"` list. */
export function splitNameList(list: string): string[] {
    return list.split(',').map((s) => s.trim()).filter((s) => s.length);
}

/** Every name a group or view may legitimately reference: models, groups, and "Model/Submodel". */
export function validNames(doc: Document): Set<string> {
    const names = new Set<string>();
    for (const g of groupElements(doc)) names.add(attr(g, 'name'));
    for (const m of modelElements(doc)) {
        const mn = attr(m, 'name');
        names.add(mn);
        for (const sm of childElements(m, 'subModel')) names.add(`${mn}/${attr(sm, 'name')}`);
    }
    return names;
}

/** Warnings for group / view members that do not exist. */
export function checkReferences(doc: Document): string[] {
    const names = validNames(doc);
    const warnings: string[] = [];
    for (const g of groupElements(doc)) {
        for (const n of splitNameList(attr(g, 'models'))) {
            if (!names.has(n)) warnings.push(`group '${attr(g, 'name')}' contains reference to '${n}', which does not exist`);
        }
    }
    for (const v of viewElements(doc)) {
        for (const n of splitNameList(attr(v, 'models'))) {
            if (!names.has(n)) warnings.push(`view '${attr(v, 'name')}' contains reference to '${n}', which does not exist`);
        }
    }
    return warnings;
}

// ---------------------------------------------------------------------------
// Output

function escapeText(s: string): string {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function escapeAttr(s: string): string {
    return escapeText(s)
        .replace(/"/g, '&quot;')
        .replace(/\r/g, '&#13;')
        .replace(/\n/g, '&#10;')
        .replace(/\t/g, '&#9;');
}

/** Pretty printer with 2-space indents, the way xLights writes the file; whitespace-only text is dropped. */
function serializeElement(el: Element, depth: number, out: string[]): void {
    const pad = '  '.repeat(depth);
    let attrs = '';
    for (let i = 0; i < el.attributes.length; ++i) {
        const a = el.attributes[i];
        attrs += ` ${a.name}="${escapeAttr(a.value)}"`;
    }
    const kids: Element[] = [];
    let text = '';
    for (let i = 0; i < el.childNodes.length; ++i) {
        const k = el.childNodes[i];
        if (k.nodeType === 1) kids.push(k as Element);
        else if (k.nodeType === 3 || k.nodeType === 4) text += k.nodeValue ?? '';
    }
    if (kids.length) {
        if (text.trim().length) {
            throw new Error(`<${el.tagName}> mixes text and child elements; cannot pretty-print`);
        }
        out.push(`${pad}<${el.tagName}${attrs}>`);
        for (const k of kids) serializeElement(k, depth + 1, out);
        out.push(`${pad}</${el.tagName}>`);
    } else if (text.trim().length) {
        out.push(`${pad}<${el.tagName}${attrs}>${escapeText(text)}</${el.tagName}>`);
    } else {
        out.push(`${pad}<${el.tagName}${attrs}/>`);
    }
}

export function serializeLayout(doc: Document): string {
    const out: string[] = ['<?xml version="1.0" encoding="UTF-8"?>'];
    serializeElement(doc.documentElement, 0, out);
    return out.join('\n') + '\n';
}

export function saveLayout(filePath: string, doc: Document): void {
    fs.writeFileSync(filePath, serializeLayout(doc), 'utf8');
}
