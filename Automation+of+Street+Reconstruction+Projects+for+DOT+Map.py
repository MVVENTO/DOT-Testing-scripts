
# coding: utf-8

# In[39]:

import pandas as pd
import numpy as np
#import archook
#archook.get_arcpy()
import arcpy
from datetime import datetime
# import XTools Pro toolbox
arcpy.ImportToolbox("C:/Program Files (x86)/XTools/XTools Pro/Toolbox/XTools Pro.tbx")

#this is to count how long the script takes to generate output
startTime = datetime.now()
# In[2]:

# read in latest Actuals as df
actualsdf = pd.read_excel(r'Z:\PMA\TerriChan\GIS Projects\Historical Commitments\Data\Actuals\J. Actuals FY2001-FY2022 as of 05.02.22.xlsx',sheetname='ACTUALS FY2001-FY2022')


# In[3]:

actualsdf


# In[4]:

actuals_strecon = actualsdf[actualsdf['DIVISION'].isin(['Street Reconstruction'])]
actuals_strecon


# In[5]:

pivot = pd.pivot_table(actuals_strecon, index=['PROJ ID'], aggfunc=np.sum) ###
pivot


# In[6]:

# strip out whitespace in column names
pivot.rename(columns=lambda x: x.strip(),inplace=True)


# In[7]:

# reset the index so that PROJ ID is a column
pivot = pivot.reset_index()
pivot


# In[8]:

pivot = pivot[['PROJ ID','FY01','FY02','FY03','FY04','FY05','FY06','FY07','FY08','FY09','FY10','FY11','FY12','FY13','FY14','FY15','FY16','FY17','FY18','FY19','FY20','FY21']]


# In[9]:

pivot.info()


# In[10]:

pivot


# In[11]:

# read in CapPlan
#plandf = pd.read_excel(r'Z:\PMA\TerriChan\GIS Projects\Historical Commitments\Street_Reconstruction\Street Reconstruction- April 2019 Capital Plan.xlsx',sheetname='DIVISION')
plandf = pd.read_excel(r'Z:\PMA\TerriChan\GIS Projects\Historical Commitments\Data\CapitalPlan\April Plan 2022\April 2022 Plan.xlsx',sheetname='DIVISION')


# In[12]:

plandf


# In[13]:

plandf = plandf[plandf['DIVISION'].isin(['Street Reconstruction'])]


# In[14]:

tbl_plan = pd.pivot_table(plandf,index=['PROJ ID'],aggfunc=np.sum)
tbl_plan


# In[15]:

tbl_plan = tbl_plan[['FY22','FY23','FY24','FY25','FY26','FY27','FY28','FY29','FY30','FY31']]


# In[16]:

# multiply all the dollar amts in the Cap Plan by 1000 to get actual amts
tbl_plan = tbl_plan * 1000


# In[17]:

tbl_plan


# In[18]:

# reset the index so that PROJ ID can be a column
tbl_plan2 = tbl_plan.reset_index()
tbl_plan2


# In[19]:

merge = pivot.merge(tbl_plan2,how='outer',left_on='PROJ ID',right_on='PROJ ID',indicator=True)
merge


# In[20]:

# since the merge caused the FY fields to turn to float, for FY01 to FY31 cols, fill in the NaNs with 0 and change type from float to int
for i in range(1,32):
    if i < 10:
        #print 'FY0'+str(i)
        merge['FY0'+str(i)] = merge['FY0'+str(i)].fillna(0).astype(int)
    else:
        #print 'FY'+str(i)
        merge['FY'+str(i)] = merge['FY'+str(i)].fillna(0).astype(int)


# In[21]:

merge.info()


# In[22]:

# change the data type of FY01-FY31 from float to int
'''
for i in range(1,32):
    if i < 10:
        merge['FY0'+str(i)] = merge['FY0'+str(i)].astype(int)
    else:
        merge['FY'+str(i)] = merge['FY'+str(i)].astype(int)
'''

# In[23]:

#merge.info()


# In[24]:

# create a column for AgencyCode and FMSID2
merge[['AgencyCode','FMSID2']] = merge['PROJ ID'].str.split(" ",1,expand=True)


# In[25]:

merge[['AgencyCode','FMSID2']]


# In[26]:

merge


# In[27]:

merge.info()


# In[ ]:

merge.to_csv(r'Z:\PMA\TerriChan\GIS Projects\Historical Commitments\Street_Reconstruction\streetreconstruction_actuals_20220502_apr2022plan_outermerge.csv')


# ### Join the combined Actuals and Capital Plans to SDE PWMS Layers

# In[28]:

# set workspace
arcpy.env.workspace = r"Z:\PMA\TerriChan\GIS Projects\Historical Commitments\Street_Reconstruction\Data\Street_Reconstruction_Projects_for_DOT_Map.gdb"


# In[29]:

arcpy.env.overwriteOutput = True


# In[30]:

# connect to PWMS Layers
pwms_blocks = r"Database Connections\PWMS on dotgissql01.sde\PWMS.dbo.ProjectLocationBlock"
pwms_blocks


# In[31]:

pwms_ints = r"Database Connections\PWMS on dotgissql01.sde\PWMS.dbo.ProjectLocationIntersection"
pwms_ints


# In[33]:

actuals_capplan = r'Z:\PMA\TerriChan\GIS Projects\Historical Commitments\Street_Reconstruction\streetreconstruction_actuals_20220502_apr2022plan_outermerge.csv'


# In[36]:

#type(actuals_capplan)


# In[34]:

# export csv to table in file gdb using Table to Table conversion tool
arcpy.conversion.TableToTable(actuals_capplan,arcpy.env.workspace,"streetreconstruction_actuals_capplan")


# In[35]:

# create feature layer from the PWMS ProjectLocationBlock layer
arcpy.MakeFeatureLayer_management(pwms_blocks,"pwms_blocks_lyr")

# create feature layer from the PWMS ProjectLocationIntersection layer
arcpy.MakeFeatureLayer_management(pwms_ints,"pwms_intersections_lyr")

# In[36]:

# join the Actuals/Capital plan file to pwms_blocks, export out join to workspace
arcpy.AddJoin_management("pwms_blocks_lyr","FMSID","streetreconstruction_actuals_capplan","FMSID2","KEEP_COMMON")
########## need to edit this. add the FMSID field to include agency code in the pwms blocks layer....do i need to then duplicate the records with FMSID that has more than one agency code?

# join the Actuals/Capital plan file to pwms_ints, export out join to workspace
arcpy.AddJoin_management("pwms_intersections_lyr","FMSID","streetreconstruction_actuals_capplan","FMSID2","KEEP_COMMON")

# In[37]:

#pwms blocks join is exported out as feature class
arcpy.CopyFeatures_management("pwms_blocks_lyr","PWMS_Blocks")

#pwms intersections join is exported out as feature class
arcpy.CopyFeatures_management("pwms_intersections_lyr","PWMS_Intersections")

# In[44]:

# alter the field names using ModifyTable from XTools Pro.
#arcpy.XToolsGP_ModifyTable_xtp
arcpy.XToolsGP_ModifyTable_xtp(r"Z:/PMA/TerriChan/GIS Projects/Historical Commitments/Street_Reconstruction/Data/Street_Reconstruction_Projects_for_DOT_Map.gdb/PWMS_Blocks","Z:/PMA/TerriChan/GIS Projects/Historical Commitments/Street_Reconstruction/Data/Street_Reconstruction_Projects_for_DOT_Map.gdb/PWMS_Blocks_ModifyTable1","Z:\PMA\TerriChan\GIS Projects\Historical Commitments\Street_Reconstruction\dataset_pwms_blocks_schema.xml","#","#","#","DO_NOT_COPY_DOMAINS","DO_NOT_COPY_SUBTYPES","DO_NOT_COPY_ATTACHMENTS")
arcpy.XToolsGP_ModifyTable_xtp(r"Z:/PMA/TerriChan/GIS Projects/Historical Commitments/Street_Reconstruction/Data/Street_Reconstruction_Projects_for_DOT_Map.gdb/PWMS_Intersections","Z:/PMA/TerriChan/GIS Projects/Historical Commitments/Street_Reconstruction/Data/Street_Reconstruction_Projects_for_DOT_Map.gdb/PWMS_Intersections_ModifyTable1","Z:\PMA\TerriChan\GIS Projects\Historical Commitments\Street_Reconstruction\dataset_pwms_intersections_schema.xml","#","#","#","DO_NOT_COPY_DOMAINS","DO_NOT_COPY_SUBTYPES","DO_NOT_COPY_ATTACHMENTS")


# In[43]:

#arcpy.XToolsGP_Export2Excel_xtp("Z:/PMA/TerriChan/GIS Projects/Historical Commitments/Street_Reconstruction/Data/Street_Reconstruction_Projects_for_DOT_Map.gdb/PWMS_ProjectLocationBlock","Z:/PMA/TerriChan/GIS Projects/Historical Commitments/Street_Reconstruction/Data/Test_xtoolspro.xlsx","FMSID;ProjTitle","false","false","true")

