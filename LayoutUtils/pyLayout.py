# Python module implementing transformations of the xLights rgbeffects XML file.
#  The original intent was 3D transformations of the layout, bulk edits, having multiple
#   show configurations in the same file, etc.
#
# This module is nothing special, nothing you wouldn't have written yourself
#     if you only had the time.  You may therefore use this under:
#
#   Unlicense (http://unlicense.org/)
#     or
#   Creative Commons CC0 (https://creativecommons.org/publicdomain/zero/1.0/legalcode)

import argparse
import math
import re
import sys
import textwrap
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
        #self.printNode(mg)
        pass

    def visitmodelGroups(self, n):
        if (n.attributes):
            raise Exception("Unexpected attributes in node tag: "+n.tagName)
        for mg in n.childNodes:
            if mg.nodeType == xml.dom.Node.ELEMENT_NODE:
                self.visitmodelGroup(mg)

    def visitmodel(self, m):
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

class Selection(Visitor):
    def __init__(self):
        self.models = {}
        self.groups = {}
        self.objs = {}
        self.resolveGroups = False
        self.resolveNames = {} # Searching this iteration
        self.nextResolveNames = {} # To find next iteration
        self.resolvedNames = {} # Found past iterations
        self.seltyp = ''
        self.selval = ''
        self.layout = None

    def select(self, layout, sel):
        # Do initial selection
        ss = sel.split('=')
        self.seltyp = ss[0]
        if (len(ss) > 1):
            self.selval = ss[1]
        self.layout = layout
        self.visitRoot(layout)
        # Resolve group members
        while self.nextResolveNames:
            self.resolveGroups = True
            self.resolveNames = self.nextResolveNames
            self.nextResolveNames = {}
            self.visitRoot(layout)
            self.resolveGroups = False

    def addGroup(self, g):
        self.groups[g.getAttribute('name')] = g

    def addObject(self, o):
        self.objs[o.getAttribute('name')] = o

    def addModel(self, m):
        self.models[m.getAttribute('name')] = m

    def visitmodelGroup(self, g):
        if (self.resolveGroups):
            on = g.getAttribute('name')
            if on in self.resolveNames:
                if on in self.resolvedNames:
                    return
                self.resolvedNames[on] = on
                self.addGroup(g)
                for n in g.getAttribute('models').split(','):
                    nn = n.split('/')[0]
                    if nn not in self.resolvedNames and nn not in self.resolveNames:
                        self.nextResolveNames[nn] = nn
            return;
        if (self.seltyp.lower() == 'type' and self.selval.lower() == 'group'):
            self.addGroup(g)
            return
        if (self.seltyp.lower() == 'group' and re.match(self.selval, g.getAttribute('name'))):
            self.addGroup(g)
            return
        if (self.seltyp.lower() == 'ingroup' and re.match(self.selval, g.getAttribute('name'))):
            for n in g.getAttribute('models').split(','):
                nn = n.split('/')[0]
                self.nextResolveNames[nn] = nn
            return
        if ((self.seltyp.lower() == 'tagcolour' or self.seltyp.lower() == 'tagcolor') and g.hasAttribute('TagColour') and g.getAttribute('TagColour') == self.selval):
            self.addGroup(g)
            return
        pass

    def visitview_object(self, o):
        if (self.seltyp.lower() == 'type' and (self.selval.lower() == 'obj' or self.selval.lower() == o.getAttribute('DisplayAs').lower())):
            self.addObject(o)
            return
        if (self.seltyp.lower() == 'obj' and re.match(self.selval, o.getAttribute('name'))):
            self.addObject(o)
            return
        if (self.seltyp.lower() == 'inactiveobj' and o.hasAttribute('Active') and o.getAttribute('Active') == '0'):
            self.addObject(o)
            return
        pass

    def visitmodel(self, m):
        if (self.resolveGroups):
            on = m.getAttribute('name')
            if on in self.resolveNames:
                if on in self.resolvedNames:
                    return
                self.resolvedNames[on] = on
                self.addModel(m)
            return;
        if (self.seltyp.lower() == 'type' and (self.selval.lower() == 'model' or self.selval.lower() == m.getAttribute('DisplayAs').lower())):
            self.addModel(m)
            return
        if (self.seltyp.lower() == 'model' and re.match(self.selval, m.getAttribute('name'))):
            self.addModel(m)
            return
        if (self.seltyp.lower() == 'inactivemodel' and m.hasAttribute('Active') and m.getAttribute('Active') == '0'):
            self.addModel(m)
            return
        if ((self.seltyp.lower() == 'tagcolour' or self.seltyp.lower() == 'tagcolor') and m.hasAttribute('TagColour') and m.getAttribute('TagColour') == self.selval):
            self.addModel(m)
            return
        pass
