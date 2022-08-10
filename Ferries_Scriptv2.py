# Author: Melissa A Vento
# Date: 07/13/2022
# Description: python script to fully automate Ferries database

# For most new projects, chances are they are either in St. George Terminal in SI or Whitehall terminal in Manhattan. 
# duplicate existing locations that have a new project there

import pandas as pd
import numpy as np
import arcpy
import re
from datetime import datetime
from collections import defaultdict, OrderedDict
# import XTools Pro toolbox
arcpy.ImportToolbox("C:/Program Files (x86)/XTools/XTools Pro/Toolbox/XTools Pro.tbx")

#this is to count how long the script takes to generate output
Start_time = datetime.now()

# How to more fully automate ferries projects :  For most new projects, chances are they are either in St. George Terminal in SI or Whitehall terminal in Manhattan. 
# duplicate existing locations that have a new project there

#####################STEP A ########################

### Read files and set workspace
# Read Actuals excel file 
ACTUALS = pd.read_excel(r'K. Actuals FY2001-FY2022 as of 06.01.22.xlsx',sheet_name='ACTUALS FY2001-FY2022')
ACTUALS.head()
#ACTUALS = "L. Actuals FY2001-FY2022 as of 07.05.22.xlsx"
# read projects with Ferries column from Actuals 
actual_dfcons = ACTUALS[ACTUALS['ACCT DESC'].isin(['IOTB CONSTRU','CONSTRUCTION']) & ACTUALS['DIVISION'].isin(['Ferries'])]

# Read April plan excel file 
CAPITAL_PLAN = "April 2022 Plan.xlsx"

old_location_layer = r"Ferries_Projects_locations_20220502_fixed"
old_ferries_layer = r'Ferries_Projects_20220502'

# set workspace
# arcpy.env.workspace = r'C:\Users\mvento\Desktop\Ferries\FERRIES.gdb'
arcpy.env.workspace = r'Z:\Administrative_Guide\PMA\Melissa Vento\ferries\FERRIES.gdb'
arcpy.env.overwriteOutput = True

# Capital plan excel file
plandf = CAPITAL_PLAN[CAPITAL_PLAN['ACCT DESC'].isin(['IOTB CONSTRU','CONSTRUCTION']) & ACTUALS['DIVISION'].isin(['Ferries'])]


################### STEP 1 ######################
# All find New projects in Whitehall and St. George


###### Search for Projects in St. George ####
# Shows Projects in St. George 

def St_George(x, y, z):
    result = [x + " " + y + " "]
    print(" St.George", result)

x = actual_dfcons[actual_dfcons['PROJ ID DESC'].str.contains('St.George')]
y = actual_dfcons[actual_dfcons['PROJ ID DESC'].str.contains('SIF')]
z = actual_dfcons[actual_dfcons['PROJ ID DESC'].str.contains('FMF')]

# Kennedy class
ken = actual_dfcons[actual_dfcons['PROJ ID DESC'].str.contains('Kennedy')]

# Barberi class
Baberi = actual_dfcons[actual_dfcons['PROJ ID DESC'].str.contains('Barberi')]
newh = actual_dfcons[actual_dfcons['PROJ ID DESC'].str.contains('Newhouse')]

# Austen class 
austen = actual_dfcons[actual_dfcons['PROJ ID DESC'].str.contains('Austen')]

# Molinari class
m = actual_dfcons[actual_dfcons['PROJ ID DESC'].str.contains('Molinari')]

# BRONX
# Cosgrove class
cos = actual_dfcons[actual_dfcons['PROJ ID DESC'].str.contains('Cosgrove ')]


print("New projects in St. George")
print(x)
print(y)
print(z)
print(ken)
print(Baberi)
print(newh)
print(austen)
print(m)


print("New projects in the Bronx")
print(cos)




########### Search for Projects in Whitehall ############
# Shows Projects in Whitehall
a = actual_dfcons[actual_dfcons['PROJ ID DESC'].str.contains('Whitehall')]
print("New projects in Whitehall")
print(a)

#use regex to get the terminals in Whitehall
## Findall that start with W
find_w_capPlan = plandf[plandf['PROJ DESC'].str.match('^W.*')== True]
print("Whitehall found")
print(find_w_capPlan)

## Findall that start with W
find_w_actual = actual_dfcons[actual_dfcons['PROJ ID DESC'].str.match('^W.*')== True]
print("Whitehall found")
print(find_w_actual)


