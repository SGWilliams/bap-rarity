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
#import pandas.io.sql as psql
import numpy as np
from sciencebasepy import SbSession
from io import StringIO
import urllib
import csv
import openpyxl
import os
import requests
#import xml.etree.ElementTree as ET

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

## ------------------------Taxa Work---------------------------------
def TaxaWork(Taxa):
    # Set taxa variables  Taxa='Amph' Taxa='Bird' Taxa='Mamm' Taxa='Rept'
    tblSQL = home + 'tblRarityHuc' + Taxa + '.csv'
    xlsJenk = home + 'Jenkins2015_' + Taxa + 'SppLists.xlsx'
    if Taxa == 'Amph':
        taxa = 'amphibian'
        t = 'a'
    elif Taxa == 'Bird':
        taxa = 'bird'
        t = 'b'
    elif Taxa == 'Mamm':
        taxa = 'mammal'
        t = 'm'
    elif Taxa == 'Rept':
        taxa = 'reptile'
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
    #dfGapID = pd.read_csv('N:\\temp\\ScienceBaseHabMapCSV_20190412.csv')

    # Subset to taxa
    dfGapID = dfGapID[dfGapID['GAP_code'].str.slice(0,1) == t]
    # Subset to full species
    dfGapID = dfGapID[dfGapID['GAP_code'].str.slice(5,6) == 'x']
    
    # Subset the columns
    dfGapID = dfGapID[['GAP_code', 'common_name', 'scientific_name', 'OriginUS']]
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
    # Classify spp with mean percent use <=10% as "narrow" habitat breadth,
    #         and >=10% as "wide" habitat breadth (1=narrow, 0=wide)
    dfMPU['percUse','habBreadth'] = np.where(dfMPU['percUse','mean']<9.95, 1, 0)
    # Save as CSV (had to do this to get Spp column included in dataframe 
    #         and remove MultiIndexed Header)
    dfMPU.to_csv(home + 'tmpMPU.csv')
    # Open CSV as dataframe - skip over multiIndexed header
    dfMPU = pd.read_csv(home + 'tmpMPU.csv', skiprows=3, header=None)
    # subset the columns (0=Spp, 3=habBreadth)
    #dfMPU = dfMPU[[0,3]]
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
    # Classify Spp-L2 as endemic if >= 50% (1=L2 endemic, 0=not endemic)
    dfGE['L2endemic'] = np.where(dfGE['percL2']>=50.0, 1, 0)    
    # Subset L2 Endemics
    dfGE = dfGE.loc[dfGE['L2endemic'] == 1]
    # Subset the columns
    dfGE = dfGE[['Spp', 'percL2', 'L2endemic']]
    # rename the columns
    dfGE = dfGE.rename(index=str, columns={"Spp":"gapSppCode"})

    # Join Gap info, Habitat Breadth and Geographic Range
    dfGap = pd.merge(pd.merge(dfGapID, dfMPU, on='gapSppCode', how='left'), dfGE, on='gapSppCode', how='left')
    # Fill in zero where NaN
    dfGap = dfGap.replace(np.nan, 0, regex=True)

    # GET IUCN-GAP TABLES FROM SB HABMAP ITEM
    sb = ConnectToSB()
    habItem = sb.get_item("527d0a83e4b0850ea0518326")
    for file in habItem["files"]:
        if file["name"].startswith("IUCN_Gap"):
            dfIUCN = pd.read_csv(StringIO(sb.get(file["url"])))
    #dfIUCN = pd.read_csv('N:\\temp\\IUCN_Gap_20190412.csv')
    # Subset to taxa
    dfIUCN = dfIUCN[dfIUCN['gapSppCode'].str.slice(0,1) == t]
    # Replace nulls
    dfIUCN = dfIUCN.replace(np.nan, '', regex=True)
    # Calculate iucnTrend based on iucnCategory and iucnPopulationTrend
    def setTrend(row):
        if (row['iucnCategory'] == 'VU') | (row['iucnCategory'] == 'CR') | (row['iucnCategory'] == 'EN') | (row['iucnPopulationTrend'] == 'decreasing'):
            val = '1'
        else:
            val = '0'
        return val    
    dfIUCN['iucnTrend'] = dfIUCN.apply(setTrend, axis=1)
    # Subset the columns
    #dfIUCN = dfIUCN[['gapSppCode', 'iucnTaxonID', 'iucnComName', 'iucnSciName', 'iucnTrend']]
    dfIUCN = dfIUCN[['gapSppCode', 'iucnTaxonID', 'iucnComName', 'iucnSciName', 'iucnCategory', 'iucnPopulationTrend', 'iucnTrend']]
      
    # Join Gap-IUCN...
    dfGI = pd.merge(dfGap, dfIUCN, on='gapSppCode', how='left')
    # Add zeros into missing iucnTrend
    dfGI['iucnTrend'] = dfGI['iucnTrend'].replace(np.nan, 0, regex=True)
    # Add blanks into remaining missing fields
    dfGI = dfGI.replace(np.nan, '', regex=True)
    #dfGI.csv_to_file(home + 'tmpGI.csv')

    # Open file from Jenkins website, if fails then from BAP-Rarity repository
    try:
        dls = 'http://biodiversitymapping.org/docs/USA%20' + taxa + '%20species%20lists.xlsx'
        urllib.urlretrieve(dls, xlsJenk)
    except:
        dls = 'https://raw.githubusercontent.com/SGWilliams/bap-rarity/master/Jenkins2015_' + Taxa + 'SppLists.xlsx'
        urllib.urlretrieve(dls, xlsJenk)
    # Rename worksheet name in Rept file
    if Taxa == 'Rept':
        ss=openpyxl.load_workbook(xlsJenk)
        ss_sheet = ss['Endemic']
        ss_sheet.title = 'Endemics'
        ss.save(xlsJenk) 
    # Open worksheet
    dfJenk = pd.read_excel(open(xlsJenk, 'rb'), sheetname='Endemics')
    # Rename columns
    dfJenk = dfJenk.rename(index=str, columns={"Scientific_name":"BINOMIAL", "SPCRECID":"Species_ID", "SCI_NAME":"BINOMIAL"})
    # Subset the columns, if Species_ID doesn't exist then add it and set to zero
    try:
        dfJenk = dfJenk[['Species_ID','BINOMIAL']]
    except:
        dfJenk['Species_ID']=0
    # Add column for endemic status
    dfJenk['Jend'] = 1

    # Join Gap-IUCN and Jenkins based on iucnSciName, then iucnCode, then iucnSynonyms
    # Set up output file
    # first record - write new file, add headers
    tmpTbl = open(home + 'tmpTbl.csv', 'wb')
    # create the csv writer object
    csvwriter = csv.writer(tmpTbl)
    # create the header
    #header = 'gapSppCode gapComName gapSciName originUS iucnTrend habBreadth L2endemic Jend'
    header = 'gapSppCode gapComName gapSciName originUS meanPercUse habBreadth percL2 L2endemic iucnCategory iucnPopulationTrend iucnTrend Jend'
    csvwriter.writerow(header.split())
    #csvwriter.writerow(JD.split())
    tmpTbl.close()

    # Iterate through GI table
    #dfGI2 = dfGI.loc[dfGI['gapSppCode'] == 'aNJFRx']  # match on SciName
    #dfGI2 = dfGI.loc[dfGI['gapSppCode'] == 'aPBTRx']  # match on SpeciesID
    #dfGI2 = dfGI.loc[dfGI['gapSppCode'] == 'aCUTRx']  # no match
    
    for row in dfGI.itertuples(index=True, name='Pandas'):
    #for row in dfGI2.itertuples(index=True, name='Pandas'):
        # Set variables
        #        strUC = getattr(row,"gapSppCode")
        #        strGapComName = getattr(row,"gapComName")
        #        strGapSciName = getattr(row,"gapSciName")
        #        strOriginUS = str(getattr(row,"originUS"))
        #        intIucnTrend = str(getattr(row,"iucnTrend"))
        #        intHabBreadth = str(getattr(row,"habBreadth"))
        #        intL2endemic = str(getattr(row,"L2endemic"))
        #        intIucnTaxonID = getattr(row,"iucnTaxonID")
        #        strIucnSciName = getattr(row,"iucnSciName")
        strUC = getattr(row,"gapSppCode")
        strGapComName = getattr(row,"gapComName")
        strGapSciName = getattr(row,"gapSciName")
        strOriginUS = str(getattr(row,"originUS"))
        fltMeanPercUse = str(getattr(row,"meanPercUse"))
        intHabBreadth = str(getattr(row,"habBreadth"))
        fltPercL2 = str(getattr(row,"percL2"))
        intL2endemic = str(getattr(row,"L2endemic"))
        strIucnCat = getattr(row,"iucnCategory")
        strIucnPopT = getattr(row,"iucnPopulationTrend")
        intIucnTrend = str(getattr(row,"iucnTrend"))
        intIucnTaxonID = getattr(row,"iucnTaxonID")
        strIucnSciName = getattr(row,"iucnSciName")
        
        # Find match on iucnSciName
        try:
            intJend = dfJenk.loc[dfJenk['BINOMIAL'] == strIucnSciName, 'Jend'].item()
            print(strUC + ' matched Jenk on SciName')
        except:
            # Find match on iucnTaxonID
            try:
                intJend = dfJenk.loc[dfJenk['Species_ID'] == intIucnTaxonID, 'Jend'].item()
                print(strUC + ' matched Jenk on SpeciesID')
            except:
                # Find match on iucnSynonyms
                try: 
                    # retrieve IUCN synonym by accepted name
                    urlS = "http://apiv3.iucnredlist.org/api/v3/species/synonym/" + \
                        strIucnSciName + "?token=" + os.environ["IUCN_TOKEN"]
                    jsonS = requests.get(urlS).json()
                    # Assess whether or not any results came back
                    if jsonS["count"] > 0:
                        # search through results for synonym match to Jenkin BIONOMIAL
                        n = jsonS["count"] - 1
                        while n >= 0:
                            iucnSynonym = jsonS["result"][n]["synonym"]
                            print(strUC + ' matched Jenk on synonym ' + str(n) + ' : ' + iucnSynonym)
                            intJend = dfJenk.loc[dfJenk['BINOMIAL'] == iucnSynonym, 'Jend'].item()
                            n = n-1
                    else:
                        # If no match on SciName, TaxonID or synonym, set to GapIUCN.originUS
                        print(strUC + ' No Jenk match')
                        if strOriginUS == 'Native':
                            intJend = '1'
                        else:
                            intJend = '0'
                except:
                    # If no match on SciName, TaxonID or synonym, set to GapIUCN.originUS
                    print(strUC + ' No Jenk match')
                    if strOriginUS == 'Native':
                        intJend = '1'
                    else:
                        intJend = '0'
                    #print('Jend: ' + intJend)

        # Write output to csv file
        # combine strings and append to file
        #        rowStr = strUC + ',' \
        #               + strGapComName + ',' \
        #               + strGapSciName + ',' \
        #               + strOriginUS + ',' \
        #               + intIucnTrend + ',' \
        #               + intHabBreadth + ',' \
        #               + intL2endemic + ',' \
        #               + str(intJend)
        rowStr = strUC + ',' \
               + strGapComName + ',' \
               + strGapSciName + ',' \
               + strOriginUS + ',' \
               + fltMeanPercUse + ',' \
               + intHabBreadth + ',' \
               + fltPercL2 + ',' \
               + intL2endemic + ',' \
               + strIucnCat + ',' \
               + strIucnPopT + ',' \
               + intIucnTrend + ',' \
               + str(intJend)

        #print(' rowStr: ' + rowStr)
        # data record - append to file, add data
        tmpTbl = open(home + 'tmpTbl.csv', 'ab')
        # create the csv writer object
        csvwriter = csv.writer(tmpTbl)
        csvwriter.writerow(rowStr.split(','))
        #csvwriter.writerow(JD.split())
        tmpTbl.close()
        
    # Open temp CSV file as dataframe
    dfGIJ = pd.read_csv(home + 'tmpTbl.csv')

    # Calc Endemic=1 if both L2endemic and Jend equal 1
    '''   
    L2endemic    Jend    Endemic
        0          0        0
        0          1        0
        1          0        0
        1          1        1
    '''    
    def setEndemic(row):
        if (row['L2endemic'] == 1) & (row['Jend'] == 1):
            val = '1'
        else:
            val = '0'
        return val    
    dfGIJ['Endemic'] = dfGIJ.apply(setEndemic, axis=1)

    # Not sure why a new column can't be calc'd from a previously cal'c column,
    #  solution is to save as CSV, then reopen
    dfGIJ.to_csv(home + 'tmpGIJ.csv', index=False)
    dfGIJ = pd.read_csv(home + 'tmpGIJ.csv')

    # Calc Group based on habBreadth, L2endemic and iucnTrend
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
        if (row['habBreadth'] == 0) & (row['Endemic'] == 0) & (row['iucnTrend'] == 0):
            val = 'A'
        elif (row['habBreadth'] == 0) & (row['Endemic'] == 1) & (row['iucnTrend'] == 0):
            val = 'B'
        elif (row['habBreadth'] == 1) & (row['Endemic'] == 0) & (row['iucnTrend'] == 0):
            val = 'C'
        elif (row['habBreadth'] == 0) & (row['Endemic'] == 0) & (row['iucnTrend'] == 1):
            val = 'D'
        elif (row['habBreadth'] == 1) & (row['Endemic'] == 1) & (row['iucnTrend'] == 0):
            val = 'E'
        elif (row['habBreadth'] == 1) & (row['Endemic'] == 0) & (row['iucnTrend'] == 1):
            val = 'F'
        elif (row['habBreadth'] == 0) & (row['Endemic'] == 1) & (row['iucnTrend'] == 1):
            val = 'G'
        elif (row['habBreadth'] == 1) & (row['Endemic'] == 1) & (row['iucnTrend'] == 1):
            val = 'H'
        else:
            val = 'X'
        return val    
    dfGIJ['Group'] = dfGIJ.apply(setGroup, axis=1)
    
    # Not sure why a new column can't be calc'd from a previously cal'c column
    # Need to save as CSV, then reopen
    dfGIJ.to_csv(home + 'tmpGIJ.csv', index=False)
    dfGIJ = pd.read_csv(home + 'tmpGIJ.csv')

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
    '''    
    def setSubgroup(row):
        if (row['Group'] == 'A'):
            val = 'A'
        elif (row['Group'] == 'B') | (row['Group'] == 'C') | (row['Group'] == 'E'):
            val = 'TR'
        elif (row['Group'] == 'D') | (row['Group'] == 'F') | (row['Group'] == 'G') | (row['Group'] == 'H'):
            val = 'DD'
        else:
            val = 'XXX'
        return val    
    dfGIJ['Subgroup'] = dfGIJ.apply(setSubgroup, axis=1)

    # Not sure why a new column can't be calc'd from a previously cal'c column
    # Need to save as CSV, then reopen
    dfGIJ.to_csv(home + 'tmpGIJ.csv', index=False)
    dfGIJ = pd.read_csv(home + 'tmpGIJ.csv')

    # Calc potential rarity based on group
    def setRare(row):
        if (row['Group'] == 'A'):
            val = '0'
        else:
            val = '1'
        return val    
    dfGIJ['potRare'] = dfGIJ.apply(setRare, axis=1)
    dfGIJ.to_csv(home + 'tmpGIJ' + t + '.csv', index=False)
    # dfGIJ = pd.read_csv(home + 'tmpGIJ.csv')
    
    return (dfGIJ)
    
# =======================================================================
# Generate taxa output
print('Working on Amph...')
dfAmph = TaxaWork('Amph')
print('Working on Bird...')
dfBird = TaxaWork('Bird')
print('Working on Mamm...')
dfMamm = TaxaWork('Mamm')
print('Working on Rept...')
dfRept = TaxaWork('Rept')

# Combine taxa output
frames = [dfAmph, dfBird, dfMamm, dfRept]
dfRarity = pd.concat(frames)
# Write output to CSV file
dfRarity.to_csv(home + 'tmpRarity.csv', index=False)