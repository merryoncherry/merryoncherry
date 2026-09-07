#!/usr/bin/env node
// xLights layout file processing, for bulk editing and transforming layout
// elements in ways that are tough to accomplish with xLights by itself.
//
// Revamp of LayoutUtils/pyLayout.py in TypeScript. Placement math (3D
// transforms of every model type) and format conversion come from xlLayoutCalcs.
//
// Order of operations:
//   read --layout  ->  --transform (whole layout)  ->  --edit (selections)  ->  --outformat  ->  write --outlayout

import * as fs from 'fs';
import * as path from 'path';
import { Command } from 'commander';
import { identifyXml, migrateToFormat, transformLayoutPlacement, TargetFormat } from 'xllayoutcalcs';
import { applyEdit, parseEdits } from './Edits';
import { checkReferences, loadLayout, modelElements, groupElements, viewObjectElements, saveLayout } from './LayoutDoc';
import { transformMatrix } from './Transform';

interface CliOptions {
    layout: string;
    outlayout?: string;
    transform?: string;
    edit?: string;
    outformat: string;
    presets?: string;
    gridlines: boolean;
    respectlocked: boolean;
    check: boolean;
    quiet: boolean;
}

const program = new Command();
program
    .name('xllayout')
    .description(
        'xLights layout file processing: 3D transforms, bulk edits, and format conversion of xlights_rgbeffects.xml.\n\n' +
        'Transform: semicolon-delimited steps applied in order about the world origin:\n' +
        '    translate:<x,y,z>  scale:<x,y,z>  rotx:<deg>  roty:<deg>  rotz:<deg>\n\n' +
        'Edits: semicolon-delimited <selection>:<action>:<arguments>.\n' +
        '  selection: Model=<regex> | Group=<regex> | InGroup=<regex> | Obj=<regex> | Type=<Model|Group|Obj|DisplayAs>\n' +
        '             | TagColour=<value> | InactiveModel | InactiveObj      (regexes match at the start of the name)\n' +
        '  action:    active:<true/false> | brighten:<percent> | darken:<percent> | setbrightness:<value>\n' +
        '             | dimcurveall:<brightness,gamma> | dimcurvergb:<rb,rg,gb,gg,bb,bg> | delete:true\n' +
        '             | translate:<x,y,z> | scale:<x,y,z> | rotx:<deg> | roty:<deg> | rotz:<deg> | transform:<step|step...>\n\n' +
        'Not all operations leave the layout consistent, and xlights_networks.xml is not touched. Keep backups.',
    )
    .requiredOption('--layout <file>', 'xlights_rgbeffects.xml input file')
    .option('--outlayout <file>', 'xlights_rgbeffects.xml output (omit for a dry run)')
    .option('--transform <spec>', 'Whole-layout 3D transform steps (see above)')
    .option('--edit <spec>', 'Edits to make (see above)')
    .option('--outformat <fmt>', 'Output layout format: keep (as input), x2026_2 (pre-2026.3 xLights), x2026_3 (2026.3+), x2026_15 (2026.15+)', 'keep')
    .option('--presets <file>', 'xlights_effectpresets.json to embed when converting to x2026_2 (default: next to --layout)')
    .option('--gridlines', 'Also transform Gridlines view objects', false)
    .option('--respectlocked', 'Leave Locked models and objects where they are', false)
    .option('--check', 'Report group/view references that do not exist (always done; this only exits afterwards)', false)
    .option('--quiet', 'Less output', false);

function main(): number {
    program.parse(process.argv);
    const opts = program.opts<CliOptions>();
    const say = (msg: string): void => {
        if (!opts.quiet) console.log(msg);
    };

    say(`Reading ${opts.layout}`);
    const doc = loadLayout(opts.layout);
    const id = identifyXml(doc);
    say(`  format ${id.format}: ${modelElements(doc).length} models, ${groupElements(doc).length} groups, ${viewObjectElements(doc).length} view objects`);

    for (const w of checkReferences(doc)) console.warn(`WARNING: ${w}`);
    if (opts.check) return 0;

    if (opts.transform) {
        const m = transformMatrix(opts.transform);
        const res = transformLayoutPlacement(doc, m, {
            includeGridlines: opts.gridlines,
            respectLocked: opts.respectlocked,
            logger: (msg) => console.warn(msg),
        });
        say(`Transform "${opts.transform}": ${res.modelsTransformed} models and ${res.viewObjectsTransformed} view objects moved` +
            (res.skipped.length ? `, ${res.skipped.length} skipped` : ''));
        if (!opts.quiet) {
            for (const s of res.skipped) {
                if (!s.reason.startsWith('Gridlines')) say(`  skipped ${s.name}: ${s.reason}`);
            }
        }
    }

    if (opts.edit) {
        for (const edit of parseEdits(opts.edit)) {
            const r = applyEdit(doc, edit);
            say(`Edit ${edit.selector}:${edit.command}:${edit.arg} -> ${r.selected} selected, ${r.changed} changed${r.notes.length ? ' (' + r.notes.join('; ') + ')' : ''}`);
            if (r.selected === 0) console.warn(`WARNING: edit "${edit.selector}" selected nothing`);
        }
    }

    let presetsJson: string | undefined;
    if (opts.outformat !== 'keep') {
        const target = opts.outformat as TargetFormat;
        if (target !== 'x2026_2' && target !== 'x2026_3' && target !== 'x2026_15') {
            console.error(`ERROR: unknown --outformat "${opts.outformat}" (use keep, x2026_2, x2026_3, x2026_15)`);
            return 2;
        }
        let presetsIn: string | undefined;
        if (target === 'x2026_2') {
            const candidate = opts.presets ?? path.join(path.dirname(opts.layout), 'xlights_effectpresets.json');
            if (fs.existsSync(candidate)) {
                presetsIn = fs.readFileSync(candidate, 'utf8');
                say(`  embedding effect presets from ${candidate}`);
            }
        }
        const res = migrateToFormat(doc, target, presetsIn);
        presetsJson = res.effectPresetsJson;
        say(`Converted ${res.detectedFormat} -> ${target}: ${res.changes.length} changes`);
        if (!opts.quiet) for (const c of res.changes.slice(0, 12)) say(`  ${c}`);
        if (!opts.quiet && res.changes.length > 12) say(`  ... ${res.changes.length - 12} more`);
    }

    if (opts.outlayout) {
        saveLayout(opts.outlayout, doc);
        say(`Wrote ${opts.outlayout}`);
        if (presetsJson) {
            const pj = path.join(path.dirname(opts.outlayout), 'xlights_effectpresets.json');
            fs.writeFileSync(pj, presetsJson, 'utf8');
            say(`Wrote ${pj} (effect presets moved out of the layout by the format conversion)`);
        }
    } else {
        say('No --outlayout given: nothing written');
    }
    return 0;
}

try {
    process.exit(main());
} catch (err) {
    console.error(`ERROR: ${err instanceof Error ? err.message : String(err)}`);
    process.exit(1);
}