for i in 
################### STEP 1.A ######################
## New projects with no location 
# Email Natalia

# else:

'''
#send email to Natalia
import os
import smtplib
from email.message import EmailMessage

class EmailDataOwnersClass:
    def email_Natalia():
        print("Email Natalia for location") 

    def email_Elaine():
        print("Email Elaine to update the FundStatus and ProjStatus columns ")

if __name__ == "__main__":
    EMAIL_ADDRESS = os.environ.get('MVento@dot.nyc.gov')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')


    msg = EmailMessage()
    msg['subject'] = 'New Ferries Location Address'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = 'nraknimoff@dot.nyc.gov'
    msg.set_content('Hello Natalia, I am emailing you for the location/address of the following new point: ')
    
    with smtplib.SMTP_SSL('smtp.dot.nyc.gov', 587) as smtp:
        smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)

        smtp.send_message(msg)
        print("Email was sent to Natalia Rakhimoff")
'''
##################### STEP 4 ##################

def Projects_Actuals_CapitalPlan():
    actualsdf = pd.read_excel(ACTUALS,sheetname='ACTUALS FY2001-FY2022')
    # actualsdf = pd.read_excel(r'\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\TerriChan\GIS Projects\Historical Commitments\Data\Actuals\J. Actuals FY2001-FY2022 as of 05.02.22.xlsx',sheetname='ACTUALS FY2001-FY2022')
    actualsdf = actualsdf[actualsdf['DIVISION'].isin(['Waterway Bridges', 'Roadway Bridges'])]
    # create a pivot table df grouping on PROJ ID
    actualsbyproj = pd.pivot_table(actualsdf,index=['PROJ ID'], aggfunc=np.sum)
    actualsbyproj.rename(columns=lambda x: x.strip(),inplace=True)
    actualsbyproj = actualsbyproj.reset_index()
    actualsbyproj = actualsbyproj[['PROJ ID','FY01','FY02','FY03','FY04','FY05','FY06','FY07','FY08','FY09','FY10','FY11','FY12','FY13','FY14','FY15','FY16','FY17','FY18','FY19','FY20','FY21']]    # print(actualsbyproj)
    plandf = pd.read_excel(CAPITAL_PLAN,sheetname='DIVISION')
    parksdf = pd.read_excel(CAPITAL_PLAN_PARKS,sheetname='RAW',header=None)
    # plandf = pd.read_excel(r'\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\TerriChan\GIS Projects\Historical Commitments\Data\CapitalPlan\April Plan 2022\April 2022 Plan.xlsx',sheetname='DIVISION')
    # parksdf = pd.read_excel(r'\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\TerriChan\GIS Projects\Historical Commitments\Data\CapitalPlan\April Plan 2022\Parks - April 2022 Capital Plan.xlsx',sheetname='RAW',header=None)  

    plandf = plandf[plandf['DIVISION'].isin(['Bridges'])]
    # add col in plandf to indicate money is DOT
    # print(plandf)
    plandf['FundingAgency'] = 'DOT'
    # print(plandf)
    # since some fields in the Parks Funded Plan aren't the exact same spelling in the DOT Capital Plan
    # change the fields in Parks Funded Plan to match. 
    parksdf.columns = ['FMS ID','FMS DESC','BLIN','BLINE DESC','TYPC','TYPC DESC','ACCT','ACCT DESC','BORO','BORO DESC','CSOB','CSOB DESC','FUNDING','FY22','FY23','FY24','FY25','FY26','FY27','FY28','FY29','FY30','FY31','FY22-31']
    # add col in parksdf to indicate money is Parks
    plandf['FundingAgency'] = 'DOT'

    # since some fields in the Parks Funded Plan aren't the exact same spelling in the DOT Capital Plan
