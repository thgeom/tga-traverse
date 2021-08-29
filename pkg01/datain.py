from os import path
import pandas as pd

# Class of Control Point  Coordinates from CSV file
class ControlPointCoords:
    dtformat = False
    def __init__(self, fdir, fname):
        self.fdir = fdir
        self.fname = fname
        self.pathname = fdir + fname

    def getdata(self, tcp):                                              # sep='\s+', to define separator
        file_exist = True
        self.cpctab = None
        try:
            if not path.exists(self.pathname):
                msg = 'File : {} : does not exist.!!!'.format(self.pathname)
                msg += '\nPlease check \"ControlPointFile\" in Parameter File'
                warn_message(msg)
                file_exist = False
                sys.exit(1)
            """
            cpctab = pd.read_csv(self.pathname, encoding='utf-8', sep='\s+',
                                      usecols=['Name', 'North', 'East', 'Elev', 'Code', 'UTM'])[['Name','East','North','Elev','Code','UTM']]
            """
            df = pd.read_csv(self.pathname, encoding='utf-8', sep='\s+')    # Read data from file
            df = df.rename(columns=lambda x: x.upper())                 # Convert Column names to upper case
            dfcolnames = list(df.columns)
            #print(df)
            #colnames = ['Name', 'East', 'North', 'Elev', 'Code', 'UTM'] # List of required Columns
            #colnames = tcp.params_dict['CPF_Columns']
            colnames = tcp.cpf_colnames
            colnames = [x.upper() for x in colnames]
            is_colexist = True
            for col in colnames:                                # Check the required Column Name exist?
                if not (col in dfcolnames):
                    is_colexist = False
                    warn_message('{} : does not exist in Control Point File \n-> {}'.format(col, self.pathname))
                    #sys.exit(1)
                    return
            if is_colexist:
                df = df.filter(items=colnames)
            self.cpctab = df
            self.dtformat = True
        except:
            #sys.exit('File : {} : incorrect format.!!!'.format(self.pathname))
            if file_exist:
                warn_message('File : {} : incorrect format.!!!'.format(self.pathname))
            #self.cpctab = None

    def show_data(self):
        print('>>>Control Point Coordinates')
        print(self.cpctab.to_string(index=False))

# Class of Traverse observation data from CSV file
class TravDataCSV:
    dtformat = False
    def __init__(self, fdir, fname):
        self.fdir = fdir
        self.fname = fname
        self.pathname = fdir + fname

    def getdata(self, tcp):                                              # sep='\s+', to define separator
        file_exist = True
        self.travtab = None
        try:
            if not path.exists(self.pathname):
                msg = 'File : {} : does not exist.!!!'.format(self.pathname)
                msg += '\nPlease check \"ObservDataFile\" in Parameter File'
                warn_message(msg)
                file_exist = False
                sys.exit(1)
            """
            travtab = pd.read_csv(self.pathname, encoding='utf-8', sep='\s+',
                                      usecols=['Name','HorAng','HorDist'])[['Name','HorAng','HorDist']]
            """
            df = pd.read_csv(self.pathname, encoding='utf-8', sep='\s+')
            df = df.rename(columns=lambda x: x.upper())
            dfcolnames = list(df.columns)
            #print(df)
            #colnames = ['Name','HorAng','HorDist']
            #colnames = tcp.params_dict['ODF_Columns']
            colnames = tcp.odf_colnames
            colnames = [x.upper() for x in colnames]
            is_colexist = True
            for col in colnames:                                # Check the required Column Name exist?
                if not (col in dfcolnames):
                    is_colexist = False
                    warn_message('{} : does not exist in Observation Data File \n-> {}'.format(col, self.pathname))
                    sys.exit(1)
            if is_colexist:
                df = df.filter(items=colnames)
            self.travtab = df
            self.dtformat = True
        except:
            if file_exist:
                warn_message('File : {} : incorrect format.!!!'.format(self.pathname))
            #self.travtab = None


    def show_data(self):
        print('>>>Observation Data')
        #print(self.travtab.head(20))
        print(self.travtab.to_string(index=False))
