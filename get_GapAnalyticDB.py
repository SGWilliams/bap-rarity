# -*- coding: utf-8 -*-
"""
get_GapAnalyticDB.py

enviroment: base

Example of how to retrieve data from Gap_AnalyticDB as pandas data frame.
 
 
Created on 14nov2018

@author: sgwillia
=======================================================================
"""
# Import gapconfig variables
import sys
sys.path.append('C:/Code')
import gapconfig
import pyodbc
import pandas as pd
import pandas.io.sql as psql

# =======================================================================
# LOCAL VARIABLES
home = "N:/Git_Repositories/bap-rarity/"

# =======================================================================
# LOCAL FUNCTIONS 
## --------------Cursor and Database Connections--------------------
def ConnectToDB(connectionStr):
    '''
    (str) -> cursor, connection

    Provides a cursor within and a connection to the database

    Argument:
    connectionStr -- The SQL Server compatible connection string
        for connecting to a database
    '''
    try:
        con = pyodbc.connect(connectionStr)
    except:
        connectionStr = connectionStr.replace('11.0', '10.0')
        con = pyodbc.connect(connectionStr)

    return con.cursor(), con

## ----------------Gap Analytic Database Connection----------------------
def ConnectGapAnalyticDB():
    '''
    Returns a cursor and connection within the Gap_AnalyticDB database.
    '''
    # Database connection parameters
    dbConStr = """DRIVER=SQL Server Native Client 11.0;
                    SERVER=CHUCK\SQL2014;
                    UID=;
                    PWD=;
                    TRUSTED_CONNECTION=Yes;
                    DATABASE=Gap_AnalyticDB;"""

    return ConnectToDB(dbConStr)

# =======================================================================
# OPEN DB AND GET TAXA TABLE
# Get a connection to the dB
cur, conn = ConnectGapAnalyticDB()

# Pull a table of variables back into a data frame
sql = """
SELECT [strUC]
      ,[strScientificName]
      ,[strSubSciNameText]
      ,[strSubspeciesLetter]
      ,[strCommonName]
      ,[strSort]
      ,[strTaxaLetter]
      ,[intNSglobal]
      ,[strNSelcode]
      ,[intITIScode]
      ,[intGapNSmatch]
      ,[intGapITISmatch]
      ,[strSbUrlHM]
      ,[strDoiHM]
      ,[strSbUrlRM]
      ,[strDoiRM]
  FROM [GAP_AnalyticDB].[dbo].[tblTaxa]"""

strSQL = sql.format(sql)
dfSpp = psql.read_sql(strSQL, conn)
tbSpp = pd.DataFrame(dfSpp)
   
# =======================================================================
# SET UP LOOP ON SPECIES
# Iterate through DB table
for row in tbSpp.itertuples(index=True, name='Pandas'):    
    # set variables
    strUC = getattr(row,"strUC")
    if getattr(row,"strSubspeciesLetter") == 'x':
        # set full species sciName
        strSciName = getattr(row,"strScientificName")
    elif getattr(row,"strSubspeciesLetter") != 'x':
        # build full species sciName
        strSciName = getattr(row,"strScientificName") + " " + getattr(row,"strSubSciNameText")

    strScientificName = getattr(row,"strScientificName")
    strSubSciNameText = getattr(row,"strSubSciNameText")
    strComName = getattr(row,"strCommonName")
    intITIScode = getattr(row,"intITIScode")
    strSbHabID = getattr(row,"strSbUrlHM")[-24:]

    if strUC == 'aFBFRx':  # reset sppCode if script fails along the way
        print(strUC)
        print(' ' + strScientificName)
        print(' ' + strSubSciNameText)
        print(' ' + strSciName)
    
        # pull itis data down, extract taxa hierarchy, reformat and create json
        ITISstring = "http://services.itis.gov/?wt=json&q=tsn:{0}".format(intITIScode)
        url = bis.itis.getITISSearchURL(ITISstring,False,False)
        ITISjson = requests.get(url).json()   
        hierStr = ITISjson["response"]["docs"][0]["hierarchySoFarWRanks"][0].replace("$","\",\"")
        hierStr = hierStr.replace(":","\":\"")
        hierStr = re.sub(r'.*"Kingdom', '{"hierarchySoFarWRanks": {"Kingdom', hierStr)
        hierStr = hierStr[:-2]+'}}'
        hierDic = json.loads(hierStr)
        outJson = strUC + '_ITIS.json'
        pthJson = outDir + '/' + outJson
        
        with open(pthJson, 'w') as jf:
            json.dump(hierDic, jf)
        
        # attach file to SB habitat item
        AttachFile(strUC, pthJson)
    
        # pull down sb item json and add titles
        # Connect to ScienceBase
        sb = ConnectToSB()
        Item = sb.get_item(strSbHabID)
     
        # add title to itis json file
        files = Item["files"]
        for f in files:
            # update the description of the json file we just uploaded
            if f["name"].find(outJson) > -1:
                f["title"] = "ITIS Information"
            sb.update_item(Item)

############################################

#    print(hierDic)
#
#print('ItisClass: '+hierDic['Class'])
#print('GapClass: '+strClass)
#print('ItisOrder: '+hierDic['Order'])
#print('GapOrder: '+strOrder)
#print('ItisFamily: '+hierDic['Family'])
#print('GapFamily: '+strFamily)
#if hierDic['Family'] != strFamily:
#    print strUC


'''
CommonName = ITISjson["response"]["docs"][0]["vernacular"][0].replace("$","").split("English")[0]
print(CommonName)
SciName = ITISjson["response"]["docs"][0]["nameWInd"]
print(SciName)
usage = ITISjson["response"]["docs"][0]["usage"]
print(usage)

b = bis.itis.checkITISSolr(SciName)
for x in b['itisData'][0]['commonnames']:
    print(x['name'])
print(b['itisData'][0]['nameWOInd'])
print(b['itisData'][0]['tsn'])
'''