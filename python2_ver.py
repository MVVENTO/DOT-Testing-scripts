#Wilson Cho
#Bridge Layer Script
#This script updates the current bridge_locations_layer using values from various sources such as the actuals, capital plan, bridge tally report and the project center. 
#It creates a copy of the bridge layer and performs the update of the values and dissolves the rows to create a new layer. 

import numpy as np
import pandas as pd
import re
import arcpy
pd.options.mode.chained_assignment = None  # default='warn'
from collections import defaultdict, OrderedDict
from datetime import date
#Alter the names of the variables below to change the files that are used when you want to update

ACTUALS = "L. Actuals FY2001-FY2022 as of 07.05.22.xlsx"
# ACTUALS = 'K. Actuals FY2001-FY2022 as of 06.01.22 with test.xlsx'
CAPITAL_PLAN = "April 2022 Plan.xlsx"
# CAPITAL_PLAN = "April 2022 Plan with test.xlsx"

CAPITAL_PLAN_PARKS = "Parks - April 2022 Capital Plan.xlsx"
#The bridge tally exported as an .xlsx seems to be formatted in such a way that pandas cannot get the column names. 
BRIDGE_TALLY = "Bridge Tally Report v3-Ad Hoc.csv"
BRIDGE_PROJECT_CENTER = "ProjectCenter.xlsx"
ACTUALSTEMP = "bridges_actuals_20220502_apr2022plan_outermerge.csv"
#Additionally change the name of location_layer to the current one as well as the workspace to the correct directory
#This process can likely be automated by running through the names of the location layers and finding the most recent one
#At the moment the code does not delete the previous layer and instead creates/works on a copy of it to ensure nothing is lost. 

old_location_layer = r"Bridge_Projects_locations_20220502_fixed1"
old_bridge_layer = r'Bridge_Projects_20220502'
# arcpy.env.workspace = r'C:\Users\wcho\Desktop\HistoricalCommitments\Bridges\foldertest.gdb'
arcpy.env.workspace = r'\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\Wilson Cho\HistoricalCommitments\Bridges\tester.gdb'
arcpy.env.overwriteOutput = True

pavement_FMSIDs = ["HBM1212","HBX663"]

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
    planFdf = pd.read_excel(CAPITAL_PLAN,sheetname='DIVISION')
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
    actualsdesg = actualsdf[actualsdf['ACCT DESC'].isin(['DESIGN-CONSU']) & actualsdf['DIVISION'].isin(['Roadway Bridges', 'Waterway Bridges'])]
    # print(actualsdesg)
    tbldesg = pd.pivot_table(actualsdesg, index=['PROJ ID'],aggfunc=np.sum)
    # print(tbldesg)
    tbldesg.rename(columns=lambda x: x.strip(),inplace=True)
    # print(tbldesg)
    tbldesg2 = tbldesg.reset_index()
    tbldesg2 = tbldesg2[['PROJ ID','FY01','FY02','FY03','FY04','FY05','FY06','FY07','FY08','FY09','FY10','FY11','FY12','FY13','FY14','FY15','FY16','FY17','FY18','FY19','FY20','FY21']]
    # print(tbldesg2)
    plandesgn = plandf[plandf['ACCT DESC'].isin(['DESIGN']) & plandf['DIVISION'].isin(['Bridges'])]
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

    # pivot the full plan which contains DOT funded and Parks funded money and sum up by PROJ ID
    planbyproj = pd.pivot_table(fullplan,index='PROJ ID',aggfunc=np.sum)
    # print(planbyproj)
    # this is getting all the columns in the Plan since there are some projs whose commitments didnt show up in FY21 yet
    planbyproj2 = planbyproj * 1000
    # reset the index so that PROJ ID can be a column
    planbyproj2 = planbyproj2.reset_index()

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

##Converts the format of FY## into its corresponding integer year
def getFY(fy):
    fy = str(fy)
    temp = ""
    #use regex to get the fy years
    match = re.search(r'.*([0-9][0-9])',fy)
    if(match != None):
        temp = match.group(1)
        temp = "20" + temp
        temp = (int)(temp)
    return (temp)

