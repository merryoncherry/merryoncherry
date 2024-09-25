import makerjs, { IModel, IPath } from "makerjs";

const slitEndWidth = 1.0/16;
const slitEndLength = 1/8;
//const slitLength = 0.5+1.0/16; // For the longer seeds
const slitLength = 0.5-1.0/16; // For the shorter seeds
const addKerf = .032; //1/32+.001;  // It's really based on 1/16 diameter kerf already

// mode -- 1: single path, 2: close path, 3: 1 end, 4: other end, 5: path between,
//  6: Leave off first dogbone
//  7: Leave off second dogbone

/*
9---8               5---4
|   |               |   |
|   7---------------6   |
|                       |
|   12--------------1   |
|   |               |   |
10--11              2---3
*/

export function makeSlit(x: number, y: number, ang: number, mode: number) {
    const p1x = x+(slitLength/2 - addKerf)*Math.cos(ang) + addKerf*Math.sin(ang);
    const p1y = y+(slitLength/2 - addKerf)*Math.sin(ang) - addKerf*Math.cos(ang);
    const p6x = x+(slitLength/2 - addKerf)*Math.cos(ang) - addKerf*Math.sin(ang);
    const p6y = y+(slitLength/2 - addKerf)*Math.sin(ang) + addKerf*Math.cos(ang);
    const p2x = p1x+(slitEndLength/2+addKerf*0)*Math.sin(ang);
    const p2y = p1y-(slitEndLength/2+addKerf*0)*Math.cos(ang);
    const p5x = p6x-(slitEndLength/2+addKerf*0)*Math.sin(ang);
    const p5y = p6y+(slitEndLength/2+addKerf*0)*Math.cos(ang);
    const p3x = p2x+(slitEndWidth/2+addKerf*2)*Math.cos(ang);
    const p3y = p2y+(slitEndWidth/2+addKerf*2)*Math.sin(ang);
    const p4x = p5x+(slitEndWidth/2+addKerf*2)*Math.cos(ang);
    const p4y = p5y+(slitEndWidth/2+addKerf*2)*Math.sin(ang);
    const p7x = x-(slitLength/2 - addKerf)*Math.cos(ang) - addKerf*Math.sin(ang); // Other end
    const p7y = y-(slitLength/2 - addKerf)*Math.sin(ang) + addKerf*Math.cos(ang);
    const p12x = x-(slitLength/2 - addKerf)*Math.cos(ang) + addKerf*Math.sin(ang);
    const p12y = y-(slitLength/2 - addKerf)*Math.sin(ang) - addKerf*Math.cos(ang);
    const p8x = p7x-(slitEndLength/2+addKerf*0)*Math.sin(ang);
    const p8y = p7y+(slitEndLength/2+addKerf*0)*Math.cos(ang);
    const p11x = p12x+(slitEndLength/2+addKerf*0)*Math.sin(ang);
    const p11y = p12y-(slitEndLength/2+addKerf*0)*Math.cos(ang);
    const p9x = p8x-(slitEndWidth/2+addKerf*2)*Math.cos(ang);
    const p9y = p8y-(slitEndWidth/2+addKerf*2)*Math.sin(ang);
    const p10x = p11x-(slitEndWidth/2+addKerf*2)*Math.cos(ang);
    const p10y = p11y-(slitEndWidth/2+addKerf*2)*Math.sin(ang);
    const p1 = new makerjs.paths.Line([p1x, p1y], [p2x, p2y]);
    const p1_6 = new makerjs.paths.Line([p1x, p1y], [p6x, p6y]);
    const p2 = new makerjs.paths.Line([p2x, p2y], [p3x, p3y]);
    const p3 = new makerjs.paths.Line([p3x, p3y], [p4x, p4y]);
    const p4 = new makerjs.paths.Line([p4x, p4y], [p5x, p5y]);
    const p5 = new makerjs.paths.Line([p5x, p5y], [p6x, p6y]);
    const p5_1 = new makerjs.paths.Line([p5x, p5y], [p1x, p1y]);
    const p6 = new makerjs.paths.Line([p6x, p6y], [p7x, p7y]);
    const p7 = new makerjs.paths.Line([p7x, p7y], [p8x, p8y]);
    const p7_12 = new makerjs.paths.Line([p7x, p7y], [p12x, p12y]);
    const p8 = new makerjs.paths.Line([p8x, p8y], [p9x, p9y]);
    const p9 = new makerjs.paths.Line([p9x, p9y], [p10x, p10y]);
    const p10 = new makerjs.paths.Line([p10x, p10y], [p11x, p11y]);
    const p11 = new makerjs.paths.Line([p11x, p11y], [p12x, p12y]);
    const p11_7 = new makerjs.paths.Line([p11x, p11y], [p7x, p7y]);
    const p12 = new makerjs.paths.Line([p12x, p12y], [p1x, p1y]);

    if (mode <= 2) {
        const rv: {[key:string]: makerjs.paths.Line} = {
            "_a": p1,
            "_b": p2,
            "_c": p3,
            "_d": p4,
            "_e": p5,
            "_f": p6,
            "_g": p7,
            "_h": p8,
            "_i": p9,
            "_j": p10,
            "_k": p11,
        };
        if (mode === 2 || addKerf) {
            rv["_l"] = p12;
        }
        return rv;
    }
    else if (mode === 3)
    {
        return {
            "_a": p1,
            "_b": p2,
            "_c": p3,
            "_d": p4,
            "_e": p5_1,
        };
    }
    else if (mode === 4)
    {
        return {
            "_g": p7,
            "_h": p8,
            "_i": p9,
            "_j": p10,
            "_k": p11_7,
        };
    }
    else if (mode === 5)
    {
        return {
            "_a": p1_6,
            "_b": p6,
            "_c": p7_12,
            "_d": p12,
        };
    }
    else if (mode === 6)
    {
        return {
            "_a": p1_6,
            "_b": p6,
            "_c": p7,
            "_d": p8,
            "_e": p9,
            "_f": p10,
            "_g": p11,
            "_h": p12,
        };
    }
    else if (mode === 7)
    {
        return {
            "_a": p1,
            "_b": p2,
            "_c": p3,
            "_d": p4,
            "_e": p5,
            "_f": p6,
            "_g": p7_12,
            "_h": p12,
        };
    }
}

