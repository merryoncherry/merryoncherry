import argparse
import math
import sys
import xml.dom.minidom

class TextRemover:
    def __init__(self):
        pass
    def removeText(self, n):
        txts = []
        for cn in n.childNodes:
            if cn.nodeType == xml.dom.Node.ELEMENT_NODE:
                self.removeText(cn)
            if cn.nodeType == xml.dom.Node.TEXT_NODE:
                txts.append(cn)
        for t in txts:
            txt = t.nodeValue
            txt = txt.replace(' ', '')
            txt = txt.replace("\n", '')
            txt = txt.replace("\r", '')
            txt = txt.replace("\t", '')
            txt = txt.replace("\b", '')
            if len(txt):
                raise Exception("Removing text found something not whitespace: "+txt+'/'+txt.encode('utf-8').hex())
            n.removeChild(t)
            t.unlink()

class PxTransformBase:
    def __init__(self):
        pass

    @staticmethod
    def scale(x, y, z, sx, sy, sz):
        return (x*sx, y*sy, z*sz)

    @staticmethod
    def getScales(xv, yv, zv):
        (xx, xy, xz) = xv
        (yx, yy, yz) = yv
        (zx, zy, zz) = zv
        return (math.sqrt(xx*xx+xy*xy+xz*xz),
                math.sqrt(yx*yx+yy*yy+yz*yz),
                math.sqrt(zx*zx+zy*zy+zz*zz))

    @staticmethod
    def rotate(x, y, z, rx, ry, rz):
        # X rotation
        nx = x
        ny = (y * math.cos(rx * math.pi / 180.0) -
              z * math.sin(rx * math.pi / 180.0) )
        nz = (z * math.cos(rx * math.pi / 180.0) +
              y * math.sin(rx * math.pi / 180.0) )
        x=nx
        y=ny
        z=nz

        # Y rotation
        ny = y
        nz = (z * math.cos(ry * math.pi / 180.0) -
              x * math.sin(ry * math.pi / 180.0) )
        nx = (x * math.cos(ry * math.pi / 180.0) +
              z * math.sin(ry * math.pi / 180.0) )
        x=nx
        y=ny
        z=nz

        # Z rotation
        nz = z
        nx = (x * math.cos(rz * math.pi / 180.0) -
              y * math.sin(rz * math.pi / 180.0) )
        ny = (y * math.cos(rz * math.pi / 180.0) +
              x * math.sin(rz * math.pi / 180.0) )
        x=nx
        y=ny
        z=nz

        return (x, y, z)

    @staticmethod
    def createUnitVectors(sx, sy, sz, rx, ry, rz):
        x_x = 1
        x_y = 0
        x_z = 0

        y_x = 0
        y_y = 1
        y_z = 0

        z_x = 0
        z_y = 0
        z_z = 1

        (x_x, x_y, x_z) = PxTransformBase.scale(x_x, x_y, x_z, sx, sy, sz)
        (y_x, y_y, y_z) = PxTransformBase.scale(y_x, y_y, y_z, sx, sy, sz)
        (z_x, z_y, z_z) = PxTransformBase.scale(z_x, z_y, z_z, sx, sy, sz)

        (x_x, x_y, x_z) = PxTransformBase.rotate(x_x, x_y, x_z, rx, ry, rz)
        (y_x, y_y, y_z) = PxTransformBase.rotate(y_x, y_y, y_z, rx, ry, rz)
        (z_x, z_y, z_z) = PxTransformBase.rotate(z_x, z_y, z_z, rx, ry, rz)

        return ((x_x, x_y, x_z), (y_x, y_y, y_z), (z_x, z_y, z_z))

    @staticmethod
    def invertUnitVectors(ux, uy, uz):
        (sx, sy, sz) = PxTransformBase.getScales(ux, uy, uz)
        (x_x, x_y, x_z) = ux
        # Use the y component of X to establish Z rotation.  y can't be nonzero without it.
        # This is a singularity if x_y and x_x are 0... which would occur if rot y = +/-90
        #  In this case, rot_z will do what rot x did at the beginning...
        if (x_y == 0 and x_x == 0):
            rotZ = 0
        else:
            rotZ = math.atan2(x_y, x_x)
        rotZ = rotZ * 180 / math.pi
        # Reverse the Z rotation, derive the Y rotation from remaining X unit vector
        (x_x, x_y, x_z) = PxTransformBase.rotate(x_x, x_y, x_z, 0, 0, -rotZ)
        if (x_z == 0 and x_x == 0):
            rotY = 0
        else:
            rotY = math.atan2(-x_z, x_x)
        rotY = rotY * 180 / math.pi
        # Reverse the Z and Y rotation on the Y vector (could as well have done Z).  This will
        #  make establishing X rotation on the Y unit vector straightforward
        (y_x, y_y, y_z) = uy
        (y_x, y_y, y_z) = PxTransformBase.rotate(y_x, y_y, y_z, 0, 0, -rotZ)
        (y_x, y_y, y_z) = PxTransformBase.rotate(y_x, y_y, y_z, 0, -rotY, 0)
        if (y_y == 0 and y_z == 0):
            rotX = 0
        else:
            rotX = math.atan2(y_z, y_y)
        rotX = rotX * 180 / math.pi
        return (sx, sy, sz, rotX, rotY, rotZ)

    def transformPoint(self, pt):
        return pt

    def transformPtScaleRot(self, vec):
        (x, y, z, sx, sy, sz, rx, ry, rz) = vec

        (ux, uy, uz) = PxTransformBase.createUnitVectors(sx, sy, sz, rx, ry, rz)
        (x_x, x_y, x_z) = ux
        (y_x, y_y, y_z) = uy
        (z_x, z_y, z_z) = uz

        (nx,  ny,  nz) = self.transformPoint((x, y, z))
        (nxx, nxy, nxz) = self.transformPoint((x+x_x, y+x_y, z+x_z))
        (nyx, nyy, nyz) = self.transformPoint((x+y_x, y+y_y, z+y_z))
        (nzx, nzy, nzz) = self.transformPoint((x+z_x, y+z_y, z+z_z))

        (nsx, nsy, nsz, nrx, nry, nrz) = PxTransformBase.invertUnitVectors(
                (nxx-nx, nxy-ny, nxz-nz),(nyx-nx, nyy-ny, nyz-nz),(nzx-nx, nzy-ny, nzz-nz))

        return (nx, ny, nz, nsx, nsy, nsz, nrx, nry, nrz)

