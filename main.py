#=========================================================================
# This program shall be used for Traverse adjustment, then send output to Excel file
# Developed by Boonlerd Nitiwattananon, E-mail: boonlerd.niti@gmail.com
# This program can be used and modified for any purpose
# *** Concept of this program ***
# There are 3 data files for Traverse computation
# 1.Project parameter file
# 2.Control points coordinates file
# 3.Observation data file
# From these 3 files the program will create Traverse Control Parameters object to manipulate all data,
# the Compass Rule method has been used for linear misclosure adjustment,
# then make a report in the Excel file format
# GUI using TKinter
# Version beta release on August 6, 2021
# August 9, 2021
# Add feature of CSV file output for result of computation
# by create writeCSV method in TraverseControlParams using pandas DataFrame "df.to_csv"
# August 12, 2021
# Modify flow control of file existing checking & data file format checking
# August 24, 2021
# Rearrange code into python project with 2 packages
# Try to learn package & module
# August 28, 2021
# Review code for calling from package to package and rearrange modules
#=========================================================================

# Import necessary modules
import sys
#from os import path
import getopt
import base64
import urllib.error
from urllib.request import urlopen
from tkinter import filedialog as fd


# Import own package
#import pkg01.tcp
from pkg01.datain import *
from pkg01.tcp import *
from pkg02.trvcomp import *
from pkg02.dataout import *

batch = False
inputfile = ''
proj_dic = {}
#ctrdir = 'd:/TGA_Lisp/'
ctrdir = ''


#==========
# Create instance for Control Point Coordinates
def getCPC(fdir, fcpc, tcp):
    cpc = ControlPointCoords(fdir, fcpc)
    cpc.getdata(tcp)                                                       # Get data from csv file
    return cpc

# Create instance for traverse data
def getTrvData(fdir, ftrv, tcp):
    trv = TravDataCSV(fdir, ftrv)
    trv.getdata(tcp)                                                       # Get data from csv file
    return trv