## Helper for fillyfy()
def fillhelper(row,t_con_dict,t_des_dict,t_proj_dict,merge_cons_dict_earliest_fy,merge_desgn_dict_earliest_fy,pc_proj_dict):
    fycon,fydesgn,projstatus = row["FYCons"],row["FYDesign"],row["ProjStatus"]


    #If the fmsid2 was found in the tally report then populate FYCons, FYDesign and ProjStatus with information from there
    if row["FMSID2"] in t_con_dict:
        fycon = getFY(t_con_dict.get(row["FMSID2"]))
        fydesgn = getFY(t_des_dict.get(row["FMSID2"]))
        projstatus = t_proj_dict.get(row["FMSID2"],row["ProjStatus"])
    #Otherwise use the earliest fy/project center
    else:
        fycon = merge_cons_dict_earliest_fy.get(row["FMSID"])
        fydesgn = merge_desgn_dict_earliest_fy.get(row["FMSID"])
        projstatus = pc_proj_dict.get(row["FMSID2"],row["ProjStatus"])
    return fycon, fydesgn, projstatus



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

# if the FMSID is found inside of actualsdict then fill in the fiscal year money otherwise fill with 0s
def updateFYRow(row,actualsdict):
    #Get list from the dictionary
    list = actualsdict.get(row["FMSID"],[])

    if list:
        #Remove final value from list
        list = list[:-1] 

        #Set the new fy values for the row

        for x in range(len(list)):
            if(x<=8):
                temp = "FY0"+str(x+1)
            else:
                temp = "FY"+str(x+1)
            row[temp]=(int)(list[x])
        
        #Get the totaled cost
        row["Cost"] = sum(map(int, list))
    else:
                # print(row["FMSID"],"has not been found in the dictionary")
        for x in range(32):
            # set fy years to 0
            if(x<=8):
                temp = "FY0"+str(x+1)
            else:
                temp = "FY"+str(x+1)
            row[temp]=0
            
        row["Cost"] = 0
    return row

#iterates through the dataframe to update the fiscal year rows
def updateFYMoney(df,actualsdict):
    #Pass in row to update fyrows
    df = df.apply(lambda row: updateFYRow(row,actualsdict),axis =1)

    
    return df

def plan_commit_helper(row):
    #Both fycons and fydesign are non null
    if row["FYCons"]!="" and row["FYDesign"]!="":
        if (int)(row["FYCons"]) >= 2022 or (int)(row["FYDesign"]) >= 2022:
            return "Planned"
        elif (int)(row["FYCons"]) < 2022 or (int)(row["FYDesign"]) < 2022:
            return "Committed"
    #if fycons is not null, assumes fydesgn is null
    elif row["FYCons"]!="":
        if (int)(row["FYCons"]) >= 2022:
            return "Planned"
        elif (int)(row["FYCons"]) < 2022:
            return "Committed"        
    elif row["FYDesign"]!="":
        if (int)(row["FYDesign"]) >= 2022:
            return "Planned"
        elif (int)(row["FYDesign"]) < 2022:
            return "Committed"
    return None

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

def plan_commit(df,actualsplan_merge):
    fy_list = ["FY01","FY02","FY03","FY04","FY05","FY06","FY07","FY08","FY09","FY10",
                "FY11","FY12","FY13","FY14","FY15","FY16","FY17","FY18","FY19",
                "FY20","FY21","FY22","FY23","FY24","FY25","FY26","FY27","FY28","FY29","FY30","FY31"]

    df["Planned_Or_Committed"] = ""
    # df.loc[:, ["FYCons","FYDesign"]] = df.loc[:, ["FYCons","FYDesign"]].fillna('')
    df["FYCons"] = pd.to_numeric(df["FYCons"])
    df["FYDesign"] = pd.to_numeric(df["FYDesign"])

    df['FYCons'] = df['FYCons'].fillna(0).astype(int).astype(str)
    df['FYDesign'] = df['FYDesign'].fillna(0).astype(int).astype(str)
    df['FYCons'] = df["FYCons"].replace('0','')
    df['FYDesign'] = df["FYDesign"].replace('0','')

    # plandf = pd.read_excel(CAPITAL_PLAN,sheetname='DIVISION')
    # plandf = plandf[plandf['DIVISION'].isin(['Bridges'])]
    # fmsid_list = plandf['PROJ ID'].tolist()
    # fmsid_list = list(dict.fromkeys(fmsid_list))
    fmsid_list = actualsplan_merge['PROJ ID'].tolist()
    fmsid_list = list(dict.fromkeys(fmsid_list))
    

    df["Planned_Or_Committed"] = df.apply(lambda row:projcheck(row,fmsid_list) if pd.notnull(row["ProjStatus"]) else plan_commit_helper(row),axis=1)
    
    #checks all fy columns to see if there exists a value greater than 0. If it does not contain one then set it to blank/null. 
    # Does not account for rows with no fy information since those will be deleted anyway
    df.loc[(df[fy_list] > 0).any(axis=1) == False, 'Planned_Or_Committed'] = ""

    return df

