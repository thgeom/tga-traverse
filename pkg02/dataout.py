import pandas as pd
import csv
import datetime
from pkg02.util import *

# Class Trav4Xls to prepare Traverse data for Excel file
class Trav4OutFile:
    def __init__(self, fdir, fout):
        self.fdir = fdir
        self.fout = fout
        self.xlsname = fdir + fout
        self.csvname = ''
        self.xlsdata = []
        self.csvtab = None

    # Add Traverse data to the object for Excel exporting
    def trv4Xls(self, trvpoints, tcp):
        j = 0
        for i in trvpoints:
            if tcp.UTM_COMP:
                if j==0 or j==len(trvpoints[0:-1]):
                    self.xlsdata.append([i.name, None, None, None, None, None, None, None, None, None, None, None, i.P[0], i.P[1], i.name])
                else:
                    self.xlsdata.append([i.name, d_m_s(i.horang,0), None, None, None, None, None, None, None, None, None, None, i.P[0], i.P[1], i.name])
                lsf = i.lsf
                if j==0 or j==len(trvpoints[0:-2]):
                    lsf = None
                fazi = d_m_s(dms(i.fazi))
                afazi = d_m_s(dms(i.afazi))
                if j==0: afazi = None
                if j==len(trvpoints[0:-1]):
                    fazi = None
                    afazi = None
                self.xlsdata.append([None, None, fazi, i.cfazi*3600, afazi, i.dist, lsf, i.gdist, i.dEN[0], i.cEN[0], i.dEN[1], i.cEN[1], None, None, None])
            else:
                #self.xlsdata.append([i.name, i.horang, dms(i.fazi), i.cfazi*3600, dms(i.afazi), i.dist, i.dEN[0], i.cEN[0], i.dEN[1], i.cEN[1], i.P[0], i.P[1], i.name])
                if j==0 or j==len(trvpoints[0:-1]):
                    self.xlsdata.append([i.name, None, None, None, None, None, None, None, None, None, i.P[0], i.P[1], i.name])
                else:
                    self.xlsdata.append([i.name, d_m_s(i.horang, 0), None, None, None, None, None, None, None, None, i.P[0], i.P[1], i.name])
                if j==len(trvpoints[0:-1]):
                    self.xlsdata.append([None, None, None, None, None, None, None, None, None, None, None, None, None])
                else:
                    afazi = d_m_s(dms(i.afazi))
                    if j==0:
                        afazi = None
                        self.xlsdata.append([None, None, d_m_s(dms(i.fazi)), i.cfazi*3600, afazi, None, None, None, None, None, None, None, None])
                    else:
                        self.xlsdata.append([None, None, d_m_s(dms(i.fazi)), i.cfazi*3600, afazi, i.gdist, i.dEN[0], i.cEN[0], i.dEN[1], i.cEN[1], None, None, None])
            j += 1
        # End for
        if not tcp.closed_themself:
            for ir, row in enumerate(self.xlsdata):                        # Clear 0.0 content
                for ic, col in enumerate(row):
                    if col==0.0:
                        self.xlsdata[ir][ic] = None


    # Writing data to Excel file using Pandas Data Frame
    # The Traverse Control Parameters & Traverse data have been utilized
    def writeXlsFile(self, tcp):
        success = False
        srow = 8
        pparams_dict = tcp.params_dict
        if tcp.UTM_COMP:
            df = pd.DataFrame(self.xlsdata, columns=['Station', 'Hor.Ang (dd-mm-ss)', 'Azimuth', 'cor.Azi (ss)', 'Adj.Azi', 'Distance (m)', 'SF', 'Grid Dist. (m)', 'Departure', 'cor.E', 'Latitude', 'cor.N', 'East', 'North', 'Station']) # DataFrame to Excel
            scol = 8
        else:
            df = pd.DataFrame(self.xlsdata, columns=['Station', 'Hor.Ang (dd-mm-ss)', 'Azimuth', 'cor.Azi (ss)', 'Adj.Azi', 'Distance (m)', 'Departure', 'cor.E', 'Latitude', 'cor.N', 'East', 'North', 'Station']) # DataFrame to Excel
            scol = 6

        #writer = pd.ExcelWriter(self.fdir + self.fout, mode='w')
        try:
            writer = pd.ExcelWriter(self.xlsname, mode='w')
        except:
            msg = 'Excel File : {} : is in used.!!!'.format(self.xlsname)
            msg += '\nPlease close it, then process again.'
            #show_message(msg)    # Case file is inused
            warn_message(msg, tcp.batch)    # Case file is inused
            #sys.exit(1)
            #os._exit(os.O_RDONLY)
            writer = None

        # Set the column width and format (General / UTM)
        def bodyOut():
            worksheet.set_column(1, 13, 9, font_name_format)
            worksheet.set_column('C:C', 9.5, azi_format)
            worksheet.set_column('D:D', 9.5, azi_format)
            worksheet.set_column('F:F', 9.5, azi_format)
            worksheet.set_column('G:K', 9, dist_format)
            worksheet.set_column('I:I', 6)
            worksheet.set_column('K:K', 6)
            worksheet.set_column('L:M', 12.5, EN_format)
            worksheet.set_column('E:E', 6, cazi_format)
            worksheet.set_column('B:B', 10, name_format)
            worksheet.set_column('N:N', 10, name_format)

        # Define inner function
        def utmbodyOut():
            worksheet.set_column(1, 13, 9, font_name_format)
            worksheet.set_column('C:C', 9.5, azi_format)
            worksheet.set_column('D:D', 9.5, azi_format)
            worksheet.set_column('F:F', 9.5, azi_format)
            worksheet.set_column('G:M', 9, dist_format)
            worksheet.set_column('H:H', 9.5, sf_format)
            worksheet.set_column('K:K', 6)
            worksheet.set_column('M:M', 6)
            worksheet.set_column('N:O', 12.5, EN_format)
            worksheet.set_column('E:E', 6, cazi_format)
            worksheet.set_column('B:B', 10, name_format)
            worksheet.set_column('P:P', 10, name_format)

        def pr_title_foot():
            # Set the row height and format.
            nrow = len(self.xlsdata) + 1
            for i in range(nrow):                                    # Set row height
                if (i % 2) == 0:
                    worksheet.set_row(srow + i, 12)
                else:
                    worksheet.set_row(srow + i, 14)

            # Add a header format.
            worksheet.set_row(srow, 34)
            header_format = workbook.add_format({'bold': True, 'valign': 'top', 'font_size': 12,
                                                 'font_name': font_style,
                                                 'bottom': 2, 'align': 'center', 'text_wrap': True,
                                                 'bg_color': '#D0E6A5'})     # '#B2CA34', '#F9DA04'
            last_record_format = workbook.add_format({'bold': 0, 'valign': 'bottom', 'font_size': 12,
                                                      'font_name': font_style,
                                                      'top': 2})

            # Write the column headers with the defined format.
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(srow, col_num + 1, value, header_format)
            # Write the column last record with the defined format.
            frow = nrow + srow
            for col_num in range(df.columns.size):
                worksheet.write(frow, col_num + 1, None , last_record_format)

            #df['Name'] = df['Name'].map('{12:s}'.format)
            #Print summation of length, correction E&N
            worksheet.write(frow-1, scol-1, 'Sum')
            worksheet.write_number(frow-1, scol, tcp.totallength, dist_format)
            worksheet.write_number(frow-1, scol+2, -round(tcp.misclosureEN[0], 3), dist_format)
            worksheet.write_number(frow-1, scol+4, -round(tcp.misclosureEN[1], 3), dist_format)

            #Print footer
            for i in range(8):
                worksheet.set_row(frow+i, 14, footer_format)
            #worksheet.write(frow+1, 5, '++++++++++++++++++++++++++++++++++++++++++')
            worksheet.write(frow+1, 5, 'Angular misclosure of Traverse : {:.1f} second'.format(tcp.misclosure_a*3600))
            worksheet.write(frow+2, 5, 'Misclosure of Traverse (errE, errN) : %.3f, %.3f' % tcp.misclosureEN)
            worksheet.write(frow+3, 5, 'Linear misclosure : ({:.3f}^2 + {:.3f}^2)^1/2 = {:.3f} meters'.format(tcp.misclosureEN[0], tcp.misclosureEN[1], tcp.misclosure))
            worksheet.write(frow+4, 5, 'Total length : {:.3f} meters'.format(tcp.totallength))
            worksheet.write(frow+5, 5, 'Accuracy of Traverse : 1 / {:.0f}'.format(tcp.accuracy))
            #worksheet.write(frow+6, 5, 'Computed Date : {}'.format(datetime.datetime.now().date()))

            #Print Title
            worksheet.write(0, scol, 'T R A V E R S E   C O M P U T A T I O N', title_format)
            worksheet.write(1, scol, 'Project : {}'.format(pparams_dict['ProjName']), title_format)
            worksheet.write(2, scol, 'Owner : {}'.format(pparams_dict['Organization']), title_format)
            worksheet.write(4, 1, 'From station : {}'.format(tcp.startname1), title2_format)
            worksheet.write(4, scol, 'To station : {}'.format(tcp.endname2), title2_format)
            worksheet.write(4, scol+6, 'Location : {}'.format(pparams_dict['Location']), title2_format)
            worksheet.write(5, 1, 'Angular misclosure : {:.1f} second'.format(tcp.misclosure_a*3600), title2_format)
            worksheet.write(5, scol, 'Linear misclosure : {:.3f} meters'.format(tcp.misclosure), title2_format)
            #worksheet.write(5, scol+6, 'Zone : {},  EPSG : {}'.format(tcp.UTM_Zone, tcp.mapParams.epsg), title2_format)
            worksheet.write(5, scol+6, 'Projection EPSG : {}'.format(tcp.EPSG), title2_format)
            worksheet.write(6, 1, 'Number of station : {:d}'.format(tcp.total_sta), title2_format)
            worksheet.write(6, scol, 'Total length : {:.3f} meters'.format(tcp.totallength), title2_format)
            worksheet.write(6, scol+6, 'Computed by : {}'.format(pparams_dict['Compute']), title2_format)
            worksheet.write(7, 1, 'Angle per station : {:.1f} second'.format(tcp.mis_ang_persta*3600), title2_format)
            worksheet.write(7, scol, 'Accuracy : 1 / {:.0f}'.format(tcp.accuracy), title2_format)
            worksheet.write(7, scol+6, 'Computed Date : {}'.format(datetime.datetime.now().date()), title2_format)

        # Case of writer is OK
        if writer!=None:
            df.to_excel(writer, sheet_name='Traverse_Comp', startrow=srow)
            workbook = writer.book
            #print(dir(workbook))
            worksheet = workbook.sheetnames['Traverse_Comp']
            #worksheet = workbook.get_worksheet_by_name('Traverse_Comp')   # Get worksheet by name

            font_style = 'Arial Narrow'
            # Add some cell formats.
            font_name_format = workbook.add_format({'font_name': font_style})
            sf_format = workbook.add_format({'num_format': '#0.00000000', 'font_name': font_style})
            azi_format = workbook.add_format({'align': 'right', 'font_name': font_style})
            #format1a = workbook.add_format({'num_format': '#0.0000', 'font_name': font_style})
            #format1a = workbook.add_format({'align': 'right', 'font_name': font_style})
            dist_format = workbook.add_format({'num_format': '#0.000', 'font_name': font_style})
            EN_format = workbook.add_format({'num_format': '#0.000', 'bold': True, 'font_name': font_style})
            cazi_format = workbook.add_format({'num_format': '#0.0', 'font_name': font_style})
            name_format = workbook.add_format({'align': 'left', 'bold': True, 'font_name': font_style})
            #format5 = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100', 'font_size': 14})
            footer_format = workbook.add_format({'font_size': 12, 'font_name': font_style})
            title_format = workbook.add_format({'align': 'left', 'bold': True, 'font_size': 14, 'font_name': font_style})
            title2_format = workbook.add_format({'align': 'left', 'bold': True, 'font_size': 11, 'font_name': font_style})
            # Print body table of traverse computation
            if tcp.UTM_COMP:
                utmbodyOut()
            else:
                bodyOut()

            # Print header & footer
            pr_title_foot()
            # Close the Pandas writer and the Excel file.
            writer.save()
            success = True                              # Write to Excel file OK
        return success

    def trv4CSV(self, travpoints_c, tcp):
        self.csvtab = tcp.cpctab
        #self.show_csvdata()
        for pt in self.csvtab.values:
            #pass
            pt[1] = round(pt[1], 3)
            pt[2] = round(pt[2], 3)
            #pt[4] = pt[4] + ' '
        #if trvctpar.params_dict['CPF_Append']:
        for trv in travpoints_c[1:]:
            #cp_rec = {'NAME':trv.name, 'EAST':'{:8.3f}'.format(trv.P[0]), 'NORTH':'{:8.3f}'.format(trv.P[1]), 'ELEV':0.0, 'CODE':'CTP', 'UTM':self.UTM_Zone}
            #cp_rec = {'NAME':trv.name, 'EAST':trv.P[0], 'NORTH':trv.P[1], 'ELEV':'-', 'CODE':'CTP', 'UTM':self.UTM_Zone}
            cp_rec = {'NAME':trv.name, 'EAST':round(trv.P[0],3), 'NORTH':round(trv.P[1],3), 'ELEV':trv.z, 'CODE':trv.code, 'UTM':tcp.UTM_Zone}

            #print('Result : {}'.format(cp_rec))
            self.csvtab = self.csvtab.append(cp_rec, ignore_index=True)
        self.show_csvtab()

    def show_csvtab(self):
        print('>>>Result of Travers Point Coordinates')
        print(self.csvtab.to_string(index=False))


    # Write result of Traverse computation to CSV file
    def writeCSV(self, tcp):
        success = False
        fdir = tcp.params_dict['WorkDirectory']
        fname = tcp.params_dict['ControlPointFile']
        pathname = fdir + fname
        if not tcp.params_dict['CPF_Append']:
            dloc = pathname.find('.')
            pathname = pathname[:dloc] + '-r' + pathname[dloc:]
        self.csvname = pathname
        df = self.csvtab
        #df = self.cpctab.applymap(lambda x: '{:8s}'.format(str(x)))
        #df = df.applymap(lambda x: '{:8s}'.format(str(x)))
        df = df.applymap(lambda x: '{:<4s}'.format(str(x)) if type(x)==str else '{:5.3f} '.format(x))
        df.columns = df.columns.map(lambda x: '{:^6s}'.format(str(x)))

        #print(df)
        try:
            #df.to_csv(pathname, sep=' ', quoting=csv.QUOTE_MINIMAL, quotechar=' ', index=False, float_format='%.3f ') # Write to file without ""
            df.to_csv(self.csvname, sep=' ', quoting=csv.QUOTE_MINIMAL, quotechar=' ', index=False) # Write to file without ""
            #df.to_csv(pathname, sep=' ', index=False)
            success = True
        except:
            msg = 'CSV File : {} : is in used.!!!'.format(self.csvname)
            warn_message(msg)
        return success
