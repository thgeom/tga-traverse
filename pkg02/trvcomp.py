from pkg02.util import *

# Class of Traverse points
class TraversePoint:
    aziin = 0.0
    fazi = 0.0
    afazi = 0.0
    cfazi = 0.0
    dEN = (0.0, 0.0)
    cEN = (0.0, 0.0)
    #sf = 1.0
    lsf = 1.0
    #utm = None
    #projto = None
    ll = (0.0, 0.0)
    numbers = 0

    def __init__(self, name, code='TP', pt=(0.0,0.0), z=0.0):
        self.name = name
        self.code = code
        self.P = pt
        self.z = z
        self.sf = 1.0
        TraversePoint.numbers += 1
        #self.sf = proj_dict['CSF']

    def _obsdata(self, horang, dist):
        self.horang = horang                            # Store in DD.MMSSS format
        self.dist = dist
        self.gdist = self.sf * dist

    def calAngular(self, azii):
        self.aziin = azii
        self.fazi = calfwdAzi(self.aziin, deg(self.horang))

    def corAngular(self, misclose_a, totalpoint, trav_no):
        self.cfazi = - (misclose_a / totalpoint * trav_no)
        self.afazi = self.fazi + self.cfazi

    def calLinear(self):
        self.dEN = caldEN(math.radians(self.afazi), self.gdist)

    def calTravPoint(self, prevTrav):
        east = prevTrav.P[0] + prevTrav.dEN[0]
        north = prevTrav.P[1] + prevTrav.dEN[1]
        self.P = (east, north)

    # Calculate of each point using PyProj
    def calSF(self):
        self.ll = proj2.transform(self.P[0], self.P[1])
        self.sf = utm.get_factors(self.ll[0], self.ll[1]).meridional_scale
        #print(self.sf)

    # Calculate the correction of each line
    def corLinear(self, misclose_e, misclose_n, totallength):
        ceast = - (misclose_e / totallength * self.dist)
        cnorth = - (misclose_n / totallength * self.dist)
        self.cEN = (ceast, cnorth)

    # calculate final coordinate
    def adjTravPoint(self, prevTrav):
        east = prevTrav.P[0] + prevTrav.dEN[0] + prevTrav.cEN[0]
        north = prevTrav.P[1] + prevTrav.dEN[1] + prevTrav.cEN[1]
        self.P = (east, north)

# For UTM Scale Factor computation
def setUTMparams(tcp):
    global proj2
    global utm

    proj2 = tcp.projto
    utm = tcp.utm


# Compute line scale factor & recompute delta E, delta N
def applyScaleFactor(tcp, travpoints):
    if tcp.closed_themself:
        travpoints_c = travpoints[1:-1]
    else:
        travpoints_c = travpoints[1:-2]
    i = 1
    for trv in travpoints_c:
        if i==1:
            trv.calSF()                                         # Calculate Scale Factor of 1st point
        travpoints[i+1].calTravPoint(trv)
        travpoints[i+1].calSF()                                    # Calculate Scale Factor of forward point
        if tcp.params_dict['CSF']==1.0:
            trv.lsf = (trv.sf + travpoints[i+1].sf) / 2.0          # calculate Line Scale Factor
            #print('{} : (Long, Lat) = {} -> SF : {:.12f} & LSF : {:.12f}'.format(trv.name, trv.ll, trv.sf, trv.lsf))
        else:
            trv.lsf = tcp.params_dict['CSF']
        trv.gdist = trv.lsf * trv.dist
        trv.calLinear()
        i += 1
    if tcp.params_dict['CSF']!=1.0:
        print('Common Scale Factor : {:.9f} has been applied'.format(tcp.params_dict['CSF']))