##Reads the Bridge Projects Locations layer and updates the Fiscal Year Money, FYCon, FYDesgn. Exports as CSV. 
def main():
    arcpy.TableToTable_conversion(location_name,r'\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\Wilson Cho\Bridge Update','newLocationLayer.csv')

    fullplan, actualsplan_merge = Projects_Actuals_CapitalPlan()
    # actualsplan_merge.to_csv("mergedplan.csv")
    df = pd.read_csv("newLocationLayer.csv")
    merge_cons,merge_desgn = mergeDesignConstruction()
    #Create a new column that contains the earliest fy year that money was committed 
    merge_cons["Earliest"] = merge_cons.apply(lambda row: getEarliestFY(row), axis = 1)
    merge_desgn["Earliest"] = merge_desgn.apply(lambda row: getEarliestFY(row), axis = 1)

    # merge_cons.to_csv("merge_cons.csv")
    # merge_desgn.to_csv("merge_desgn.csv")
    
    #Pandas seemed to read the bridge tally report oddly and some of the column names were removed. 
    tally = pd.read_csv(BRIDGE_TALLY)
    tally = tally.rename(columns={ tally.columns[0]: "FMS_ID", "Textbox12":"ProjectPhase", "Textbox15":"BIN"})

    #Read project center excel sheet and keep certain rows
    project_center = pd.read_excel(BRIDGE_PROJECT_CENTER)
    #keeps non-null rows
    project_center = project_center[project_center["FMS ID"].notnull()]
    #run replacerows to find and change name for comma delimited name
    project_center["FMS ID"] = project_center.apply(lambda row: replacerows(row),axis=1)
    #performs explodes the columns that are comma delimited. Similar to pd.explode but it is not available on python2 pandas
    project_center = project_center.drop('FMS ID', axis=1).join(project_center['FMS ID'].str.split(',', expand=True).stack().reset_index(level=1, drop=True).rename('FMS ID'))
    project_center = project_center[["FMS ID", "Project Status-Bridge","Project Phase", "Design FY","Construction FY"]]
    project_center = project_center.fillna("N/A")


    #Function to fill FYCons, FYDesgn and ProjStatus
    df = fillfy(df,tally,project_center,merge_cons,merge_desgn)
    #Create dictionary with the moneys
    actualsdict = actualsplan_merge.set_index('PROJ ID').T.to_dict('list')

    #updates the fiscal year money and the total cost
    df = updateFYMoney(df,actualsdict)

    df = plan_commit(df,actualsplan_merge)

    df.to_csv('pythonver.csv',index=False)
    print('Successfully created CSV')
    return df

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

