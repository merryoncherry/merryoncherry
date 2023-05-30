import copy
import xml.dom.minidom

#
# The goal of this program is to make an xLigts custom model
#  by assembling a central light string and custom models at regular
#  intervals along the way.
#
# You might imagine the simple case of a string of icicles.
#  2 pixels from the end, do a drop down of 7 pixels, then every 5 from that point
#  But why would it have to be an icicle?  It could be a small snoflake, or for
#    Halloween it could be a tombstone or a pumpkin
#
# So, it works this way.
#  We have string parameters.
#    Currently this is based on a linear string, that progresses in a fixed
#      increment for each bulb.  X is across, plus to the right.  Y is vertical, plus is up
#    We need to know how many pixels are in the string
#  We also have prop parameters for each prop.
#    This is everything xlights has for a custom model:
#      Node grid
#      Submodels
#      Groups that contain the model / submodels
#    In addition, we need to know where and how often to put the prop
#      If you say startLinePixel as 2, after 2 line pixels we branch off and do
#        the first model
#      After that, repeat every "repeatEvery" pixels
#      If we are supposed to stop inserting the prop before the end of the
#        string, set maxProps
#    How far to go to pixel 1, relative to the last pixel placed
#    You could scale the custom model.  But this comes down to an integer grid
#      in the end.  So beware.
#  That's the information we need.  Processing goes this way:
#    We're going to make a list of points in order.
#    This means going along the line and processing models as we hit them,
#      then going back to the line
#
#  Making submodels is the next thing.  It explodes, but if you defined them, we will too.
#    We make one submodel called 'string' for the string down the middle
#    For each prop added, we add a submodel called <propName>_<n>, which is just the pixel range in wiring order
#    For each submodel in the prop, we make a submodel called <submodel>_<n>, which is the nth instance of that submodel
#
#  We also make groups for you.
#   If you put the prop model in groups, we put the submodel for each instance of that prop in those groups
#   If you put the submodel of a prop in groups, we put the submodel of each instance of that prop in those groups
#
#  Submodel and group properties reflect the definition we saw in one of the model files

class Group:
    def __init__(self, dom):
        self.name = dom.getAttribute('name') if dom else ""
        self.layout = dom.getAttribute('layout') if dom else ""
        self.layoutGroup = dom.getAttribute('LayoutGroup') if dom else ""
        self.gridSize = dom.getAttribute('GridSize') if dom else ""
        self.models = dom.getAttribute('models').split(',',-1) if dom else []

class Submodel:
    def __init__(self, dom):
        self.name = dom.getAttribute('name') if dom else ""
        self.layout = dom.getAttribute('layout')  if dom else ""
        self.type = dom.getAttribute('type') if dom else ""
        self.versionNumber = dom.getAttribute('versionNumber') if dom else ""
        self.lines = []
        for i in range(9999):
            if not dom:
                break
            l = dom.getAttribute("line"+str(i))
            if (not l):
                break
            self.lines.append(l)

class Prop:
    def __init__(self, dom, offsetX, offsetY, startLinePixel, repeatEvery, maxProps):
        self.pointsById = {}
        self.pointsInOrder = []
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.startLinePixel = startLinePixel
        self.repeatEvery = repeatEvery
        self.maxProps = maxProps
        self.scaleX = 1
        self.scaleY = 1
        n = dom.childNodes[0]
        self.name = n.getAttribute('name')
        self.width = int(n.getAttribute('parm1'))
        self.height = int(n.getAttribute('parm2'))
        self.depth = n.getAttribute('Depth')
        self.stringType = n.getAttribute('StringType')
        self.transparency = n.getAttribute('Transparency')
        self.pixelSize = n.getAttribute('PixelSize')
        self.modelBrightness = n.getAttribute('ModelBrightness')
        self.antialias = n.getAttribute('Antialias')
        self.strandNames = n.getAttribute('StrandNames')
        self.nodeNames = n.getAttribute('NodeNames')
        self.sourceVer = n.getAttribute('SourceVersion')
        modelData = n.getAttribute('CustomModel')
        rows = modelData.split(';', -1)
        rn = 0
        origpix = {}
        for r in rows:
            cols = r.split(',', -1)
            cn = 0
            for c in cols:
                cn = cn + 1
                if c:
                    ln = int(c)
                    origpix[ln] = (rn, cn)
            rn = rn + 1
        spix = sorted(origpix.keys())
        (baser, basec) = origpix[spix[0]]
        pn = 0
        for p in spix:
           self.pointsById[p] = pn
           (pr, pc) = origpix[p]
           self.pointsInOrder.append( (self.offsetX + (pc-basec)*self.scaleX, self.offsetY + (baser-pr)*self.scaleY ) )
           pn = pn + 1
        self.submodels = []
        for smn in n.getElementsByTagName('subModel'):
            self.submodels.append(Submodel(smn))
        self.groups = []
        for grn in n.getElementsByTagName('modelGroup'):
            self.groups.append(Group(grn))