// Make C
const mm1 = .03937;
const cw = 4*mm1;
const ch = 10*mm1;
const ccw = 1*mm1;

/*
3-----------------------2
|                       |
|   6---------------7   |
|   |               |   |
|   |       +       |   |
|   |               |   |
4---5               8---1
*/

export function makeC(x: number, y: number, ang: number, mode: number) {
    const p1x = x+(ch/2)*Math.cos(ang) + (cw/2)*Math.sin(ang);
    const p1y = y+(ch/2)*Math.sin(ang) - (cw/2)*Math.cos(ang);
    const p2x = x+(ch/2)*Math.cos(ang) - (cw/2)*Math.sin(ang);
    const p2y = y+(ch/2)*Math.sin(ang) + (cw/2)*Math.cos(ang);
    const p3x = x-(ch/2)*Math.cos(ang) - (cw/2)*Math.sin(ang);
    const p3y = y-(ch/2)*Math.sin(ang) + (cw/2)*Math.cos(ang);
    const p4x = x-(ch/2)*Math.cos(ang) + (cw/2)*Math.sin(ang);
    const p4y = y-(ch/2)*Math.sin(ang) - (cw/2)*Math.cos(ang);
    const p5x = x-(ch/2-ccw)*Math.cos(ang) + (cw/2)*Math.sin(ang);
    const p5y = y-(ch/2-ccw)*Math.sin(ang) - (cw/2)*Math.cos(ang);
    const p6x = x-(ch/2-ccw)*Math.cos(ang) - (cw/2-ccw)*Math.sin(ang);
    const p6y = y-(ch/2-ccw)*Math.sin(ang) + (cw/2-ccw)*Math.cos(ang);
    const p7x = x+(ch/2-ccw)*Math.cos(ang) - (cw/2-ccw)*Math.sin(ang);
    const p7y = y+(ch/2-ccw)*Math.sin(ang) + (cw/2-ccw)*Math.cos(ang);
    const p8x = x+(ch/2-ccw)*Math.cos(ang) + (cw/2)*Math.sin(ang);
    const p8y = y+(ch/2-ccw)*Math.sin(ang) - (cw/2)*Math.cos(ang);
    const p1 = new makerjs.paths.Line([p1x, p1y], [p2x, p2y]);
    const p2 = new makerjs.paths.Line([p2x, p2y], [p3x, p3y]);
    const p3 = new makerjs.paths.Line([p3x, p3y], [p4x, p4y]);
    const p4 = new makerjs.paths.Line([p4x, p4y], [p5x, p5y]);
    const p5 = new makerjs.paths.Line([p5x, p5y], [p6x, p6y]);
    const p6 = new makerjs.paths.Line([p6x, p6y], [p7x, p7y]);
    const p7 = new makerjs.paths.Line([p7x, p7y], [p8x, p8y]);
    const p8 = new makerjs.paths.Line([p8x, p8y], [p1x, p1y]);

    const rv: {[key:string]: makerjs.paths.Line} = {
        "_a": p1,
        "_b": p2,
        "_c": p3,
        "_d": p4,
        "_e": p5,
        "_f": p6,
        "_g": p7,
        "_h": p8,
    };
    return rv;
}