# create buffer around the pwms_blocks joined layer
arcpy.analysis.Buffer("PWMS_Blocks_ModifyTable1","PWMS_Blocks_ModifyTable1_buff25ft","25 Feet","#","#","NONE","#","PLANAR")
# create buffer around the pwms_intersections joined layer
arcpy.analysis.Buffer("PWMS_Intersections_ModifyTable1","PWMS_Intersections_ModifyTable1_buff5ft","5 Feet","#","#","NONE","#","PLANAR")

# var to hold list of FMSID2s from actuals and capplan. For projects with more than one agency code, the FMSID2 will repeat in list
fmsid2_list = merge['FMSID2'].tolist()

# get list of FMSID2s that repeat from actuals and capplan
visited = set()
dup_fmsid2 = [fmsid2 for fmsid2 in fmsid2_list if fmsid2 in visited or (visited.add(fmsid2) or False)]

# list of FMSIDs w/ agency code from actuals and capplan
#fmsid_list = merge['PROJ ID'].tolist()

# create dict where keys are FMSIDs w/ agency code and values are FMSID2s.
'''
fmsid_dict = {}
for fmsid in fmsid_list:
    fmsid_dict[fmsid] = fmsid[4:]
'''

def unique_fmsids(layer, field):
    with arcpy.da.SearchCursor(layer, [field]) as cursor:
        return sorted({row[0] for row in cursor})

# create list to be used for sql query
fmsid2s_sql = []

# create list of unique values in the FMSID column of pwms blocks buffered layer.
pwms_blocks_fmsid2_list = unique_fmsids("PWMS_Blocks_ModifyTable1", "FMSID2")
# create list of unique values in the FMSID column of pwms intersections buffered layer.
pwms_ints_fmsid2_list = unique_fmsids("PWMS_Intersections_ModifyTable1", "FMSID2")
# combine the two lists into one list making sure the FMSID2s are unique in pwms_fmsid2_unique_list
pwms_fmsid2_unique_list = list(set(pwms_blocks_fmsid2_list + pwms_ints_fmsid2_list))

# loop through dup_fmsid2 (list of dupe fmsids2 from actuals/capplan) and if items are in the list of unique values in FMSID2 col of pwms block/intersection buffered layers
# add itemss to list that i will be using for the sql query
for fmsid2 in dup_fmsid2:
    if fmsid2 in pwms_fmsid2_unique_list:
        fmsid2s_sql.append(str(fmsid2))

# convert fmsid2s_sql list to tuple for sql query
fmsid2s_tuple_sql = tuple(fmsid2s_sql)
print 'sql query of FMSID2s that have more than one agency code: ', fmsid2s_tuple_sql
print
# sql query
sql_query = '"FMSID2" IN {}'.format(fmsid2s_tuple_sql)

# duplicate PWMS blocks buffer layer, name it v2, to append on later!
arcpy.CopyFeatures_management("PWMS_Blocks_ModifyTable1_buff25ft","PWMS_Blocks_ModifyTable1_buff25ft_v2")

### duplicate PWMS ints buffer layer, name it v2, to append on later
arcpy.CopyFeatures_management("PWMS_Intersections_ModifyTable1_buff5ft","PWMS_Intersections_ModifyTable1_buff5ft_v2")

# query for all the FMSID2s in sql in the pwms block/intersection buffered layers. use MakeFeatureLayer to create the pwms_blocks_dupe feature layer
#arcpy.MakeFeatureLayer_management("PWMS_Blocks_ModifyTable1_buff25ft","pwms_blocks_dupe",sql_query,"#","#")


pwms_blocks_dupe = arcpy.MakeFeatureLayer_management("PWMS_Blocks_ModifyTable1_buff25ft","pwms_blocks_dupe",sql_query,"#","#") #794 records gets queried, instead of half that
pwms_ints_dupe = arcpy.MakeFeatureLayer_management("PWMS_Intersections_ModifyTable1_buff5ft","pwms_ints_dupe",sql_query,"#","#")

# to use selectbyattribute, make featurelayer
arcpy.SelectLayerByAttribute_management(pwms_blocks_dupe,"NEW_SELECTION","#")
arcpy.SelectLayerByAttribute_management(pwms_ints_dupe,"NEW_SELECTION","#")

###
#arcpy.MakeFeatureLayer_management("PWMS_Intersections_ModifyTable1_buff5ft","pwms_ints_dupe",sql_query,"#","#")

#join the actuals/capplan to the feature layer to update the Cost and FY fields....only updating the agencycode in the v2 copy......
arcpy.AddJoin_management(pwms_blocks_dupe,"FMSID2","streetreconstruction_actuals_capplan","FMSID2","KEEP_COMMON")
#arcpy.AddJoin_management("PWMS_Blocks_ModifyTable1_buff25ft","FMSID2","streetreconstruction_actuals_capplan","FMSID2","KEEP_COMMON")
###
arcpy.AddJoin_management(pwms_ints_dupe,"FMSID2","streetreconstruction_actuals_capplan","FMSID2","KEEP_COMMON")

# create actual feature class pwms_blocks_dupe_for_edit
#arcpy.CopyFeatures_management("PWMS_Blocks_ModifyTable1_buff25ft","pwms_blocks_dupe_for_edit")
pwms_blocks_dupe_for_edit = arcpy.CopyFeatures_management("pwms_blocks_dupe","pwms_blocks_dupe_for_edit")

###
# create actual feature class pwms_ints_dupe_for_edit
pwms_ints_dupe_for_edit = arcpy.CopyFeatures_management("pwms_ints_dupe","pwms_ints_dupe_for_edit")

#list all the fields in the join
print "these are the fields in the join: "
# list of fields should include FMSID, FMSID2, Cost, FY fields from the temp pwms_blocks_dupe layer (PWMS_Blocks_ModifyTable1_buff25ft), and
# FY fields from the streetreconstruction_actuals_capplan table
fields = []
print 'STEP 1'
for f in arcpy.ListFields(pwms_blocks_dupe_for_edit):
    if 'FY' in f.name and f.name[-2:].isdigit(): #or Cost or FMSID in f.name
        fields.append(str(f.name))
        print "pwms_blocks_dupe_for_edit field: ", f.name
print

more_fields = ['PWMS_Blocks_ModifyTable1_buff25ft_Cost','PWMS_Blocks_ModifyTable1_buff25ft_FMSID','PWMS_Blocks_ModifyTable1_buff25ft_FMSID2']

for field in more_fields:
    fields.append(field)
    print field

fields.extend(['OBJECTID'])
print fields
print


#list all the fields in the join with pwms ints buffer
fields_ints = []
for f in arcpy.ListFields(pwms_ints_dupe_for_edit):
    # find fiscal year columns and append toe fields list
    if 'FY' in f.name and f.name[-2:].isdigit():
        fields_ints.append(str(f.name))
    print "pwms_ints_dupe_for_edit field: ", f.name

fields_ints.extend(['PWMS_Intersections_ModifyTable1_buff5ft_Cost','PWMS_Intersections_ModifyTable1_buff5ft_FMSID','PWMS_Intersections_ModifyTable1_buff5ft_FMSID2','OBJECTID'])

print fields_ints
print
# print the fields of pwms_blocks_dupe_for_edit
#print "pwms_blocks_dupe_for_edit fields are: "
#for f in 
print

# sum up index 31 (FY01) to index 61 (FY31) from the streetreconstruction_actuals_capplan table
def getCost(row):
    fy01_fy31_cost = 0

    for i in range(31,62):
        fy01_fy31_cost += row[i]

    return fy01_fy31_cost

# if there's 'FY' or 'FMSID' or 'FMSID2' or 'Cost' in the name of the field, add it to fields list

# in the layer the dupe row is right after the original row.
#can try for each other row, do the '850' agency code change. put in OBJECTID in the list of fields and objectid starts at 1. if objectid is even number, then change the agencycode to 850
num_rows = arcpy.GetCount_management(pwms_blocks_dupe_for_edit)

print 'dupe_layer_for_edit has {} rows'.format(num_rows[0])

def updateFields(dupe_layer_for_edit, flds):
    count = 1
    with arcpy.da.UpdateCursor(dupe_layer_for_edit, flds) as cursor:
        for row in cursor:
            # if objectid, which is the last item in fields list, is even num, change agencycode to 850, update Cost, FY01-FY31.
            OBJECTID = row[-1]
    
            print 'count: ', count         
            print 'objectid type: {} and value: {}'.format(type(OBJECTID),str(OBJECTID))
            
            #change agency code to 850 for every even numbered OBJECTID row
            if int(OBJECTID) % 2 == 0:
                
                # update FMSID value
                #row[-2] = '850 ' + row[-1]
                row[-3] = '850 ' + row[-2]
                # update Cost. Or should I use the Cost field from pwms...?
                #row[-3] = getCost(row)
                row[-4] = getCost(row)
                # update FY01 to FY31 fields, by using the streetreconstruction_actuals_capplan FY fields to update the PWMS FY fields
                #row[0] = row[31]
                #row[1] = row[32]
                #...
                #row[30] = row[61]
                for i in range(0,31):
                    row[i] = row[i+31]

                cursor.updateRow(row)
            count+=1
