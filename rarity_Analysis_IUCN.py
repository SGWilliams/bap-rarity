# -*- coding: utf-8 -*-
"""
rarity_Analysis.py

enviroment: base 2.7

Input: derived from rarity_GapAnalyticDB.py 
           tblRarityHucAmph.csv
           tblRarityHucAmph.csv
           tblRarityHucAmph.csv
           tblRarityHucAmph.csv
       IUCN_Gap.csv table from GAP Habitat Map Collection Item
       ScienceBaseHabMapCSV_<date>.csv table from GAP Habitat Map Collection Item

Output are tblNatSumm.csv and tblEcoSumm.csv
 
Created on 12mar2019

@author: sgwilliams
=======================================================================
"""
# IMPORT PACKAGES
import sys
import socket
import pandas as pd
import numpy as np
from sciencebasepy import SbSession
from io import StringIO
import gc
import csv
import os
import requests

# =======================================================================
# LOCAL VARIABLES

# set paths based on local host
# identify location
host = socket.gethostname()
#print(host)

if host == 'Nigel':
    # set local paths
    home = "N:/Git_Repositories/bap-rarity/"
    sys.path.append('C:/Code')
    #print('HOSTNAME: ' + host)
    #print('HOME DIRECTORY: ' + home)
elif host == 'Batman10':
    # set local paths
    home = "C:/Users/Anne/Documents/Git_Repositories/bap-rarity/"
    sys.path.append('C:/Code')
    #print('HOSTNAME: ' + host)
    #print('HOME DIRECTORY: ' + home)
elif host == 'IGSWIDWBWS222':
    # set local paths
    home = "C:/Users/ldunn/Documents/GitRepo/bap-rarity/"
    sys.path.append('C:/Code')
    #print('HOSTNAME: ' + host)
    #print('HOME DIRECTORY: ' + home)
elif host == 'BaSIC-MacBook-Air.local':
    # set local paths
    home = "/Users/Steve/Git_Repos/bap-rarity/"
    sys.path.append('/Users/Steve/Documents')
    #print('HOSTNAME: ' + host)
    #print('HOME DIRECTORY: ' + home)
else:
    print('HOSTNAME: ' + host + 'is not defined')
    print('HALTING SCRIPT')
    sys.exit()

# import SB user/password from sbconfig
import sbconfig


# =======================================================================
# LOCAL FUNCTIONS 
## -------------Replace null variables with empty string-----------------
def xstr(s):
    if s is None:
        return ''
    return (s)


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


# =======================================================================
# Get GAP species info and IUCN-GAP table from SB HabMap item
print('Opening and combining SB files...')
sb = ConnectToSB()
habItem = sb.get_item("527d0a83e4b0850ea0518326")
for file in habItem["files"]:
    if file["name"].startswith("ScienceBaseHabMapCSV"):
        dfGapID = pd.read_csv(StringIO(sb.get(file["url"])))
    elif file["name"].startswith("IUCN_Gap"):
        dfIUCN = pd.read_csv(StringIO(sb.get(file["url"])))
#dfGapID = pd.read_csv('N:\\temp\\ScienceBaseHabMapCSV_20190412.csv')
#dfIUCN = pd.read_csv('N:\\temp\\IUCN_Gap_20190412.csv')

# Add blanks into missing fields
dfGapID = dfGapID.replace(np.nan, '', regex=True)
# Subset GapID to full species (n = 1590)
dfGapID = dfGapID[dfGapID['GAP_code'].str.slice(5,6) == 'x']
# rename the columns
dfGapID = dfGapID.rename(index=str, columns={"GAP_code":"gapSppCode", "common_name":"gapComName", "scientific_name":"gapSciName"})
# Subset the columns
dfGapID = dfGapID[['gapSppCode', 'gapComName', 'gapSciName']]

# Replace nulls in IUCN-GAP (n = 1590)
dfIUCN = dfIUCN.replace(np.nan, '', regex=True)
# Subset the columns
dfIUCN = dfIUCN[['gapSppCode',
                 'iucnTaxonID',
                 'iucnComName',
                 'iucnSciName',
                 'iucnOriginUS']]
#dfIUCN.to_csv(home + 'tmpIUCN.csv', index=False)