def generatePT(directionX, directionY, linePixels, mname, props):
    propCounts = []
    points = []
    submodelInstances = {}

    curPx = 0
    nProps = 0
    curX = 0.0
    curY = 0.0

    propNexts = []
    submodels = []
    groupsByName = {}

    for p in props:
        propNexts.append(p.startLinePixel)
        propCounts.append(0)
        for g in p.groups:
            if g.name not in groupsByName:
                ng = copy.deepcopy(g)
                ng.models = []
                groupsByName[ng.name] = ng

    linepx = ''
    while 1:
        for i in range(len(propNexts)):
            if propNexts[i] == curPx:
                if propCounts[i] >= props[i].maxProps:
                    continue

                startpt = len(points)

                # Handle the points this generates
                prop = props[i]
                for pt in prop.pointsInOrder:
                    (px, py) = pt
                    points.append( (curX+px, curY+py) )

                # Generate a submodel for it
                psm = Submodel(None)
                basename = prop.name
                if basename not in submodelInstances:
                    submodelInstances[basename] = 0
                submodelInstances[basename] = submodelInstances[basename] + 1
                psm.name = basename+"_"+str(submodelInstances[basename])
                psm.layout = "horizontal"
                psm.type = "ranges"
                psm.bufferstyle = "Default"
                psm.versionNumber = "5"
                psm.lines.append(str(startpt+1)+'-'+str(len(points)))
                submodels.append(psm)

                # Place submodel in appropriage groups if the basename is there
                for g in prop.groups:
                    if prop.name in g.models:
                        groupsByName[g.name].models.append("EXPORTEDMODEL/"+psm.name)

                # Generate the other submodels
                for s in prop.submodels:
                    ns = copy.deepcopy(s)
                    if s.name not in submodelInstances:
                        submodelInstances[s.name] = 0
                    submodelInstances[s.name] = submodelInstances[s.name] + 1
                    # Generate name
                    ns.name = s.name + "_"+str(submodelInstances[s.name])
                    # Massage the lines
                    ns.lines = []
                    for l in s.lines:
                        parts = l.split(',', -1)
                        np = []
                        for p in parts:
                            ranges = p.split('-', -1)
                            nr = []
                            for r in ranges:
                                nr.append(str(int(r)+startpt))
                            np.append('-'.join(nr))
                        ns.lines.append(','.join(np))

                    submodels.append(ns)

                    # Place those in groups
                    for g in prop.groups:
                        if "EXPORTEDMODEL/"+s.name in g.models:
                            groupsByName[g.name].models.append("EXPORTEDMODEL/"+ns.name)

                propCounts[i] = propCounts[i] + 1
                nProps = nProps + 1
                propNexts[i] = curPx + props[i].repeatEvery
        curPx = curPx + 1
        if curPx > linePixels:
            break
        curX += directionX
        curY += directionY
        points.append( (curX, curY) )
        if (len(linepx)) :
            linepx = linepx + ","
        linepx += str(len(points))

    print ('Total Points: ', len(points), ".  Total Props: ", nProps)

    # Now we bound these points
    (minx, miny) = points[0]
    (maxx, maxy) = points[0]
    for p in points:
        (px, py) = p
        minx = min(minx, px)
        miny = min(miny, py)
        maxx = max(maxx, px)
        maxy = max(maxy, py)

    w = int(maxx-minx) + 1
    h = int(maxy-miny) + 1

    data = []
    for r in range(h):
        data.append([])
        for c in range(w):
            data[-1].append(-1)

    pn = 0
    for p in points:
        (x, y) = p
        c = int(x-minx)
        r = int(y-miny)
        pn = pn + 1
        data[r][c] = pn;

    data.reverse()
    dstr = ""
    for r in data:
        if (len(dstr)):
            dstr = dstr + ';'
        rstr = ""
        cn = 0
        for c in r:
            if (c >= 0):
                rstr += str(c)
            if (cn < len(r)-1):
                rstr = rstr + ','
            cn = cn + 1
        dstr = dstr + rstr

    # Make a new document
    od = xml.dom.minidom.Document()
    mn = od.createElement("custommodel")
    cp = props[0]
    mn.setAttribute("name", mname)
    mn.setAttribute('parm1', str(w))
    mn.setAttribute('parm2', str(h))
    mn.setAttribute('Depth',  cp.depth)
    mn.setAttribute('StringType', cp.stringType)
    mn.setAttribute('Transparency', cp.transparency)
    mn.setAttribute('PixelSize', cp.pixelSize)
    mn.setAttribute('ModelBrightness', cp.modelBrightness)
    mn.setAttribute('Antialias', cp.antialias)
    #mn.setAttribute('StrandNames', ...)
    #mn.setAttribute('NodeNames', ...)
    mn.setAttribute('SourceVersion', cp.sourceVer)
    mn.setAttribute('CustomModel', dstr)

    # Make a submodel for the string
    stn = od.createElement("subModel")
    stn.setAttribute('name', 'string')
    stn.setAttribute('layout', 'horizontal')
    stn.setAttribute('type', 'ranges')
    stn.setAttribute('bufferstyle', 'default')
    stn.setAttribute('line0', linepx)
    mn.appendChild(stn)

    # Write out the submodels
    for s in submodels:
        sn = od.createElement("subModel")
        sn.setAttribute('name', s.name)
        sn.setAttribute('layout', s.layout)
        sn.setAttribute('type', s.type)
        sn.setAttribute('versionNumber', s.versionNumber)
        for i in range(len(s.lines)):
            sn.setAttribute("line"+str(i), s.lines[i])
        mn.appendChild(sn)

    # Make the groups
    for g in groupsByName:
        grp = groupsByName[g]
        gn = od.createElement("modelGroup")
        gn.setAttribute('name', grp.name)
        gn.setAttribute('layout', grp.layout)
        gn.setAttribute('LayoutGroup', grp.layoutGroup)
        gn.setAttribute('GridSize', grp.gridSize)
        gn.setAttribute('models', ','.join(grp.models))
        mn.appendChild(gn)

    od.appendChild(mn)

    # Write output file
    with open(mname+".xmodel","w") as outfile:
        od.writexml(outfile)