class PxTransformTranslate(PxTransformBase):
    def __init__(self, deltax, deltay, deltaz):
        super().__init__()
        self.dx = deltax
        self.dy = deltay
        self.dz = deltaz

    def transformPoint(self, pt):
        (x, y, z) = pt;
        x = x+self.dx;
        y = y+self.dy;
        z = z+self.dz;
        return (x, y, z)

    #def transformPtScaleRot(self, vec):
    #    (x, y, z, sx, sy, sz, rx, ry, rz) = vec
    #    x = x+self.dx
    #    y = y+self.dy
    #    z = z+self.dz
    #    return (x, y, z, sx, sy, sz, rx, ry, rz)

class PxTransformScale(PxTransformBase):
    def __init__(self, scalex, scaley, scalez):
        super().__init__()
        self.sx = scalex
        self.sy = scaley
        self.sz = scalez

    def transformPoint(self, pt):
        (x, y, z) = pt;
        return PxTransformBase.scale(x, y, z, self.sx, self.sy, self.sz)

    #def transformPtScaleRot(self, vec):
    #    (x, y, z, sx, sy, sz, rx, ry, rz) = vec
    #    (x, y, z) =  PxTransformBase.scale(x, y, z, self.sx, self.sy, self.sz)
    #    # TODO This is wrong if it is rotated because of how it is applied
    #    return (x, y, z, sx*self.sx, sy*self.sy, sz*self.sz, rx, ry, rz)

class PxTransformRotate(PxTransformBase):
    def __init__(self, rotx, roty, rotz):
        super().__init__()
        self.rx = rotx
        self.ry = roty
        self.rz = rotz

    def transformPoint(self, pt):
        (x, y, z) = pt;
        return PxTransformBase.rotate(x, y, z, self.rx, self.ry, self.rz)

    #def transformPtScaleRot(self, vec):
    #    (x, y, z, sx, sy, sz, rx, ry, rz) = vec
    #    (x, y, z) =  PxTransformBase.rotate(x, y, z, self.rx, self.ry, self.rz)
    #    # TODO This is wrong if it is a variety of things because of how it is applied
    #    return (x, y, z, sx, sy, sz, rx+self.rx, ry+self.ry, rz+self.rz)


