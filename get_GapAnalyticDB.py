# -*- coding: utf-8 -*-
"""
get_GapAnalyticDB.py

enviroment: base

Example of how to retrieve data from Gap_AnalyticDB as pandas data frame.
 
 
Created on 14nov2018

@author: sgwillia
=======================================================================
"""
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
# Look at dataframe
tbSpp

# Look at dataframe column names
tbSpp.columns

# Look at data from one column
tbSpp['strUC']

# Look at data from one row based on row index
tbSpp.iloc[0]
# now set as a variable
row0 = tbSpp.iloc[0]
# it's an object that you can call fields from
row0.intITIScode
type(row0.intITIScode)

# Look at data from one row based on value in column
tbSpp.loc[tbSpp['strUC'] == 'bBAEAx']
# now set as a variable
rowSpp = tbSpp.loc[tbSpp['strUC'] == 'bBAEAx']
# you can also call fields from that
rowSpp.intITIScode
type(rowSpp.intITIScode)

# Look at data from one column, one row via row index number
tbSpp['strUC'][0]
tbSpp['strUC'][1719]



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

    if strUC == 'aHELLa':  # reset sppCode if script fails along the way
        print(strUC)
        print('strScientificName: ' + strScientificName)
        print('strSubSciNameText: ' + strSubSciNameText)
        print('strSciName: ' + strSciName)
    