# Open IUCN data downloaded in original analysis on 
#   Monday, ‎April ‎3, ‎2017, ‏‎12:01:26 PM by Leah Dunn
#  (n = 2119)
print('Combine with IUCN data file...')
dfIUCNdata = pd.read_table(home + 'IUCN_Tab_DL.txt')
# Create SciName column
dfIUCNdata['SciName'] = dfIUCNdata['Genus'] + ' ' + dfIUCNdata['Species']
# Subset the columns
dfIUCNdata = dfIUCNdata[['Species ID',
                         'SciName',
                         'Red List status',
                         'Red List criteria',
                         'Population trend']]
# Rename columns
dfIUCNdata.columns = ['SpeciesID',
                      'SciName',
                      'RedListStatus',
                      'RedListCriteria',
                      'PopulationTrend']
# Replace nulls in IUCNdata
dfIUCNdata = dfIUCNdata.replace(np.nan, '', regex=True)
#dfIUCNdata.to_csv(home + 'tmpIUCNdata.csv', index=False)

# Join IUCN-GAP and IUCN data table (1557 inner matches on IUCN ID)
dfIG = pd.merge(dfIUCN, dfIUCNdata, left_on='iucnTaxonID', right_on='SpeciesID', how='left')
# Add blanks into missing fields
dfIG = dfIG.replace(np.nan, '', regex=True)
# 1557 GAP species iucnTaxonID match IUCNdata SpeciesID
# 7 GAP species have no match in IUCN data (iucnTaxonID = '')
#    - set Origin manually
def setOrigin(row):
    if ((row['gapSppCode'] == 'bHOREx') | (row['gapSppCode'] == 'rBRVIx') | (row['gapSppCode'] == 'rCHTUx') | (row['gapSppCode'] == 'rMILKx')):
        val = 'Native'
    elif ((row['gapSppCode'] == 'mHORSx') | (row['gapSppCode'] == 'rRAWHx') | (row['gapSppCode'] == 'rWOSLx')):
        val = 'Introduced'
    else:
        val = row['iucnOriginUS']
    return val    
dfIG['originUS'] = dfIG.apply(setOrigin, axis=1)
#dfIG.to_csv(home + 'tmpIG.csv', index=False)

# 26 GAP species iucnTaxonID do not match up to IUCNdata table
#    - pull information from IUCN API

# Create a list of 26 unmatched species
dfSpp0 = dfIG[(dfIG['iucnTaxonID'] != '') & (dfIG['SpeciesID'] == '')]

# first record - create new file, add headers
tmpIUCNspp = open(home + 'tmpIUCNspp.csv', 'wb')
# create the csv writer object
csvwriter = csv.writer(tmpIUCNspp)
# create the header
header = 'SpeciesID SciName RedListStatus PopulationTrend'
csvwriter.writerow(header.split())
tmpIUCNspp.close()

print('Gathering IUCN data for unsmatched species...')
# ---------------------------
# Iterate through table
# dfSpp0 = dfSpp0.loc[tbSpp['gapSppCode'] == 'bELTRx']
# set row count to 1
rowNum = 1  
for row in dfSpp0.itertuples(index=True, name='Pandas'):
    # set variables
    strUC = getattr(row,"gapSppCode")
    intIucnID = getattr(row,"iucnTaxonID")
    strIucnComName = getattr(row,"iucnComName")
    strIucnSciName = getattr(row,"iucnSciName")
    strIucnOgn = getattr(row,"originUS")
    
    print(str(rowNum) + ' - Fetching IUCN API info for ' + strUC + ' (' + strIucnComName + ')')
    # pull iucn data down, reformat and create json
    '''
    Red List
    Population Trend (decreasing, stable/increasing/unknown)
    Threatened Categories (critical CR, endangered EN, 
      vulnerable VU) characterized as decreasing even if 
      IUCN population trend is stable or unknown.
    '''
    # retrieve global assessment for species by IUCN SciName
    urlA = "http://apiv3.iucnredlist.org/api/v3/species/id/" + \
        str(round(intIucnID)).rstrip('0').rstrip('.') + "?token=" + os.environ["IUCN_TOKEN"]
    jsonA = requests.get(urlA).json()
    # extract threatened category
    strRedListStatus = xstr(jsonA["result"][0]["category"])
    
    # retrieve global narrative for species by IUCN SciName
    urlN = "http://apiv3.iucnredlist.org/api/v3/species/narrative/id/" + \
    str(round(intIucnID)).rstrip('0').rstrip('.') + "?token=" + os.environ["IUCN_TOKEN"]
    jsonN = requests.get(urlN).json()
    # extract population trend
    strPopulationTrend = xstr(jsonN["result"][0]["populationtrend"])

    # combine strings and append to file
    rowStr = str(round(intIucnID)).rstrip('0').rstrip('.') + ',' \
           + strIucnSciName + ',' \
           + strRedListStatus + ',' \
           + strPopulationTrend
    #print(' rowStr: ' + rowStr)
    # data record - append to file, add data
    tmpIUCNspp = open(home + 'tmpIUCNspp.csv', 'ab')
    # create the csv writer object
    csvwriter = csv.writer(tmpIUCNspp)
    csvwriter.writerow(rowStr.split(','))
    #csvwriter.writerow(JD.split())
    tmpIUCNspp.close()
    
    # count up on index value
    rowNum += 1