##Updates the locationslayer with the CSV from main(). Also performs the Dissolve on the layer.
def arcpyupdatelocationslayer():
    inFeatures = location_name
    outFeatureclass = r'in_memory\\bridge_projects_dissolved'

    fields = ["FundStatus","ProjStatus","FYCons","FYDesign","Cost","Planned_Or_Committed","FY01","FY02","FY03","FY04","FY05","FY06","FY07","FY08","FY09","FY10",
              "FY11","FY12","FY13","FY14","FY15","FY16","FY17","FY18","FY19",
              "FY20","FY21","FY22","FY23","FY24","FY25","FY26","FY27","FY28","FY29","FY30","FY31"]
    fy = ["FY01","FY02","FY03","FY04","FY05","FY06","FY07","FY08","FY09","FY10",
              "FY11","FY12","FY13","FY14","FY15","FY16","FY17","FY18","FY19",
              "FY20","FY21","FY22","FY23","FY24","FY25","FY26","FY27","FY28","FY29","FY30","FY31"]
    df = pd.read_csv("pythonver.csv")
    #replace any empty spaces with None/nan
    non_null_df = df.replace(r'^\s*$', np.nan, regex=True)
    non_null_df = non_null_df[non_null_df["BIN"].notnull()]
    bin_location_dict = defaultdict(list)
    #create dictionary with comma delimited bin for each fmsid based on the bridge project locations layer
    for index, row in non_null_df.iterrows():
        bin_location_dict[row["FMSID2"]].append(row["BIN"])

    for key in bin_location_dict:
        converted_list = [str(element) for element in bin_location_dict.get(key)]
        bin_location_dict[key] = ",".join(converted_list)

    df = df[fields]
    df[fy] = df[fy].astype(int)
    df['FundStatus'] = df['FundStatus'].where(df['FundStatus'].notnull(),None )
    df['ProjStatus'] = df['ProjStatus'].where(df['ProjStatus'].notnull(),None )

    i = 0
    testarray = df.values
    # Iterate through the fields of the layer and update them with the information in the updated csv
    with arcpy.da.UpdateCursor(inFeatures,fields) as cursor:
        for row in cursor:
            for x in range(0,len(row) ):
                # print(row[x],testarray[i][x])
                row[x] = testarray[i][x]
            i+=1
            cursor.updateRow(row)
    
    with arcpy.da.UpdateCursor(inFeatures,"Cost") as cursor:
        for row in cursor:
            if row[0] == 0:
                cursor.deleteRow()
    dissolveFields = ["Division","FMSID","PROJ_ID_DE","FYCons","FYDesign","FundStatus","ProjStatus","Cost","Planned_Or_Committed",
                      "FY01","FY02","FY03","FY04","FY05","FY06","FY07","FY08","FY09","FY10",
                      "FY11","FY12","FY13","FY14","FY15","FY16","FY17","FY18","FY19",
                      "FY20","FY21","FY22","FY23","FY24","FY25","FY26","FY27","FY28","FY29","FY30","FY31",
                      "FMSID2"]    
    arcpy.Dissolve_management(inFeatures,outFeatureclass,dissolveFields,"","MULTI_PART","DISSOLVE_LINES")

    #adds bin field and sets value based on FMSID2. If they are not found in the newly created dictionary the BIN is taken frmo the old layer
    arcpy.AddField_management(outFeatureclass, "BIN", "TEXT", 
                          field_length=500)
    with arcpy.da.UpdateCursor(outFeatureclass,["FMSID2","BIN"]) as cursor:
        for row in cursor:
                row[1] = bin_location_dict.get(row[0])
                cursor.updateRow(row)    
    print('Updated Bridge Locations Layer')
    # arcpy.JoinField_management(outFeatureclass,in_field="FMSID2",join_table=inFeatures,join_field='FMSID2', fields=["BoroCode","BoroName","BoroCD","AssemDist","StSenDist","CongDist","CounDist","FEMAFldz","FEMAFldT","HrcEvac","NTAName"])