# change the fields in Parks Funded Plan to match. 
    parksdf.rename(columns={'FMS ID': 'PROJ ID', 
                        'FMS DESC': 'PROJ DESC', 
                        'BLIN': 'BLINE'},inplace=True)
    parksdf['FundingAgency'] = 'DPR'
    # print(parksdf)
    # print(parksdf.info())

    # concatenate the DOT Capital Plan and the Parks Funded Plan
    frames = [plandf, parksdf]
    fullplan = pd.concat(frames)  
    # print(fullplan)
    # print(fullplan.info())

    ###fullplan.to_excel(r'Z:\PMA\TerriChan\GIS Projects\Historical Commitments\Bridges\bridges_DOT_Parks_Jan2022Plan_concat_w_agencyfunding.xlsx')

    # pivot the full plan which contains DOT funded and Parks funded money and sum up by PROJ ID
    planbyproj = pd.pivot_table(fullplan,index='PROJ ID',aggfunc=np.sum)
    # print(planbyproj)
    # this is getting all the columns in the Plan since there are some projs whose commitments didnt show up in FY21 yet
    planbyproj2 = planbyproj * 1000
    # reset the index so that PROJ ID can be a column
    planbyproj2 = planbyproj2.reset_index()

    # print(planbyproj3)

    # planbyproj3.to_csv(r'Z:\PMA\TerriChan\GIS Projects\Historical Commitments\Bridges\bridges_DOT_Parks_Jan2022Plan_pivot.csv')

    # take only FY22-FY31 cols from the full plan (since FY21 commitments are mostly all in Actuals by now)
    planbyproj2 = planbyproj2[['PROJ ID','FY22','FY23','FY24','FY25','FY26','FY27','FY28','FY29','FY30','FY31']]
    
    # print(planbyproj2)
    actualsplan_merge = actualsbyproj.merge(planbyproj2,how='outer',left_on='PROJ ID',right_on='PROJ ID',indicator=True)
    # print(actualsplan_merge)
    # since the merge caused the FY fields to turn to float, for FY01 to FY31 cols, fill in the NaNs with 0
    for i in range(1,32):
        if i < 10:
            #print 'FY0'+str(i)
            actualsplan_merge['FY0'+str(i)] = actualsplan_merge['FY0'+str(i)].fillna(0).astype(int)
        else:
            #print 'FY'+str(i)
            actualsplan_merge['FY'+str(i)] = actualsplan_merge['FY'+str(i)].fillna(0).astype(int)
    # change the data type of FY01-FY31 from float to int

    return fullplan, actualsplan_merge



