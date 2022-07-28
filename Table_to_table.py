#example 1

import arcpy
arcpy.env.workspace = "C:/"
arcpy.TableToTable_conversion(".dbf", "C:/", "")

#example 2

# Description: Use TableToTable with an expression to create a subset
# of the original table.

# Import system modules
import arcpy

#Set environment settings
arcpy.env.workspace = "C:/"

# Set local variables
inTable = ".dbf"
outLocation = "C:/output/output"
outTable = "e"

# Set the expression, with help from the AddFieldDelimiters function, to select
# the appropriate field delimiters for the data type
expression = arcpy.AddFieldDelimiters(arcpy.env.workspace, "NAME_") + " = 'e'"

# Execute TableToTable
arcpy.TableToTable_conversion(inTable, outLocation, outTable, expression)