##Exports the NTA and Metadata from the old bridge project layer and imports them into the new layer.
def updateNTAMeta():
    Bridge_Project_dict = {}
    # Bridge_Project_bin_dict ={}
    inFeatures = dissolved_name
    metadata = r'metadata.xml'
    #get nta names from the old layer
    with arcpy.da.SearchCursor(old_bridge_layer,["FMSID2","NTAName","BIN"]) as cursor:
        for row in cursor: 
            Bridge_Project_dict[row[0]] = row[1]
            # Bridge_Project_bin_dict[row[0]] = row[2]
    # print(Bridge_Project_dict)

    #if the nta was not filled in after the asset join then take the value from the old layer
    with arcpy.da.UpdateCursor(inFeatures,["FMSID2","NTAName","BIN"]) as cursor:
        for row in cursor:
            #if row is empty then take the value from the old bridge layer that
            if row[1] == None:
                if row[0] in Bridge_Project_dict:
                    row[1] = Bridge_Project_dict.get(row[0])
            #check bins to see if they are all 7 characters and above. If they are not then take the valuef rom the old layer 
            # if row[2] != None:
            #     if len(row[2]) <7:
            #         if row[0] in Bridge_Project_bin_dict:
                        # print("ran: ", row[0], row[2], Bridge_Project_bin_dict.get(row[0]))
                        # row[2] = Bridge_Project_bin_dict.get(row[0])
            cursor.updateRow(row)
    
    dir = arcpy.GetInstallInfo("desktop")["InstallDir"]
    translator = dir + "Metadata/Translator/ESRI_ISO2ISO19139.xml"
    #export the metadata of the old layer and import it into the new one 
    arcpy.ExportMetadata_conversion (old_bridge_layer, translator,metadata)
    arcpy.ImportMetadata_conversion(metadata,Target_Metadata=inFeatures,Enable_automatic_updates=True)
    print('updated NTA and Metadata')

def findbin(str):
    match = re.search(r'(\d(?:[- ]*\d){6})',str)
    if(match != None):
        return match.group(1)
    return None  

