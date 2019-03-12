# -*- coding: utf-8 -*-
"""
rarity_GapAnalyticDB.py

enviroment: base 2.7

Summarizes Gap_AnalyticDB data for species rarity analysis.
Summary by Species, HUC12/L2ecorgion, and GAP Status.
Output are 4 taxa summary tables.
Utilizes all polygons from Huc12 and Ecoregion datasets. 
No hucs are discarded.

Created on 3dec2018

@author: sgwillia
=======================================================================
"""
# IMPORT PACKAGES
import sys
import socket
import pyodbc
import pandas as pd
import pandas.io.sql as psql
import os.path

# =======================================================================
# LOCAL VARIABLES
# Set variable to use existing output if it exists, otherwise replace
replaceTable = 'yes' # 'yes' to replace

# set paths based on local host
# identify location
host = socket.gethostname()
#print(host)

if host == 'Thrasher':
    # set local paths
    home = "N:/Git_Repositories/bap-rarity/"
    sys.path.append('C:/Code')
    print('HOSTNAME: ' + host)
    print('HOME DIRECTORY: ' + home)
elif host == 'Batman10':
    # set local paths
    home = "C:/Users/Anne/Documents/Git_Repositories/bap-rarity/"
    sys.path.append('C:/Code')
    print('HOSTNAME: ' + host)
    print('HOME DIRECTORY: ' + home)
elif host == 'IGSWIDWBWS222':
    # set local paths
    home = "C:/Users/ldunn/Documents/GitRepo/bap-rarity/"
    sys.path.append('C:/Code')
    print('HOSTNAME: ' + host)
    print('HOME DIRECTORY: ' + home)
elif host == 'BaSIC-MacBook-Air.local':
    # set local paths
    home = "/Users/Steve/Git_Repos/bap-rarity/"
    sys.path.append('/Users/Steve/Documents')
    print('HOSTNAME: ' + host)
    print('HOME DIRECTORY: ' + home)
else:
    print('HOSTNAME: ' + host + 'is not defined')
    print('HALTING SCRIPT')
    sys.exit()

outPrefix = home + 'tblRarityHuc'
tblAmph = home + 'tblRarityHucAmph.csv'
tblBird = home + 'tblRarityHucBird.csv'
tblMamm = home + 'tblRarityHucMamm.csv'
tblRept = home + 'tblRarityHucRept.csv'
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
    if (host == 'Thrasher') or (host == 'Batman10'):
        # Database connection parameters
        dbConStr = """DRIVER=SQL Server Native Client 11.0;
                      SERVER=CHUCK\SQL2014;
                      UID=;
                      PWD=;
                      TRUSTED_CONNECTION=Yes;
                      DATABASE=Gap_AnalyticDB;
                   """
        return ConnectToDB(dbConStr)
    elif host == 'IGSWIDWBWS222':
        # Database connection parameters
        dbConStr = """DRIVER=SQL Server Native Client 11.0;
                      SERVER=IGSWIDWBvm181;
                      UID=;
                      PWD=;
                      TRUSTED_CONNECTION=Yes;
                      DATABASE=Gap_AnalyticDB;
                   """
        return ConnectToDB(dbConStr)

## ----------------Rarity Query of Gap Analytic DB ----------------------
def qryRarity(taxa):
    '''
    Returns a dataframe for rarity analysis from Gap_AnalyticDB database.
    '''
    # Get a connection to the dB
    cur, conn = ConnectGapAnalyticDB()
    
    # Pull a table of variables back into a data frame for the taxa
    sql = """
    SELECT * 
    FROM qtblRarityHuc
    WHERE Taxa = '""" + taxa[:1] + """'
    """    
    strSQL = sql.format(sql)
    qrySQL = psql.read_sql(strSQL, conn)
    dfSQL = pd.DataFrame(qrySQL).fillna(0)
    outTable = outPrefix + taxa + '.csv'
    dfSQL.to_csv(outTable, sep=',', encoding='utf-8')
   
    print('   ...finished.')
    
    return dfSQL

# =======================================================================
# Evaluate existance of output tables and replace option, then implement

if os.path.exists(tblAmph) == False:
    print('Amphibian output does not exist - running query...')
    sqlQuery = qryRarity('Amph')
elif replaceTable == 'yes':
    print('Amphibian output exists - replacing...')
    os.remove(tblAmph)
    sqlQuery = qryRarity('Amph')
else:
    print('Amphibian output exists - not replacing.')

if os.path.exists(tblBird) == False:
    print('Avian output does not exist - running query...')
    sqlQuery = qryRarity('Bird')
elif replaceTable == 'yes':
    print('Avian output exists - replacing...')
    os.remove(tblBird)
    sqlQuery = qryRarity('Bird')
else:
    print('Avian output exists - not replacing.')

if os.path.exists(tblMamm) == False:
    print('Mammalian output does not exist - running query...')
    sqlQuery = qryRarity('Mamm')
elif replaceTable == 'yes':
    print('Mammalian output exists - replacing...')
    os.remove(tblMamm)
    sqlQuery = qryRarity('Mamm')
else:
    print('Mammalian output exists - not replacing.')

if os.path.exists(tblRept) == False:
    print('Reptilian output does not exist - running query...')
    sqlQuery = qryRarity('Rept')
elif replaceTable == 'yes':
    print('Reptilian output exists - replacing...')
    os.remove(tblRept)
    sqlQuery = qryRarity('Rept')
else:
    print('Reptilian output exists - not replacing.')

