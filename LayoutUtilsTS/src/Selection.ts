// Selecting models, groups, and view objects with the pyLayout selector language.
//
//   Model=<regex>        models whose name matches (anchored at the start, like Python re.match)
//   Group=<regex>        model groups whose name matches
//   InGroup=<regex>      everything inside the matching groups: member models, nested groups (recursively)
//   Obj=<regex>          view objects whose name matches
//   Type=<type>          Model / Group / Obj, or a DisplayAs value ("Arches", "Tree 360", "Tree", "Image", ...)
//   TagColour=<value>    models and groups with that TagColour (TagColor also accepted)
//   InactiveModel        models with Active="0"
//   InactiveObj          view objects with Active="0"

import { getBaseDisplayAs } from 'xllayoutcalcs';
import { attr, groupElements, modelElements, splitNameList, viewObjectElements } from './LayoutDoc';

export interface Selection {
    models: Map<string, Element>;
    groups: Map<string, Element>;
    objs: Map<string, Element>;
}

export interface Selector {
    type: string;
    value: string;
}

export function parseSelector(text: string): Selector {
    const eq = text.indexOf('=');
    if (eq < 0) return { type: text.trim().toLowerCase(), value: '' };
    return { type: text.slice(0, eq).trim().toLowerCase(), value: text.slice(eq + 1).trim() };
}

/** Python's re.match semantics: the pattern must match at the start of the name. */
function anchored(pattern: string): RegExp {
    return new RegExp(`^(?:${pattern})`);
}

function displayAsMatches(el: Element, want: string): boolean {
    const da = attr(el, 'DisplayAs');
    const w = want.toLowerCase();
    return da.toLowerCase() === w || getBaseDisplayAs(da).toLowerCase() === w;
}

export function select(doc: Document, selector: Selector | string): Selection {
    const sel = typeof selector === 'string' ? parseSelector(selector) : selector;
    const result: Selection = { models: new Map(), groups: new Map(), objs: new Map() };
    const models = modelElements(doc);
    const groups = groupElements(doc);
    const objs = viewObjectElements(doc);
    const modelByName = new Map(models.map((m) => [attr(m, 'name'), m]));
    const groupByName = new Map(groups.map((g) => [attr(g, 'name'), g]));

    const rx = sel.value ? anchored(sel.value) : undefined;
    const type = sel.type;
    const val = sel.value.toLowerCase();

    switch (type) {
        case 'type':
            if (val === 'group') for (const g of groups) result.groups.set(attr(g, 'name'), g);
            if (val === 'model') for (const m of models) result.models.set(attr(m, 'name'), m);
            if (val === 'obj') for (const o of objs) result.objs.set(attr(o, 'name'), o);
            for (const m of models) if (displayAsMatches(m, sel.value)) result.models.set(attr(m, 'name'), m);
            for (const o of objs) if (displayAsMatches(o, sel.value)) result.objs.set(attr(o, 'name'), o);
            break;
        case 'model':
            for (const m of models) if (rx && rx.test(attr(m, 'name'))) result.models.set(attr(m, 'name'), m);
            break;
        case 'group':
            for (const g of groups) if (rx && rx.test(attr(g, 'name'))) result.groups.set(attr(g, 'name'), g);
            break;
        case 'obj':
            for (const o of objs) if (rx && rx.test(attr(o, 'name'))) result.objs.set(attr(o, 'name'), o);
            break;
        case 'ingroup': {
            // Members of the matching groups, following nested groups.
            const pending: string[] = [];
            const seen = new Set<string>();
            for (const g of groups) {
                if (rx && rx.test(attr(g, 'name'))) {
                    for (const n of splitNameList(attr(g, 'models'))) pending.push(n.split('/')[0]);
                }
            }
            while (pending.length) {
                const n = pending.pop()!;
                if (seen.has(n)) continue;
                seen.add(n);
                const m = modelByName.get(n);
                if (m) {
                    result.models.set(n, m);
                    continue;
                }
                const g = groupByName.get(n);
                if (g) {
                    result.groups.set(n, g);
                    for (const mem of splitNameList(attr(g, 'models'))) pending.push(mem.split('/')[0]);
                }
            }
            break;
        }
        case 'inactivemodel':
            for (const m of models) if (attr(m, 'Active') === '0') result.models.set(attr(m, 'name'), m);
            break;
        case 'inactiveobj':
            for (const o of objs) if (attr(o, 'Active') === '0') result.objs.set(attr(o, 'name'), o);
            break;
        case 'tagcolour':
        case 'tagcolor':
            for (const m of models) if (attr(m, 'TagColour') === sel.value) result.models.set(attr(m, 'name'), m);
            for (const g of groups) if (attr(g, 'TagColour') === sel.value) result.groups.set(attr(g, 'name'), g);
            break;
        default:
            throw new Error(`Unknown selector "${sel.type}" (expected Model, Group, InGroup, Obj, Type, TagColour, InactiveModel, InactiveObj)`);
    }
    return result;
}

export function selectionSize(s: Selection): number {
    return s.models.size + s.groups.size + s.objs.size;
}