## Reads in the capital plan and the actuals in order to map any missing or new FMSIDs in the Bridge Project Location layer. 
## Utilizes the DOT Bridge layer and the current Bridge Project Location layer to match a BIN.
def mapmissing():
    #dot_bridges_layer = r'DOT_Bridges_copy'
    dot_bridges_layer = r'\\dotfp\40Worth_DatafilesII\Administrative_Guide\PMA\Maxwell Siegel\Asset Management\Access Database\Asset DB.gdb\Bridges\DOT_Bridges'
    fmsiddict ={}
    arcpy.CopyFeatures_management(old_location_layer, location_name)

    #create dictionary to get existing fmsids
    with arcpy.da.SearchCursor(location_name,["FMSID","BIN"]) as cursor:
        for row in cursor: 
            #just to check fmsid
            fmsiddict[row[0]] =row[1]
    
    # read actuals file and keep proj id/ proj id desc         
    actualsdf = pd.read_excel(ACTUALS,sheetname='ACTUALS FY2001-FY2022')
    #only keep certain rows
    actualsdf = actualsdf[actualsdf['ACCT DESC'].isin(['IOTB CONSTRU','CONSTRUCTION']) & actualsdf['DIVISION'].isin(['Waterway Bridges', 'Roadway Bridges'])]
    actualsdf = actualsdf[["PROJ ID", "PROJ ID DESC"]]
    #read capital plan keeping bridge rows and renaming columns
    plandf = pd.read_excel(CAPITAL_PLAN,sheetname='DIVISION')
    plandf = plandf[plandf['DIVISION'].isin(['Bridges'])]
    plandf = plandf[["PROJ ID","PROJ DESC"]]
    plandf = plandf.rename(columns={'PROJ DESC': 'PROJ ID DESC'})

    #combine capital plan and actuals df
    combined = pd.concat([actualsdf,plandf],ignore_index=True)
    # combined = combined.reset_index()

    #create and fill new column BIN with information in the dict
    combined["BIN"] = combined["PROJ ID"].apply(lambda x: fmsiddict.get(x))
    excluded = ["841 CONVERTED","002 ADJACTUAL"]
    #keeps null values only and excludes certain FMSIDs
    #not sure if excluding it is necessary
    combined = combined[combined['BIN'].isnull() ]
    combined = combined[~combined["PROJ ID"].isin(excluded)]

    #this is the list of entries/fmsids in the actuals that do not appear in the layer but also have a bin that can be found
    combined["BIN"] = combined["PROJ ID DESC"].apply(lambda x: findbin(x))
    combined = combined[~combined['BIN'].isnull() ]
    combined["BIN"] = combined["BIN"].str.replace('-','')
    combined= combined.reset_index()
    list_to_layer = []

    rowdict = OrderedDict()
    #create and fill ordered dictionary with the fields of the bridge location layer
    fields = arcpy.ListFields(location_name)
    for field in fields:
        rowdict[field.name] = None
    
    # ADDS NEW ROW TO THE BRIDGE LAYERS IF an existing bin is found in the bridge_projects location layer and removes them from the df
    indexes_to_drop = []
    for index, row in combined.iterrows():
        #iterates through every row of the df with bins that do not exist in the layer
        #create update cursor searching for matching bins
        where_clause = "BIN='{}'".format(row["BIN"])
        with arcpy.da.UpdateCursor(location_name,"*",where_clause=where_clause) as cursor:
            for row2 in cursor:
                # print(row2)
                counter = 0
                #copy the row 
                tempdict = rowdict.copy()
                for key in tempdict.keys():
                    tempdict[key] = row2[counter]
                    counter = counter + 1
                # change some aspects of the new row
                tempdict["FMSID"] = row["PROJ ID"]
                tempdict["PROJ_ID_DE"] = row["PROJ ID DESC"]
                tempdict["FMSID2"] = row["PROJ ID"][4:]
                tempdict["BIN"] = row["BIN"]
                tempdict["FMSIDBIN"] = row["PROJ ID"]+row["BIN"]
                list_to_layer.append(tempdict.values())
                # combined.drop(index,inplace=True)
                indexes_to_drop.append(index)

    indexes_to_drop = list(dict.fromkeys(indexes_to_drop))
    combined.drop(combined.index[indexes_to_drop],inplace=True)
    combined.reset_index(inplace=True)

    #this is for the bridge projects that did not get their bins found in the current bridge project locations layer
    #instead we are looking at the dot_bridges layer 

    #create empty dictionary with fields of dot bridges layer
    dot_bridge_dict = OrderedDict()
    fields = arcpy.ListFields(dot_bridges_layer)
    for field in fields:
        dot_bridge_dict[field.name] = None
    #iterate through remaining values in df to check if their bins are found in dot bridge 
    indexes_to_drop = []
    for index, row in combined.iterrows():
            where_clause = "BIN='{}'".format(row["BIN"])
            #finds rows in dot bridge layer where the bin is the same
            with arcpy.da.SearchCursor(dot_bridges_layer,"*",where_clause=where_clause) as cursor:
                #should only run once if an entry is found because BINs are distinct the DOT Bridge Layer
                for row2 in cursor:
                    #Copies all of the data found by the cursor into a dictionary to map values
                    counter=0
                    tempdotdict = dot_bridge_dict.copy()
                    tempdict = rowdict.copy()
                    for key in tempdotdict.keys():
                        tempdotdict[key] = row2[counter]
                        counter = counter + 1
                    #map corresponding values from dot bridges layer to our row dict
                    tempdict["FMSID"] = row["PROJ ID"]
                    tempdict["FMSIDBIN"] = row["PROJ ID"]+row["BIN"]
                    tempdict["BIN"] = row["BIN"]
                    tempdict["PROJ_ID_DE"] = row["PROJ ID DESC"]
                    tempdict["FMSID2"] = row["PROJ ID"][4:]
                    tempdict["FEATURE_CA"] = tempdotdict.get("FEATURE_CARRIED")
                    tempdict["FEATURE_CR"] = tempdotdict.get("FEATURE_CROSSED")
                    tempdict["Shape"] = tempdotdict.get("SHAPE")
                    
                    # tempdict["X"] = tempdotdict.get("SHAPE")[0]
                    # tempdict["Y"] = tempdotdict.get("SHAPE")[1]

                    tempdict["BoroCode"] = tempdotdict.get("BoroCode")
                    tempdict["BoroCD"] = tempdotdict.get("BoroCD")
                    tempdict["BoroName"] = tempdotdict.get("BoroName")
                    tempdict["NTAName"] = tempdotdict.get("NTAName")
                    tempdict["FEMAFldT"] = tempdotdict.get("FEMAFldT")
                    tempdict["FEMAFldz"] = tempdotdict.get("FEMAFldz")

                    tempdict["HrcEvac"] = tempdotdict.get("HrcEvac")
                    tempdict["Division"] = "Bridges"
                    tempdict["Date"] = tempdotdict.get("Date")

                    tempdict["AssemDist"] = tempdotdict.get("AssemDist")
                    tempdict["CounDist"] = tempdotdict.get("CounDist")
                    tempdict["CongDist"] = tempdotdict.get("CongDist")
                    tempdict["StSenDist"] = tempdotdict.get("StSenDist")
                    #append to a list that will be used to add layers and drop from the df
                    list_to_layer.append(tempdict.values())
                    indexes_to_drop.append(index)
    
    combined.drop(combined.index[indexes_to_drop],inplace=True)
    #prints out the new rows that will be added
    for x in list_to_layer:
        print("Adding to bridge_project_location layer: " +x[10])
    #inserts these rows into the location layer 
    if list_to_layer:         
        cursor = arcpy.da.InsertCursor(location_name,"*")
        for row in list_to_layer:
            cursor.insertRow(row)
    else:
        print("no new entries added")

