from pyproj import CRS, Transformer, Proj
from pkg02.util import *


# UTM parameter
crs_UTM47 = CRS.from_epsg(32647)        # WGS84 UTM zone47
crs_UTM48 = CRS.from_epsg(32648)        # WGS84 UTM zone47
crs_WGS84 = CRS.from_epsg(4326)         # WGS84
crs_75UTM47 = CRS.from_epsg(24047)      # IND75 UTM zone47
crs_75UTM48 = CRS.from_epsg(24048)      # IND75 UTM zon
crs_IND75 = CRS.from_epsg(4240)         # IND75
EPSG = 32647                            # Default = UTM-WGS84

# Class of Traverse Control Parameters
# To define environment of Traverse Computation
class TravControlParams:
    misclosure_a = 0.0
    mis_ang_persta = 0.0
    misclosureEN = ()
    misclosure = 0.0
    total_sta = 0
    totallength = 0.0
    accuracy = 1.0
    closed_themself = False
    UTM_COMP = False
    UTM_Zone = '-'
    EPSG = None
    #infilename = ''

    def __init__(self, proj_dict):
        self.params_dict = proj_dict
        self._initparams()

    def setStartEndPoints(self, startname1, startname2, endname1, endname2):
        self.startname1 = startname1
        self.startname2 = startname2
        self.endname1 = endname1
        self.endname2 = endname2

    # Set parameters of Traverse
    def _initparams(self):
        try:
            self.cpf_colnames = self.params_dict['CPF_Columns']
            self.odf_colnames = self.params_dict['ODF_Columns']
            self.EPSG = self.params_dict['EPSG']
        except:
            self.cpf_colnames = ['Name', 'East', 'North', 'Elev', 'Code', 'UTM']
            self.odf_colnames = ['Name','HorAng','HorDist']
            self.EPSG = self.params_dict['EPSG']
        self.setMapProjection()

    # Set Map parameters
    def setMapProjection(self):
        epsg = self.EPSG
        if epsg!=None:
            self.crs = CRS.from_epsg(epsg)
            self.utm = Proj(self.crs)
            self.projto = Transformer.from_crs(self.crs, crs_WGS84, always_xy=True)
        else:
            self.EPSG = ''

    # Find Control points from library & compute their parameters
    def computeTCPdata(self, cpc):
        startPoint = True
        not_found = nf1 = nf2 = nf3 = nf4 = False
        zone = self.UTM_Zone
        self.cpctab = cpc.cpctab
        colnames = self.cpf_colnames
        colnames = [x.upper() for x in colnames]
        e_cn = colnames.index('EAST')
        n_cn = colnames.index('NORTH')
        self.startP1 = [pt for pt in cpc.cpctab.values if self.startname1 in pt]
        if self.startP1==[]:
            print('{} not found in Control Point file.'.format(self.startname1))
            nf1 = True
        self.startP2 = [pt for pt in cpc.cpctab.values if self.startname2 in pt]
        if self.startP2==[]:
            print('{} not found in Control Point file.'.format(self.startname2))
            startPoint = False
            nf2 = True
        self.endP1 = [pt for pt in cpc.cpctab.values if self.endname1 in pt]
        if self.endP1==[]:
            print('{} not found in Control Point file.'.format(self.endname1))
            nf3 = True
        self.endP2 = [pt for pt in cpc.cpctab.values if self.endname2 in pt]
        if self.endP2==[]:
            print('{} not found in Control Point file.'.format(self.endname2))
            nf4 = True
        not_found = nf1 or nf2 or nf3 or nf4
        if not_found and startPoint:
            if (self.startname1==self.endname1 and self.startname2==self.endname2) and startPoint:
                self.closed_themself = True
                self.startP = (self.startP2[0][e_cn], self.startP2[0][n_cn])
                self.endPo = (self.endP2[0][e_cn], self.endP2[0][n_cn])
                #startAzi = input('Enter Azimuth {} -> {} (dd.mmsss) : '.format(self.startname1, self.startname2))
                startAzi = self.params_dict['StartAzimuth']
                self.startAzi = deg(float(startAzi))
                self.startP = (self.startP2[0][e_cn], self.startP2[0][n_cn])
                self.endAzi = self.startAzi
                self.dEN = (0.0, 0.0)
                zone = self.startP2[0][-1]
            else:
                msg = 'Please check Name of Control Point.[CPF & ODF]!!!'
                warn_message(msg)
                return startPoint and not not_found

        if not not_found:
            self.startPo = (self.startP1[0][e_cn], self.startP1[0][n_cn])
            self.startP = (self.startP2[0][e_cn], self.startP2[0][n_cn])
            self.endP = (self.endP1[0][e_cn], self.endP1[0][n_cn])
            self.endPo = (self.endP2[0][e_cn], self.endP2[0][n_cn])
            self.startAzi = azimuth(self.startPo, self.startP)
            self.startAzi = math.degrees(self.startAzi)
            self.endAzi = azimuth(self.endP, self.endPo)
            self.endAzi = math.degrees(self.endAzi)
            self.dEN = (self.endP[0] - self.startP[0], self.endP[1] - self.startP[1])
            zone = self.startP2[0][-1]

        if (zone=='Z47' or zone=='Z48') and (self.EPSG!=''):
            self.UTM_COMP = True
            self.UTM_Zone = zone
            #self.setMapProjection()
            #print('UTM Zone : {}'.format(zone))
        return startPoint

    def updateTCP(self):
        #self.startP1 = self.endP1
        self.endP2 = self.startP2


    def showTCPdata(self):
        if not self.closed_themself:
            print('>>>List of Traverse control points')
            print('1st Control @Start: {}'.format(self.startP1[0][:-2]))
            print('2nd Control @Start: {}'.format(self.startP2[0][:-2]))
            print('1st Control @End: {}'.format(self.endP1[0][:-2]))
            print('2nd Control @End: {}'.format(self.endP2[0][:-2]))
        else:
            self.updateTCP()
            print('Control @Start: {}'.format(self.startP2[0][:-2]))

        print('Start Azimuth (dd.mmsss) : {:.5f}'.format(dms(self.startAzi)))
        print('End Azimuth (dd.mmsss) : {:.5f}'.format(dms(self.endAzi)))
        #print('Angular misclosure of Traverse : {:.1f} second'.format(self.misclosure_a*3600))
        #print('Delta E, Delta N of Traverse : {}'.format(self.dEN))
        #print('Delta E, Delta N of Traverse : %.3f, %.3f' % self.dEN)           # Format of list
        #print('Total length : {:.3f} meteres'.format(self.totallength))
        #print('Linear misclosure of Traverse : {:.3f} meters'.format(self.misclosure))
        #print('Accuracy of Traverse : 1 / {:.0f}'.format(self.accuracy))