def mergeDesignConstruction():
    actualsdf = pd.read_excel(ACTUALS,sheetname='ACTUALS FY2001-FY2022')
    # print(actualsdf.head()) 
    actualsdfcons = actualsdf[actualsdf['ACCT DESC'].isin(['IOTB CONSTRU','CONSTRUCTION']) & actualsdf['DIVISION'].isin(['Waterway Bridges', 'Roadway Bridges'])]
    tblcons = pd.pivot_table(actualsdfcons,index=['PROJ ID'], aggfunc=np.sum)
    # print(tblcons)
    tblcons.rename(columns=lambda x: x.strip(),inplace=True)
    tbl_cons2 = tblcons.reset_index()
    # we're using FY21 from Actuals since FY21 is over
    tbl_cons2 = tbl_cons2[['PROJ ID','FY01','FY02','FY03','FY04','FY05','FY06','FY07','FY08','FY09','FY10','FY11','FY12','FY13',
                           'FY14','FY15','FY16','FY17','FY18','FY19','FY20','FY21']]
    plandf = pd.read_excel(CAPITAL_PLAN,sheetname='DIVISION')
    parksdf = pd.read_excel(CAPITAL_PLAN_PARKS,sheetname='RAW')
    # print(plandf.info())
    if 'FMS ID' not in parksdf.columns:
        parksdf = pd.read_excel(CAPITAL_PLAN_PARKS,sheetname='RAW',header=None)
    # print(parksdf)
    parksdf_headers = ['FMS ID','FMS DESC','BLIN','BLINE DESC','TYPC','TYPC DESC','ACCT','ACCT DESC','BORO','BORO DESC',
                       'CSOB','CSOB DESC','FUNDING','FY22','FY23','FY24','FY25','FY26','FY27','FY28','FY29','FY30','FY31','FY22-31']
    # print(len(parksdf_headers))  
    parksdf.columns = parksdf_headers
    plancons = plandf[plandf['ACCT DESC'].isin(['CONSTRUCTION']) & plandf['DIVISION'].isin(['Bridges'])]
    # print(plancons) 
    parksdf.rename(columns={'FMS ID': 'PROJ ID', 
                        'FMS DESC': 'PROJ DESC', 
                        'BLIN': 'BLINE'},inplace=True)
    parkscons = parksdf[parksdf['ACCT DESC'].isin(['CONSTRUCTION'])]
    # print(parkscons)
    frames = [plancons, parkscons]
    fullplancons = pd.concat(frames)
    # print(fullplancons)
    tbl_plancons = pd.pivot_table(fullplancons,index='PROJ ID',aggfunc=np.sum)
    # print(tbl_plancons)
    tbl_plancons = tbl_plancons[['FY22','FY23','FY24','FY25','FY26','FY27','FY28','FY29','FY30','FY31']]
    tbl_plancons = tbl_plancons * 1000
    # print(tbl_plancons)
    tbl_plancons2 = tbl_plancons.reset_index()
    merge_cons = tbl_cons2.merge(tbl_plancons2,how='outer',left_on='PROJ ID',right_on='PROJ ID',indicator=True)
    # print(merge_cons)
    for i in range(1,32):
        if i < 10:
            #print 'FY0'+str(i)
            merge_cons['FY0'+str(i)] = merge_cons['FY0'+str(i)].fillna(0)
        else:
            #print 'FY'+str(i)
            merge_cons['FY'+str(i)] = merge_cons['FY'+str(i)].fillna(0)
    # print(merge_cons)

    #merge_cons.to_csv(r'Z:\PMA\TerriChan\GIS Projects\Historical Commitments\Bridges\bridges_cons_acct_desc_actuals_20220502_apr2022plan_parks_outermerge.csv')
    actualsdesg = actualsdf[actualsdf['ACCT DESC'].isin(['DESIGN-CONSU']) & actualsdf['DIVISION'].isin(['Ferries'])]
    # print(actualsdesg)
    tbldesg = pd.pivot_table(actualsdesg, index=['PROJ ID'],aggfunc=np.sum)
    # print(tbldesg)
    tbldesg.rename(columns=lambda x: x.strip(),inplace=True)
    # print(tbldesg)
    tbldesg2 = tbldesg.reset_index()
    tbldesg2 = tbldesg2[['PROJ ID','FY01','FY02','FY03','FY04','FY05','FY06','FY07','FY08','FY09','FY10','FY11','FY12','FY13','FY14','FY15','FY16','FY17','FY18','FY19','FY20','FY21']]
    # print(tbldesg2)
    plandesgn = plandf[plandf['ACCT DESC'].isin(['DESIGN']) & plandf['DIVISION'].isin(['Ferries'])]
    # print(plandesgn)
    parksdesgn = parksdf[parksdf['ACCT DESC'].isin(['DESIGN'])]
    frames = [plandesgn, parksdesgn]
    fullplandesgn = pd.concat(frames)
    # print(fullplandesgn)
    tbl_plandesgn= pd.pivot_table(fullplandesgn,index='PROJ ID',aggfunc=np.sum)
    tbl_plandesgn = tbl_plandesgn * 1000
    tbl_plandesgn2 = tbl_plandesgn.reset_index()
    tbl_plandesgn2 = tbl_plandesgn2[['PROJ ID','FY22','FY23','FY24','FY25','FY26','FY27','FY28','FY29','FY30','FY31']]
    # print(tbl_plandesgn2)
    merge_desgn = tbldesg2.merge(tbl_plandesgn2,how='outer',left_on='PROJ ID',right_on='PROJ ID',indicator=True)
    for i in range(1,32):
        if i < 10:
            #print 'FY0'+str(i)
            merge_desgn['FY0'+str(i)] = merge_desgn['FY0'+str(i)].fillna(0)
        else:
            #print 'FY'+str(i)
            merge_desgn['FY'+str(i)] = merge_desgn['FY'+str(i)].fillna(0)
    # print(merge_desgn.info())
    for i in range(1,30):
        if i < 10:
            merge_desgn['FY0'+str(i)] = merge_desgn['FY0'+str(i)].astype(int)
        else:
            merge_desgn['FY'+str(i)] = merge_desgn['FY'+str(i)].astype(int)
    #merge_desgn.to_csv(r'Z:\PMA\TerriChan\GIS Projects\Historical Commitments\Bridges\bridges_design_acct_desc_actuals_20220502_apr2022plan_parks_outermerge.csv')

    return merge_cons,merge_desgn