#reorder the fields of the updated layer to match those of the old one
def reorder_fields():
    arcpy.env.overwriteOutput = True

    inFeatures = dissolved_name

    arcpy.AddField_management(inFeatures, "isExist", "TEXT", 
                          field_length=500)
    fields = arcpy.ListFields(inFeatures)

    # Get field mappings of Input Table
    fieldMappings = arcpy.FieldMappings()
    fieldMappings.addTable(inFeatures)
    # Create an empty FieldMappings Object
    newFieldMappings = arcpy.FieldMappings()
    fielddict = OrderedDict()
    #exclude the first two fields which are objectid and SHAPE 
    fields = fields[2:]
    #create dictionary with each field and its position in the new layer
    for x in range(len(fields)):
        fielddict[(fields[x].name).lower()] = x

    old_fields = arcpy.ListFields(old_bridge_layer)

    old_fields =old_fields[2:]
    for field in old_fields:
        #add the fields in the order that they take place in the old layer but with the new values.
        newFieldMappings.addFieldMap(fieldMappings.getFieldMap(fielddict.get((field.name).lower())))
    #sometimes overwrite does not seem to work so just delete the layer with the same name just in case. 
    if arcpy.Exists (reordered_name): 
        arcpy.Delete_management (reordered_name)
    
    #export the new layer and delete the old one
    arcpy.FeatureClassToFeatureClass_conversion(inFeatures,arcpy.env.workspace,reordered_name,field_mapping=newFieldMappings)
    #cleaning up 
    if arcpy.Exists(dissolved_name):
        arcpy.Delete_management(dissolved_name)
    print("reordered fields")

#gets projectstaus and funding status from pavementworks layer for the projects involved. 
def pavementworks(fmsid_list):
    #ProjectStatus
    #FundingStatus
    pavementworksdbf = r'Database Connections\PWMS on dotgissql01.sde\PWMS.dbo.ProjectLocationIntersection'
    pavement_dict ={}
    #check the pavementworks layer for the corresponding layer fmsids in the list
    for fmsid in fmsid_list:
        where_clause = "FMSID='{}'".format(fmsid)
        #if it is found then copy the funding status and projstatus into a dictionary
        with arcpy.da.SearchCursor(pavementworksdbf,["FMSID","FundingStatus","ProjectStatus"],where_clause=where_clause) as cursor:
            for row in cursor: 
                pavement_dict[row[0]] = [row[1],row[2]]
    for fmsid in fmsid_list:
        #loop through again to bring the values back 
        where_clause = "FMSID2='{}'".format(fmsid)
        with arcpy.da.UpdateCursor(location_name,["FMSID2","FundStatus","ProjStatus"],where_clause=where_clause) as cursor:
            for row in cursor: 
                #update the funding status and proj status of the pavement work rows
                row[1] = pavement_dict.get(row[0])[0]
                row[2] = pavement_dict.get(row[0])[1]
                cursor.updateRow(row)
    print("Got FundStatus and ProjStatus from PavementWorks Layer")