# in the pwms_blocks_dupe_for_edit layer, change the FMSID to have diff agency code, change the Cost and FY column values too. 
# do the same for the pwms_ints_dupe_for_edit layer
#fields = fy_fields + ['Cost','FMSID','FMSID2']
updateFields("pwms_blocks_dupe_for_edit", fields)
updateFields("pwms_ints_dupe_for_edit", fields_ints)
  
# create the required FieldMap and FieldMappings objects. set Field Mappings so that the Append tool will work.
#PWMS_Blocks_ModifyTable1_buff25ft_Division
#fm_list = ["fm_division","fm_fmsid","fm_projiddesc","fm_fycons","fm_fydesign","fm_fundstatus","fm_projstatus","fm_cost","fm_porc","fm_fmsid2"]

##############
##############
###############
# create the FY FieldMappings objects and add them to the fm_list for PWMS BLOCKS
fm_division = arcpy.FieldMap()
fm_fmsid = arcpy.FieldMap()
fm_projiddesc = arcpy.FieldMap()
fm_fycons = arcpy.FieldMap()
fm_fydesign = arcpy.FieldMap()
fm_fundstatus = arcpy.FieldMap()
fm_projstatus = arcpy.FieldMap()
fm_cost = arcpy.FieldMap()
fm_porc = arcpy.FieldMap()
fm_fmsid2 = arcpy.FieldMap()
fm_fy1 = arcpy.FieldMap()
fm_fy2 = arcpy.FieldMap()
fm_fy3 = arcpy.FieldMap()
fm_fy4 = arcpy.FieldMap()
fm_fy5 = arcpy.FieldMap()
fm_fy6 = arcpy.FieldMap()
fm_fy7 = arcpy.FieldMap()
fm_fy8 = arcpy.FieldMap()
fm_fy9 = arcpy.FieldMap()
fm_fy10 = arcpy.FieldMap()
fm_fy11 = arcpy.FieldMap()
fm_fy12 = arcpy.FieldMap()
fm_fy13 = arcpy.FieldMap()
fm_fy14 = arcpy.FieldMap()
fm_fy15 = arcpy.FieldMap()
fm_fy16 = arcpy.FieldMap()
fm_fy17 = arcpy.FieldMap()
fm_fy18 = arcpy.FieldMap()
fm_fy19 = arcpy.FieldMap()
fm_fy20 = arcpy.FieldMap()
fm_fy21 = arcpy.FieldMap()
fm_fy22 = arcpy.FieldMap()
fm_fy23 = arcpy.FieldMap()
fm_fy24 = arcpy.FieldMap()
fm_fy25 = arcpy.FieldMap()
fm_fy26 = arcpy.FieldMap()
fm_fy27 = arcpy.FieldMap()
fm_fy28 = arcpy.FieldMap()
fm_fy29 = arcpy.FieldMap()
fm_fy30 = arcpy.FieldMap()
fm_fy31 = arcpy.FieldMap()
fms = arcpy.FieldMappings()

####### Add the target table to the field mappings class to set the correct schema#################
fms.addTable("PWMS_Blocks_ModifyTable1_buff25ft_v2")

# get list of FY fields
fy_fields = []
for i in range(1,32):
    if i < 10:
        fy_fields.append('FY0' + str(i))
    else:
        fy_fields.append('FY' + str(i))
        
diss_field_names = ['Division','FMSID','PROJ_ID_DESC','FYCons','FYDesign','FundStatus','ProjStatus','Cost','Planned_Or_Committed','FMSID2'] + fy_fields

#loop thru each field in FieldMappings object
def deleteFieldsFromFieldMappings(fms):
    for fm in fms.fieldMappings:
        outField = fm.outputField
        fieldName = outField.name
        print 'fieldName in fms: ', fieldName
        if fieldName not in diss_field_names:
            print 'fieldName to delete from fms: ',fieldName
            fms.removeFieldMap(fms.findFieldMapIndex(fieldName))

deleteFieldsFromFieldMappings(fms)                           
# get the field names from target PWMS_Blocks_ModifyTable1_buff25ft_v2 file that are in the correct spelling
                          
# get field names of the pwms_blocks_dupe_for_edit layer as list
dupe_division = "PWMS_Blocks_ModifyTable1_buff25ft_Division"
dupe_fmsid = "PWMS_Blocks_ModifyTable1_buff25ft_FMSID"
dupe_projiddesc = "PWMS_Blocks_ModifyTable1_buff25ft_PROJ_ID_DESC"
dupe_fycons = "PWMS_Blocks_ModifyTable1_buff25ft_FYCons"
dupe_fydesign = "PWMS_Blocks_ModifyTable1_buff25ft_FYDesign"
dupe_fundstatus = "PWMS_Blocks_ModifyTable1_buff25ft_FundStatus"
dupe_projstatus = "PWMS_Blocks_ModifyTable1_buff25ft_ProjStatus"
dupe_cost = "PWMS_Blocks_ModifyTable1_buff25ft_Cost"
dupe_porc = "PWMS_Blocks_ModifyTable1_buff25ft_Planned_Or_Committed"
dupe_fmsid2 = "PWMS_Blocks_ModifyTable1_buff25ft_FMSID2"
dupe_fy1 = "PWMS_Blocks_ModifyTable1_buff25ft_FY01"
dupe_fy2 = "PWMS_Blocks_ModifyTable1_buff25ft_FY02"
dupe_fy3 = "PWMS_Blocks_ModifyTable1_buff25ft_FY03"
dupe_fy4 = "PWMS_Blocks_ModifyTable1_buff25ft_FY04"
dupe_fy5 = "PWMS_Blocks_ModifyTable1_buff25ft_FY05"
dupe_fy6 = "PWMS_Blocks_ModifyTable1_buff25ft_FY06"
dupe_fy7 = "PWMS_Blocks_ModifyTable1_buff25ft_FY07"
dupe_fy8 = "PWMS_Blocks_ModifyTable1_buff25ft_FY08"
dupe_fy9 = "PWMS_Blocks_ModifyTable1_buff25ft_FY09"
dupe_fy10 = "PWMS_Blocks_ModifyTable1_buff25ft_FY10"
dupe_fy11 = "PWMS_Blocks_ModifyTable1_buff25ft_FY11"
dupe_fy12 = "PWMS_Blocks_ModifyTable1_buff25ft_FY12"
dupe_fy13 = "PWMS_Blocks_ModifyTable1_buff25ft_FY13"
dupe_fy14 = "PWMS_Blocks_ModifyTable1_buff25ft_FY14"
dupe_fy15 = "PWMS_Blocks_ModifyTable1_buff25ft_FY15"
dupe_fy16 = "PWMS_Blocks_ModifyTable1_buff25ft_FY16"
dupe_fy17 = "PWMS_Blocks_ModifyTable1_buff25ft_FY17"
dupe_fy18 = "PWMS_Blocks_ModifyTable1_buff25ft_FY18"
dupe_fy19 = "PWMS_Blocks_ModifyTable1_buff25ft_FY19"
dupe_fy20 = "PWMS_Blocks_ModifyTable1_buff25ft_FY20"
dupe_fy21 = "PWMS_Blocks_ModifyTable1_buff25ft_FY21"
dupe_fy22 = "PWMS_Blocks_ModifyTable1_buff25ft_FY22"
dupe_fy23 = "PWMS_Blocks_ModifyTable1_buff25ft_FY23"
dupe_fy24 = "PWMS_Blocks_ModifyTable1_buff25ft_FY24"
dupe_fy25 = "PWMS_Blocks_ModifyTable1_buff25ft_FY25"
dupe_fy26 = "PWMS_Blocks_ModifyTable1_buff25ft_FY26"
dupe_fy27 = "PWMS_Blocks_ModifyTable1_buff25ft_FY27"
dupe_fy28 = "PWMS_Blocks_ModifyTable1_buff25ft_FY28"
dupe_fy29 = "PWMS_Blocks_ModifyTable1_buff25ft_FY29"
dupe_fy30 = "PWMS_Blocks_ModifyTable1_buff25ft_FY30"
dupe_fy31 = "PWMS_Blocks_ModifyTable1_buff25ft_FY31"
 
# add fields to their corresponding FieldMap objects
#for field in arcpy.ListFields("PWMS_Blocks_ModifyTable1_buff25ft_v2",):
#    fm.addInputField("PWMS_Blocks_ModifyTable1_buff25ft_v2", )

#for fname in target_fieldnames:
#    fm.addInputField("PWMS_Blocks_ModifyTable1_buff25ft_v2", fname)

#for fname in fields_for_fms:
#    fm.addInputField("pwms_blocks_dupe_for_edit", fname)

# var to hold the part of fm name that's after the _
# if the var is in the key as substring, addInputField
'''
for element in fm_list:
    underscore_index = element.index('_')
    fm_substring = element[underscore_index + 1:]
    for key, val in target_fieldnames.items():
        if fm_substring in key:
            element.addInputField("PWMS_Blocks_ModifyTable1_buff25ft_v2", key)

for element in fm_list:
    underscore_index = element.index('_')
    fm_substring = element[underscore_index + 1:]
    for key, val in fields_for_fms.items():
        if fm_substring in key:
            element.addInputField("pwms_blocks_dupe_for_edit", key)
'''