const cinchW = 1/8;
const cinchThick = 3/8;
const cinchExtra = 1/8;

////////////////////
//      3x cinchW
//  *-----------*
//  |           |
//  |   *---*   |
//  |   |   |   |  <- Y = cinchExtra
//  |   |   *---*  <- p1
//  |   |
//  |   |     +   <- Y = cinchThick; + = center point
//  |   |
//  |   |   *---*
//  |   |   |   |  <- Y = cinchExtra
//  |   *---*   |
//  |           |
//  *-----------*
export function Cinch(x: number, y: number, ang: number) {
    const p1x  = x+(cinchW/2)*Math.cos(ang) - (cinchThick/2)*Math.sin(ang);
    const p1y  = y+(cinchW/2)*Math.sin(ang) + (cinchThick/2)*Math.cos(ang);
    const p6x  = x+(cinchW/2)*Math.cos(ang) + (cinchThick/2)*Math.sin(ang);
    const p6y  = y+(cinchW/2)*Math.sin(ang) - (cinchThick/2)*Math.cos(ang);
    const p2x  = x+(cinchW/2)*Math.cos(ang) - (cinchThick/2+cinchExtra+cinchW)*Math.sin(ang);
    const p2y  = y+(cinchW/2)*Math.sin(ang) + (cinchThick/2+cinchExtra+cinchW)*Math.cos(ang);
    const p5x  = x+(cinchW/2)*Math.cos(ang) + (cinchThick/2+cinchExtra+cinchW)*Math.sin(ang);
    const p5y  = y+(cinchW/2)*Math.sin(ang) - (cinchThick/2+cinchExtra+cinchW)*Math.cos(ang);
    const p3x  = x+(cinchW*-2.5)*Math.cos(ang) - (cinchThick/2+cinchExtra+cinchW)*Math.sin(ang);
    const p3y  = y+(cinchW*-2.5)*Math.sin(ang) + (cinchThick/2+cinchExtra+cinchW)*Math.cos(ang);
    const p4x  = x+(cinchW*-2.5)*Math.cos(ang) + (cinchThick/2+cinchExtra+cinchW)*Math.sin(ang);
    const p4y  = y+(cinchW*-2.5)*Math.sin(ang) - (cinchThick/2+cinchExtra+cinchW)*Math.cos(ang);
    const p12x = x+(cinchW*-0.5)*Math.cos(ang) - (cinchThick/2)*Math.sin(ang);
    const p12y = y+(cinchW*-0.5)*Math.sin(ang) + (cinchThick/2)*Math.cos(ang);
    const p7x  = x+(cinchW*-0.5)*Math.cos(ang) + (cinchThick/2)*Math.sin(ang);
    const p7y  = y+(cinchW*-0.5)*Math.sin(ang) - (cinchThick/2)*Math.cos(ang);
    const p11x = x+(cinchW*-0.5)*Math.cos(ang) - (cinchThick/2+cinchExtra)*Math.sin(ang);
    const p11y = y+(cinchW*-0.5)*Math.sin(ang) + (cinchThick/2+cinchExtra)*Math.cos(ang);
    const p8x  = x+(cinchW*-0.5)*Math.cos(ang) + (cinchThick/2+cinchExtra)*Math.sin(ang);
    const p8y  = y+(cinchW*-0.5)*Math.sin(ang) - (cinchThick/2+cinchExtra)*Math.cos(ang);
    const p10x = x+(cinchW*-1.5)*Math.cos(ang) - (cinchThick/2+cinchExtra)*Math.sin(ang);
    const p10y = y+(cinchW*-1.5)*Math.sin(ang) + (cinchThick/2+cinchExtra)*Math.cos(ang);
    const p9x  = x+(cinchW*-1.5)*Math.cos(ang) + (cinchThick/2+cinchExtra)*Math.sin(ang);
    const p9y  = y+(cinchW*-1.5)*Math.sin(ang) - (cinchThick/2+cinchExtra)*Math.cos(ang);

    const p1 = new makerjs.paths.Line([p1x, p1y], [p2x, p2y]);
    const p2 = new makerjs.paths.Line([p2x, p2y], [p3x, p3y]);
    const p3 = new makerjs.paths.Line([p3x, p3y], [p4x, p4y]);
    const p4 = new makerjs.paths.Line([p4x, p4y], [p5x, p5y]);
    const p5 = new makerjs.paths.Line([p5x, p5y], [p6x, p6y]);
    const p6 = new makerjs.paths.Line([p6x, p6y], [p7x, p7y]);
    const p7 = new makerjs.paths.Line([p7x, p7y], [p8x, p8y]);
    const p8 = new makerjs.paths.Line([p8x, p8y], [p9x, p9y]);
    const p9 = new makerjs.paths.Line([p9x, p9y], [p10x, p10y]);
    const p10 = new makerjs.paths.Line([p10x, p10y], [p11x, p11y]);
    const p11 = new makerjs.paths.Line([p11x, p11y], [p12x, p12y]);
    const p12 = new makerjs.paths.Line([p12x, p12y], [p1x, p1y]);

    const rv: {[key:string]: makerjs.paths.Line} = {
        "_a": p1,
        "_b": p2,
        "_c": p3,
        "_d": p4,
        "_e": p5,
        "_f": p6,
        "_g": p7,
        "_h": p8,
        "_i": p9,
        "_j": p10,
        "_k": p11,
        "_l": p12,
    };
    return rv;
}

