# -*- coding: utf-8 -*-
"""
rarity_Analysis.py

enviroment: base 2.7

Input: derived from rarity_GapAnalyticDB.py 
           tblRarityHucAmph.csv
           tblRarityHucAmph.csv
           tblRarityHucAmph.csv
           tblRarityHucAmph.csv
       Jenkins2015 excel files (https://biodiversitymapping.org/wordpress/index.php/home/)
       IUCN_Gap.csv table from GAP Habitat Map Collection Item
       ScienceBaseHabMapCSV_<date>.csv table from GAP Habitat Map Collection Item

Output are ...
 
Created on 12mar2019

@author: sgwilliams
=======================================================================
"""
# IMPORT PACKAGES
import sys
import socket
import pandas as pd
import pandas.io.sql as psql
import numpy as np
import os.path
from sciencebasepy import SbSession
from io import StringIO
import urllib
import requests
import xml.etree.ElementTree as ET

# import SB user/password from sbconfig
import sbconfig
# =======================================================================
# LOCAL VARIABLES
# Set variable to use existing output if it exists, otherwise replace
replaceTable = 'no' # 'yes' to replace

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

# =======================================================================
# LOCAL FUNCTIONS 
## -------------------Connect to ScienceBase-------------------------
def ConnectToSB(username=sbconfig.sbUserName, password=sbconfig.sbWord):
    '''
    (string) -> connection to ScienceBase
    
    Creats a connection to ScienceBase. You will have to enter your password.
    
    Arguments:
    username -- your ScienceBase user name.
    password -- your ScienceBase password.
    '''

    sb = SbSession()
    sb.login(username, password)
    return sb