class Visitor:
    def __init__(self):
        pass

    def printNode(self, n):
        print(n.toprettyxml())

    def visitcolor(self, name, rgb):
        #(r, g, b) = rgb
        #print ('Color for '+name+': '+r+','+g+','+b)
        pass

    def visitcolors(self, n):
        if (n.attributes):
            raise Exception("Unexpected attributes in node tag: "+n.tagName)
        #Colors are a set of nodes, 
        for clr in n.childNodes:
            if clr.nodeType == xml.dom.Node.ELEMENT_NODE:
                self.visitcolor(clr.tagName, (clr.getAttribute('Red'), clr.getAttribute('Green'), clr.getAttribute('Blue')))
        pass

    def visiteffects(self, n):
        if (n.attributes):
            #self.printNode(n)
            #raise Exception("Unexpected attributes in node tag: "+n.tagName)
            # effects version="0007"
            pass
        for eff in n.childNodes:
            if eff.nodeType == xml.dom.Node.ELEMENT_NODE:
                #self.printNode(eff)
                pass
        pass

    def visitlayoutGroups(self, n):
        if (n.attributes):
            raise Exception("Unexpected attributes in node tag: "+n.tagName)
        for lg in n.childNodes:
            if lg.nodeType == xml.dom.Node.ELEMENT_NODE:
                #self.printNode(lg)
                pass
        pass

    def visitmodelGroup(self, mg):
        # TODO: This needs a lot of work for rotator / deleter / renamer
        #self.printNode(mg)
        pass

    def visitmodelGroups(self, n):
        if (n.attributes):
            raise Exception("Unexpected attributes in node tag: "+n.tagName)
        for mg in n.childNodes:
            if mg.nodeType == xml.dom.Node.ELEMENT_NODE:
                self.visitmodelGroup(mg)

    def visitmodel(self, m):
        # TODO: This needs a lot of work for rotator / deleter
        #self.printNode(m)
        pass

    def visitmodels(self, n):
        if (n.attributes):
            raise Exception("Unexpected attributes in node tag: "+n.tagName)
        for m in n.childNodes:
            if m.nodeType == xml.dom.Node.ELEMENT_NODE:
                self.visitmodel(m)
        pass

    def visitpalettes(self, n):
        if (n.attributes):
            raise Exception("Unexpected attributes in node tag: "+n.tagName)
        for p in n.childNodes:
            if p.nodeType == xml.dom.Node.ELEMENT_NODE:
                #self.printNode(p)
                pass
        pass

    def visitperspectives(self, n):
        if (n.attributes):
            # self.printNode(n)
            # raise Exception("Unexpected attributes in node tag: "+n.tagName)
            #  current="Default Perspective"
            pass
        for p in n.childNodes:
            if p.nodeType == xml.dom.Node.ELEMENT_NODE:
                #self.printNode(p)
                pass
        pass

    def visitsettings(self, n):
        if (n.attributes):
            raise Exception("Unexpected attributes in node tag: "+n.tagName)
        for s in n.childNodes:
            if s.nodeType == xml.dom.Node.ELEMENT_NODE:
                #self.printNode(s)
                #<... value="...">
                pass
        pass

    def visitview(self, v):
        #self.printNode(v)
        pass

    def visitviews(self, n):
        if (n.attributes):
            raise Exception("Unexpected attributes in node tag: "+n.tagName)
        for v in n.childNodes:
            if v.nodeType == xml.dom.Node.ELEMENT_NODE:
                self.visitview(v)
                pass
        pass

    def visitview_object(self, vo):
        pass

    def visitview_objects(self, n):
        if (n.attributes):
            raise Exception("Unexpected attributes in node tag: "+n.tagName)
        for vo in n.childNodes:
            if vo.nodeType == xml.dom.Node.ELEMENT_NODE:
                self.visitview_object(vo)
        pass

    def visitViewpoint(self, vp):
        pass

    def visitViewpoints(self, n):
        if (n.attributes):
            raise Exception("Unexpected attributes in node tag: "+n.tagName)
        for vp in n.childNodes:
            if vp.nodeType == xml.dom.Node.ELEMENT_NODE:
                self.visitViewpoint(vp)
        pass

    def visitxrgb(self, n):
        if (n.tagName != 'xrgb'):
            raise Exception('Root not "xrgb"')
        for attrName, attrValue in n.attributes.items():
            raise Exception('Root "xrgb" unexpected attribute "'+attrName+'"')
        for cn in n.childNodes:
            if (cn.nodeType == xml.dom.Node.ELEMENT_NODE):
                if (cn.tagName == 'colors'):
                    self.visitcolors(cn)
                elif (cn.tagName == 'effects'):
                    self.visiteffects(cn)
                elif (cn.tagName == 'layoutGroups'):
                    self.visitlayoutGroups(cn)
                elif (cn.tagName == 'modelGroups'):
                    self.visitmodelGroups(cn)
                elif (cn.tagName == 'models'):
                    self.visitmodels(cn)
                elif (cn.tagName == 'palettes'):
                    self.visitpalettes(cn)
                elif (cn.tagName == 'perspectives'):
                    self.visitperspectives(cn)
                elif (cn.tagName == 'settings'):
                    self.visitsettings(cn)
                elif (cn.tagName == 'views'):
                    self.visitviews(cn)
                elif (cn.tagName == 'view_objects'):
                    self.visitview_objects(cn)
                elif (cn.tagName == 'Viewpoints'):
                    self.visitViewpoints(cn)
                else:
                    raise Exception("Unexpected xrgb node tag: "+cn.tagName)
                pass
            elif (cn.nodeType == xml.dom.Node.ATTRIBUTE_NODE):
                pass
            elif (cn.nodeType == xml.dom.Node.TEXT_NODE):
                pass
            else:
                # CDATA_SECTION_NODE, ENTITY_NODE, PROCESSING_INSTRUCTION_NODE, COMMENT_NODE, DOCUMENT_NODE, DOCUMENT_TYPE_NODE, NOTATION_NODE
                raise Exception('Strange node type: '+str(cn.nodeType))

    def visitRoot(self, n):
        self.visitxrgb(n.documentElement)
        pass