export function arcOfCircles(cx: number, cy: number, arcRadius: number, count: number, circleRadius: number, start: number, sweep: number, midpoints: boolean) {
    const angleStep = midpoints ? sweep/count : (sweep / (count-1));
    if (midpoints) start += (angleStep/2);

    const models: {[key:string] : IModel} = {};

    for (let i = 0; i < count; i++) {
        const angle = start + i * angleStep;
        const x = cx + arcRadius * Math.cos(makerjs.angle.toRadians(angle));
        const y = cy + arcRadius * Math.sin(makerjs.angle.toRadians(angle));

        // Correctly using makerjs.paths.Circle for defining a circle path
        models['circle_' + i] = {
            paths: {
                circle: new makerjs.paths.Circle([x, y], circleRadius + addKerf)
            }
        };
    }
    return models;
}

export function RayOfCircles(cx: number, cy: number, ang: number, r1: number, r2: number, rcir: number, count: number, midpoints: boolean) {
    const paths: {[key:string] : IPath} = {};

    const rstep = midpoints ? (r2-r1) / count : (r2-r1)/(count-1);
    if (midpoints) r1 += rstep/2;

    for (let i = 0; i < count; i++) {
        const x = cx + (r1 + i * rstep) * Math.cos(ang);
        const y = cy + (r1 + i * rstep) * Math.sin(ang);

        paths['circ_' + i] = new makerjs.paths.Circle([x, y], rcir+addKerf);
    }
    return paths;
}

export function RayOfCinchesDeg(cx: number, cy: number, angdeg: number, r1: number, r2: number, count: number, cang: number, midpoints: boolean) {
    const models: {[key:string] : IModel} = {};

    const rstep = midpoints ? (r2-r1) / count : (r2-r1)/(count-1);
    if (midpoints) r1 += rstep/2;

    const ang = makerjs.angle.toRadians(angdeg);

    for (let i = 0; i < count; i++) {
        const x = cx + (r1 + i * rstep) * Math.cos(ang);
        const y = cy + (r1 + i * rstep) * Math.sin(ang);

        models['cinch_' + i] = {paths: Cinch(x, y, ang+cang*Math.PI/180)};
    }
    return models;
}


export function RayOfCirclesDeg(cx: number, cy: number, startangdeg: number, r1: number, r2: number, rcir: number, count: number, midpoints: boolean) {
    const paths: {[key:string] : IPath} = {};

    const rstep = midpoints ? (r2-r1) / count : (r2-r1)/(count-1);
    if (midpoints) r1 += rstep/2;

    const ang = makerjs.angle.toRadians(startangdeg);

    for (let i = 0; i < count; i++) {
        const x = cx + (r1 + i * rstep) * Math.cos(ang);
        const y = cy + (r1 + i * rstep) * Math.sin(ang);

        paths['circ_' + i] = new makerjs.paths.Circle([x, y], rcir+addKerf);
    }
    return paths;
}