# Adjustment computation for Traverse
def traverseAdustment(trvctpar, travpoints):

    #Compute azimuth of each traverse
    i = 1
    for trv in travpoints[1:-1]:
        if i==1:
            trv.calAngular(trvctpar.startAzi)
        else:
            #print(i)
            trv.calAngular(travpoints[i-1].fazi)
        i += 1

    """
    print('>>>Computed Azimuth')
    for trv in travpoints[1:-1]:
        print('@{} Azimuth forward (dd.mmsss) : {:.5f}'.format(trv.name, dms(trv.fazi)))
    """

    #Compute angular Misclosure & azimuth adjustment
    misclose_a = travpoints[-2].fazi - trvctpar.endAzi
    trvctpar.misclosure_a = misclose_a
    trvctpar.total_sta = len(travpoints[1:-1])
    trvctpar.mis_ang_persta = misclose_a / trvctpar.total_sta
    #print(travpoints[-2].fazi, trvctpar.endAzi)
    print('>Angular misclosure (dd.mmsss) : {:.5f}'.format(dms(misclose_a)))
    i = 1
    for trv in travpoints[1:-1]:
        trv.corAngular(misclose_a, len(travpoints[1:-1]), i)
        print('@{} Adj. Azimuth forward (dd.mmsss) : {:.5f}'.format(trv.name, dms(trv.afazi)))
        trv.calLinear()
        #print('Delta E, N of each line (dE, dN) : %.4f, %.4f' % trv.dEN)
        i += 1
    #print('Final Azimuth : {}'.format(dms(trvctpar.endAzi)))
    # Define points of Traverse (Closed / Fixed)
    if trvctpar.closed_themself:
        travpoints_c = travpoints[1:-1]                       # For Closed Traverse themself
    else:
        travpoints_c = travpoints[1:-2]                       # For Traverse connected to Existing Network

    print('>EPSG : {}'.format(trvctpar.EPSG))
    if trvctpar.UTM_COMP:                      ### Apply UTM scale factor
        setUTMparams(trvctpar)                 # Set UTM parameters
        applyScaleFactor(trvctpar, travpoints)

    # Compute linear Misclosure & adjustment
    misclose_e = 0.0
    misclose_n = 0.0
    totallength = 0.0
    for trv in travpoints_c:
        #print(trv.dEN)
        misclose_e += trv.dEN[0]
        misclose_n += trv.dEN[1]
        totallength += trv.gdist
    misclose_e -= trvctpar.dEN[0]                     # Sum dEN - dEN of control points
    misclose_n -= trvctpar.dEN[1]
    trvctpar.misclosureEN = (misclose_e, misclose_n)
    #trvctpar.misclosure = math.sqrt(math.pow(misclose_e,2) + math.pow(misclose_n,2))
    trvctpar.misclosure = (misclose_e ** 2 + misclose_n ** 2) ** 0.5
    trvctpar.totallength = totallength
    trvctpar.accuracy = totallength / trvctpar.misclosure
    #print('Fixed. delta E,N : {}'.format(trvctpar.dEN))
    #print('Misclosure of Traverse (dE,dN) : {}'.format(trvctpar.misclosureEN))
    print('>Misclosure of Traverse (dE,dN) : %.3f, %.3f' % trvctpar.misclosureEN)
    print('>Linear misclosure (m.) : {:.3f}'.format(trvctpar.misclosure))
    print('>Total length of Traverse (m.) : {:.3f}'.format(trvctpar.totallength))
    print('==========================================')
    #print('Accuracy of Traverse : 1 / {:.0f}'.format(trvctpar.accuracy))

    #Compute linear correction
    for trv in travpoints_c:
        trv.corLinear(misclose_e, misclose_n, totallength)

    #Compute final coordinates
    i = 2
    """
    while i<=len(travpoints[1:-1]):
        travpoints[i].adjTravPoint(travpoints[i-1])
        i += 1
    """
    for trv in travpoints[2:-1]:
        trv.adjTravPoint(travpoints[i-1])
        #print('Check @{:9s} E: {:11.3f} N: {:12.3f}'.format(trv.name, trv.P[0], trv.P[1]))
        i += 1
    if trvctpar.closed_themself:
        #pass
        travpoints[-1].P = travpoints[1].P
        travpoints[0].P = travpoints[-2].P


    """
    print('>>>Result of Traverse Coordinates')
    for trv in travpoints:
        print('@{:9s} E: {:11.3f} N: {:12.3f}'.format(trv.name, trv.P[0], trv.P[1]))
        #print(trv)
    """
    # Add result to Control point coordinates
    #trvctpar.addTrv2TCP(travpoints_c)
    return travpoints_c                     # Return new computed point