#replaces the name of projects that are simplified BASEFMSID-number - number format to comma delimited. For example BRCO36-45 would become BRC036,BRC037,BRC038...BRC045
def replacerows(row):
    start =0
    end = 0
    base = ""
    #look for a combination of 2 or more numbers seperated by a - and another 2 or more numbers. This will not catch every scenario but keeping it at 1 number is risky as you may get unwanted catches.
    #The regular expression captures the first part of the FMSID as well as the two number sections.
    # Created with HBRC036-45 in mind.
    match = re.search(r'(.*)([0-9]{2,})-([0-9]{2,})',row["FMS ID"])
    if(match != None):
        #get the base fmsid and the two numbers
        base = match.group(1)
        start = (int)(match.group(2))
        end = (int)(match.group(3))
        numbers = range(start,end+1)
        tempname = ""
        #iterate through the numbers and create comma deliminated name
        for num in numbers: 
            tempname = tempname + base+(str)(num)+","
        tempname = tempname[:-1]
        row["FMS ID"] = tempname
        return tempname

    return row["FMS ID"]

def tester(row,dict):
    if (row["In Approved April 2022 Plan"] * 1000) in dict:
        return dict.get((row["In Approved April 2022 Plan"] * 1000))
    if (row["In Approved April 2022 Parks Plan"] * 1000) in dict:
        return dict.get((row["In Approved April 2022 Parks Plan"] * 1000))
    return None

def findfmsid(str):
    if str == "" or str == np.nan or str == None:
        return None
    match = re.search(r"(?i)(\(HBCR.*$)",str)
    if(match != None):
        return match.group(1)
    return None  

def c37(): 
    df = pd.read_excel("C37 - Poor Bridges_20220429.xlsx",skiprows=21,sheetname="C37")
    
    # c37dict = defaultdict(list)
    location_dict = {}
    #create dictionary with comma delimited bin for each fmsid based on the bridge project locations layer
    with arcpy.da.SearchCursor(old_location_layer,["FMSID","PlanCost"]) as cursor:
        for row in cursor: 
            if row[0] not in location_dict:
                location_dict[(row[1])] = row[0]

    case2 = df[df["Feature Carried"].str.contains("(",regex=False,na=False)]
    case2["testFMSID"] = case2["Feature Carried"].apply(lambda x: findfmsid(x))
    case2 = case2[case2["testFMSID"].notnull()]
    
    case2["testFMSID"] = case2["testFMSID"].str.strip()
    case2["testFMSID"] = case2["testFMSID"].str.replace(r"\(|\)", "")
    case2 = case2[["testFMSID","In Approved April 2022 Plan","BIN"]]
    case2_gby = case2.groupby('testFMSID')['In Approved April 2022 Plan'].sum()
    tempdict = case2_gby.to_dict()
    for key in tempdict:
        tempdict[key] = round(tempdict[key],0)
    case2["In Approved April 2022 Plan"] = case2["testFMSID"].map(tempdict)
    case2 = case2[["In Approved April 2022 Plan","BIN"]]
    case2_dict =  dict(zip(case2["BIN"], case2["In Approved April 2022 Plan"]))

    df["In Approved April 2022 Plan"] = df.apply(lambda row: case2_dict.get(row["BIN"],row["In Approved April 2022 Plan"]),axis=1)
    df["testFMSID"] = df.apply(lambda row: tester(row,location_dict),axis=1)

    df.to_csv("c37_test.csv",encoding='utf-8')

    # case2.to_csv("case2.csv",encoding='utf-8')
    # print(df)
    # print(location_dict.get(25494000))
    
    # binmatch = pd.read_excel("Bridges Offline April 2022 Plan.xlsx",sheetname = "DOT PIVOT",skiprows=9)
    # print(binmatch.info())
    # binmatch = binmatch[binmatch["PROJ DESC"].notnull()]
    # binmatch["BIN"] = binmatch["PROJ DESC"].apply(lambda x: findbin(x))
    # binmatch["BIN"] =binmatch["BIN"].str.replace("-","")
    # binmatch = binmatch[binmatch["BIN"].notnull()]
    # binmatch
    # print(binmatch[["PROJ ID","BIN"]])

today = date.today()
#create names of the layers
day= today.strftime("%Y%m%d")
dissolved_name = "temp"+day
reordered_name = "Bridge_Projects_"+day
location_name = "Bridge_Projects_locations_"+day

# print("starting bridge layer update..")
# mapmissing()
# #edit pavement_FMSIDs if new pavement work projects are added
# pavementworks(fmsid_list=pavement_FMSIDs)
# main()
# arcpyupdatelocationslayer()
# assetjoin()
# updateNTAMeta()
# reorder_fields()
c37()