# ---------------------------

# Open IUCN API table
dfSpp1 = pd.read_csv(home + 'tmpIUCNspp.csv')
# Add blanks into missing fields
dfSpp1 = dfSpp1.replace(np.nan, '', regex=True)
# Drop duplicates
dfSpp1 = dfSpp1.drop_duplicates()

# Drop API fields from list of 26
dfSpp2 = dfSpp0[['gapSppCode',
               'iucnTaxonID',
               'iucnComName',
               'iucnSciName',
               'originUS']]
# Join Spp data
dfSpp = pd.merge(dfSpp2, dfSpp1, left_on='iucnTaxonID', right_on = 'SpeciesID', how = 'inner')

# Drop original 26, and then add new 26 back in
dfIGa = dfIG[(dfIG['iucnTaxonID'] == '') | (dfIG['SpeciesID'] != '')]
frames = [dfIGa, dfSpp]
dfIG2 = pd.concat(frames)

# Calculate Trend(0/1) based on origin, status and trend
def setTrend(row):
    if (((row['originUS'] == 'Native') |\
         (row['originUS'] == 'Reintroduced')) & \
        ((row['RedListStatus'] == 'VU') |\
         (row['RedListStatus'] == 'CR') |\
         (row['RedListStatus'] == 'EN') |\
         (row['PopulationTrend'] == 'decreasing'))):
        val = '1'
    else:
        val = '0'
    return val    
dfIG2['iucnTrend'] = dfIG2.apply(setTrend, axis=1)

# Subset the columns
dfIG2 = dfIG2[['gapSppCode',
                 'iucnTaxonID',
                 'iucnComName',
                 'iucnSciName',
                 'originUS',
                 'RedListStatus',
                 'PopulationTrend',
                 'iucnTrend']]
  
# Join GapID and IUCN-GAP tables
dfGI = pd.merge(dfGapID, dfIG2, on='gapSppCode', how='inner')
#dfGI.to_csv(home + 'tmpGI.csv', index=False)

# Open rarity_GapAnalyticDB.py taxa output and set numeric column types
print('Opening and combining taxa SQL files...')
dfSQLa = pd.read_csv(home + 'tblRarityHucAmph.csv', dtype=str)
dtypes = {"hucPix": np.int64,
          "ecoPix": np.int64, 
          "gs1SppPix": np.int64, 
          "gs2SppPix": np.int64, 
          "gs3SppPix": np.int64, 
          "gs4SppPix": np.int64, 
          "totalSppPix": np.int64}
for col, col_type in dtypes.items():
    dfSQLa[col] = dfSQLa[col].astype(col_type)

dfSQLb = pd.read_csv(home + 'tblRarityHucBird.csv', dtype=str)
dtypes = {"hucPix": np.int64,
          "ecoPix": np.int64, 
          "gs1SppPix": np.int64, 
          "gs2SppPix": np.int64, 
          "gs3SppPix": np.int64, 
          "gs4SppPix": np.int64, 
          "totalSppPix": np.int64}
for col, col_type in dtypes.items():
    dfSQLb[col] = dfSQLb[col].astype(col_type)
    
dfSQLm = pd.read_csv(home + 'tblRarityHucMamm.csv', dtype=str)
dtypes = {"hucPix": np.int64,
          "ecoPix": np.int64, 
          "gs1SppPix": np.int64, 
          "gs2SppPix": np.int64, 
          "gs3SppPix": np.int64, 
          "gs4SppPix": np.int64, 
          "totalSppPix": np.int64}