#==================
def main(argv):
    global inputfile
    global proj_dict
    global batch

    batch = False
    progName = 'Traverse Computation V.[\u03B2]'
    trvFrm = Tk()
    trvFrm.title("Welcome to THGeom Academy")
    trvFrm.geometry('565x495')                  # Size ('WidthxHeight')
    trvFrm.geometry('+400+100')                 # Position ('+Left+Top')
    #trvFrm.configure(background='#FFFFFF')      # Set background color
    #trvFrm.configure(background='#AAFFFF')
    #my_img = PhotoImage(file = "D:/usr/bnn/ABSC/Project/MAP4BD/Make_App_Prog/Python/THGA_Logo5_254x254.png")
    try:
        #image_url = "https://thgeomacademy.files.wordpress.com/2021/07/thga_logo5_200x200.png"
        image_url = "https://thgeomacademy.files.wordpress.com/2021/07/tga_281x214.png"
        image_byt = urlopen(image_url).read()
        image_b64 = base64.encodebytes(image_byt)
        my_img = PhotoImage(data = image_b64)
        l2 = Label(trvFrm,  image=my_img)
        l2.grid(row=0,column=2)
    except urllib.error.URLError:
        trvFrm.geometry('565x310')
        Label(trvFrm, text='***** THGeom Academy *****', width=25, font=('Arial', 18)).grid(row=0, column=2)

    Label(trvFrm, text=progName, width=40, font=('Arial', 16)).grid(row=2, column=2)
    print(progName)
    Label(trvFrm, text='Compass Rule Method', width=40, font=('Arial', 12)).grid(row=4, column=2)
    #statusbox(trvFrm,'Compass Rule Method', 4)

    # Check argument from command line
    def is_cmdline():
        global inputfile
        global outputfile_a

        batch = False
        inputfile = 'projParams.par'
        outputfile = 'travout-x.xlsx'
        inputfile_a, outputfile_a = '', ''
        #print('argv : {}'.format(argv))
        try:
            opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
        except getopt.GetoptError:
            print('usage: trav.exe -i <inputfile> -o <outputfile>')
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                msg = 'usage: trav.exe -i <inputfile> -o <outputfile>'
                print(msg)
                #show_message(msg)
                sys.exit()
            elif opt in ("-i", "--ifile"):
                inputfile_a = arg
            elif opt in ("-o", "--ofile"):
                outputfile_a = arg
        #print('-i : {}'.format(inputfile_a))
        if inputfile_a != '':
            inputfile = inputfile_a
            batch = True
            if not path.exists(inputfile):
                print('File : {} : does not exist.!!!'.format(inputfile))
                sys.exit()
        return batch
    # End is_cmdline

    # For select button
    def selectfile():
        global inputfile
        global proj_dict

        #proj_dict = {}
        inputfile = ''
        #Label(trvFrm, text='{}'.format(inputfile), width=40, bg='#FFFFFF').grid(row=6, column=2)
        labelfile.config(text='{}'.format(inputfile), width=50, bg='#FFFFFF')
        #labelfile['text'] = '{}'.format(inputfile)
        for label_i in labels:
            label_i.config(text='{}'.format(inputfile), width=40)
        inputfile = fd.askopenfilename(title='Select Parameter File')
        if inputfile!='':
            #Label(trvFrm, text='File : {} : selected'.format(inputfile), width=40, bg='#D0E6A5').grid(row=6, column=2)
            labelfile.config(text='File : {} : selected'.format(inputfile), width=len(inputfile)+22, font=('CordiaUPC', 14, 'bold'), bg='#D0E6A5', fg='#000000')
            # Get Project parameters as global variable
            proj_dict = getProjParams(ctrdir, inputfile)               # Dictionary of Project parameters

            if proj_dict=={}:
                #Label(trvFrm, text='File : {} : incorrect format'.format(inputfile), width=40, bg='#FFE6A5').grid(row=6, column=2)
                labelfile.config(text='File : {} : ***incorrect format'.format(inputfile), width=len(inputfile)+25, font=('CordiaUPC', 15, 'italic'), bg='#FF0000', fg='#FFFFFF')
                ok_button['state'] = DISABLED
            else:
                ok_button['state'] = NORMAL
        else:
            ok_button['state'] = DISABLED
        #ctrfile = ctrdir + inputfile
    # End selectfile

    # To process computation
    def doprocess():
        if outputfile_a != '':
            outputfile = outputfile_a
        else:
            outputfile = proj_dict['OutputFile']

        statusbox(labels[0],'Processing...', 8)
        # Create points from from observation data
        travpointx = []
        for trv in trvdata.travtab.values:
            trvpt = TraversePoint(trv[0])                           # Create Traverse point instance
            trvpt._obsdata(trv[1], trv[2])                          # Assign observation data
            travpointx.append(trvpt)                                # Append traverse point to list

        """
        #print('>>>Observation data')
        #print(travpointx)
        for trv in travpointx:
            print('{:9s} {:10.5f} {:10.3f}'.format(trv.name, trv.horang, trv.dist))
        """

        # Detect Name of Control points
        cnameStart1 = travpointx[0].name             # From Traverse observation data
        cnameStart2 = travpointx[1].name             # 2 Started points shall be Control points
        cnameEnd1 = travpointx[-2].name              # 2 Ended points shall be  Control points too
        cnameEnd2 = travpointx[-1].name


        # Setting traverse control parameters
        tcp.setStartEndPoints(cnameStart1, cnameStart2, cnameEnd1, cnameEnd2)   # Set Traverse Control Points
        tcpok = tcp.computeTCPdata(cpc)
        # Look up coordinate of control point and calculate necessary parameters
        # if any incorrect parameter  tcpok will be False
        if not tcpok:
            msg = '*** Incorrect Traverse Parameter!!! \nPlease check the previous messages'
            warn_message(msg, batch)
            return                                  # Exit this method
        if tcp.closed_themself:
            travpointx[0].fazi = tcp.startAzi
            travpointx[1].P = tcp.startP
            #travpointx[-1].P = tcp.startPo
        else:
            travpointx[0].P = tcp.startPo                        # Set 1st Control point coordinate @Startt
            travpointx[0].fazi = tcp.startAzi
            travpointx[1].P = tcp.startP                         # Set 2nd Control point coordinate
            travpointx[-2].P = tcp.endP                          # Set 3rd Control point coordinate @End
            travpointx[-2].fazi = tcp.endAzi
            travpointx[-1].P = tcp.endPo                         # Set 4th Control point coordinate

        tcp.showTCPdata()           # Print Control points
        #tcp.UTM_COMP = True
        if not batch:
            statusbox(labels[2],'Adjustment', 10)
        # Call adjustment method
        travpnts_c = traverseAdustment(tcp, travpointx)  # For adjustment & return new computed pnts

        outfileobj = Trav4OutFile(workdir, outputfile)   # Create instance for Excel
        outfileobj.trv4CSV(travpnts_c, tcp)
        outfileobj.trv4Xls(travpointx, tcp)
        csvok = outfileobj.writeCSV(tcp)                            # Write result coordinate to CSV
        #print(outfileobj.data)
        xlsok = outfileobj.writeXlsFile(tcp)                     # Write output to Excel file
        if xlsok and csvok:
            #statusbox(trvFrm,'Completed.', 12)
            if not batch:
                labels[3].config(text='Completed.', width=40, font=('Tahoma', 12), fg='#65B017')
                labels[3].grid(row=12, column=2)
            #print('Output File : {} : has been created.'.format(xlsobj.pathname))
            msg = 'Accuracy of Traverse : 1 / {:.0f}'.format(tcp.accuracy) + '\n\n'
            msg += 'CSV File : {} :  and'.format(outfileobj.csvname) + '\n'
            msg += 'Excel File : {} : have been created.'.format(outfileobj.xlsname)
            show_message(msg, batch)
    # End doprocess

    # For continue button
    def tocontinue():
        global trvdata
        global cpc
        global tcp
        global workdir
        if inputfile!='':
            #trvFrm.quit()
            workdir = proj_dict['WorkDirectory']
            tcp = TravControlParams(proj_dict)   # Create instance of Traverse Control Parameters

            obsdatafile = proj_dict['ObservDataFile']   # proj_dict["ObservDataFile"] = 'Loop-1.csv'
            if batch:
                print('Observation Data File : {}'.format(obsdatafile))
            else:
                statusbox(labels[1],'Observation Data File : {}'.format(obsdatafile), 9)

            ### To be modified 2021-08-10
            # Get Traverse data from file
            trvdata = getTrvData(workdir, obsdatafile, tcp)
            if not trvdata.dtformat:
                selectfile()
            else:
                trvdata.show_data()
                # Create Monument Control Points
                cpc = getCPC(workdir, proj_dict['ControlPointFile'], tcp)                            # Read Control point file
                if not cpc.dtformat:
                    selectfile()
                else:
                    cpc.show_data()

            if trvdata.dtformat and cpc.dtformat:
                doprocess()
        else:
            msg = 'Please select a Project Parameter file!!!'
            show_message(msg)
    # End tocontinue

    # Create blank labels to display status
    labels = []
    for nr in [8, 9, 10, 12]:
        label_i = Label(trvFrm, text='', width=40)
        label_i.grid(row=nr, column=2)
        labels.append(label_i)

    # Check is command line
    batch = is_cmdline()
    #print('batch : {}'.format(batch))
    # Case of command line as batch process
    if batch:
        if not path.exists(inputfile):
            sys.exit('File : {} : does not exist.!!!'.format(inputfile))
        else:
            proj_dict = getProjParams(ctrdir, inputfile)               # Dictionary of Project parameters
            if proj_dict=={}:
                sys.exit('File : {} : ***incorrect format.'.format(inputfile))
            tocontinue()
        sys.exit()

    # Check inputfile exist?, if not display dialog to select one
    if not path.exists(inputfile):
        #inputfile = fd.askopenfilename(title='Select Parameter File')
        inputfile = ''
        labelfile = Label(trvFrm, text='', width=40)   # To display the selected Project Parameter file
        #labelfile.pack()
        labelfile.grid(row=6, column=2)

        sel_button = Button(trvFrm, text=" Select Parameter File ", bg='#ADC865', font=('Arial Black', 9), command=selectfile)
        #sel_button.pack()
        sel_button.grid(row=5, column=2)

        ok_button = Button(trvFrm, text=' Continue ', font=('Arial Black', 9), state=DISABLED, command=tocontinue)
        #ok_button.pack()
        ok_button.grid(row=7, column=2)

    #print(trvFrm.children)
    if trvFrm.children=={}:                         # Check GUI trvFrm terminated?
        sys.exit('Terminated by user.')
    trvFrm.mainloop()


if __name__ == "__main__":
    if len(sys.argv)>1:
        main(sys.argv[1:])
    else:
        main(sys.argv)