fm_division.addInputField("pwms_blocks_dupe_for_edit", dupe_division)
fm_fmsid.addInputField("pwms_blocks_dupe_for_edit", dupe_fmsid)
fm_projiddesc.addInputField("pwms_blocks_dupe_for_edit", dupe_projiddesc)
fm_fycons.addInputField("pwms_blocks_dupe_for_edit", dupe_fycons)
fm_fydesign.addInputField("pwms_blocks_dupe_for_edit", dupe_fydesign)
fm_fundstatus.addInputField("pwms_blocks_dupe_for_edit", dupe_fundstatus)
fm_projstatus.addInputField("pwms_blocks_dupe_for_edit", dupe_projstatus)
fm_cost.addInputField("pwms_blocks_dupe_for_edit", dupe_cost)
fm_porc.addInputField("pwms_blocks_dupe_for_edit", dupe_porc)
fm_fmsid2.addInputField("pwms_blocks_dupe_for_edit", dupe_fmsid2)
fm_fy1.addInputField("pwms_blocks_dupe_for_edit", dupe_fy1)
fm_fy2.addInputField("pwms_blocks_dupe_for_edit", dupe_fy2)
fm_fy3.addInputField("pwms_blocks_dupe_for_edit", dupe_fy3)
fm_fy4.addInputField("pwms_blocks_dupe_for_edit", dupe_fy4)
fm_fy5.addInputField("pwms_blocks_dupe_for_edit", dupe_fy5)
fm_fy6.addInputField("pwms_blocks_dupe_for_edit", dupe_fy6)
fm_fy7.addInputField("pwms_blocks_dupe_for_edit", dupe_fy7)
fm_fy8.addInputField("pwms_blocks_dupe_for_edit", dupe_fy8)
fm_fy9.addInputField("pwms_blocks_dupe_for_edit", dupe_fy9)
fm_fy10.addInputField("pwms_blocks_dupe_for_edit", dupe_fy10)
fm_fy11.addInputField("pwms_blocks_dupe_for_edit", dupe_fy11)
fm_fy12.addInputField("pwms_blocks_dupe_for_edit", dupe_fy12)
fm_fy13.addInputField("pwms_blocks_dupe_for_edit", dupe_fy13)
fm_fy14.addInputField("pwms_blocks_dupe_for_edit", dupe_fy14)
fm_fy15.addInputField("pwms_blocks_dupe_for_edit", dupe_fy15)
fm_fy16.addInputField("pwms_blocks_dupe_for_edit", dupe_fy16)
fm_fy17.addInputField("pwms_blocks_dupe_for_edit", dupe_fy17)
fm_fy18.addInputField("pwms_blocks_dupe_for_edit", dupe_fy18)
fm_fy19.addInputField("pwms_blocks_dupe_for_edit", dupe_fy19)
fm_fy20.addInputField("pwms_blocks_dupe_for_edit", dupe_fy20)
fm_fy21.addInputField("pwms_blocks_dupe_for_edit", dupe_fy21)
fm_fy22.addInputField("pwms_blocks_dupe_for_edit", dupe_fy22)
fm_fy23.addInputField("pwms_blocks_dupe_for_edit", dupe_fy23)
fm_fy24.addInputField("pwms_blocks_dupe_for_edit", dupe_fy24)
fm_fy25.addInputField("pwms_blocks_dupe_for_edit", dupe_fy25)
fm_fy26.addInputField("pwms_blocks_dupe_for_edit", dupe_fy26)
fm_fy27.addInputField("pwms_blocks_dupe_for_edit", dupe_fy27)
fm_fy28.addInputField("pwms_blocks_dupe_for_edit", dupe_fy28)
fm_fy29.addInputField("pwms_blocks_dupe_for_edit", dupe_fy29)
fm_fy30.addInputField("pwms_blocks_dupe_for_edit", dupe_fy30)
fm_fy31.addInputField("pwms_blocks_dupe_for_edit", dupe_fy31)

count = 0
#print "type of FieldMappings obj: ", type(fms)
for item in fms.fieldMappings:
    print "fm: ", item
    count+=1
print "count of FieldMappings objs: ", count

# set the output field properties for FieldMap objects
division_name = fm_division.outputField
division_name.name = "Division"
fm_division.outputField = division_name

fmsid_name = fm_fmsid.outputField
fmsid_name.name = "FMSID"
fm_fmsid.outputField = fmsid_name

projiddesc_name = fm_projiddesc.outputField
projiddesc_name.name = "PROJ_ID_DESC"
fm_projiddesc.outputField = projiddesc_name

fycons_name = fm_fycons.outputField
fycons_name.name = "FYCons"
fm_fycons.outputField = fycons_name

fydesign_name = fm_fydesign.outputField
fydesign_name.name = "FYDesign"
fm_fydesign.outputField = fydesign_name

fundstatus_name = fm_fundstatus.outputField
fundstatus_name.name = "FundStatus"
fm_fundstatus.outputField = fundstatus_name

projstatus_name = fm_projstatus.outputField
projstatus_name.name = "ProjStatus"
fm_projstatus.outputField = projstatus_name

cost_name = fm_cost.outputField
cost_name.name = "Cost"
fm_cost.outputField = cost_name

porc_name = fm_porc.outputField
porc_name.name = "Planned_Or_Committed"
fm_porc.outputField = porc_name

fmsid2_name = fm_fmsid2.outputField
fmsid2_name.name = "FMSID2"
fm_fmsid2.outputField = fmsid2_name

fy1_name = fm_fy1.outputField
fy1_name.name = "FY01"
fm_fy1.outputField = fy1_name

fy2_name = fm_fy2.outputField
fy2_name.name = "FY02"
fm_fy2.outputField = fy2_name

fy3_name = fm_fy3.outputField
fy3_name.name = "FY03"
fm_fy3.outputField = fy3_name

fy4_name = fm_fy4.outputField
fy4_name.name = "FY04"
fm_fy4.outputField = fy4_name

fy5_name = fm_fy5.outputField
fy5_name.name = "FY05"
fm_fy5.outputField = fy5_name

fy6_name = fm_fy6.outputField
fy6_name.name = "FY06"
fm_fy6.outputField = fy6_name

fy7_name = fm_fy7.outputField
fy7_name.name = "FY07"
fm_fy7.outputField = fy7_name

fy8_name = fm_fy8.outputField
fy8_name.name = "FY08"
fm_fy8.outputField = fy8_name

fy9_name = fm_fy9.outputField
fy9_name.name = "FY09"
fm_fy9.outputField = fy9_name

fy10_name = fm_fy10.outputField
fy10_name.name = "FY10"
fm_fy10.outputField = fy10_name

fy11_name = fm_fy11.outputField
fy11_name.name = "FY11"
fm_fy11.outputField = fy11_name

fy12_name = fm_fy12.outputField
fy12_name.name = "FY12"
fm_fy12.outputField = fy12_name

fy13_name = fm_fy13.outputField
fy13_name.name = "FY13"
fm_fy13.outputField = fy13_name

fy14_name = fm_fy14.outputField
fy14_name.name = "FY14"
fm_fy14.outputField = fy14_name

fy15_name = fm_fy15.outputField
fy15_name.name = "FY15"
fm_fy15.outputField = fy15_name

fy16_name = fm_fy16.outputField
fy16_name.name = "FY16"
fm_fy16.outputField = fy16_name

fy17_name = fm_fy17.outputField
fy17_name.name = "FY17"
fm_fy17.outputField = fy17_name

fy18_name = fm_fy18.outputField
fy18_name.name = "FY18"
fm_fy18.outputField = fy18_name

fy19_name = fm_fy19.outputField
fy19_name.name = "FY19"
fm_fy19.outputField = fy19_name

fy20_name = fm_fy20.outputField
fy20_name.name = "FY20"
fm_fy20.outputField = fy20_name

fy21_name = fm_fy21.outputField
fy21_name.name = "FY21"
fm_fy21.outputField = fy21_name

fy22_name = fm_fy22.outputField
fy22_name.name = "FY22"
fm_fy22.outputField = fy22_name

fy23_name = fm_fy23.outputField
fy23_name.name = "FY23"
fm_fy23.outputField = fy23_name

fy24_name = fm_fy24.outputField
fy24_name.name = "FY24"
fm_fy24.outputField = fy24_name

fy25_name = fm_fy25.outputField
fy25_name.name = "FY25"
fm_fy25.outputField = fy25_name

fy26_name = fm_fy26.outputField
fy26_name.name = "FY26"
fm_fy26.outputField = fy26_name

fy27_name = fm_fy27.outputField
fy27_name.name = "FY27"
fm_fy27.outputField = fy27_name

fy28_name = fm_fy28.outputField
fy28_name.name = "FY28"
fm_fy28.outputField = fy28_name

fy29_name = fm_fy29.outputField
fy29_name.name = "FY29"
fm_fy29.outputField = fy29_name

fy30_name = fm_fy30.outputField
fy30_name.name = "FY30"
fm_fy30.outputField = fy30_name

fy31_name = fm_fy31.outputField
fy31_name.name = "FY31"
fm_fy31.outputField = fy31_name

print 'STEP 20'
# add the FieldMap objects to the FieldMappings object

