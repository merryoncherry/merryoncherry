// Public Domain

import {
    ArcOfCircles,
    CircleOfSlits,
    ArcOutline2A,
    RayOfCinchesDeg,
} from './MakeSlit';

import makerjs from 'makerjs';

import { writeFile } from 'fs/promises';

const addKerf: number = .032; //1/32+.001;  // It's really based on 1/16 diameter kerf already

const slitMode = 1; // 1 slit, 2 connect, 3 separate

const t1x = 2.4;
const t1y = 2.4;
const t2x = 85.6;
const t2y = 96.0;

const sx1 = 17;
const sy1 = 98.4-25.5;
const sx2 = 88-17;
const sy2 = 25.5;

const pspc = 7.0/8.0;
const srref = 3.5;

const tree1 = {
    slits1: {
        models: CircleOfSlits(slitMode, t1x, t1y, 0, 90, 10, 50, pspc, 48, 0, true, true),
    },
    slits1b: {
        models: CircleOfSlits(slitMode, t1x, t1y, 0, 90, 10+49.0*7/8, 1, pspc, 49, 90, false, true),
    },
    outline1: {
        paths: ArcOutline2A(t1x, t1y, -12, 114, 94, 8, 55),
        layer: 'blue',
    },
    topholes1: {
        paths: ArcOfCircles(t1x, t1y, 8.75, 13, 3/32, 0, 90, false),
    },
    botholes1: {
        paths: ArcOfCircles(t1x, t1y, 54, 25, 3/32, 0, 90, false),
    },
    /*
    leftholes1: {
        paths: RayOfCirclesDeg(t1x, t1y, -1, 10, 54, 1/32, 26, false),
    },
    rightholes1: {
        paths: RayOfCirclesDeg(t1x, t1y, 91, 10, 54, 1/32, 26, false),
    },
    */
    leftCinches1: {
        models: RayOfCinchesDeg(t1x, t1y - .8, 0, 10, 53, 13, 90, false),
    },
    rightCinches1: {
        models: RayOfCinchesDeg(t1x - .8, t1y, 90, 10, 53, 13, -90, false),
    },
};

const tree2 = {
    slits2: {
        models: CircleOfSlits(slitMode, t2x, t2y, 180, 90, 10, 50, pspc, 48, 0, true, true),
    },
    slits2b: {
        models: CircleOfSlits(slitMode, t2x, t2y, 180, 90, 10+49.0*7/8, 1, pspc, 49, 90, false, true),
    },
    outline2: {
        paths: ArcOutline2A(t2x, t2y, 168, 114, 94, 8, 55),
        layer: 'blue',
    },
    topholes2: {
        paths: ArcOfCircles(t2x, t2y, 8.75, 13, 3/32, 180, 90, false),
    },
    botholes2: {
        paths: ArcOfCircles(t2x, t2y, 54, 25, 3/32, 180, 90, false),
    },
    /*
    leftholes2: {
        paths: RayOfCirclesDeg(t2x, t2y, 179, 10, 54, 1/32, 26, false),
    },
    rightholes2: {
        paths: RayOfCirclesDeg(t2x, t2y, 271, 10, 54, 1/32, 26, false),
    },
    */
    leftCinches2: {
        models: RayOfCinchesDeg(t2x, t2y + .8, 180, 10, 53, 13, 90, false),
    },
    rightCinches2: {
        models: RayOfCinchesDeg(t2x + .8, t2y, -90, 10, 53, 13, -90, false),
    },
};

const spinner1 = {
    circ1:{
        paths: {spinout: new makerjs.paths.Circle([sx1, sy1], 16.5)},
        layer: 'blue',
    },
    spina1: {
        models: CircleOfSlits(slitMode, sx1, sy1, 0, 360, srref-pspc, 16, pspc, 30, 0, false, false),
    },
    spinb1: {
        models: CircleOfSlits(slitMode, sx1, sy1, 6, 360, srref+pspc*3, 12, pspc, 30, 0, false, false),
    },
    spinc1: {
        models: CircleOfSlits(slitMode, sx1, sy1, 3, 360, srref+pspc*9, 6, pspc, 60, 0, false, false),
    },
    ih1: {
        paths: ArcOfCircles(sx1, sy1, srref-pspc*2, 6, 1/32, 0, 360, true),
    },
    mh1: {
        paths: ArcOfCircles(sx1, sy1, srref+pspc*2, 30, 1/32, 0, 360, true),
    },
    oh1: {
        paths: ArcOfCircles(sx1, sy1, srref+pspc*8, 60, 1/32, 0, 360, true),
    },
    xh1: {
        paths: ArcOfCircles(sx1, sy1, srref+pspc*14, 120, 1/32, 0, 360, true),
    },
};

const spinner2 = {
    circ2:{
        paths: {spinout: new makerjs.paths.Circle([sx2, sy2], 16.5)},
        layer: 'blue',
    },
    spina2: {
        models: CircleOfSlits(slitMode, sx2, sy2, 0, 360, srref-pspc, 16, pspc, 30, 0, false, false),
    },
    spinb2: {
        models: CircleOfSlits(slitMode, sx2, sy2, 6, 360, srref+pspc*3, 12, pspc, 30, 0, false, false),
    },
    spinc2: {
        models: CircleOfSlits(slitMode, sx2, sy2, 3, 360, srref+pspc*9, 6, pspc, 60, 0, false, false),
    },
    ih2: {
        paths: ArcOfCircles(sx2, sy2, srref-pspc*2, 6, 1/32, 0, 360, true),
    },
    mh2: {
        paths: ArcOfCircles(sx2, sy2, srref+pspc*2, 30, 1/32, 0, 360, true),
    },
    oh2: {
        paths: ArcOfCircles(sx2, sy2, srref+pspc*8, 60, 1/32, 0, 360, true),
    },
    xh2: {
        paths: ArcOfCircles(sx2, sy2, srref+pspc*14, 120, 1/32, 0, 360, true),
    },
};

const wholeThing = {
    models: {
        box: {
            ...new makerjs.models.Rectangle(88, 98.4),
            layer: 'red',
        },
        ...tree1,
        ...tree2,
        ...spinner1,
        ...spinner2,
    },
    units: makerjs.unitType.Inch,
};

const dxfContent = makerjs.exporter.toDXF(wholeThing);
writeFile('tree1.dxf', dxfContent)
    .then(() => console.log('Saved tree DXF file.'))
    .catch(console.error);

const svgExportOptions: {[key: string]: unknown} = {
    //units: 'in',
};

if (addKerf === 0) {
    svgExportOptions['strokeWidth'] = 6;
}

const svgContent = makerjs.exporter.toSVG(wholeThing, svgExportOptions);
writeFile('tree1.svg', svgContent)
    .then(() => console.log('Saved tree SVG file.'))
    .catch(console.error);
