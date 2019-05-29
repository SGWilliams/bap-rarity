# -*- coding: utf-8 -*-
"""
MatchJenkinsIUCN.py

enviroment: base 2.7

Input: Jenkins2015 excel files (https://biodiversitymapping.org/wordpress/index.php/home/)
       IUCN_Gap.csv table from GAP Habitat Map Collection Item
       ScienceBaseHabMapCSV_<date>.csv table from GAP Habitat Map Collection Item

Output: tblJenkMatch.csv
 
Created on 24may2019

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
import urllib
import csv
import openpyxl
import os
import requests

# import SB user/password from sbconfig
import sbconfig
# =======================================================================
# LOCAL VARIABLES

# set paths based on local host
# identify location
host = socket.gethostname()
#print(host)

if host == 'Thrasher':
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


## --------------------- Write to CSV file ----------------------
def WriteRecord(spp, gcn, gsc, iti, isn, icn, mt, b, je):
    # combine strings and append to file
    rowStr = BINOMIAL + ',' + str(intJend) + ',' + matchType + ',' + strUC + ',' + strGSN + ',' + strGCN + ',' + strITI + ',' + strISN + ',' + strICN
    #print(' rowStr: ' + rowStr)
    # data record - append to file, add data
    tblMatchJenkins = open(home + 'tblMatchJenkins.csv', 'ab')
    # create the csv writer object
    csvwriter = csv.writer(tblMatchJenkins)
    csvwriter.writerow(rowStr.split(','))
    #csvwriter.writerow(JD.split())
    tblMatchJenkins.close()
    return rowStr


# =======================================================================
# Get GAP species info and IUCN-GAP table from SB HabMap item
sb = ConnectToSB()
habItem = sb.get_item("527d0a83e4b0850ea0518326")
for file in habItem["files"]:
    if file["name"].startswith("IUCN_Gap"):
        dfIUCN = pd.read_csv(StringIO(sb.get(file["url"])))
#dfIUCN = pd.read_csv('N:\\temp\\IUCN_Gap_20190412.csv')

# Replace nulls in IUCN-GAP
dfIUCN = dfIUCN.replace(np.nan, '', regex=True)

# Subset the columns
dfIUCN = dfIUCN[['gapSppCode', 
                 'gapSciName', 
                 'gapComName', 
                 'iucnTaxonID', 
                 'iucnSciName', 
                 'iucnComName']]

# Build a table of Jenkin's IUCN endemics from individual taxa files
xlsJenkAmph = home + 'Jenkins2015_AmphSppLists.xlsx'
xlsJenkBird = home + 'Jenkins2015_BirdSppLists.xlsx'
xlsJenkMamm = home + 'Jenkins2015_MammSppLists.xlsx'
xlsJenkRept = home + 'Jenkins2015_ReptSppLists.xlsx'

# Open files from Jenkins website, if fails then from BAP-Rarity repository
try:
    dls = 'http://biodiversitymapping.org/docs/USA%20amphibian%20species%20lists.xlsx'
    urllib.urlretrieve(dls, xlsJenkAmph)
except:
    dls = 'https://raw.githubusercontent.com/SGWilliams/bap-rarity/master/Jenkins2015_AmphSppLists.xlsx'
    urllib.urlretrieve(dls, xlsJenkAmph)
try:
    dls = 'http://biodiversitymapping.org/docs/USA%20bird%20species%20lists.xlsx'
    urllib.urlretrieve(dls, xlsJenkBird)
except:
    dls = 'https://raw.githubusercontent.com/SGWilliams/bap-rarity/master/Jenkins2015_BirdSppLists.xlsx'
    urllib.urlretrieve(dls, xlsJenkBird)
try:
    dls = 'http://biodiversitymapping.org/docs/USA%20mammal%20species%20lists.xlsx'
    urllib.urlretrieve(dls, xlsJenkMamm)
except:
    dls = 'https://raw.githubusercontent.com/SGWilliams/bap-rarity/master/Jenkins2015_MammSppLists.xlsx'
    urllib.urlretrieve(dls, xlsJenkMamm)
try:
    dls = 'http://biodiversitymapping.org/docs/USA%20reptile%20species%20lists.xlsx'
    urllib.urlretrieve(dls, xlsJenkRept)
except:
    dls = 'https://raw.githubusercontent.com/SGWilliams/bap-rarity/master/Jenkins2015_ReptSppLists.xlsx'
    urllib.urlretrieve(dls, xlsJenkRept)
    
# Rename worksheet name in Rept file
ss=openpyxl.load_workbook(xlsJenkRept)
ss_sheet = ss['Endemic']
ss_sheet.title = 'Endemics'
ss.save(xlsJenkRept) 

# Open worksheets
dfJenkAmph = pd.read_excel(open(xlsJenkAmph, 'rb'), sheetname='Endemics')
dfJenkBird = pd.read_excel(open(xlsJenkBird, 'rb'), sheetname='Endemics')
dfJenkMamm = pd.read_excel(open(xlsJenkMamm, 'rb'), sheetname='Endemics')
dfJenkRept = pd.read_excel(open(xlsJenkRept, 'rb'), sheetname='Endemics')

# Rename columns
dfJenkAmph = dfJenkAmph.rename(index=str, columns={"Scientific_name":"BINOMIAL", "SPCRECID":"Species_ID", "SCI_NAME":"BINOMIAL"})
dfJenkBird = dfJenkBird.rename(index=str, columns={"Scientific_name":"BINOMIAL", "SPCRECID":"Species_ID", "SCI_NAME":"BINOMIAL"})
dfJenkMamm = dfJenkMamm.rename(index=str, columns={"Scientific_name":"BINOMIAL", "SPCRECID":"Species_ID", "SCI_NAME":"BINOMIAL"})
dfJenkRept = dfJenkRept.rename(index=str, columns={"Scientific_name":"BINOMIAL", "SPCRECID":"Species_ID", "SCI_NAME":"BINOMIAL"})

# Subset the columns, if Species_ID doesn't exist then add it and set to zero
try:
    dfJenkAmph = dfJenkAmph[['Species_ID','BINOMIAL']]
except:
    dfJenkAmph['Species_ID']=0
try:
    dfJenkBird = dfJenkBird[['Species_ID','BINOMIAL']]
except:
    dfJenkBird['Species_ID']=0
try:
    dfJenkMamm = dfJenkMamm[['Species_ID','BINOMIAL']]
except:
    dfJenkMamm['Species_ID']=0
try:
    dfJenkRept = dfJenkRept[['Species_ID','BINOMIAL']]
except:
    dfJenkRept['Species_ID']=0

# Concatenate Jenkins IUCN endemic taxa tables
frames = [dfJenkAmph, dfJenkBird, dfJenkMamm, dfJenkRept]
dfJenk = pd.concat(frames)

# Set up output file for matching results
# first record - write new file, add headers
tblMatchJenkins = open(home + 'tblMatchJenkins.csv', 'wb')
# create the csv writer object
csvwriter = csv.writer(tblMatchJenkins)
# create the header
header = 'jenkBINOMIAL Jend matchType gapSppCode gapSciName gapComName iucnTaxonID iucnSciName iucnComName'
csvwriter.writerow(header.split())
tblMatchJenkins.close()

# Iterate through Jenk table and find match based on iucnSciName, then iucnSynonyms
#dfJenk = dfJenk.loc[dfJenk['BINOMIAL'] == 'Aphelocoma insularis']  #bISSJx match on >1 synonym
#dfJenk = dfJenk.loc[dfJenk['BINOMIAL'] == 'Chrysemys dorsalis']  # match on SciName
#dfJenk = dfJenk.loc[dfJenk['BINOMIAL'] == 'Deirochelys reticularia']  # multiple matches
for row in dfJenk.itertuples(index=True, name='Pandas'):
    # Set variables
    BINOMIAL = getattr(row,"BINOMIAL")
    # Create empty series
    strUClist = pd.Series([])
    
    # Find match on iucnSciName
    # match single item series and set intJend
    if len(dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'gapSppCode']) == 1:
        strUC = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'gapSppCode'].item()
        strGSN = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'gapSciName'].item()
        strGCN = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'gapComName'].item()
        intITI = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'iucnTaxonID'].item()
        strITI = "{:.0f}".format(intITI)
        strISN = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'iucnSciName'].item()
        strICN = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'iucnComName'].item()
        matchType = 'Matched on iucnSciName'
    # match multiple items in series and set intJend
    elif len(dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'gapSppCode']) > 1:            
        # create series of species to be attributed
        strUClist = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'gapSppCode']
        cnt = len(dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'gapSppCode'])
    # when no iucnSciName matches exits
    else:
        # Find match on iucnSynonyms
        try: 
            # retrieve IUCN accepted name by synonym
            urlS = "http://apiv3.iucnredlist.org/api/v3/species/synonym/" + \
                BINOMIAL + "?token=" + os.environ["IUCN_TOKEN"]
            jsonS = requests.get(urlS).json()
            # if any results came back, get first one and set accepted name
            if jsonS["count"] > 0:
                # get accepted name
                iucnAcceptedName = jsonS["result"][0]["accepted_name"]
                # if 1 item in series
                if len(dfIUCN.loc[dfIUCN['iucnSciName'] == str(iucnAcceptedName), 'gapSppCode']) == 1:
                    strUC = dfIUCN.loc[dfIUCN['iucnSciName'] == str(iucnAcceptedName), 'gapSppCode'].item()
                    strGSN = dfIUCN.loc[dfIUCN['iucnSciName'] == str(iucnAcceptedName), 'gapSciName'].item()
                    strGCN = dfIUCN.loc[dfIUCN['iucnSciName'] == str(iucnAcceptedName), 'gapComName'].item()
                    intITI = dfIUCN.loc[dfIUCN['iucnSciName'] == str(iucnAcceptedName), 'iucnTaxonID'].item()
                    strITI = "{:.0f}".format(intITI)
                    strISN = dfIUCN.loc[dfIUCN['iucnSciName'] == str(iucnAcceptedName), 'iucnSciName'].item()
                    strICN = dfIUCN.loc[dfIUCN['iucnSciName'] == str(iucnAcceptedName), 'iucnComName'].item()
                    matchType = 'Matched on iucnSynonym (' + iucnAcceptedName + ')'
                # if > 1 item in series, match multiple items in series and set intJend
                elif len(dfIUCN.loc[dfIUCN['iucnSciName'] == str(iucnAcceptedName), 'gapSppCode']) > 1:
                    # create series of species to be attributed
                    strUClist = dfIUCN.loc[dfIUCN['iucnSciName'] == str(iucnAcceptedName), 'gapSppCode']
                    cnt = len(dfIUCN.loc[dfIUCN['iucnSciName'] == str(iucnAcceptedName), 'gapSppCode'])
                else:
                    # If no match on iucnSciName or iucnSynonym, try to match on gapSciName
                    try:
                        strUC = dfIUCN.loc[dfIUCN['gapSciName'] == BINOMIAL, 'gapSppCode'].item()
                        strGSN = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'gapSciName'].item()
                        strGCN = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'gapComName'].item()
                        intITI = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'iucnTaxonID'].item()
                        strITI = "{:.0f}".format(intITI)
                        strISN = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'iucnSciName'].item()
                        strICN = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'iucnComName'].item()
                        matchType = 'Matched on gapSciName'
                    except:
                        print(' Failed to match on iucnSciName iucnSynonym or gapSciName (>1), ' + BINOMIAL)
                        strUC = ''
                        strGSN = ''
                        strGCN = ''
                        intITI = ''
                        strITI = ''
                        strISN = ''
                        strICN = ''
                        matchType = 'Failed to match on iucnSciName iucnSynonym or gapSciName'
            # if no results came back
            else:
                # If no match on iucnSciName or iucnSynonym, try to match on gapSciName
                try:
                    strUC = dfIUCN.loc[dfIUCN['gapSciName'] == BINOMIAL, 'gapSppCode'].item()
                    strGSN = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'gapSciName'].item()
                    strGCN = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'gapComName'].item()
                    intITI = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'iucnTaxonID'].item()
                    strITI = "{:.0f}".format(intITI)
                    strISN = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'iucnSciName'].item()
                    strICN = dfIUCN.loc[dfIUCN['iucnSciName'] == BINOMIAL, 'iucnComName'].item()
                    matchType = 'Matched on gapSciName'
                except:
                    print(' Failed to match on iucnSciName iucnSynonym or gapSciName (==0), ' + BINOMIAL)
                    strUC = ''
                    strGSN = ''
                    strGCN = ''
                    intITI = ''
                    strITI = ''
                    strISN = ''
                    strICN = ''
                    matchType = 'Failed to match on iucnSciName iucnSynonym or gapSciName'
        except:
            print(' Failed to get IUCN API response : ' + BINOMIAL)
            strUC = ''
            strGSN = ''
            strGCN = ''
            intITI = ''
            strITI = ''
            strISN = ''
            strICN = ''
            matchType = 'Failed to get IUCN API response'

    # Write single or multiple records to csv file
    intJend = "1"
    if len(strUClist) == 0:
        WriteRecord(strUC, strGSN, strGCN, strITI, strISN, strICN, matchType, BINOMIAL, intJend)
    else:
        while cnt > 0:
            s = cnt - 1
            f = cnt
            strUC = strUClist[s:f].item()
            strGSN = dfIUCN.loc[dfIUCN['gapSppCode'] == strUC, 'gapSciName'].item()
            strGCN = dfIUCN.loc[dfIUCN['gapSppCode'] == strUC, 'gapComName'].item()
            intITI = dfIUCN.loc[dfIUCN['gapSppCode'] == strUC, 'iucnTaxonID'].item()
            strITI = "{:.0f}".format(intITI)            
            strISN = dfIUCN.loc[dfIUCN['gapSppCode'] == strUC, 'iucnSciName'].item()
            strICN = dfIUCN.loc[dfIUCN['gapSppCode'] == strUC, 'iucnComName'].item()
            matchType = 'Matched on iucnSciName several times'
            WriteRecord(strUC, strGSN, strGCN, strITI, strISN, strICN, matchType, BINOMIAL, intJend)
            cnt = cnt - 1