fms.addFieldMap(fm_division)
print 'STEP 21'
fms.addFieldMap(fm_fmsid)
fms.addFieldMap(fm_projiddesc)
fms.addFieldMap(fm_fycons)
fms.addFieldMap(fm_fydesign)
fms.addFieldMap(fm_fundstatus)
fms.addFieldMap(fm_projstatus)
fms.addFieldMap(fm_cost)
fms.addFieldMap(fm_porc)
fms.addFieldMap(fm_fmsid2)
fms.addFieldMap(fm_fy1)
fms.addFieldMap(fm_fy2)
fms.addFieldMap(fm_fy3)
fms.addFieldMap(fm_fy4)
fms.addFieldMap(fm_fy5)
fms.addFieldMap(fm_fy6)
fms.addFieldMap(fm_fy7)
fms.addFieldMap(fm_fy8)
fms.addFieldMap(fm_fy9)
fms.addFieldMap(fm_fy10)
fms.addFieldMap(fm_fy11)
fms.addFieldMap(fm_fy12)
fms.addFieldMap(fm_fy13)
fms.addFieldMap(fm_fy14)
fms.addFieldMap(fm_fy15)
fms.addFieldMap(fm_fy16)
fms.addFieldMap(fm_fy17)
fms.addFieldMap(fm_fy18)
fms.addFieldMap(fm_fy19)
fms.addFieldMap(fm_fy20)
fms.addFieldMap(fm_fy21)
fms.addFieldMap(fm_fy22)
fms.addFieldMap(fm_fy23)
fms.addFieldMap(fm_fy24)
fms.addFieldMap(fm_fy25)
fms.addFieldMap(fm_fy26)
fms.addFieldMap(fm_fy27)
fms.addFieldMap(fm_fy28)
fms.addFieldMap(fm_fy29)
fms.addFieldMap(fm_fy30)
fms.addFieldMap(fm_fy31)
#for fm in fms.fieldMappings:
#    fms.addFieldMap(item)

#for i in range(0, fms.fieldCount):
#    fm = fms.fieldMappings[i]
#    fms.addFieldMap(fm)
    
# append
print 'STEP 22'
arcpy.management.Append(["pwms_blocks_dupe_for_edit"],"PWMS_Blocks_ModifyTable1_buff25ft_v2","NO_TEST",fms,"#")


print 'STEP 23'
# create the FY FieldMappings objects and add them to the fm_list for PWMS INTERSECTIONS
fm_division = arcpy.FieldMap()
fm_fmsid = arcpy.FieldMap()
fm_projiddesc = arcpy.FieldMap()
fm_fycons = arcpy.FieldMap()
fm_fydesign = arcpy.FieldMap()
fm_fundstatus = arcpy.FieldMap()
fm_projstatus = arcpy.FieldMap()
fm_cost = arcpy.FieldMap()
fm_porc = arcpy.FieldMap()
fm_fmsid2 = arcpy.FieldMap()
fm_fy1 = arcpy.FieldMap()
fm_fy2 = arcpy.FieldMap()
fm_fy3 = arcpy.FieldMap()
fm_fy4 = arcpy.FieldMap()
fm_fy5 = arcpy.FieldMap()
fm_fy6 = arcpy.FieldMap()
fm_fy7 = arcpy.FieldMap()
fm_fy8 = arcpy.FieldMap()
fm_fy9 = arcpy.FieldMap()
fm_fy10 = arcpy.FieldMap()
fm_fy11 = arcpy.FieldMap()
fm_fy12 = arcpy.FieldMap()
fm_fy13 = arcpy.FieldMap()
fm_fy14 = arcpy.FieldMap()
fm_fy15 = arcpy.FieldMap()
fm_fy16 = arcpy.FieldMap()
fm_fy17 = arcpy.FieldMap()
fm_fy18 = arcpy.FieldMap()
fm_fy19 = arcpy.FieldMap()
fm_fy20 = arcpy.FieldMap()
fm_fy21 = arcpy.FieldMap()
fm_fy22 = arcpy.FieldMap()
fm_fy23 = arcpy.FieldMap()
fm_fy24 = arcpy.FieldMap()
fm_fy25 = arcpy.FieldMap()
fm_fy26 = arcpy.FieldMap()
fm_fy27 = arcpy.FieldMap()
fm_fy28 = arcpy.FieldMap()
fm_fy29 = arcpy.FieldMap()
fm_fy30 = arcpy.FieldMap()
fm_fy31 = arcpy.FieldMap()
fms2 = arcpy.FieldMappings()

####### Add the target table to the field mappings class to set the correct schema#################
print 'STEP 24'
fms2.addTable("PWMS_Intersections_ModifyTable1_buff5ft_v2")

print 'STEP 25'
deleteFieldsFromFieldMappings(fms2)

print 'STEP 26'
# get field names of the pwms_blocks_dupe_for_edit layer as list
dupe_division = "PWMS_Intersections_ModifyTable1_buff5ft_Division"
dupe_fmsid = "PWMS_Intersections_ModifyTable1_buff5ft_FMSID"
dupe_projiddesc = "PWMS_Intersections_ModifyTable1_buff5ft_PROJ_ID_DESC"
dupe_fycons = "PWMS_Intersections_ModifyTable1_buff5ft_FYCons"
dupe_fydesign = "PWMS_Intersections_ModifyTable1_buff5ft_FYDesign"
dupe_fundstatus = "PWMS_Intersections_ModifyTable1_buff5ft_FundStatus"
dupe_projstatus = "PWMS_Intersections_ModifyTable1_buff5ft_ProjStatus"
dupe_cost = "PWMS_Intersections_ModifyTable1_buff5ft_Cost"
dupe_porc = "PWMS_Intersections_ModifyTable1_buff5ft_Planned_Or_Committed"
dupe_fmsid2 = "PWMS_Intersections_ModifyTable1_buff5ft_FMSID2"
dupe_fy1 = "PWMS_Intersections_ModifyTable1_buff5ft_FY01"
dupe_fy2 = "PWMS_Intersections_ModifyTable1_buff5ft_FY02"
dupe_fy3 = "PWMS_Intersections_ModifyTable1_buff5ft_FY03"
dupe_fy4 = "PWMS_Intersections_ModifyTable1_buff5ft_FY04"
dupe_fy5 = "PWMS_Intersections_ModifyTable1_buff5ft_FY05"
dupe_fy6 = "PWMS_Intersections_ModifyTable1_buff5ft_FY06"
dupe_fy7 = "PWMS_Intersections_ModifyTable1_buff5ft_FY07"
dupe_fy8 = "PWMS_Intersections_ModifyTable1_buff5ft_FY08"
dupe_fy9 = "PWMS_Intersections_ModifyTable1_buff5ft_FY09"
dupe_fy10 = "PWMS_Intersections_ModifyTable1_buff5ft_FY10"
dupe_fy11 = "PWMS_Intersections_ModifyTable1_buff5ft_FY11"
dupe_fy12 = "PWMS_Intersections_ModifyTable1_buff5ft_FY12"
dupe_fy13 = "PWMS_Intersections_ModifyTable1_buff5ft_FY13"
dupe_fy14 = "PWMS_Intersections_ModifyTable1_buff5ft_FY14"
dupe_fy15 = "PWMS_Intersections_ModifyTable1_buff5ft_FY15"
dupe_fy16 = "PWMS_Intersections_ModifyTable1_buff5ft_FY16"
dupe_fy17 = "PWMS_Intersections_ModifyTable1_buff5ft_FY17"
dupe_fy18 = "PWMS_Intersections_ModifyTable1_buff5ft_FY18"
dupe_fy19 = "PWMS_Intersections_ModifyTable1_buff5ft_FY19"
dupe_fy20 = "PWMS_Intersections_ModifyTable1_buff5ft_FY20"
dupe_fy21 = "PWMS_Intersections_ModifyTable1_buff5ft_FY21"
dupe_fy22 = "PWMS_Intersections_ModifyTable1_buff5ft_FY22"
dupe_fy23 = "PWMS_Intersections_ModifyTable1_buff5ft_FY23"
dupe_fy24 = "PWMS_Intersections_ModifyTable1_buff5ft_FY24"
dupe_fy25 = "PWMS_Intersections_ModifyTable1_buff5ft_FY25"
dupe_fy26 = "PWMS_Intersections_ModifyTable1_buff5ft_FY26"
dupe_fy27 = "PWMS_Intersections_ModifyTable1_buff5ft_FY27"
dupe_fy28 = "PWMS_Intersections_ModifyTable1_buff5ft_FY28"
dupe_fy29 = "PWMS_Intersections_ModifyTable1_buff5ft_FY29"
dupe_fy30 = "PWMS_Intersections_ModifyTable1_buff5ft_FY30"
dupe_fy31 = "PWMS_Intersections_ModifyTable1_buff5ft_FY31"