export function ArcOfCircles(cx: number, cy: number, outerRadius: number, count: number, innerCircleRadius: number, start: number, sweep: number, midpoints: boolean) {
    const paths: {[key:string] : IPath} = {};

    const angleStep = midpoints ? sweep/count : (sweep / (count-1));
    if (midpoints) start += (angleStep/2);

    for (let i = 0; i < count; i++) {
        const angle = start + i * angleStep;
        const x = cx + outerRadius * Math.cos(makerjs.angle.toRadians(angle));
        const y = cy + outerRadius * Math.sin(makerjs.angle.toRadians(angle));

        // Correctly using makerjs.paths.Circle for defining a circle path
        paths['circle_' + i] = new makerjs.paths.Circle([x, y], innerCircleRadius + addKerf);
    }

    return paths;
}

export function ArcOutline(cx: number, cy: number, start: number, sweep: number, r1: number, r2: number) {
    const sang = makerjs.angle.toRadians(start);
    const eang = makerjs.angle.toRadians(start+sweep);

    const paths: {[key:string] : IPath} = {};
    paths['i'] = new makerjs.paths.Arc([cx, cy], r1, start, start+sweep);
    paths['s'] = new makerjs.paths.Line([cx+r1*Math.cos(sang), cy+r1*Math.sin(sang)], [cx+r2*Math.cos(sang), cy+r2*Math.sin(sang)]);
    paths['o'] = new makerjs.paths.Arc([cx, cy], r2, start, start+sweep);
    paths['e'] = new makerjs.paths.Line([cx+r2*Math.cos(eang), cy+r2*Math.sin(eang)], [cx+r1*Math.cos(eang), cy+r1*Math.sin(eang)]);

    return paths;
}

export function ArcOutline2A(cx: number, cy: number, start: number, sweep1: number, sweep2: number, r1: number, r2: number) {
    const sang1d = start;
    const eang1d = start+sweep1;
    const sang2d = start-(sweep2-sweep1)/2;
    const eang2d = start+sweep1+(sweep2-sweep1)/2;
    const sang1 = makerjs.angle.toRadians(sang1d);
    const eang1 = makerjs.angle.toRadians(eang1d);
    const sang2 = makerjs.angle.toRadians(sang2d);
    const eang2 = makerjs.angle.toRadians(eang2d);

    const paths: {[key:string] : IPath} = {};
    paths['i'] = new makerjs.paths.Arc([cx, cy], r1, sang1d, eang1d);
    paths['s'] = new makerjs.paths.Line([cx+r1*Math.cos(sang1), cy+r1*Math.sin(sang1)], [cx+r2*Math.cos(sang2), cy+r2*Math.sin(sang2)]);
    paths['o'] = new makerjs.paths.Arc([cx, cy], r2, sang2d, eang2d);
    paths['e'] = new makerjs.paths.Line([cx+r2*Math.cos(eang2), cy+r2*Math.sin(eang2)], [cx+r1*Math.cos(eang1), cy+r1*Math.sin(eang1)]);

    return paths;
}

export function CircleOfSlits(slitMode: number, cx: number, cy: number, startangle: number, sweep: number, radius: number, scount: number, spacing: number, count: number, twist: number, midpoints: boolean, dwim: boolean) {
    const models: {[key:string] : IModel} = {};

    twist = makerjs.angle.toRadians(twist);

    const angleStep = (midpoints || !dwim) ? (sweep / count) : (sweep/(count-1));
    if (midpoints) startangle += (angleStep/2);
    for (let i = 0; i < count; i++) {
        for (let j = 0; j < scount; ++j) {
            const angle = startangle + i * angleStep;
            const ang = makerjs.angle.toRadians(angle);
            const x = cx + (radius + j * spacing) * Math.cos(ang);
            const y = cy + (radius + j * spacing) * Math.sin(ang);

            if (slitMode <= 2) {
                models['slit_' + i + '_' + j] = {paths: makeSlit(x, y, ang+twist, slitMode)};
            }
            else if (slitMode === 3) {
                models['slit_' + i + '_' + j + 'a'] = {
                    paths: makeSlit(x, y, ang+twist, 3),
                };
                models['slit_' + i + '_' + j + 'b'] = {
                    paths: makeSlit(x, y, ang+twist, 4),
                };
                models['slit_' + i + '_' + j + 'c'] = {
                    paths: makeSlit(x, y, ang+twist, 5),
                    layer: 'cuton'
                };
            }
        }
    }

    return models;
}