#returns the first instance of a non 0 year.
def getEarliestFY(row):
    #Get earliest occurance of a fy year
    if row["FY01"] != 0:
        return 2001
    elif row["FY02"] != 0:
        return 2002
    elif row["FY03"] != 0:
        return 2003
    elif row["FY04"] != 0:
        return 2004
    elif row["FY05"] != 0:
        return 2005
    elif row["FY06"] != 0:
        return 2006
    elif row["FY07"] != 0:
        return 2007
    elif row["FY08"] != 0:
        return 2008
    elif row["FY09"] != 0:
        return 2009
    elif row["FY10"] != 0:
        return 2010
    elif row["FY11"] != 0:
        return 2011
    elif row["FY12"] != 0:
        return 2012
    elif row["FY13"] != 0:
        return 2013
    elif row["FY14"] != 0:
        return 2014
    elif row["FY15"] != 0:
        return 2015
    elif row["FY16"] != 0:
        return 2016
    elif row["FY17"] != 0:
        return 2017
    elif row["FY18"] != 0:
        return 2018
    elif row["FY19"] != 0:
        return 2019
    elif row["FY20"] != 0:
        return 2020
    elif row["FY21"] != 0:
        return 2021
    elif row["FY22"] != 0:
        return 2022
    elif row["FY23"] != 0:
        return 2023
    elif row["FY24"] != 0:
        return 2024
    elif row["FY25"] != 0:
        return 2025
    elif row["FY26"] != 0:
        return 2026
    elif row["FY27"] != 0:
        return 2027
    elif row["FY28"] != 0:
        return 2028
    elif row["FY29"] != 0:
        return 2029
    elif row["FY30"] != 0:
        return 2030 
    else:
        return 2031


def projcheck(row,fmsid_list):

    cancel_match = re.search(r"(?i)(canceled|terminated)",row["ProjStatus"])
    if(cancel_match != None):
        return ""
    committed_match = re.search(r"(?i)(Completed|Construction(?!\s+Solicitation)|Closeout|Substantial\sCompletion)",row["ProjStatus"])
    if(committed_match != None):
        return "Committed"
    if row["FMSID"] not in fmsid_list:
        print(row["FMSID"], row["ProjStatus"])
        return ""
    planned_match = re.search(r"(?i)(On\sHold|Design\sProcurement|Planning\sPhase|Preliminary\sDesign|Final\sDesign|Design\sIn-House|Design\sComponent\sRehab|Amtrack|REI\sProcurement|QA\sProcurement|CSS\sProcurement|Construction Solicitation|ESA|Planned|Procurement)",row["ProjStatus"])
    if(planned_match != None):
        return "Planned"

    # return row["Planned_Or_Committed"]
    return ""


#iterates through the dataframe to update the fiscal year rows
def updateFYMoney(df,actualsdict):
    #Pass in row to update fyrows
    df = df.apply(lambda row: updateFYRow(row,actualsdict),axis =1)

    
    return df

# Fills the FYCons, FYDesign and ProjStatus with either information found in the tally report or the project center.
def fillfy(df,tally,project_center,merge_cons,merge_desgn):
    #Create dictionaries based on FMSID for the tally report,earliest fy and projectcenter
    tally=tally[["FMS_ID","Design_FY","Construction_FY","ProjectStatus","ProjectPhase"]]
    t_con_dict = dict(zip(tally.FMS_ID,tally.Construction_FY))
    t_des_dict = dict(zip(tally.FMS_ID,tally.Design_FY))
    t_proj_dict = dict(zip(tally.FMS_ID,tally.ProjectPhase+"," +tally.ProjectStatus))
    pc_proj_dict = dict(zip(project_center["FMS ID"],project_center["Project Phase"] +", " +project_center["Project Status-Bridge"]))
    merge_cons_dict_earliest_fy = dict(zip(merge_cons["PROJ ID"],merge_cons["Earliest"]))
    merge_desgn_dict_earliest_fy = dict(zip(merge_desgn["PROJ ID"],merge_desgn["Earliest"]))

    #Set to blank for testing
    # df["FYCons"] = ""
    # df["FYDesign"] =""
    # df["ProjStatus"] = ""

    # df["FY01"],df["FY02"], df["FY03"],df["FY04"],df["FY05"],df["FY06"],df["FY07"],df["FY08"],df["FY09"],df["FY10"]= 0,0,0,0,0,0,0,0,0,0
    # df["FY11"],df["FY12"], df["FY13"],df["FY14"],df["FY15"],df["FY16"],df["FY17"],df["FY18"],df["FY19"],df["FY20"]= 0,0,0,0,0,0,0,0,0,0
    # df["FY21"],df["FY22"], df["FY23"],df["FY24"],df["FY25"],df["FY26"],df["FY27"],df["FY28"],df["FY29"],df["FY30"]= 0,0,0,0,0,0,0,0,0,0
    # df["FY31"] = 0
    
    #Apply function to get values for FYCons, FYDesign and ProjStatus
    df[["FYCons","FYDesign","ProjStatus"]] = df.apply(lambda row: pd.Series (fillhelper(row,t_con_dict,t_des_dict,t_proj_dict,merge_cons_dict_earliest_fy,merge_desgn_dict_earliest_fy,pc_proj_dict)), axis =1)

    # print(df[["FYCons","FYDesign","ProjStatus"]].head())
    df['ProjStatus'] = df['ProjStatus'].str.strip()


    return df 