print 'STEP 27'
fm_division.addInputField("pwms_ints_dupe_for_edit", dupe_division)
fm_fmsid.addInputField("pwms_ints_dupe_for_edit", dupe_fmsid)
fm_projiddesc.addInputField("pwms_ints_dupe_for_edit", dupe_projiddesc)
fm_fycons.addInputField("pwms_ints_dupe_for_edit", dupe_fycons)
fm_fydesign.addInputField("pwms_ints_dupe_for_edit", dupe_fydesign)
fm_fundstatus.addInputField("pwms_ints_dupe_for_edit", dupe_fundstatus)
fm_projstatus.addInputField("pwms_ints_dupe_for_edit", dupe_projstatus)
fm_cost.addInputField("pwms_ints_dupe_for_edit", dupe_cost)
fm_porc.addInputField("pwms_ints_dupe_for_edit", dupe_porc)
fm_fmsid2.addInputField("pwms_ints_dupe_for_edit", dupe_fmsid2)
fm_fy1.addInputField("pwms_ints_dupe_for_edit", dupe_fy1)
fm_fy2.addInputField("pwms_ints_dupe_for_edit", dupe_fy2)
fm_fy3.addInputField("pwms_ints_dupe_for_edit", dupe_fy3)
fm_fy4.addInputField("pwms_ints_dupe_for_edit", dupe_fy4)
fm_fy5.addInputField("pwms_ints_dupe_for_edit", dupe_fy5)
fm_fy6.addInputField("pwms_ints_dupe_for_edit", dupe_fy6)
fm_fy7.addInputField("pwms_ints_dupe_for_edit", dupe_fy7)
fm_fy8.addInputField("pwms_ints_dupe_for_edit", dupe_fy8)
fm_fy9.addInputField("pwms_ints_dupe_for_edit", dupe_fy9)
fm_fy10.addInputField("pwms_ints_dupe_for_edit", dupe_fy10)
fm_fy11.addInputField("pwms_ints_dupe_for_edit", dupe_fy11)
fm_fy12.addInputField("pwms_ints_dupe_for_edit", dupe_fy12)
fm_fy13.addInputField("pwms_ints_dupe_for_edit", dupe_fy13)
fm_fy14.addInputField("pwms_ints_dupe_for_edit", dupe_fy14)
fm_fy15.addInputField("pwms_ints_dupe_for_edit", dupe_fy15)
fm_fy16.addInputField("pwms_ints_dupe_for_edit", dupe_fy16)
fm_fy17.addInputField("pwms_ints_dupe_for_edit", dupe_fy17)
fm_fy18.addInputField("pwms_ints_dupe_for_edit", dupe_fy18)
fm_fy19.addInputField("pwms_ints_dupe_for_edit", dupe_fy19)
fm_fy20.addInputField("pwms_ints_dupe_for_edit", dupe_fy20)
fm_fy21.addInputField("pwms_ints_dupe_for_edit", dupe_fy21)
fm_fy22.addInputField("pwms_ints_dupe_for_edit", dupe_fy22)
fm_fy23.addInputField("pwms_ints_dupe_for_edit", dupe_fy23)
fm_fy24.addInputField("pwms_ints_dupe_for_edit", dupe_fy24)
fm_fy25.addInputField("pwms_ints_dupe_for_edit", dupe_fy25)
fm_fy26.addInputField("pwms_ints_dupe_for_edit", dupe_fy26)
fm_fy27.addInputField("pwms_ints_dupe_for_edit", dupe_fy27)
fm_fy28.addInputField("pwms_ints_dupe_for_edit", dupe_fy28)
fm_fy29.addInputField("pwms_ints_dupe_for_edit", dupe_fy29)
fm_fy30.addInputField("pwms_ints_dupe_for_edit", dupe_fy30)
fm_fy31.addInputField("pwms_ints_dupe_for_edit", dupe_fy31)
print 'STEP 28'
# set the output field properties for FieldMap objects
division_name = fm_division.outputField
division_name.name = "Division"
fm_division.outputField = division_name

fmsid_name = fm_fmsid.outputField
fmsid_name.name = "FMSID"
fm_fmsid.outputField = fmsid_name

projiddesc_name = fm_projiddesc.outputField
projiddesc_name.name = "PROJ_ID_DESC"
fm_projiddesc.outputField = projiddesc_name

fycons_name = fm_fycons.outputField
fycons_name.name = "FYCons"
fm_fycons.outputField = fycons_name

fydesign_name = fm_fydesign.outputField
fydesign_name.name = "FYDesign"
fm_fydesign.outputField = fydesign_name

fundstatus_name = fm_fundstatus.outputField
fundstatus_name.name = "FundStatus"
fm_fundstatus.outputField = fundstatus_name

projstatus_name = fm_projstatus.outputField
projstatus_name.name = "ProjStatus"
fm_projstatus.outputField = projstatus_name

cost_name = fm_cost.outputField
cost_name.name = "Cost"
fm_cost.outputField = cost_name

porc_name = fm_porc.outputField
porc_name.name = "Planned_Or_Committed"
fm_porc.outputField = porc_name

fmsid2_name = fm_fmsid2.outputField
fmsid2_name.name = "FMSID2"
fm_fmsid2.outputField = fmsid2_name

fy1_name = fm_fy1.outputField
fy1_name.name = "FY01"
fm_fy1.outputField = fy1_name

fy2_name = fm_fy2.outputField
fy2_name.name = "FY02"
fm_fy2.outputField = fy2_name

fy3_name = fm_fy3.outputField
fy3_name.name = "FY03"
fm_fy3.outputField = fy3_name

fy4_name = fm_fy4.outputField
fy4_name.name = "FY04"
fm_fy4.outputField = fy4_name

fy5_name = fm_fy5.outputField
fy5_name.name = "FY05"
fm_fy5.outputField = fy5_name

fy6_name = fm_fy6.outputField
fy6_name.name = "FY06"
fm_fy6.outputField = fy6_name

fy7_name = fm_fy7.outputField
fy7_name.name = "FY07"
fm_fy7.outputField = fy7_name

fy8_name = fm_fy8.outputField
fy8_name.name = "FY08"
fm_fy8.outputField = fy8_name

fy9_name = fm_fy9.outputField
fy9_name.name = "FY09"
fm_fy9.outputField = fy9_name

fy10_name = fm_fy10.outputField
fy10_name.name = "FY10"
fm_fy10.outputField = fy10_name

fy11_name = fm_fy11.outputField
fy11_name.name = "FY11"
fm_fy11.outputField = fy11_name

fy12_name = fm_fy12.outputField
fy12_name.name = "FY12"
fm_fy12.outputField = fy12_name

fy13_name = fm_fy13.outputField
fy13_name.name = "FY13"
fm_fy13.outputField = fy13_name

fy14_name = fm_fy14.outputField
fy14_name.name = "FY14"
fm_fy14.outputField = fy14_name

fy15_name = fm_fy15.outputField
fy15_name.name = "FY15"
fm_fy15.outputField = fy15_name

fy16_name = fm_fy16.outputField
fy16_name.name = "FY16"
fm_fy16.outputField = fy16_name

fy17_name = fm_fy17.outputField
fy17_name.name = "FY17"
fm_fy17.outputField = fy17_name

fy18_name = fm_fy18.outputField
fy18_name.name = "FY18"
fm_fy18.outputField = fy18_name

fy19_name = fm_fy19.outputField
fy19_name.name = "FY19"
fm_fy19.outputField = fy19_name

fy20_name = fm_fy20.outputField
fy20_name.name = "FY20"
fm_fy20.outputField = fy20_name

fy21_name = fm_fy21.outputField
fy21_name.name = "FY21"
fm_fy21.outputField = fy21_name

fy22_name = fm_fy22.outputField
fy22_name.name = "FY22"
fm_fy22.outputField = fy22_name

fy23_name = fm_fy23.outputField
fy23_name.name = "FY23"
fm_fy23.outputField = fy23_name

fy24_name = fm_fy24.outputField
fy24_name.name = "FY24"
fm_fy24.outputField = fy24_name

fy25_name = fm_fy25.outputField
fy25_name.name = "FY25"
fm_fy25.outputField = fy25_name

fy26_name = fm_fy26.outputField
fy26_name.name = "FY26"
fm_fy26.outputField = fy26_name

fy27_name = fm_fy27.outputField
fy27_name.name = "FY27"
fm_fy27.outputField = fy27_name

fy28_name = fm_fy28.outputField
fy28_name.name = "FY28"
fm_fy28.outputField = fy28_name

fy29_name = fm_fy29.outputField
fy29_name.name = "FY29"
fm_fy29.outputField = fy29_name

fy30_name = fm_fy30.outputField
fy30_name.name = "FY30"
fm_fy30.outputField = fy30_name

fy31_name = fm_fy31.outputField
fy31_name.name = "FY31"
fm_fy31.outputField = fy31_name

