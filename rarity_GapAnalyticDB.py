# -*- coding: utf-8 -*-
"""
rarity_GapAnalyticDB.py

enviroment: base

Pulls Gap_AnalyticDB data for species rarity analysis.
 
 
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

outTable = home + 'qryRaritySummary.csv'
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
def qryRarity():
    '''
    Returns a dataframe for rarity analysis from Gap_AnalyticDB database.
    '''
    # Get a connection to the dB
    cur, conn = ConnectGapAnalyticDB()
    
    # Pull a table of variables back into a data frame
    sql = """
    WITH 
    sel_hucs AS (
        SELECT lu_boundary.value, 
               hucs.objectid, 
               hucs.huc12rng, 
               lu_boundary.padus1_4, 
               lu_boundary.hucs
        FROM lu_boundary 
             INNER JOIN hucs
              ON lu_boundary.hucs = hucs.objectid
        WHERE huc12rng like '10250017%'),
    
    dist_spp AS (
        SELECT TOP (100) PERCENT 
               lu_boundary_species.count, 
               sel_hucs_1.hucs, 
               sel_hucs_1.huc12rng, 
               lu_boundary_species.species_cd, 
               sel_hucs_1.padus1_4
        FROM sel_hucs AS sel_hucs_1 
             INNER JOIN lu_boundary_species
              ON sel_hucs_1.value = lu_boundary_species.boundary
        ORDER BY sel_hucs_1.hucs,
                 lu_boundary_species.species_cd, 
                 sel_hucs_1.padus1_4,
                 sel_hucs_1.huc12rng), 
        
    total_cnt_spp AS (
        SELECT dist_spp_3.hucs, 
               dist_spp_3.huc12rng, 
               tblTaxa.strTaxaLetter, 
               dist_spp_3.species_cd, 
               SUM(dist_spp_3.count) AS total_spp_count
        FROM dist_spp AS dist_spp_3 
             INNER JOIN tblTaxa
              ON dist_spp_3.species_cd = tblTaxa.strUC 
             INNER JOIN padus1_4
              ON dist_spp_3.padus1_4 = padus1_4.objectid
        GROUP BY dist_spp_3.hucs, 
                 dist_spp_3.huc12rng, 
                 tblTaxa.strTaxaLetter, 
                 dist_spp_3.species_cd), 
        
    spp_pad1 AS (
        SELECT dist_spp_2.hucs, 
               dist_spp_2.huc12rng, 
               tblTaxa_4.strTaxaLetter, 
               dist_spp_2.species_cd, 
               SUM(dist_spp_2.count) AS padstat1_count
        FROM dist_spp AS dist_spp_2 
             INNER JOIN tblTaxa AS tblTaxa_4
              ON dist_spp_2.species_cd = tblTaxa_4.strUC 
             INNER JOIN padus1_4 AS padus1_4_4 
              ON dist_spp_2.padus1_4 = padus1_4_4.objectid
        WHERE (RTRIM(LTRIM(padus1_4_4.gap_sts)) = '1')
        GROUP BY dist_spp_2.hucs, 
                 dist_spp_2.huc12rng, 
                 tblTaxa_4.strTaxaLetter, 
                 dist_spp_2.species_cd), 
    
    spp_pad2 AS (
        SELECT dist_spp_1.hucs, 
               dist_spp_1.huc12rng, 
               tblTaxa_3.strTaxaLetter, 
               dist_spp_1.species_cd, 
               SUM(dist_spp_1.count) AS padstat2_count
        FROM dist_spp AS dist_spp_1 
             INNER JOIN tblTaxa AS tblTaxa_3
              ON dist_spp_1.species_cd = tblTaxa_3.strUC 
             INNER JOIN padus1_4 AS padus1_4_3 
              ON dist_spp_1.padus1_4 = padus1_4_3.objectid
        WHERE (RTRIM(LTRIM(padus1_4_3.gap_sts)) = '2')
        GROUP BY dist_spp_1.hucs, 
                 dist_spp_1.huc12rng, 
                 tblTaxa_3.strTaxaLetter, 
                 dist_spp_1.species_cd), 
                 
    spp_pad3 AS (
        SELECT dist_spp.hucs, 
               dist_spp.huc12rng, 
               tblTaxa_2.strTaxaLetter, 
               dist_spp.species_cd, 
               SUM(dist_spp.count) AS padstat3_count
        FROM dist_spp AS dist_spp 
             INNER JOIN tblTaxa AS tblTaxa_2 
              ON dist_spp.species_cd = tblTaxa_2.strUC 
             INNER JOIN padus1_4 AS padus1_4_2 
              ON dist_spp.padus1_4 = padus1_4_2.objectid
        WHERE (RTRIM(LTRIM(padus1_4_2.gap_sts)) = '3')
        GROUP BY dist_spp.hucs, 
                 dist_spp.huc12rng, 
                 tblTaxa_2.strTaxaLetter, 
                 dist_spp.species_cd), 
                 
    spp_pad4 AS (
        SELECT dist_spp.hucs, 
               dist_spp.huc12rng, 
               tblTaxa_1.strTaxaLetter, 
               dist_spp.species_cd, 
               SUM(dist_spp.count) AS padstat4_count
        FROM dist_spp AS dist_spp 
             INNER JOIN tblTaxa AS tblTaxa_1 
              ON dist_spp.species_cd = tblTaxa_1.strUC 
             INNER JOIN padus1_4 AS padus1_4_1 
              ON dist_spp.padus1_4 = padus1_4_1.objectid
        WHERE (RTRIM(LTRIM(padus1_4_1.gap_sts)) = '4')
        GROUP BY dist_spp.hucs, 
                 dist_spp.huc12rng, 
                 tblTaxa_1.strTaxaLetter, 
                 dist_spp.species_cd)
     
    SELECT total_cnt_spp.strTaxaLetter AS Taxa, 
           LEFT(total_cnt_spp.species_cd, 1)
            + UPPER(SUBSTRING(total_cnt_spp.species_cd, 2, 4))
            + RIGHT(total_cnt_spp.species_cd, 1)  AS spp, 
           total_cnt_spp.huc12rng AS huc, 
           total_cnt_spp.total_spp_count AS spp_pixel_count, 
           spp_pad1.padstat1_count AS spp_gs1_pixel_count, 
           spp_pad2.padstat2_count AS spp_gs2_pixel_count, 
           spp_pad3.padstat3_count AS spp_gs3_pixel_count, 
           spp_pad4.padstat4_count AS spp_gs4_pixel_count, 
           COALESCE (spp_pad1.padstat1_count, 0) 
            + COALESCE (spp_pad2.padstat2_count, 0) 
            + COALESCE (spp_pad3.padstat3_count, 0) 
            + COALESCE (spp_pad4.padstat4_count, 0) AS spp_gs_total_check
    FROM total_cnt_spp AS total_cnt_spp 
         LEFT OUTER JOIN spp_pad3 AS spp_pad3 
          ON total_cnt_spp.hucs = spp_pad3.hucs AND 
             total_cnt_spp.huc12rng = spp_pad3.huc12rng AND 
             total_cnt_spp.species_cd = spp_pad3.species_cd 
         LEFT OUTER JOIN spp_pad2 AS spp_pad2
          ON total_cnt_spp.hucs = spp_pad2.hucs AND
             total_cnt_spp.huc12rng = spp_pad2.huc12rng AND
             total_cnt_spp.species_cd = spp_pad2.species_cd 
         LEFT OUTER JOIN spp_pad4 AS spp_pad4
          ON total_cnt_spp.hucs = spp_pad4.hucs AND 
             total_cnt_spp.huc12rng = spp_pad4.huc12rng AND 
             total_cnt_spp.species_cd = spp_pad4.species_cd 
         LEFT OUTER JOIN spp_pad1 AS spp_pad1
          ON total_cnt_spp.hucs = spp_pad1.hucs AND 
             total_cnt_spp.huc12rng = spp_pad1.huc12rng AND 
             total_cnt_spp.species_cd = spp_pad1.species_cd
    """    
    strSQL = sql.format(sql)
    qrySQL = psql.read_sql(strSQL, conn)
    dfSQL = pd.DataFrame(qrySQL).fillna(0)
    dfSQL.to_csv(outTable, sep=',', encoding='utf-8')
   
    print(dfSQL.columns)
    
    return dfSQL

# =======================================================================
# Evaluate existance of output table and replace option, then implement
if os.path.exists(outTable) == False:
    print('Output does not exist - running query...')
    sqlQuery = qryRarity()
elif replaceTable == 'yes':
    print('Output exists - replacing...')
    os.remove(outTable)
    sqlQuery = qryRarity()
else:
    print('Output exists - not replacing.')















