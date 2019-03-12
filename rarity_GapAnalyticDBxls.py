# -*- coding: utf-8 -*-
"""
rarity_GapAnalyticDBxls.py

enviroment: base 2.7

Summarizes Gap_AnalyticDB data for species rarity analysis.
Summary by Species, HUC12/L2ecorgion, and GAP Status.
Output are 4 taxa summary tables.
Specifically written to mimic the original XLS work 
done by Anne Davidson and Leah Dunn (50% hucs discard rule).
 
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

outPrefix = home + 'tblRarity'
tblAmph = home + 'tblRarityAmphXLS.csv'
tblBird = home + 'tblRarityBirdXLS.csv'
tblMamm = home + 'tblRarityMammXLS.csv'
tblRept = home + 'tblRarityReptXLS.csv'
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
    
    # Pull a table of variables back into a data frame
    sql = """
    -- qryRarityXLS.sql
    -- drop the temp tables if they exist
    IF OBJECT_ID('tempdb.dbo.#polyMax', 'U') IS NOT NULL 
      DROP TABLE tempdb.dbo.#polyMax; 
    IF OBJECT_ID('tempdb.dbo.#polyData', 'U') IS NOT NULL 
      DROP TABLE tempdb.dbo.#polyData; 
    IF OBJECT_ID('tempdb.dbo.#distSpp', 'U') IS NOT NULL 
      DROP TABLE tempdb.dbo.#distSpp; 
    IF OBJECT_ID('tempdb.dbo.#summSpp', 'U') IS NOT NULL 
      DROP TABLE tempdb.dbo.#summSpp; 
    -- drop the output table if it exists
    IF OBJECT_ID('dbo.qtblRarityXLS', 'U') IS NOT NULL 
      DROP TABLE dbo.qtblRarityXLS; 

    -- reassign all huc12/ecoL2 polygons to a single ecoL2 category
	-- drop hucs that have < 50% within ecoL2 polygon (water)
    WITH 
    -- add column identifying null ecoL2 polygons, sum count of huc12/ecoL2 combinations
    polySum AS (        
        SELECT hucs.huc12rng, 
               eco_l4.na_l2code,
			   CASE 
			    WHEN (eco_l4.na_l2code IS NULL) THEN 0 ELSE 1
			   END AS NNN,
               SUM(lu_boundary.count) AS cntTotal
        FROM lu_boundary 
             INNER JOIN hucs
              ON lu_boundary.hucs = hucs.objectid
             LEFT JOIN eco_l4
              ON lu_boundary.eco_l4 = eco_l4.fid
        --WHERE hucs.huc12rng like '030902%'
        GROUP BY hucs.huc12rng, 
                 eco_l4.na_l2code),

    -- sum based on huc/NNN 
    polyNNN AS (
        SELECT huc12rng,
		       NNN,
			   SUM(cntTotal) AS cntTotalNNN
        FROM   polySum
		GROUP BY huc12rng, NNN),

    -- find max NNN for each huc in polyNNN
    polyNNNMaxes AS (
        SELECT pNNN.*
        FROM   polyNNN pNNN
        INNER JOIN
            (SELECT huc12rng, MAX(cntTotalNNN) AS maxCntTotalNNN
             FROM polyNNN
             GROUP BY huc12rng) groupedNNNp
        ON pNNN.huc12rng = groupedNNNp.huc12rng AND
           pNNN.cntTotalNNN = groupedNNNp.maxCntTotalNNN),

	-- create list of hucs to keep
	keepHucs AS (
	    SELECT huc12rng
		FROM polyNNNMaxes
		WHERE NNN = 1),

    -- subset keepHucs from polySum
	polySum2 AS (
	    SELECT pS.huc12rng,
		       pS.na_l2code,
			   cntTotal
		FROM keepHucs kH
		INNER JOIN polySum pS
		ON kH.huc12rng = pS.huc12rng),
	
	-- find max nonNull for each huc in polySum2
	polyMaxes AS (
        SELECT pS2.*
        FROM   polySum2 pS2
        INNER JOIN
            (SELECT huc12rng, MAX(cntTotal) AS maxCntTotal
             FROM polySum2
			 WHERE na_l2code IS NOT NULL
             GROUP BY huc12rng) groupedl2p
        ON pS2.huc12rng = groupedl2p.huc12rng AND
           pS2.cntTotal = groupedl2p.maxCntTotal)

	-- deal with ties, store as temp table
    SELECT pM.huc12rng, 
           pM.na_l2code            
    INTO #polyMax
    FROM  (SELECT polyMaxes.huc12rng, 
                  polyMaxes.na_l2code,
                  ROW_NUMBER() OVER
                   (PARTITION BY polyMaxes.huc12rng 
                    ORDER BY polyMaxes.cntTotal DESC, 
                  polyMaxes.na_l2code ASC ) AS RowN
           FROM polyMaxes) pM  
    WHERE RowN = 1;                        --  81,748 records

    -- huc/ecoregion count data, save as temp table
    SELECT lu_boundary.value AS bndValue, 
           hucs.huc12rng, 
           lu_boundary.padus1_4, 
           #polyMax.na_l2code,
           lu_boundary.count AS bndCnt
    INTO #polyData
    FROM #polyMax
         INNER JOIN hucs
          ON #polyMax.huc12rng = hucs.huc12rng
         INNER JOIN lu_boundary 
          ON hucs.objectid = lu_boundary.hucs
         LEFT JOIN eco_l4
          ON lu_boundary.eco_l4 = eco_l4.fid;   -- 1,522,589 records

    -- attach species distribution info, store as temp table
    SELECT 
        #polyData.bndValue, 
        #polyData.huc12rng,
        #polyData.padus1_4,
        #polyData.na_l2code,
        lu_boundary_species.species_cd,
        SUM(lu_boundary_species.count) AS bndsppCnt
    INTO #distSpp
    FROM #polyData 
         INNER JOIN lu_boundary_species
          ON #polyData.bndValue = lu_boundary_species.boundary
    GROUP BY #polyData.bndValue, 
             #polyData.huc12rng,
             #polyData.padus1_4,
             #polyData.na_l2code,
             lu_boundary_species.species_cd;    -- 267,849,366 records

    -- generate table of total species distribution count per huc
    WITH
    sppTotal AS (
        SELECT dist_spp_0.huc12rng, 
               dist_spp_0.species_cd,
               dist_spp_0.na_l2code,
               SUM(dist_spp_0.bndSppCnt) AS totalSppPix
        FROM #distSpp AS dist_spp_0 
             LEFT JOIN padus1_4 AS padus1_4_0
              ON dist_spp_0.padus1_4 = padus1_4_0.objectid
        GROUP BY dist_spp_0.huc12rng, 
                 dist_spp_0.species_cd,
                 dist_spp_0.na_l2code),   

    -- generate table of gap status 1 species distribution count per huc
    sppPad1 AS (
        SELECT dist_spp_1.huc12rng, 
               dist_spp_1.species_cd,
               SUM(dist_spp_1.bndsppCnt) AS gs1SppPix
        FROM #distSpp AS dist_spp_1 
             LEFT JOIN padus1_4 AS padus1_4_1 
              ON dist_spp_1.padus1_4 = padus1_4_1.objectid
        WHERE (RTRIM(LTRIM(padus1_4_1.gap_sts)) = '1')
        GROUP BY dist_spp_1.huc12rng, 
                 dist_spp_1.species_cd),
        
    -- generate table of gap status 2 species distribution count per huc
    sppPad2 AS (
        SELECT dist_spp_2.huc12rng, 
               dist_spp_2.species_cd,
               SUM(dist_spp_2.bndsppCnt) AS gs2SppPix
        FROM #distSpp AS dist_spp_2 
             LEFT JOIN padus1_4 AS padus1_4_2 
              ON dist_spp_2.padus1_4 = padus1_4_2.objectid
        WHERE (RTRIM(LTRIM(padus1_4_2.gap_sts)) = '2')
        GROUP BY dist_spp_2.huc12rng, 
                 dist_spp_2.species_cd), 
                 
    -- generate table of gap status 3 species distribution count per huc
    sppPad3 AS (
        SELECT dist_spp_3.huc12rng, 
               dist_spp_3.species_cd,
               SUM(dist_spp_3.bndsppCnt) AS gs3SppPix
        FROM #distSpp AS dist_spp_3 
             LEFT JOIN padus1_4 AS padus1_4_3 
              ON dist_spp_3.padus1_4 = padus1_4_3.objectid
        WHERE (RTRIM(LTRIM(padus1_4_3.gap_sts)) = '3')
        GROUP BY dist_spp_3.huc12rng, 
                 dist_spp_3.species_cd) 

    -- combine gap status and total counts, save as temp table
    SELECT sppTotal.huc12rng,
           sppTotal.na_l2code, 
           UPPER(LEFT(sppTotal.species_cd, 1)) AS Taxa, 
           LEFT(sppTotal.species_cd, 1)
            + UPPER(SUBSTRING(sppTotal.species_cd, 2, 4))
            + RIGHT(sppTotal.species_cd, 1) AS Spp, 
           ISNULL(sppPad1.gs1SppPix, 0) AS gs1SppPix, 
           ISNULL(sppPad2.gs2SppPix, 0) AS gs2SppPix, 
           ISNULL(sppPad3.gs3SppPix, 0) AS gs3SppPix, 
           totalSppPix - (ISNULL(sppPad1.gs1SppPix, 0) + 
                          ISNULL(sppPad2.gs2SppPix, 0) + 
                          ISNULL(sppPad3.gs3SppPix, 0)) AS gs4SppPix, 
           sppTotal.totalSppPix
    INTO #summSpp
    FROM sppTotal 
         LEFT OUTER JOIN sppPad1
          ON sppTotal.huc12rng = sppPad1.huc12rng AND 
             sppTotal.species_cd = sppPad1.species_cd
         LEFT OUTER JOIN sppPad2
          ON sppTotal.huc12rng = sppPad2.huc12rng AND
             sppTotal.species_cd = sppPad2.species_cd
         LEFT OUTER JOIN sppPad3 
          ON sppTotal.huc12rng = sppPad3.huc12rng AND 
             sppTotal.species_cd = sppPad3.species_cd;  -- 21,343,783 records    

    -- combine summSpp, huc and l2 info, save as output table
    WITH
    -- caluclate pixel count for each huc
    huc_data AS (
        SELECT huc12rng,
               SUM(bndCnt) AS hucPix
        FROM #polyData
        GROUP BY huc12rng),    

    -- calculate pixel count for each redefined L2 ecoregion
    l2_data AS (
        SELECT na_l2code,
               SUM(bndCnt) AS ecoPix
        FROM #polyData
        GROUP BY na_l2code),

    -- generate table of l2 ecoregion names
    l2_names AS (
        SELECT DISTINCT
            na_l2code,
            REPLACE(na_l2name,' (?)','') AS na_l2name
        FROM eco_l4)
    
    SELECT #summSpp.huc12rng,
           huc_data.hucPix,
           #summSpp.na_l2code,
           l2_names.na_l2name,
           l2_data.ecoPix,
           #summSpp.Taxa,
           #summSpp.Spp,
           #summSpp.gs1SppPix,
           #summSpp.gs2SppPix,
           #summSpp.gs3SppPix,
           #summSpp.gs4SppPix,
           #summSpp.totalSppPix
    INTO qtblRarityXLS
    FROM #summSpp
         INNER JOIN huc_data
          ON #summSpp.huc12rng = huc_data.huc12rng
         INNER JOIN l2_data
          ON #summSpp.na_l2code = l2_data.na_l2code
         INNER JOIN l2_names
          ON #summSpp.na_l2code = l2_names.na_l2code;  -- 21,343,783 records
    -- 00:17:16 to run on BaSIC SQL Server
    
    -- pull results by taxa
    SELECT * 
    FROM qtblRarityXLS
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