class LayoutTransformVisitor(Visitor):
    def __init__(self, transformers):
        super().__init__()
        self.txforms = transformers;

    def DONOTvisitViewpoint(self, vp):
        # TODO: These probably need work, but not sure how all the numbers apply
        x = -float(vp.getAttribute("posX"))
        y = -float(vp.getAttribute("posY"))
        z = -float(vp.getAttribute("posZ"))
        ax = float(vp.getAttribute("angleX"))
        ay = float(vp.getAttribute("angleY"))
        az = float(vp.getAttribute("angleZ"))
        d = float(vp.getAttribute("distance"))
        z = float(vp.getAttribute("zoom"))
        panx = float(vp.getAttribute("panx"))
        pany = float(vp.getAttribute("pany"))
        panz = float(vp.getAttribute("panz"))
        zcx = float(vp.getAttribute("zoom_corrx"))
        zcy = float(vp.getAttribute("zoom_corry"))

        # Transforming the viewpoint may not be what was wanted at all.
        #for t in self.txforms:
        #    (x, y, z) = t.transformPoint((-x, -y, -z))

        #vp.setAttribute("posX", str(-x))
        #vp.setAttribute("posY", str(-y))
        #vp.setAttribute("posZ", str(-z))
        #ax = float(vp.getAttribute("angleX"))
        #ay = float(vp.getAttribute("angleY"))
        #az = float(vp.getAttribute("angleZ"))
        #d = float(vp.getAttribute("distance"))
        #z = float(vp.getAttribute("zoom"))
        #panx = float(vp.getAttribute("panx"))
        #pany = float(vp.getAttribute("pany"))
        #panz = float(vp.getAttribute("panz"))
        #zcx = float(vp.getAttribute("zoom_corrx"))
        #zcy = float(vp.getAttribute("zoom_corry"))

        pass

    def processPSR(self, n, an_x, an_y, an_z, an_sx, an_sy, an_sz, an_rx, an_ry, an_rz):
        x = float(n.getAttribute(an_x))
        y = float(n.getAttribute(an_y))
        z = float(n.getAttribute(an_z))
        sx = float(n.getAttribute(an_sx))
        sy = float(n.getAttribute(an_sy))
        sz = float(n.getAttribute(an_sz))
        rx = float(n.getAttribute(an_rx))
        ry = float(n.getAttribute(an_ry))
        rz = float(n.getAttribute(an_rz))
        for t in self.txforms:
            (x, y, z, sx, sy, sz, rx, ry, rz) = t.transformPtScaleRot((x,y,z,sx,sy,sz,rx,ry,rz))
        n.setAttribute(an_x, str(x))
        n.setAttribute(an_y, str(y))
        n.setAttribute(an_z, str(z))
        n.setAttribute(an_sx, str(sx))
        n.setAttribute(an_sy, str(sy))
        n.setAttribute(an_sz, str(sz))
        n.setAttribute(an_rx, str(rx))
        n.setAttribute(an_ry, str(ry))
        n.setAttribute(an_rz, str(rz))

    def get3(self, n, an_x, an_y, an_z):
        x = float(n.getAttribute(an_x))
        y = float(n.getAttribute(an_y))
        z = float(n.getAttribute(an_z))
        return (x, y, z)

    def set3(self, n, an_x, an_y, an_z, x, y, z):
        n.setAttribute(an_x, str(x))
        n.setAttribute(an_y, str(y))
        n.setAttribute(an_z, str(z))

    def doTx(self, x, y, z):
        for t in self.txforms:
            (x, y, z) = t.transformPoint((x,y,z))
        return (x, y, z)

    def processPt(self, n, an_x, an_y, an_z):
        (x, y, z) = self.get3(n, an_x, an_y, an_z)
        (x, y, z) = self.doTx(x, y, z)
        self.set3(n, an_x, an_y, an_z, x, y, z)

    # Suitable for translation, rot, scale (anything linear)
    #  Not appropriate for some other things probably.
    def processRelPtPair(self, n, an1x, an1y, an1z, an2x, an2y, an2z):
            (x, y, z) = self.get3(n, an1x, an1y, an1z)
            (x2, y2, z2) = self.get3(n, an2x, an2y, an2z)
            (xt, yt, zt) = self.doTx(x, y, z)
            (x2t, y2t, z2t) = self.doTx(x+x2, y+y2, z+z2)
            self.set3(n, an1x, an1y, an1z, xt, yt, zt)
            self.set3(n, an2x, an2y, an2z, x2t-xt, y2t-yt, z2t-zt)

    def visitview_object(self, vo):
        # These can have position, scale, rotation
        # Scale comes first, then rotation, then location because scaling x always makes it wider
        # Right handed coordinates for rotation, application order X, Y, Z
        otype = vo.getAttribute('DisplayAs')
        if (otype == 'Image'):
            self.processPSR(vo, 'WorldPosX', 'WorldPosY', 'WorldPosZ', 'ScaleX', 'ScaleY', 'ScaleZ', 'RotateX', 'RotateY', 'RotateZ')
        elif (otype == 'Ruler'): # Not clear if this is correct, but probably doesn't matter
            self.processPt(vo, 'WorldPosX', 'WorldPosY', 'WorldPosZ')
            #self.processPt(vo, 'X2', 'Y2', 'Z2') # also probably relative
        elif (otype == 'Gridlines'): # Leave alone for now
            #self.processPSR(vo, 'WorldPosX', 'WorldPosY', 'WorldPosZ', 'ScaleX', 'ScaleY', 'ScaleZ', 'RotateX', 'RotateY', 'RotateZ')
            pass
        else:
            self.printNode(vo)
            raise Exception("Didn't know how to process 3D Object: "+otype)
        pass

    def visitmodel(self, m):
        # This depends bit on model type
        mtype = m.getAttribute('DisplayAs')
        if (mtype == 'Custom' or mtype == 'Window Frame' or mtype == 'Cube' or mtype == 'Vert Matrix' or mtype == 'Horiz Matrix' or mtype == 'Star' or mtype == 'Circle' or mtype == 'Sphere' or mtype == 'Image' or mtype == 'Spinner' or mtype == 'Wreath'):
            self.processPSR(m, 'WorldPosX', 'WorldPosY', 'WorldPosZ', 'ScaleX', 'ScaleY', 'ScaleZ', 'RotateX', 'RotateY', 'RotateZ')
        elif (mtype[0:5] == 'Tree '):
            self.processPSR(m, 'WorldPosX', 'WorldPosY', 'WorldPosZ', 'ScaleX', 'ScaleY', 'ScaleZ', 'RotateX', 'RotateY', 'RotateZ')
        elif (mtype[0:3] == 'Dmx'):
            self.processPSR(m, 'WorldPosX', 'WorldPosY', 'WorldPosZ', 'ScaleX', 'ScaleY', 'ScaleZ', 'RotateX', 'RotateY', 'RotateZ')
        elif (mtype == 'Single Line' or mtype == 'Channel Block'):
            # X2/Y2/T2 is a delta from WPXYZ
            self.processRelPtPair(m, 'WorldPosX', 'WorldPosY', 'WorldPosZ', 'X2', 'Y2', 'Z2')
        elif (mtype == 'Candy Canes'):
            # X2/Y2/T2 is a delta from WPXYZ
            self.processRelPtPair(m, 'WorldPosX', 'WorldPosY', 'WorldPosZ', 'X2', 'Y2', 'Z2')
            # TODO: RotateX, Height, CandyCaneHeight, Angle
        elif (mtype == 'Arches'):
            # X2/Y2/T2 is a delta from WPXYZ
            self.processRelPtPair(m, 'WorldPosX', 'WorldPosY', 'WorldPosZ', 'X2', 'Y2', 'Z2')
            # TODO: RotateX, Height, Angle
        elif (mtype == 'Icicles'):
            # X2/Y2/T2 is a delta from WPXYZ
            self.processRelPtPair(m, 'WorldPosX', 'WorldPosY', 'WorldPosZ', 'X2', 'Y2', 'Z2')
            # TODO: RotateX, Height, Shear
        elif (mtype == 'Poly Line'):
            (wx, wy, wz) = self.get3(m, 'WorldPosX', 'WorldPosY', 'WorldPosZ')
            npts = int(m.getAttribute('NumPoints'))
            pcs = m.getAttribute("PointData").split(",")
            dx = float(pcs[0])
            dy = float(pcs[1])
            dz = float(pcs[2])
            # We will canonicalize these so point 1 is at world X,Y,Z
            wx = wx+dx
            wy = wy+dy
            wz = wz+dz
            (twx, twy, twz) = self.doTx(wx, wy, wz)
            sdata = ""
            for i in range(0, npts):
                x = float(pcs[i * 3 + 0]) - dx
                y = float(pcs[i * 3 + 1]) - dy
                z = float(pcs[i * 3 + 2]) - dz
                # There is a different way to do this, for linear transforms
                (tx, ty, tz) = self.doTx(x+wx, y+wy, z+wz)
                if len(sdata):
                    sdata = sdata + ','
                sdata = sdata + str(tx-twx) + ',' + str(ty-twy) + ',' + str(tz-twz)
            self.set3(m, 'WorldPosX', 'WorldPosY', 'WorldPosZ', twx, twy, twz)
            m.setAttribute('PointData', sdata)
            # TODO: ScaleX, ScaleY, ScaleZ - is this for drops?
        else:
            self.printNode(m)
            raise Exception("Didn't know how to process layout model type: "+mtype)
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='xLights layout parser and transformer')
    parser.add_argument('--layout', type=str, # nargs='+',
                        #nargs = 1,
                        required = True,
                        help='xlights_rgbeffects.xml input file')
    parser.add_argument('--outlayout', type=str, required=False, help='xlights_rgbeffects.xml output')
    parser.add_argument('--transform', type=str, required = False, help='Transformations; semicolon-delimited list of rotx:<value>, roty:<value>, rotz:value, translate:<xvalue,yvalue,zvalue>, scale:<xvalue,yvalue,zvalue>')

    args = parser.parse_args()

    print(args.layout)
    layout = xml.dom.minidom.parse(args.layout)

    TextRemover().removeText(layout)

    if (args.transform):
        txs = []
        txstrs = args.transform.split(';')
        for txstr in txstrs:
            parts = txstr.split(':')
            if (len(parts) != 2):
                raise Exception('transform option is semicolon-delimited list of command:arguments, but found: '+txstr)
            cmd = parts[0]
            carg = parts[1]
            if cmd == 'translate':
                tcs = carg.split(',')
                if len(tcs) != 3:
                    raise Exception('translate option takes x,y,z')
                txs.append(PxTransformTranslate(float(tcs[0]), float(tcs[1]), float(tcs[2])));
                pass
            elif cmd == 'scale':
                tcs = carg.split(',')
                if len(tcs) != 3:
                    raise Exception('translate option takes x,y,z')
                txs.append(PxTransformScale(float(tcs[0]), float(tcs[1]), float(tcs[2])));
                pass
            elif cmd == 'rotx':
                txs.append(PxTransformRotate(float(carg), 0, 0))
                pass
            elif cmd == 'roty':
                txs.append(PxTransformRotate(0, float(carg), 0))
                pass
            elif cmd == 'rotz':
                txs.append(PxTransformRotate(0, 0, float(carg)))
                pass
            else:
                raise Exception("Not a valid command: "+cmd)

        t = LayoutTransformVisitor(txs)
        t.visitRoot(layout)

    if (args.outlayout):
        with open(args.outlayout,"w") as file_handle:
            layout.writexml(file_handle, indent='', addindent='  ', newl='\n', encoding=None, standalone=None)
            file_handle.close()