def plan_commit(df,actualsplan_merge):
    fy_list = ["FY01","FY02","FY03","FY04","FY05","FY06","FY07","FY08","FY09","FY10",
                "FY11","FY12","FY13","FY14","FY15","FY16","FY17","FY18","FY19",
                "FY20","FY21","FY22","FY23","FY24","FY25","FY26","FY27","FY28","FY29","FY30","FY31"]

    df["Planned_Or_Committed"] = ""
    df["FYCons"] = pd.to_numeric(df["FYCons"])
    df["FYDesign"] = pd.to_numeric(df["FYDesign"])

    df['FYCons'] = df['FYCons'].fillna(0).astype(int).astype(str)
    df['FYDesign'] = df['FYDesign'].fillna(0).astype(int).astype(str)
    df['FYCons'] = df["FYCons"].replace('0','')
    df['FYDesign'] = df["FYDesign"].replace('0','')

  
    fmsid_list = actualsplan_merge['PROJ ID'].tolist()
    fmsid_list = list(dict.fromkeys(fmsid_list))

    df["Planned_Or_Committed"] = df.apply(lambda row:projcheck(row,fmsid_list) if pd.notnull(row["ProjStatus"]) else plan_commit_helper(row),axis=1)
    
    #checks all fy columns to see if there exists a value greater than 0. If it does not contain one then set it to blank/null. 
    # Does not account for rows with no fy information since those will be deleted anyway
    df.loc[(df[fy_list] > 0).any(axis=1) == False, 'Planned_Or_Committed'] = ""

    return df


############## MAIN ###################

##Reads the Ferries Projects Locations layer and updates the Fiscal Year Money, FYCon, FYDesgn. Exports as CSV. 
def main():
    arcpy.TableToTable_conversion(location_name,r'\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\Wilson Cho\Bridge Update','newLocationLayer.csv')

    actualsplan_merge = Projects_Actuals_CapitalPlan()
    
    df = pd.read_csv("newProjectLocationLayer.csv")
    merge_cons,merge_desgn = mergeDesignConstruction()
    #Create a new column that contains the earliest fy year that money was committed 
    merge_cons["Earliest"] = merge_cons.apply(lambda row: getEarliestFY(row), axis = 1)
    merge_desgn["Earliest"] = merge_desgn.apply(lambda row: getEarliestFY(row), axis = 1)


    #Function to fill FYCons, FYDesgn and ProjStatus
    df = fillfy(df,merge_cons,merge_desgn)
    #Create dictionary with the moneys
    actualsdict = actualsplan_merge.set_index('PROJ ID').T.to_dict('list')

    #updates the fiscal year money and the total cost
    df = updateFYMoney(df,actualsdict)

    df = plan_commit(df,actualsplan_merge)

    df.to_csv('Ferries.csv',index=False)
    print('Successfully created CSV')
    return df