for col, col_type in dtypes.items():
    dfSQLm[col] = dfSQLm[col].astype(col_type)
    
dfSQLr = pd.read_csv(home + 'tblRarityHucRept.csv', dtype=str)
dtypes = {"hucPix": np.int64,
          "ecoPix": np.int64, 
          "gs1SppPix": np.int64, 
          "gs2SppPix": np.int64, 
          "gs3SppPix": np.int64, 
          "gs4SppPix": np.int64, 
          "totalSppPix": np.int64}
for col, col_type in dtypes.items():
    dfSQLr[col] = dfSQLr[col].astype(col_type)
    
# Join taxa tables
frames = [dfSQLa, dfSQLb, dfSQLm, dfSQLr]
dfSQL = pd.concat(frames)

# Remove taxa dataframes from memory
del [[dfSQLa, dfSQLb, dfSQLm, dfSQLr]]
gc.collect()
dfSQLa=pd.DataFrame()
dfSQLb=pd.DataFrame()
dfSQLm=pd.DataFrame()
dfSQLr=pd.DataFrame()

print('Running calculations on GAP habitat data...')
# PERCENT PROTECTED (Status 1 & 2)
dfSQL['SppProt'] = dfSQL['gs1SppPix'] + dfSQL['gs2SppPix']

# National Spp Protection Summary
dfNSS = dfSQL.groupby(['Spp']).agg({'SppProt':'sum', 'totalSppPix':'sum'})
dfNSS['SppPercProt'] = (dfNSS['SppProt']/dfNSS['totalSppPix'])*100
# Round and convert to integer
dfNSS['SppPercProt'] = dfNSS['SppPercProt'].round().astype(int)
# Convert index into column
dfNSS = dfNSS.reset_index(level=['Spp'])

# Level 2 Ecoregion Spp Protection Summary
dfESS = dfSQL.groupby(['Spp', 'na_l2code', 'na_l2name']).agg({'SppProt':'sum', 'totalSppPix':'sum'})
dfESS['SppPercProt'] = (dfESS['SppProt']/dfESS['totalSppPix'])*100
# Round and convert to integer
dfESS['SppPercProt'] = dfESS['SppPercProt'].round().astype(int)
# Convert index into column
dfESS = dfESS.reset_index(level=['Spp', 'na_l2code', 'na_l2name'])
# Create combined spp & L2 column
dfESS['Spp_L2'] = dfESS['Spp'] + '_' + dfESS['na_l2code'].astype(str)

# HABITAT BREADTH   
# Calc: percent use for spp/huc combinations
dfSQL['percUse'] = (dfSQL['totalSppPix']/dfSQL['hucPix'])*100
#dfSql.columns
#dfSql.head()
#dfSql.iloc[100]    
# Mean percent use across all the hucs in distribution for each spp
dfMPU = dfSQL.groupby(['Spp']).agg({'percUse': ['count','mean']})    
# Classify spp with mean percent use <=10% as "narrow" habitat breadth,
#         and >=10% as "wide" habitat breadth (1=narrow, 0=wide)
dfMPU['percUse','habBreadth'] = np.where(dfMPU['percUse','mean']<9.95, 1, 0)
# Save as CSV (had to do this to get Spp column included in dataframe 
#         and remove MultiIndexed Header)
dfMPU.to_csv(home + 'tmpMPU.csv')
# Open CSV as dataframe - skip over multiIndexed header
dfMPU = pd.read_csv(home + 'tmpMPU.csv', skiprows=3, header=None)
# rename the columns
dfMPU = dfMPU.rename(index=str, columns={0:"gapSppCode", 1:"hucCount", 2:"meanPercUse", 3:"habBreadth"})
    
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
# Classify Spp-L2 as endemic if >= 75% (1=L2 endemic, 0=not endemic)
dfGE['L2endemic'] = np.where(dfGE['percL2']>=75.0, 1, 0)
# Subset L2 Endemics
dfGE = dfGE.loc[dfGE['L2endemic'] == 1]
# Subset the columns
dfGE = dfGE[['Spp', 'L2endemic']]
# rename the columns
dfGE = dfGE.rename(index=str, columns={"Spp":"gapSppCode"})