#Model=<regex>, Group=<regex>, Obj=<regex>, TagColor=r,g,b, InactiveModel, InactiveObj, Type=<type>


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
        if (otype == 'Image' or otype == 'Terrian' or otype == 'Mesh'):
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

class Mutator:
    def __init__(self):
        pass

    def printNode(self, n):
        print(n.toprettyxml())

    def visitmodelGroup(self, mg):
        #self.printNode(mg)
        return True

    def visitmodelGroups(self, n):
        # Go through models/groups/objs and delete stuff
        if (n.attributes):
            raise Exception("Unexpected attributes in node tag: "+n.tagName)
        removes = []
        for mg in n.childNodes:
            if mg.nodeType == xml.dom.Node.ELEMENT_NODE:
                if not self.visitmodelGroup(mg):
                    removes.append(mg)
        for m in removes:
            mg.removeChild(m)
            m.unlink()

    def visitmodel(self, m):
        return True

    def visitmodels(self, n):
        # Go through and delete stuff from 'models'
        if (n.attributes):
            raise Exception("Unexpected attributes in node tag: "+n.tagName)
        removes = []
        for m in n.childNodes:
            if m.nodeType == xml.dom.Node.ELEMENT_NODE:
                if not self.visitmodel(m):
                    removes.append(m)
        for m in removes:
            n.removeChild(m)
            m.unlink()

    def visitview_object(self, vo):
        return True

    def visitview_objects(self, n):
        # Go through models/groups/objs and delete stuff
        if (n.attributes):
            raise Exception("Unexpected attributes in node tag: "+n.tagName)
        removes = []
        for vo in n.childNodes:
            if vo.nodeType == xml.dom.Node.ELEMENT_NODE:
                if not self.visitview_object(vo):
                    removes.append(vo)
        for vo in removes:
            n.removeChild(vo)
            vo.unlink()
        pass

    def visitView(self, n):
        return True

    def visitViews(self, n):
        # Clean up views - remove models/groups that we just removed
        if (n.attributes):
            raise Exception("Unexpected attributes in node tag: "+n.tagName)
        removes = []
        for vi in n.childNodes:
            if vi.nodeType == xml.dom.Node.ELEMENT_NODE:
                if not self.visitView(vi):
                    removes.append(vi)
        for vi in removes:
            n.removeChild(vi)
            vi.unlink()
        pass

    def visitxrgb(self, n):
        if (n.tagName != 'xrgb'):
            raise Exception('Root not "xrgb"')
        for attrName, attrValue in n.attributes.items():
            raise Exception('Root "xrgb" unexpected attribute "'+attrName+'"')
        for cn in n.childNodes:
            if (cn.nodeType == xml.dom.Node.ELEMENT_NODE):
                if (cn.tagName == 'colors'):
                    pass
                elif (cn.tagName == 'effects'):
                    pass
                elif (cn.tagName == 'layoutGroups'):
                    pass
                elif (cn.tagName == 'modelGroups'):
                    self.visitmodelGroups(cn)
                elif (cn.tagName == 'models'):
                    self.visitmodels(cn)
                elif (cn.tagName == 'palettes'):
                    pass
                elif (cn.tagName == 'perspectives'):
                    pass
                elif (cn.tagName == 'settings'):
                    pass
                elif (cn.tagName == 'views'):
                    self.visitViews(cn);
                elif (cn.tagName == 'view_objects'):
                    self.visitview_objects(cn)
                elif (cn.tagName == 'Viewpoints'):
                    pass
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