# add the FieldMap objects to the FieldMappings object
print 'STEP 29'
fms2.addFieldMap(fm_division)
fms2.addFieldMap(fm_fmsid)
fms2.addFieldMap(fm_projiddesc)
fms2.addFieldMap(fm_fycons)
fms2.addFieldMap(fm_fydesign)
fms2.addFieldMap(fm_fundstatus)
fms2.addFieldMap(fm_projstatus)
fms2.addFieldMap(fm_cost)
fms2.addFieldMap(fm_porc)
fms2.addFieldMap(fm_fmsid2)
fms2.addFieldMap(fm_fy1)
fms2.addFieldMap(fm_fy2)
fms2.addFieldMap(fm_fy3)
fms2.addFieldMap(fm_fy4)
fms2.addFieldMap(fm_fy5)
fms2.addFieldMap(fm_fy6)
fms2.addFieldMap(fm_fy7)
fms2.addFieldMap(fm_fy8)
fms2.addFieldMap(fm_fy9)
fms2.addFieldMap(fm_fy10)
fms2.addFieldMap(fm_fy11)
fms2.addFieldMap(fm_fy12)
fms2.addFieldMap(fm_fy13)
fms2.addFieldMap(fm_fy14)
fms2.addFieldMap(fm_fy15)
fms2.addFieldMap(fm_fy16)
fms2.addFieldMap(fm_fy17)
fms2.addFieldMap(fm_fy18)
fms2.addFieldMap(fm_fy19)
fms2.addFieldMap(fm_fy20)
fms2.addFieldMap(fm_fy21)
fms2.addFieldMap(fm_fy22)
fms2.addFieldMap(fm_fy23)
fms2.addFieldMap(fm_fy24)
fms2.addFieldMap(fm_fy25)
fms2.addFieldMap(fm_fy26)
fms2.addFieldMap(fm_fy27)
fms2.addFieldMap(fm_fy28)
fms2.addFieldMap(fm_fy29)
fms2.addFieldMap(fm_fy30)
fms2.addFieldMap(fm_fy31)

# append
arcpy.management.Append(["pwms_ints_dupe_for_edit"],"PWMS_Intersections_ModifyTable1_buff5ft_v2","NO_TEST",fms2,"#")

# merge the buffered pwms_blocks and pwms_intersections modifytable layer, then dissolve ########need to put in the pwms intersections buff4ft v2 layer instead!!!!
#arcpy.management.Merge(["PWMS_Blocks_ModifyTable1_buff25ft_v2","PWMS_Intersections_ModifyTable1_buff5ft"],"PWMS_blocks_ints_merge")
arcpy.management.Merge(["PWMS_Blocks_ModifyTable1_buff25ft_v2","PWMS_Intersections_ModifyTable1_buff5ft_v2"],"PWMS_blocks_ints_merge")
# list of fields to dissolve on.

#diss_fields = [f for f in arcpy.ListFields("PWMS_blocks_ints_merge") if f.name in diss_field_names]
# how do i get just subset of the fields to dissolve on?
#diss_fields = arcpy.ListFields("PWMS_Blocks_ModifyTable1")
#print 'length of diss_fields: ', len(diss_fields)
#print 'diss_fields: ', diss_fields
#for f in diss_fields:
#    print f.name
#print 'type of diss_fields[0]: ', type(diss_fields[0])

print
for f in diss_field_names:
    print f
# dissolve
arcpy.management.Dissolve("PWMS_blocks_ints_merge","PWMS_blocks_ints_merge_diss",diss_field_names,"#","MULTI_PART","DISSOLVE_LINES")

# In[ ]:
########################################### ASSET JOIN POLITICAL BOUNDS ####################################################



# Run asset joins to add political boundaries to layer. First read in layers needed for asset join.
Working0 = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working0"
boro_shp = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\Boundaries\Bounds for Scripts\Borough_Boundaries_WaterAreas_21A.shp"
Working1 = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working1"
nyss_shp = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\Boundaries\Bounds for Scripts\State_Senate_WaterAreas_21A.shp"
Working2 = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working2"
nycg_shp = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\Boundaries\Bounds for Scripts\US_Congressional_WaterAreas_21A.shp"
Working3 = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working3"
nycc_shp = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\Boundaries\Bounds for Scripts\City_Council_WaterAreas_21A.shp"
Working4 = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working4"
nyad_shp = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\Boundaries\Bounds for Scripts\State_Assembly_WaterAreas_21A.shp"
Working5 = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working5"
nycd_shp = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\Boundaries\Bounds for Scripts\CommunityDistricts_WaterAreas_21A.shp"
nta_shp = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\Boundaries\Bounds for Scripts\NTA_2020.shp"
Working6 = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working6"
Working7 = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working7"
FEMA_FIRM = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\S_FLD_HAZ_AR_dissolve_2263.shp"
FEMA_TYPE = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\S_FLD_HAZ_AR_dissolve_subtype_2263.shp"
Hurricane_Zones = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\HurricaneEvacuationZones_dissolve_2263.shp"
Working8 = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working8"
Working9 = r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working9"
####### Add the target table to the field mappings class to set the correct schema#################

####when you create fieldmappings obj and add tables to get the schema fields, you can get the field maps from the fieldmappings obj at this point
####then edit the field maps with the correct field name, length, type, merge rule. then replace the field maps.
#join to BoroCD
#fieldmappings = gp.CreateObject("FieldMappings")
fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable("PWMS_blocks_ints_merge_diss")
fieldmappings.addTable(nycd_shp)
fieldmap = fieldmappings.getFieldMap(fieldmappings.findFieldMapIndex("boro_cd"))
field = fieldmap.outputField
field.name = "BoroCD"
field.aliasName = "BoroCD"
field.length = 500
field.type = "String"
fieldmap.outputField = field
fieldmap.mergeRule = "join"
fieldmap.joinDelimiter = ', '
fieldmappings.replaceFieldMap(fieldmappings.findFieldMapIndex("boro_cd"), fieldmap)

arcpy.SpatialJoin_analysis("PWMS_blocks_ints_merge_diss", nycd_shp, Working0, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "INTERSECT", "", "")
arcpy.DeleteField_management(Working0,"Join_Count;TARGET_FID;Shape_Leng;Shape_STAr;Shape_STLe;Shape_Le_1")
print "completed join to Community District Boundaries"

#join to assembly district
#fieldmappings = gp.CreateObject("FieldMappings")
fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable("Z:/PMA/Maria_Rodriguez/Asset Management Database/Assets_Working.gdb/Working0")
fieldmappings.addTable(nyad_shp)
fieldmap = fieldmappings.getFieldMap(fieldmappings.findFieldMapIndex("AssemDist"))
field = fieldmap.outputField
field.name = "AssemDist"
field.aliasName = "AssemDist"
field.length = 500
field.type = "String"
fieldmap.outputField = field
fieldmap.mergeRule = "join"
fieldmap.joinDelimiter = ', '
fieldmappings.replaceFieldMap(fieldmappings.findFieldMapIndex("AssemDist"), fieldmap)

arcpy.SpatialJoin_analysis("Z:/PMA/Maria_Rodriguez/Asset Management Database/Assets_Working.gdb/Working0", nyad_shp, Working1, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "INTERSECT", "", "")
arcpy.DeleteField_management(Working1,"Join_Count;TARGET_FID;Shape_Leng;Shape_STAr;Shape_STLe")
print "completed join to assembly districts"