# LOWER 10% OF TAXA
# Identify species that have distributions in the lower 10% of taxa.
dfTSP = dfSQL.groupby(['Taxa', 'Spp']).agg({'totalSppPix': ['sum']})
# Convert index into column
dfTSP = dfTSP.reset_index().to_csv(home + 'tmpTSP.csv', index=False)  
# Remove 2nd line of multi-index header
import pyexcel as pe
sheet = pe.load(home + 'tmpTSP.csv')
del sheet.row[1]
sheet.save_as(home + 'tmpTSP.csv')
# Remove subspecies
dfTSP = pd.read_csv(home + 'tmpTSP.csv')
# Subset to full species (n = 1590)
dfTSP = dfTSP[dfTSP['Spp'].str.slice(5,6) == 'x']
# Order each taxa
dfTSP['Rank'] = dfTSP.groupby(['Taxa'])['totalSppPix'].rank(ascending=True)
#dfTSP.to_csv(home + 'dfTSP.csv', index=False)
# Identify bottom 10% within each taxa
a = 0.1014      # needed 10.14% to match
df10p = (dfTSP.groupby('Taxa',group_keys=False).apply(lambda x: x.nsmallest(int(len(x) * a), 'Rank')))
#df10p.to_csv(home + 'tmp10p.csv', index=False)
df10p['spp10p'] = 1
# Subset the columns
df10p = df10p[['Spp', 'spp10p']]
# rename the columns
df10p = df10p.rename(index=str, columns={"Spp":"gapSppCode"})

# Remove SQL table from memory
del [dfSQL]
gc.collect()
dfSQL=pd.DataFrame()

# Join Gap-IUCN, HabitatBreadth, GeographicRange and Spp10p 
dfSppInfo = pd.merge(pd.merge(pd.merge(
                dfGI, 
                dfMPU, 
                on='gapSppCode', 
                how='left'), 
                    dfGE, 
                    on='gapSppCode', 
                    how='left'),
                        df10p,
                        on='gapSppCode',
                        how='left')

# Fill in zero where NaN
dfSppInfo = dfSppInfo.replace(np.nan, 0, regex=True)
# Put blank back into PopulationTrend
dfSppInfo['PopulationTrend'] = dfSppInfo['PopulationTrend'].replace(0, '', regex=True)

# Round and convert to integer
dfSppInfo['L2endemic'] = dfSppInfo['L2endemic'].round().astype(int)
dfSppInfo['spp10p'] = dfSppInfo['spp10p'].round().astype(int)
    
print('Running calculations on species information...')
# Calc Endemic=1 if either L2endemic and spp10p equal 1
'''   
L2endemic    spp10p    Endemic
    0          0        0
    0          1        1
    1          0        1
    1          1        1
'''    
def setEndemic(row):
    if (row['L2endemic'] == 1) | (row['spp10p'] == 1):
        val = '1'
    else:
        val = '0'
    return val    
dfSppInfo['Endemic'] = dfSppInfo.apply(setEndemic, axis=1)

# Set habBreadth to 0 if originUS == Introduced
def sethabBreadthExotic(row):
    if (row['originUS'] == 'Introduced'):
        val = '0'
    else:
        val = row['habBreadth']
    return val
dfSppInfo['habBreadth'] = dfSppInfo.apply(sethabBreadthExotic, axis=1)

# Set iucnTrend to 0 if originUS == Exotic
def setTrendExotic(row):
    if (row['originUS'] == 'Introduced'):
        val = '0'
    else:
        val = row['iucnTrend']
    return val
dfSppInfo['iucnTrend'] = dfSppInfo.apply(setTrendExotic, axis=1)

# Not sure why a new column can't be calc'd from a previously cal'c column,
#  solution is to save as CSV, then reopen
dfSppInfo.to_csv(home + 'tmpSppInfo.csv', index=False)
dfSppInfo = pd.read_csv(home + 'tmpSppInfo.csv')