## ------------------------Taxa Work---------------------------------
def TaxaWork(Taxa):
    # Set taxa variables  Taxa = 'Amph' 
    tblSQL = home + 'tblRarityHuc' + Taxa + '.csv'
    xlsJenk = home + 'Jenkins2015_' + Taxa + 'SppLists.xlsx'
    if Taxa == 'Amph':
        taxa = 'amphibian'
        t = 'a'
    elif Taxa == 'Bird':
        taxa = 'bird'
        t = 'b'
    elif Taxa == 'Mamm':
        taxa = 'mammalian'
        t = 'b'
    elif Taxa == 'Rept':
        taxa = 'reptilian'
        t = 'r'
    else:
        print('ABORT:  Taxa variables are not set')
        exit()
    
    # Get GAP species info table from SB HabMap item
    sb = ConnectToSB()
    habItem = sb.get_item("527d0a83e4b0850ea0518326")
    for file in habItem["files"]:
        if file["name"].startswith("ScienceBaseHabMapCSV"):
            dfGapID = pd.read_csv(StringIO(sb.get(file["url"])))

    # Subset to taxa
    dfGapID = dfGapID[dfGapID['GAP_code'].str.slice(0,1) == t]   
    # Subset the columns
    dfGapID = dfGapID[['GAP_code', 'common_name', 'scientific_name', 'Global_SEQ_ID', 'OriginUS']]
    # rename the columns
    dfGapID = dfGapID.rename(index=str, columns={"GAP_code":"gapSppCode", "common_name":"gapComName", "scientific_name":"gapSciName", "OriginUS":"originUS"})

    # Open rarity_GapAnalyticDB.py output and set numeric column types
    dfSQL = pd.read_csv(tblSQL, dtype=str)
    dtypes = {"hucPix": np.int64,
              "ecoPix": np.int64, 
              "gs1SppPix": np.int64, 
              "gs2SppPix": np.int64, 
              "gs3SppPix": np.int64, 
              "gs4SppPix": np.int64, 
              "totalSppPix": np.int64}
    for col, col_type in dtypes.items():
        dfSQL[col] = dfSQL[col].astype(col_type)

    # HABITAT BREADTH   
    # Calc: percent use for spp/huc combinations
    dfSQL['percUse'] = (dfSQL['totalSppPix']/dfSQL['hucPix'])*100
    #dfSql.columns
    #dfSql.head()
    #dfSql.iloc[100]    
    # Mean percent use across all the hucs in distribution for each spp
    dfMPU = dfSQL.groupby(['Spp']).agg({'percUse': ['count','mean']})    
    # Classify spp with mean percent use <10% as "narrow" habitat breadth,
    #         and >=10% as "wide" habitat breadth (1=narrow, 0=wide)
    dfMPU['percUse','habBreadth'] = np.where(dfMPU['percUse','mean']<10.0, 1, 0)
    # Save as CSV (had to do this to get Spp column included in dataframe 
    #         and remove MultiIndexed Header)
    dfMPU.to_csv(home + 'tmpMPU.csv')
    # Open CSV as dataframe - skip over multiIndexed header
    dfMPU = pd.read_csv(home + 'tmpMPU.csv', skiprows=3, header=None)
    # subset the columns (0=Spp, 3=habBreadth)
    dfMPU = dfMPU[[0,3]]
    # rename the columns
    dfMPU = dfMPU.rename(index=str, columns={0:"gapSppCode", 3:"habBreadth"})
    
    # GEOGRAPHIC RANGE
    # Sum totalSppPix for each Spp-L2 combination, save as CSV
    dfSQL.groupby(['Spp','na_l2code']).agg({'totalSppPix':'sum'}).to_csv(home + 'tmpGE_x.csv')    
    # Sum totalSppPix for each Spp for entire CONUS, save as CSV
    dfSQL.groupby(['Spp']).agg({'totalSppPix':'sum'}).to_csv(home + 'tmpGE_y.csv')    
    # Open CSVs and merge
    dfGE_x = pd.read_csv(home + 'tmpGE_x.csv')
    dfGE_y = pd.read_csv(home + 'tmpGE_y.csv')
    dfGE = pd.merge(dfGE_x, dfGE_y, on="Spp", how='inner')   
    # Percent Spp-L2 (spp-L2 / spp-Conus)
    dfGE['percL2'] = (dfGE['totalSppPix_x']/dfGE['totalSppPix_y'])*100    
    # Classify Spp-L2 as endemic if >= 50% (1=L2 endemic, 0=not endemic)
    dfGE['L2endemic'] = np.where(dfGE['percL2']>=50.0, 1, 0)    
    # Subset L2 Endemics
    dfGE = dfGE.loc[dfGE['L2endemic'] == 1]
    # Subset the columns
    dfGE = dfGE[['Spp', 'L2endemic']]
    # rename the columns
    dfGE = dfGE.rename(index=str, columns={"Spp":"gapSppCode"})

    # Join Gap info, Habitat Breadth and Geographic Range
    dfGap = pd.merge(pd.merge(dfGapID, dfMPU, on='gapSppCode', how='outer'), dfGE, on='gapSppCode', how='outer')
    # Fill in zero where NaN
    dfGap = dfGap.replace(np.nan, 0, regex=True)

    # GET IUCN-GAP TABLES FROM SB HABMAP ITEM
    sb = ConnectToSB()
    habItem = sb.get_item("527d0a83e4b0850ea0518326")
    for file in habItem["files"]:
        if file["name"] == "IUCN_Gap.csv":
            dfIUCN = pd.read_csv(StringIO(sb.get(file["url"])))
            dfIUCN = dfIUCN.replace(np.nan, '', regex=True)
            dfIUCN['iucnTrend'] = np.where(dfIUCN['iucnPopulationTrend']=='decreasing', 1, 0)
    # Subset to taxa
    dfIUCN = dfIUCN[dfIUCN['gapSppCode'].str.slice(0,1) == t]
    # Subset the columns
    dfIUCN = dfIUCN[['gapSppCode', 'iucnTaxonID', 'iucnComName', 'iucnSciName', 'iucnTrend']]
      
    # Join Gap-IUCN...
    dfGI = pd.merge(dfGap, dfIUCN, on='gapSppCode', how='outer')
    # Add zeros into blank iucnTrend
    dfGI['iucnTrend'] = dfGI['iucnTrend'].replace(np.nan, 0, regex=True)
    # Calc Group based on habBreadth, L2endemic and popTrend
    '''
    habBreadth    L2endemic    iucnTrend    Group
        0           0               0       A
        0           1               0       B
        1           0               0       C
        0           0               1       D
        1           1               0       E
        1           0               1       F
        0           1               1       G
        1           1               1       H
    '''    
    def setGroup(row):
        if (row['habBreadth'] == 0) & (row['L2endemic'] == 0) & (row['iucnTrend'] == 0):
            val = 'A'
        elif (row['habBreadth'] == 0) & (row['L2endemic'] == 1) & (row['iucnTrend'] == 0):
            val = 'B'
        elif (row['habBreadth'] == 1) & (row['L2endemic'] == 0) & (row['iucnTrend'] == 0):
            val = 'C'
        elif (row['habBreadth'] == 0) & (row['L2endemic'] == 0) & (row['iucnTrend'] == 1):
            val = 'D'
        elif (row['habBreadth'] == 1) & (row['L2endemic'] == 1) & (row['iucnTrend'] == 0):
            val = 'E'
        elif (row['habBreadth'] == 1) & (row['L2endemic'] == 0) & (row['iucnTrend'] == 1):
            val = 'F'
        elif (row['habBreadth'] == 0) & (row['L2endemic'] == 1) & (row['iucnTrend'] == 1):
            val = 'G'
        elif (row['habBreadth'] == 1) & (row['L2endemic'] == 1) & (row['iucnTrend'] == 1):
            val = 'H'
        else:
            val = 'X'
        return val    
    dfGI['Group'] = dfGI.apply(setGroup, axis=1)
    
    # Set the Jenkins2015 download file based on Taxa
    dls = 'http://biodiversitymapping.org/docs/USA%20' + taxa + '%20species%20lists.xlsx'
    # Download the Jenkins2015 xlsx file from the web
    urllib.urlretrieve(dls, xlsJenk)    
    # Open worksheets, subset columns, add column for subset sheets
    Jall = pd.read_excel(open(xlsJenk, 'rb'), sheetname='All species')
    Jend = pd.read_excel(open(xlsJenk, 'rb'), sheetname='Endemics')
    Jend = Jend[['Species_ID']]
    Jend['Jend'] = 1
    Jgsm = pd.read_excel(open(xlsJenk, 'rb'), sheetname='Globally small ranged')
    Jgsm = Jgsm[['Species_ID']]
    Jgsm['Jgsm'] = 1
    Jusm = pd.read_excel(open(xlsJenk, 'rb'), sheetname='USA small ranged')
    Jusm = Jusm[['Species_ID']]
    Jusm['Jusm'] = 1
    Jthr = pd.read_excel(open(xlsJenk, 'rb'), sheetname='threatened')
    Jthr = Jthr[['Species_ID']]
    Jthr['Jthr'] = 1
    # Join all sheets together based on Species_ID
    dfJenk = pd.merge(pd.merge(pd.merge(pd.merge(Jall, Jend, on='Species_ID', how='outer'),
                                                 Jgsm, on='Species_ID', how='outer'), 
                                                 Jusm, on='Species_ID', how='outer'), 
                                                 Jthr, on='Species_ID', how='outer')
    # Fill in zero where NaN
    dfJenk = dfJenk.replace(np.nan, 0, regex=True)
    
    # Join Jenkins...
    dfGIJ = pd.merge(dfGI, dfJenk, left_on='iucnSciName', right_on='BINOMIAL', how='inner')
    
    # Get GAP-ITIS-NS code table from SB HabMap item
    sb = ConnectToSB()
    habItem = sb.get_item("527d0a83e4b0850ea0518326")
    for file in habItem["files"]:
        if file["name"] == "GAP_ITIS_NS_codes.csv":
            dfGapNS = pd.read_csv(StringIO(sb.get(file["url"])))
            # Subset the columns
            dfGapNS = dfGapNS[['strUC', 'intNSglobal']]

    
# =======================================================================