class Deleter(Mutator):
    def __init__(self):
        self.sel = None
        self.layout = None
        pass

    def pruneList(self, mlist):
        nm = ""
        for mn in mlist.split(','):
            pmn = mn.split('/')[0]
            if pmn in self.sel.models:
                continue
            if pmn in self.sel.groups:
                continue
            if pmn in self.sel.objs:
                continue
            if nm:
                nm = nm + ','
            nm = nm + mn
        return nm

    def visitmodelGroup(self, mg):
        if mg.getAttribute('name') in self.sel.groups:
            return False # delete
        #filter
        om = mg.getAttribute('models')
        nm = self.pruneList(om)
        mg.setAttribute('models', nm)
        return True

    def visitmodel(self, m):
        return m.getAttribute('name') not in self.sel.models

    def visitview_object(self, o):
        return o.getAttribute('name') not in self.sel.objs

    def visitView(self, v):
        om = v.getAttribute('models')
        nm = self.pruneList(om)
        v.setAttribute('models', nm)
        return True

    def delete(self, layout, sel):
        self.sel = sel
        self.visitRoot(layout)

class ValidNameBuilder(Visitor):
    def __init__(self):
        self.validNames = {}

    def visitmodelGroup(self, g):
        self.validNames[g.getAttribute('name')] = 1

    def visitmodel(self, m):
        self.validNames[m.getAttribute('name')] = 1;
        # Visit submodels
        for sm in m.childNodes:
            if sm.nodeType != xml.dom.Node.ELEMENT_NODE:
                continue
            if sm.tagName == 'subModel':
                self.validNames[m.getAttribute('name') + '/' + sm.getAttribute('name')] = 1

