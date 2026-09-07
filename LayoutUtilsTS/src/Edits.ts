// Bulk edits: <selection>:<action>:<arguments>, separated by ';'.
// Ported from LayoutUtils/pyLayout.py (main edit loop, Deleter), plus per-selection transforms.
//
//   active:<true/false>            set the Active flag on models and objects
//   brighten:<percent>             appearance brightness (objects: Brightness x pct; models: ModelBrightness on the 100% scale)
//   darken:<percent>               same as brighten
//   setbrightness:<value>          set the appearance brightness directly
//   dimcurveall:<brightness,gamma> dimming curve for all colors (brightness is -100..100)
//   dimcurvergb:<rb,rg,gb,gg,bb,bg> per-color dimming curve
//   delete:true                    remove the selection, and every reference to it in groups and views
//   translate:<x,y,z>              move the selected models / objects
//   scale:<x,y,z>                  scale about the world origin
//   rotx:<deg> roty:<deg> rotz:<deg>  rotate about the world origin
//   transform:<steps>              several transform steps separated by '|', e.g. transform:roty:30|translate:0,0,-300

import { composeTransform, PlacementTransformResult, transformPlacementElement } from 'xllayoutcalcs';
import { attr, groupElements, numAttr, splitNameList, viewElements, childElements } from './LayoutDoc';
import { select, Selection, selectionSize } from './Selection';
import { parseTransformSteps } from './Transform';

export interface Edit {
    selector: string;
    command: string;
    arg: string;
}

export function parseEdits(spec: string): Edit[] {
    const edits: Edit[] = [];
    for (const raw of spec.split(';')) {
        const item = raw.trim();
        if (!item) continue;
        const parts = item.split(':');
        if (parts.length < 3) throw new Error(`edit is a list of select:command:arg, but found: ${item}`);
        edits.push({ selector: parts[0].trim(), command: parts[1].trim().toLowerCase(), arg: parts.slice(2).join(':').trim() });
    }
    return edits;
}

function isTrue(arg: string): boolean {
    const a = arg.trim().toLowerCase();
    return a === '1' || a.startsWith('t') || a.startsWith('y');
}

function setDimmingCurve(doc: Document, model: Element, curves: { tag: string; brightness: string; gamma: string }[]): void {
    for (const dc of childElements(model, 'dimmingCurve')) model.removeChild(dc);
    const ndc = doc.createElement('dimmingCurve');
    for (const c of curves) {
        const e = doc.createElement(c.tag);
        e.setAttribute('brightness', c.brightness);
        e.setAttribute('gamma', c.gamma);
        ndc.appendChild(e);
    }
    model.appendChild(ndc);
}

/** Remove the selection and prune references to it from groups and views. */
function deleteSelection(doc: Document, sel: Selection): { removed: number; pruned: number } {
    const gone = new Set<string>([...sel.models.keys(), ...sel.groups.keys(), ...sel.objs.keys()]);
    let removed = 0;
    for (const el of [...sel.models.values(), ...sel.groups.values(), ...sel.objs.values()]) {
        el.parentNode?.removeChild(el);
        ++removed;
    }
    let pruned = 0;
    const pruneList = (el: Element): void => {
        const before = splitNameList(attr(el, 'models'));
        const after = before.filter((n) => !gone.has(n.split('/')[0]));
        if (after.length !== before.length) {
            el.setAttribute('models', after.join(','));
            pruned += before.length - after.length;
        }
    };
    for (const g of groupElements(doc)) pruneList(g);
    for (const v of viewElements(doc)) pruneList(v);
    return { removed, pruned };
}

export interface EditReport {
    edit: Edit;
    selected: number;
    changed: number;
    notes: string[];
}

export function applyEdit(doc: Document, edit: Edit): EditReport {
    const sel = select(doc, edit.selector);
    const report: EditReport = { edit, selected: selectionSize(sel), changed: 0, notes: [] };
    const targets = [...sel.models.values(), ...sel.objs.values()];

    switch (edit.command) {
        case 'brighten':
        case 'darken': {
            const pct = Number.parseFloat(edit.arg);
            if (!Number.isFinite(pct)) throw new Error(`${edit.command} takes a percentage`);
            for (const o of sel.objs.values()) {
                o.setAttribute('Brightness', `${(numAttr(o, 'Brightness', 100) * pct) / 100}`);
                ++report.changed;
            }
            for (const m of sel.models.values()) {
                // xLights model appearance brightness is an adjustment on a 100% base (-100..100).
                const cur = 100 + numAttr(m, 'ModelBrightness', 0);
                const next = Math.max(-100, Math.min(100, Math.round((cur * pct) / 100 - 100)));
                m.setAttribute('ModelBrightness', `${next}`);
                ++report.changed;
            }
            break;
        }
        case 'setbrightness': {
            const v = Number.parseFloat(edit.arg);
            if (!Number.isFinite(v)) throw new Error('setbrightness takes a number');
            for (const o of sel.objs.values()) { o.setAttribute('Brightness', `${v}`); ++report.changed; }
            for (const m of sel.models.values()) { m.setAttribute('ModelBrightness', `${Math.round(v)}`); ++report.changed; }
            break;
        }
        case 'dimcurveall': {
            const p = edit.arg.split(',').map((s) => s.trim());
            if (p.length !== 2) throw new Error('dimcurveall requires brightness,gamma');
            for (const m of sel.models.values()) {
                setDimmingCurve(doc, m, [{ tag: 'all', brightness: p[0], gamma: p[1] }]);
                ++report.changed;
            }
            break;
        }
        case 'dimcurvergb': {
            const p = edit.arg.split(',').map((s) => s.trim());
            if (p.length !== 6) throw new Error('dimcurvergb requires brightness,gamma x3 (r,g,b)');
            for (const m of sel.models.values()) {
                setDimmingCurve(doc, m, [
                    { tag: 'red', brightness: p[0], gamma: p[1] },
                    { tag: 'green', brightness: p[2], gamma: p[3] },
                    { tag: 'blue', brightness: p[4], gamma: p[5] },
                ]);
                ++report.changed;
            }
            break;
        }
        case 'active': {
            const v = isTrue(edit.arg) ? '1' : '0';
            for (const el of targets) { el.setAttribute('Active', v); ++report.changed; }
            break;
        }
        case 'delete': {
            if (!isTrue(edit.arg)) break;
            const r = deleteSelection(doc, sel);
            report.changed = r.removed;
            if (r.pruned) report.notes.push(`${r.pruned} group/view references pruned`);
            break;
        }
        case 'translate':
        case 'scale':
        case 'rotx':
        case 'roty':
        case 'rotz':
        case 'transform': {
            const spec = edit.command === 'transform' ? edit.arg : `${edit.command}:${edit.arg}`;
            const m = composeTransform(parseTransformSteps(spec, '|'));
            const res: PlacementTransformResult = { modelsTransformed: 0, viewObjectsTransformed: 0, skipped: [], warnings: [] };
            for (const el of targets) {
                if (transformPlacementElement(el, m, { includeGridlines: true }, res)) ++report.changed;
            }
            for (const s of res.skipped) report.notes.push(`skipped ${s.name}: ${s.reason}`);
            for (const w of res.warnings) report.notes.push(w);
            break;
        }
        default:
            throw new Error(`Unknown edit action "${edit.command}"`);
    }
    return report;
}