######################### STEP 4 ##############################
## Performs the asset join on the layers 
def assetjoin():
    # Run asset joins to add political boundaries to layer. First read in layers needed for asset join.
    dissolve_table = r'in_memory\\bridge_projects_dissolved'
    Working0 = r'in_memory\\Working0'
    boro_shp = r"\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\Boundaries\Bounds for Scripts\Borough_Boundaries_WaterAreas_21A.shp"
    Working1 = r'in_memory\\Working1'
    nyss_shp = r"\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\Boundaries\Bounds for Scripts\State_Senate_WaterAreas_21A.shp"
    Working2 = r'in_memory\\Working2'
    nycg_shp = r"\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\Boundaries\Bounds for Scripts\US_Congressional_WaterAreas_21A.shp"
    Working3 = r'in_memory\\Working3'
    nycc_shp = r"\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\Boundaries\Bounds for Scripts\City_Council_WaterAreas_21A.shp"
    Working4 = r'in_memory\\Working4'
    nyad_shp = r"\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\Boundaries\Bounds for Scripts\State_Assembly_WaterAreas_21A.shp"
    Working5 = r'in_memory\\Working5'

    nycd_shp = r"\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\Boundaries\Bounds for Scripts\CommunityDistricts_WaterAreas_21A.shp"

    nta_shp = r"\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\Boundaries\Bounds for Scripts\NTA_2020.shp"
    Working6 = r'in_memory\\Working6'
    Working7 = r'in_memory\\Working7'
    FEMA_FIRM = r"\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\S_FLD_HAZ_AR_dissolve_2263.shp"
    FEMA_TYPE = r"\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\S_FLD_HAZ_AR_dissolve_subtype_2263.shp"
    Hurricane_Zones = r"\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\Maria_Rodriguez\Asset Management Database\Shapefiles\HurricaneEvacuationZones_dissolve_2263.shp"
    Working8 = r'in_memory\\Working8'
    Working9 = r'in_memory\\Working9'
    ####### Add the target table to the field mappings class to set the correct schema#################

    ####when you create fieldmappings obj and add tables to get the schema fields, you can get the field maps from the fieldmappings obj at this point
    ####then edit the field maps with the correct field name, length, type, merge rule. then replace the field maps.
    #join to BoroCD
    #fieldmappings = gp.CreateObject("FieldMappings")
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(dissolve_table)
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

    arcpy.SpatialJoin_analysis(dissolve_table, nycd_shp, Working0, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "INTERSECT", "", "")
    arcpy.DeleteField_management(Working0,"Join_Count;TARGET_FID;Shape_Leng;Shape_STAr;Shape_STLe;Shape_Le_1")
    print ("completed join to Community District Boundaries")

    #join to assembly district
    #fieldmappings = gp.CreateObject("FieldMappings")
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(Working0)
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

    arcpy.SpatialJoin_analysis(Working0, nyad_shp, Working1, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "INTERSECT", "", "")
    arcpy.DeleteField_management(Working1,"Join_Count;TARGET_FID;Shape_Leng;Shape_STAr;Shape_STLe")
    print ("completed join to assembly districts")

    #join to city council
    #fieldmappings = gp.CreateObject("FieldMappings")
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(Working1)
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
    print ("completed join to city council districts")

    #join to congressional districts
    #fieldmappings = gp.CreateObject("FieldMappings")
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(Working2)
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
    print ("completed join to congressional districts")

    #join to senate districts
    #fieldmappings = gp.CreateObject("FieldMappings")
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(Working3)
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
    print ("completed join to state senate districts")

    #join to borocode
    #fieldmappings = gp.CreateObject("FieldMappings")
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(Working4)
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
    print ("completed join to borough districts:BoroCode")

    #join to boroname
    #fieldmappings = gp.CreateObject("FieldMappings")
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(Working5)
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
    print ("completed join to borough districts:BoroName")

    #join to FEMA Flood Zone
    #fieldmappings = gp.CreateObject("FieldMappings")
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(Working6)
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
    print ("completed join to FEMA Flood Zones districts")

    #join to FEMA Flood Type
    #fieldmappings = gp.CreateObject("FieldMappings")
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(Working7)
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
    print ("completed join to FEMA Flood Type districts")

    #join to Hurricane Evacuation Zones
    #fieldmappings = gp.CreateObject("FieldMappings")
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(Working8)
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
    print( "completed join to hurricane evacuation zones")

    #join to NTA
    #fieldmappings = gp.CreateObject("FieldMappings")
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(Working9)
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


    PWMS_blocks_ints_merge_diss_assetjoinNTA2020 = arcpy.SpatialJoin_analysis(Working9, nta_shp, dissolved_name, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "INTERSECT", "", "")
    arcpy.DeleteField_management(PWMS_blocks_ints_merge_diss_assetjoinNTA2020,
                                "Join_Count;TARGET_FID;Shape_Leng_1;CountyFIPS;NTA2020;NTAAbbrev;NTAType;CDTA2020;CDTAName;Shape_Leng;Shape_STAr;Shape_STLe")
    print ("completed join to NTAs")

    arcpy.Delete_management('in_memory')

print ("Script ran for:")
print (datetime.now() - Start_time)