class GroupMemberChecker(Visitor):
    def __init__(self, validNames):
        self.validNames = validNames

    def visitmodelGroup(self, g):
        if not g.getAttribute('models'):
            return
        for n in g.getAttribute('models').split(','):
            if n not in self.validNames:
                print("WARNING: group '"+g.getAttribute('name')+"' contains reference to '"+n+"', which does not exist")

    def visitview(self, v):
        if not v.getAttribute('models'):
            return
        for n in v.getAttribute('models').split(','):
            if n not in self.validNames:
                print("WARNING: view '"+v.getAttribute('name')+"' contains reference to '"+n+"', which does not exist")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=textwrap.dedent('''\
        xLights layout file processing, for bulk editing and transforming layout elements,
            in ways tough to accomplish with xLights by itself.

        Not all operations will leave your layout in a consistent state, and beware networks
            xml file is not updated.  Keep lots of backup copies.

        General overview:
            Layout is read in from --layout
            If --transform was asked to perform 3D transformations, perform them
            If --edit was specified, perform edits
            If --outlayout was specified, write the resulting layout to a file


        Edits: semicolon-delimited list of edits to make.
        Each edit of is <selection>:<action>:<arguments>.

        selection is one of:
        --------------------------------
            Model=<regex>
            Group=<regex>
            InGroup=<regex>
            Obj=<regex>
            TagColour=rgb(r, g, b)
            InactiveModel
            InactiveObj
            Type=<type>
            
        Action/arguments is one of:
        --------------------------------
            active:<true/false> - Sets the active checkbox
            brighten:<percent, less than 100%% is darken> - This is the appearance, not what is sent to the controller
            setbrightness:value - This is the appearance brightness, not what is sent to controller
            dimcurveall:<brightness,gamma> - set the brightness (+/- 100)/gamma for all colors together
            dimcurvergb:<red_bright,red_gamma,green_bright,green_gamma,blue_bright,blue_gamma> - per-color dim curve
            delete:true - This will remove models from the layout
        '''),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--layout', type=str, # nargs='+',
                        #nargs = 1,
                        required = True,
                        help='xlights_rgbeffects.xml input file')
    parser.add_argument('--outlayout', type=str, required=False, help='xlights_rgbeffects.xml output')
    parser.add_argument('--transform', type=str, required=False, help='Transformations; semicolon-delimited list of rotx:<value>, roty:<value>, rotz:value, translate:<xvalue,yvalue,zvalue>, scale:<xvalue,yvalue,zvalue>')
    parser.add_argument('--edit', type=str, required=False, help='''Edits: semicolon-delimited list of edits to make.  Each edit of is <selection>:<action>:<arguments>; see description above.''')

    args = parser.parse_args()

    print(args.layout)
    layout = xml.dom.minidom.parse(args.layout)

    TextRemover().removeText(layout)

    vnb = ValidNameBuilder()
    vnb.visitRoot(layout)
    gchk = GroupMemberChecker(vnb.validNames)
    gchk.visitRoot(layout)

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

    if (args.edit):
        edstrs = args.edit.split(';')
        for editstr in edstrs:
            parts = editstr.split(':')
            if (len(parts) != 3):
                raise Exception('edit option is semicolon-delimited list select:command:arg, but found: '+editstr)
            sel = parts[0]
            cmd = parts[1]
            cmdarg = parts[2]
            s = Selection()
            s.select(layout, sel)

            if (cmd.lower() == 'brighten' or cmd.lower() == 'darken'):
                bs = float(cmdarg)
                for x in s.objs.values():
                    bright = 100.0
                    if (x.hasAttribute('Brightness')):
                        bright = float(x.getAttribute('Brightness'))
                    x.setAttribute('Brightness', str(bright*bs / 100))
                for x in s.models.values():
                    bright = 100.0
                    if (x.hasAttribute('Brightness')):
                        bright = float(x.getAttribute('Brightness'))
                    x.setAttribute('Brightness', str(bright*bs / 100.0))

            if (cmd.lower() == 'dimcurveall'):
                cparts = cmdarg.split(',')
                if (len(cparts) != 2):
                    raise Exception('dimcurveall requires brightness,gamma')
                for x in s.models.values():
                    dcs = x.getElementsByTagName('dimmingCurve')
                    for dc in dcs:
                        x.removeChild(dc)
                        dc.unlink
                    ndc = layout.createElement('dimmingCurve')
                    ndca = layout.createElement('all')
                    ndca.setAttribute('brightness',cparts[0])
                    ndca.setAttribute('gamma',cparts[1])
                    ndc.appendChild(ndca)
                    x.appendChild(ndc)

            if (cmd.lower() == 'dimcurvergb'):
                cparts = cmdarg.split(',')
                if (len(cparts) != 6):
                    raise Exception('dimcurvergb requires brightness,gamma x3 (r,g,b)')
                for x in s.models.values():
                    dcs = x.getElementsByTagName('dimmingCurve')
                    for dc in dcs:
                        x.removeChild(dc)
                        dc.unlink
                    ndc = layout.createElement('dimmingCurve')
                    ndcr = layout.createElement('red')
                    ndcr.setAttribute('brightness',cparts[0])
                    ndcr.setAttribute('gamma',cparts[1])
                    ndc.appendChild(ndcr)
                    ndcg = layout.createElement('green')
                    ndcg.setAttribute('brightness',cparts[2])
                    ndcg.setAttribute('gamma',cparts[3])
                    ndc.appendChild(ndcg)
                    ndcb = layout.createElement('blue')
                    ndcb.setAttribute('brightness',cparts[4])
                    ndcb.setAttribute('gamma',cparts[5])
                    ndc.appendChild(ndcb)
                    x.appendChild(ndc)

            if (cmd.lower() == 'active'):
                val = '1'
                if (cmdarg == '0' or cmdarg.lower()[0] == 'f'):
                    val = '0'
                for x in s.objs.values():
                    x.setAttribute('Active', val)
                for x in s.models.values():
                    x.setAttribute('Active', val)

            if (cmd.lower() == 'delete' and (cmdarg.lower()[0] == 't' or cmdarg[0] == '1')):
                dlt = Deleter()
                dlt.delete(layout, s)

    if (args.outlayout):
        with open(args.outlayout,"w") as file_handle:
            layout.writexml(file_handle, indent='', addindent='  ', newl='\n', encoding=None, standalone=None)
            file_handle.close()