#join to city council
#fieldmappings = gp.CreateObject("FieldMappings")
fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable(r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working1")
fieldmappings.addTable(nycc_shp)
fieldmap = fieldmappings.getFieldMap(fieldmappings.findFieldMapIndex("CounDist"))
field = fieldmap.outputField
field.name = "CounDist"
field.aliasName = "CounDist"
field.length = 500
field.type = "String"
fieldmap.outputField = field
fieldmap.mergeRule = "join"
fieldmap.joinDelimiter = ', '
fieldmappings.replaceFieldMap(fieldmappings.findFieldMapIndex("CounDist"), fieldmap)

arcpy.SpatialJoin_analysis(Working1, nycc_shp, Working2, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "INTERSECT", "", "")
arcpy.DeleteField_management(Working2,"Join_Count;TARGET_FID;Shape_Leng;Shape_STAr;Shape_STLe")
print "completed join to city council districts"

#join to congressional districts
#fieldmappings = gp.CreateObject("FieldMappings")
fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable(r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working2")
fieldmappings.addTable(nycg_shp)
fieldmap = fieldmappings.getFieldMap(fieldmappings.findFieldMapIndex("CongDist"))
field = fieldmap.outputField
field.name = "CongDist"
field.aliasName = "CongDist"
field.length = 500
field.type = "String"
fieldmap.outputField = field
fieldmap.mergeRule = "join"
fieldmap.joinDelimiter = ', '
fieldmappings.replaceFieldMap(fieldmappings.findFieldMapIndex("CongDist"), fieldmap)

arcpy.SpatialJoin_analysis(Working2, nycg_shp, Working3, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "INTERSECT", "", "")
arcpy.DeleteField_management(Working3,"Join_Count;TARGET_FID;Shape_Leng;Shape_STAr;Shape_STLe")
print "completed join to congressional districts"

#join to senate districts
#fieldmappings = gp.CreateObject("FieldMappings")
fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable(r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working3")
fieldmappings.addTable(nyss_shp)
fieldmap = fieldmappings.getFieldMap(fieldmappings.findFieldMapIndex("StSenDist"))
field = fieldmap.outputField
field.name = "StSenDist"
field.aliasName = "StSenDist"
field.length = 500
field.type = "String"
fieldmap.outputField = field
fieldmap.mergeRule = "join"
fieldmap.joinDelimiter = ', '
fieldmappings.replaceFieldMap(fieldmappings.findFieldMapIndex("StSenDist"), fieldmap)

arcpy.SpatialJoin_analysis(Working3, nyss_shp, Working4, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "INTERSECT", "", "")
arcpy.DeleteField_management(Working4,"Join_Count;TARGET_FID;Shape_Leng;Shape_STAr;Shape_STLe")
print "completed join to state senate districts"

#join to borocode
#fieldmappings = gp.CreateObject("FieldMappings")
fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable(r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working4")
fieldmappings.addTable(boro_shp)
fieldmap = fieldmappings.getFieldMap(fieldmappings.findFieldMapIndex("BoroCode"))
field = fieldmap.outputField
field.name = "BoroCode"
field.aliasName = "BoroCode"
field.length = 500
field.type = "String"
fieldmap.outputField = field
fieldmap.mergeRule = "join"
fieldmap.joinDelimiter = ', '
fieldmappings.replaceFieldMap(fieldmappings.findFieldMapIndex("BoroCode"), fieldmap)

arcpy.SpatialJoin_analysis(Working4, boro_shp, Working5, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "INTERSECT", "", "")
arcpy.DeleteField_management(Working5,"Join_Count;TARGET_FID;BoroName;Shape_Leng;Shape_STAr;Shape_STLe")
print "completed join to borough districts:BoroCode"

#join to boroname
#fieldmappings = gp.CreateObject("FieldMappings")
fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable(r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working5")
fieldmappings.addTable(boro_shp)
fieldmap = fieldmappings.getFieldMap(fieldmappings.findFieldMapIndex("BoroName"))
field = fieldmap.outputField
field.name = "BoroName"
field.aliasName = "BoroName"
field.length = 500
field.type = "String"
fieldmap.outputField = field
fieldmap.mergeRule = "join"
fieldmap.joinDelimiter = ', '
fieldmappings.replaceFieldMap(fieldmappings.findFieldMapIndex("BoroName"), fieldmap)

arcpy.SpatialJoin_analysis(Working5, boro_shp, Working6, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "INTERSECT", "", "")
arcpy.DeleteField_management(Working6,"Join_Count;TARGET_FID;Shape_Leng;Shape_STAr;Shape_STLe")
print "completed join to borough districts:BoroName"

#join to FEMA Flood Zone
#fieldmappings = gp.CreateObject("FieldMappings")
fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable(r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working6")
fieldmappings.addTable(FEMA_FIRM)
fieldmap = fieldmappings.getFieldMap(fieldmappings.findFieldMapIndex("FLD_ZONE"))
field = fieldmap.outputField
field.name = "FEMAFldz"
field.aliasName = "FEMA Flood Zone"
field.length = 500
fieldmap.outputField = field
fieldmap.mergeRule = "join"
fieldmap.joinDelimiter = ', '
fieldmappings.replaceFieldMap(fieldmappings.findFieldMapIndex("FLD_ZONE"), fieldmap)
	
arcpy.SpatialJoin_analysis(Working6, FEMA_FIRM, Working7, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "INTERSECT", "", "")
arcpy.DeleteField_management(Working7,"Join_Count;TARGET_FID")
print "completed join to FEMA Flood Zones districts"

#join to FEMA Flood Type
#fieldmappings = gp.CreateObject("FieldMappings")
fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable(r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working7")
fieldmappings.addTable(FEMA_TYPE)
fieldmap = fieldmappings.getFieldMap(fieldmappings.findFieldMapIndex("ZONE_SUBTY"))
field = fieldmap.outputField
field.name = "FEMAFldT"
field.aliasName = "Flood Zone Subtype"
field.length = 255
fieldmap.outputField = field
fieldmap.mergeRule = "join"
fieldmap.joinDelimiter = ', '
fieldmappings.replaceFieldMap(fieldmappings.findFieldMapIndex("ZONE_SUBTY"), fieldmap)
	
arcpy.SpatialJoin_analysis(Working7, FEMA_TYPE, Working8, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "INTERSECT", "", "")
arcpy.DeleteField_management(Working8,"Join_Count;TARGET_FID")
print "completed join to FEMA Flood Type districts"

#join to Hurricane Evacuation Zones
#fieldmappings = gp.CreateObject("FieldMappings")
fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable(r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working8")
fieldmappings.addTable(Hurricane_Zones)
fieldmap = fieldmappings.getFieldMap(fieldmappings.findFieldMapIndex("hurricane"))
field = fieldmap.outputField
field.name = "HrcEvac"
field.aliasName = "Hurricane Evacuation Zone"
field.length = 500
fieldmap.outputField = field
fieldmap.mergeRule = "join"
fieldmap.joinDelimiter = ', '
fieldmappings.replaceFieldMap(fieldmappings.findFieldMapIndex("hurricane"), fieldmap)

arcpy.SpatialJoin_analysis(Working8, Hurricane_Zones, Working9, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "INTERSECT", "", "")
arcpy.DeleteField_management(Working9,"Join_Count;TARGET_FID;Shape_Leng_1")
print "completed join to hurricane evacuation zones"

#join to NTA
#fieldmappings = gp.CreateObject("FieldMappings")
fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable(r"Z:\PMA\Maria_Rodriguez\Asset Management Database\Assets_Working.gdb\Working9")
fieldmappings.addTable(nta_shp)
fieldmap = fieldmappings.getFieldMap(fieldmappings.findFieldMapIndex("NTAName"))
field = fieldmap.outputField
field.name = "NTAName"
field.aliasName = "Neighborhood Tabulation Area"
field.length = 7000
fieldmap.outputField = field
fieldmap.mergeRule = "join"
fieldmap.joinDelimiter = ', '
fieldmappings.replaceFieldMap(fieldmappings.findFieldMapIndex("NTAName"), fieldmap)
	
PWMS_blocks_ints_merge_diss_assetjoinNTA2020 = arcpy.SpatialJoin_analysis(Working9, nta_shp, "Z:\PMA\TerriChan\GIS Projects\Historical Commitments\Street_Reconstruction\Data\Street_Reconstruction_Projects_for_DOT_Map.gdb\PWMS_blocks_ints_merge_diss_assetjoinNTA2020", "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "INTERSECT", "", "")
arcpy.DeleteField_management(PWMS_blocks_ints_merge_diss_assetjoinNTA2020,
                             "Join_Count;TARGET_FID;Shape_Leng_1;CountyFIPS;NTA2020;NTAAbbrev;NTAType;CDTA2020;CDTAName;Shape_Leng;Shape_STAr;Shape_STLe")
print "completed join to NTAs"

#reorder fields
inputTable = PWMS_blocks_ints_merge_diss_assetjoinNTA2020

# Get field mappings of Input Table
fieldMappings = arcpy.FieldMappings()
fieldMappings.addTable(inputTable)

# Create an empty FieldMappings Object
newFieldMappings = arcpy.FieldMappings()

# Add fields in desired order. Note field index must be known

# method to get the final field schema with all the political/floodzone related bounds
def getFinalFieldSchema(dissolve_field_names):
    # clone the list of diss_field_names 

    final_field_schema = dissolve_field_names[:]
    # remove the FMSID2 field name since it is not in the right order
    final_field_schema.remove("FMSID2")

    political_bounds = ["BoroCode","BoroName","BoroCD","CounDist","AssemDist","StSenDist","CongDist"]
    flood_end_bounds = ["FEMAFldz","FEMAFldT","HrcEvac","NTAName"]

    # insert the political bound field names to the beginning of final_field_schema list
    for i in range(7):
        final_field_schema.insert(i,political_bounds[i])

    # add the flood_end_bounds field names to final_field_schema
    final_field_schema.extend(flood_end_bounds)

    # finally append the FMSID2 field name to final_field_schema
    final_field_schema.append("FMSID2")

    # return final_final_schema list
    return final_field_schema

# loop thru the correct field order then add the field map in that order

for fname in getFinalFieldSchema(diss_field_names):
    index = fieldMappings.findFieldMapIndex(fname)
    newFieldMappings.addFieldMap(fieldMappings.getFieldMap(index))

'''    
for fm in fieldMappings.fieldMappings:
    outField = fm.outputField
    fieldName = outField.name
    #index = fm.findInputFieldIndex(inputTable,fieldName)
    index = fieldMappings.findFieldMapIndex(fieldName)
    if 
    print 'fieldName in fieldMappings of pwms dissolved assetjoinNTA2020 layer: {}, fieldName index is {}, fm type is {}'.format(fieldName, index, type(fm))
    #newFieldMappings.addFieldMap(fm)
    newFieldMappings.addFieldMap(fieldMappings.getFieldMap(index))
'''
# use the feature class to feature class tool to reorganize fields
arcpy.FeatureClassToFeatureClass_conversion(inputTable,arcpy.env.workspace,"PWMS_blocks_ints_merge_diss_assetjoinNTA2020_restruct","",newFieldMappings)

print "done reordering fields"

# export final feature class's attribute table as csv for Historical Commitments PowerBI dashboard consumption
out_location = r"Z:\PMA\TerriChan\GIS Projects\Historical Commitments\PowerBI"
out_csv = "Street_Reconstruction_Projects_test.csv"
arcpy.conversion.TableToTable("PWMS_blocks_ints_merge_diss_assetjoinNTA2020_restruct",out_location,out_csv,"#","#","#")

print 'script done!'
print "Time script ran for:"
print datetime.now() - startTime