######## Main Routine #############

# This is the direction the string builds
# This can be arbitrary.  I'm working in inches, 1/2" resolution
directionX = -2
directionY = 0
linePixels = 84
mname = "HalloweenRailPixelTrim7ft"

props = []

# This loads the prop
#  offsetX, offsetY, startLinePixel, repeatEvery, maxProps
with open('PixelTrimTomb.xmodel', newline='') as modelfile:
    dom = xml.dom.minidom.parse(modelfile)
    props.append(Prop(dom, -4, -3, 19, 22, 3))

with open('PixelTrimPumpkin.xmodel', newline='') as modelfile:
    dom = xml.dom.minidom.parse(modelfile)
    props.append(Prop(dom, 0, -5, 10, 22, 4))

generatePT(directionX, directionY, linePixels, mname, props)

####

mname = "HalloweenRailPixelTrim4ft"
directionX = -2
directionY = 0
linePixels = 50

props = []

with open('PixelTrimTomb.xmodel', newline='') as modelfile:
    dom = xml.dom.minidom.parse(modelfile)
    props.append(Prop(dom, -4, -3, 18, 22, 2))

with open('PixelTrimPumpkin.xmodel', newline='') as modelfile:
    dom = xml.dom.minidom.parse(modelfile)
    props.append(Prop(dom, 0, -5, 9, 22, 2))

generatePT(directionX, directionY, linePixels, mname, props)

####

mname = "HalloweenRailPixelTrim9ft"
directionX = -2
directionY = 0
linePixels = 105

props = []

with open('PixelTrimTomb.xmodel', newline='') as modelfile:
    dom = xml.dom.minidom.parse(modelfile)
    props.append(Prop(dom, -4, -3, 18, 22, 4))

with open('PixelTrimPumpkin.xmodel', newline='') as modelfile:
    dom = xml.dom.minidom.parse(modelfile)
    props.append(Prop(dom, 0, -5, 9, 22, 5))

generatePT(directionX, directionY, linePixels, mname, props)




