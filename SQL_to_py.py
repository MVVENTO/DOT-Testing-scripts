ActivePython 2.7.18.4 (ActiveState Software Inc.) based on
Python 2.7.18.4 (default, Aug  9 2021, 23:37:24) [MSC v.1500 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> 

import os
import arcpy
from arcpy import env
arcpy.env.overwriteOutput = True
from datetime import datetime
import pyodbc
import pandas as pd

startTime = datetime.now()

#connect to sql database
connection_string = ("Driver={SQL Server};""Server=DOT55SQLAL03;""Database=Facilities;""UID=Facilities_user;""PWD=tF)Q>klj4=!(>)!>;")
connection = pyodbc.connect(connection_string)
print("connected to sql database")

# Get the tblCubicleChart in dataframe
data = pd.read_sql('SELECT * FROM tblCubicleChart', connection)
data.to_excel('Z:/PMA/Facilities Portal/MXDs/Spreadsheets/tblCubicleChart.xlsx', sheet_name='tblCubicleChart', index = False)

#convert spreadsheet to table in geodatabase
arcpy.ExcelToTable_conversion(Input_Excel_File="Z:/PMA/Facilities Portal/MXDs/Spreadsheets/tblCubicleChart.xlsx",
                              Output_Table="Z:/PMA/Facilities Portal/MXDs/FloorPlanJune2018_SecondEdits.gdb/tblCubicleChart",
                              Sheet="tblCubicleChart")
print "finished converting spreadsheet to table in a geodatabase"


'''
My jupyter notebook/Anaconda environment is not the same as the environment that IDLE (Python 2.7 for ArcGIS) is pointing to. To check for the existing libraries that IDLE has access to, 
1.	Open the Command Prompt (not Anaconda Prompt)
2.	Type in this command to change your directory  cd C:\Python27\ArcGIS10.8\Scripts
3.	To check existing libraries, type in this command  pip list
4.	If it doesn’t have the library you need (in my case, pyodbc), you can type a command along the lines of the following  pip install pyodbc
'''