# Calc Group based on originUS, habBreadth, L2endemic and iucnTrend
'''   
habBreadth    Endemic    iucnTrend    Group
    0           0           0           A
    0           1           0           B
    1           0           0           C
    0           0           1           D
    1           1           0           E
    1           0           1           F
    0           1           1           G
    1           1           1           H
'''    
def setGroup(row):
    if ((row['originUS'] == "Native") | (row['originUS'] == "Reintroduced") | (row['originUS'] == "")) & (row['habBreadth'] == 0) & (row['Endemic'] == 0) & (row['iucnTrend'] == 0):
        val = 'A'
    elif ((row['originUS'] == "Native") | (row['originUS'] == "Reintroduced") | (row['originUS'] == "")) & (row['habBreadth'] == 0) & (row['Endemic'] == 1) & (row['iucnTrend'] == 0):
        val = 'B'
    elif ((row['originUS'] == "Native") | (row['originUS'] == "Reintroduced") | (row['originUS'] == "")) & (row['habBreadth'] == 1) & (row['Endemic'] == 0) & (row['iucnTrend'] == 0):
        val = 'C'
    elif ((row['originUS'] == "Native") | (row['originUS'] == "Reintroduced") | (row['originUS'] == "")) & (row['habBreadth'] == 0) & (row['Endemic'] == 0) & (row['iucnTrend'] == 1):
        val = 'D'
    elif ((row['originUS'] == "Native") | (row['originUS'] == "Reintroduced") | (row['originUS'] == "")) & (row['habBreadth'] == 1) & (row['Endemic'] == 1) & (row['iucnTrend'] == 0):
        val = 'E'
    elif ((row['originUS'] == "Native") | (row['originUS'] == "Reintroduced") | (row['originUS'] == "")) & (row['habBreadth'] == 1) & (row['Endemic'] == 0) & (row['iucnTrend'] == 1):
        val = 'F'
    elif ((row['originUS'] == "Native") | (row['originUS'] == "Reintroduced") | (row['originUS'] == "")) & (row['habBreadth'] == 0) & (row['Endemic'] == 1) & (row['iucnTrend'] == 1):
        val = 'G'
    elif ((row['originUS'] == "Native") | (row['originUS'] == "Reintroduced") | (row['originUS'] == "")) & (row['habBreadth'] == 1) & (row['Endemic'] == 1) & (row['iucnTrend'] == 1):
        val = 'H'
    else:
        val = 'X'
    return val    
dfSppInfo['Group'] = dfSppInfo.apply(setGroup, axis=1)

# Not sure why a new column can't be calc'd from a previously cal'c column
# Need to save as CSV, then reopen
dfSppInfo.to_csv(home + 'tmpSppInfo.csv', index=False)
dfSppInfo = pd.read_csv(home + 'tmpSppInfo.csv')

# Calc Subgroup based on Group
'''   
Group    Subgroup
  A         A
  B        TR
  C        TR
  D        DD
  E        TR
  F        DD
  G        DD
  H        DD
  X         X
'''    
def setSubgroup(row):
    if (row['Group'] == 'A'):
        val = 'A'
    elif (row['Group'] == 'B') | (row['Group'] == 'C') | (row['Group'] == 'E'):
        val = 'TR'
    elif (row['Group'] == 'D') | (row['Group'] == 'F') | (row['Group'] == 'G') | (row['Group'] == 'H'):
        val = 'DD'
    else:
        val = 'X'
    return val    
dfSppInfo['Subgroup'] = dfSppInfo.apply(setSubgroup, axis=1)

# Not sure why a new column can't be calc'd from a previously cal'c column
# Need to save as CSV, then reopen
dfSppInfo.to_csv(home + 'tmpSppInfo.csv', index=False)
dfSppInfo = pd.read_csv(home + 'tmpSppInfo.csv')
# Drop duplicate records
dfSppInfo.drop_duplicates(keep='first',inplace=True)

# Calc potential rarity based on group
def setRare(row):
    if (row['Group'] == 'A') | (row['Group'] == 'X'):
        val = '0'
    else:
        val = '1'
    return val    
dfSppInfo['potRare'] = dfSppInfo.apply(setRare, axis=1)
# dfSppInfo.to_csv(home + 'tmpSppInfo.csv', index=False)
# dfSppInfo = pd.read_csv(home + 'tmpSppInfo.csv')

# Join SppInfo to National protection summary
dfNatSumm = pd.merge(dfSppInfo, 
                     dfNSS, 
                     left_on='gapSppCode',
                     right_on='Spp',
                     how='left')

# Join SppInfo to Ecoregion protection summary
dfEcoSumm = pd.merge(dfSppInfo, 
                     dfESS, 
                     left_on='gapSppCode',
                     right_on='Spp',
                     how='left')

# Write output to csv file
dfNatSumm.to_csv(home + 'tblNatSumm.csv', index=False)
dfEcoSumm.to_csv(home + 'tblEcoSumm.csv', index=False)

print('Finished')