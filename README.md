# tga-traverse
# This program read project parameter file (.par)
# :pparams.par is an example file
"""
{
"ProjName" : "Learning Community",
"Location" : "UdonThani Province",
"Organization" : "Community Section 1",
"Compute" : "TGA",
"CSF" : 1.00000,
"EPSG" : 32647,
"WorkDirectory" : "d:/TGA_TEST/CB/",
"ControlPointFile" : "travlbr2.csv",
"CPF_Columns" : ["Name", "East", "NORTH", "ELEV", "Code", "UTM"],  #List of required column name, case insensitive
"CPF_Append" : False,
"ObservDataFile" : "trav-1.csv",
"ODF_Columns" : ["Name", "HorAng", "HorDist"],
"OutputFile" : "Trav-1_out2.xlsx",
"StartAzimuth" : 0.0
}
"""
# From parameter file 
# the working directory, control point file and observation data file have been defined as
# "WorkDirectory", "ControlPointFile" and "ObservDataFile"; the example files are included (travlbr2.csv & trav-1.csv)
# For traverse adjustmet, compass rule has been used in computation processes.
# The Excel file report shall be generated as a rusult of computation (as defined by "OutputFile") 
