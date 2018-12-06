# -*- coding: utf-8 -*-
"""
rarity_IUCN.py

enviroment: base 2.7

Retrieves IUCN information from IUCN api and builds a table of
  GAP species code, sciName, comName and IUCN species ID, sciName,
  comName, protection status and population trend.

 
Created on Mon Nov 5 13:21:53 2018

@author: sgwillia
=======================================================================
"""
# Import packages
import requests
import pandas as pd
from sciencebasepy import SbSession
from io import StringIO
import os
import csv
import socket
import sys

# =======================================================================
# LOCAL VARIABLES
# Set variable to use existing output if it exists, otherwise replace
replaceTable = 'no' # 'yes' to replace

# set based on local host
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

# import SB user/password from gapconfig
import gapconfig
    
# =======================================================================
# LOCAL FUNCTIONS 
## -------------------Connect to ScienceBase-------------------------
def ConnectToSB(username=gapconfig.sbUserName, password=gapconfig.sbWord):
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

## -------------Replace null variables with empty string-----------------
def xstr(s):
    if s is None:
        return ''
    return (s)

## ---------------------Build GAP/IUCN Table-----------------------------
def buildIUCN():
    # GET SPP AND IUCN-GAP TABLES FROM SB HABMAP ITEM
    sb = ConnectToSB()
    habItem = sb.get_item("527d0a83e4b0850ea0518326")
    for file in habItem["files"]:
        if file["name"] == "ScienceBaseHabMapCSV_20180713.csv":
            gapSpp = pd.read_csv(StringIO(sb.get(file["url"])))
        elif file["name"] == "IUCN_Gap.csv":
            iucnGap = pd.read_csv(StringIO(sb.get(file["url"])))
    # combine tables (this inner join limits output to just matched IUCN IDs)
    tbSpp = pd.merge(gapSpp, iucnGap, how='inner', left_on='GAP_code', 
                     right_on='GapSpCode', sort=True,
             suffixes=('_x', '_y'), copy=True)
    # this is to replace any spaces in column names with underscores. 
    # spaces cause issues
    cols = tbSpp.columns
    cols = cols.map(lambda x:x.replace(' ','_') if isinstance(x,(str,unicode)) else x)
    tbSpp.columns = cols
    
    # =======================================================================
    # SET UP LOOP ON SPECIES
    # first record - write new file, add headers
    tblIUCN = open(home + 'tblIUCN.csv', 'wb')
    # create the csv writer object
    csvwriter = csv.writer(tblIUCN)
    # create the header
    header = 'strUC strSciName strComName iucnID iucnSci iucnCom iucnCat iucnTnd'
    csvwriter.writerow(header.split())
    #csvwriter.writerow(JD.split())
    tblIUCN.close()
    
    # Iterate through table
    # set row count to 1
    rowNum = 1
    for row in tbSpp.itertuples(index=True, name='Pandas'):
        # set variables
        strUC = getattr(row,"GAP_code")
        strSciName = getattr(row,"scientific_name")
        strComName = getattr(row,"common_name")
        intITIScode = getattr(row,"TSN_code")
        strSbHabID = getattr(row,"ScienceBase_url")[-24:]
        strGapSpCode = getattr(row,"GapSpCode")
        strTaxa = getattr(row,"Taxa")
        intIucnID = getattr(row,"IUCN_Spp_Number")
        
        # reset sppCode if script fails along the way
        #if strComName[-16:] == 'Dwarf Salamander':  
        if strUC <= 'zFFFFx':  
            print('Working on '+str(rowNum)+' : '+strUC)
            # pull iucn data down, reformat and create json
    
            # fix incorrect intIucnID values
            # get global assessment for species by scientific name
            # sciName = 'Leptonycteris nivalis'
            # urlA = "http://apiv3.iucnredlist.org/api/v3/species/" + sciName + "?token=" + os.environ["IUCN_TOKEN"]
            # urlN = "http://apiv3.iucnredlist.org/api/v3/species/narrative/" + sciName + "?token=" + os.environ["IUCN_TOKEN"]
            
            if strSciName == "Larus glaucoides":  # Wrong intIucnID = 22694346
                intIucnID = 22729877       
            if strSciName == "Larus thayeri":  # Thayer's Gull is not identified by IUCN, rather it is part of Iceland Gull
                intIucnID = 22729877    
            if strSciName == "Oceanodroma leucorhoa":  # Wrong intIucnID = 22698511
                intIucnID = 132438298
            if strSciName == "Neotoma lepida":  # Wrong intIucnID = 14589
                intIucnID = 116988741
            if strSciName == "Urocitellus brunneus":  # Wrong intIucnID = 20473 ; IUCN split into Northern & Southern IGS (intIucnID = 20498)
                intIucnID = 20497
            if strSciName == "Cervus elephus":  # Wrong intIucnID = 56003281
                intIucnID = 55997823
            if strSciName == "Gambelia wislizenii":  # Wrong intIucnID = 64014
                intIucnID = 64015
            if strSciName == "Perognathus parvus":  # Wrong intIucnID = 16637 ; Similar IUCN main_common_name
                intIucnID = 42610
            if strSciName == "Leptonycteris nivalis":  # Wrong intIucnID = 4776
                intIucnID = 11697
            '''
            Red List
            Population Trend (decreasing, stable/increasing)
            Threatened Categories (critical CR, endangered EN, 
              vulnerable VU) characterized as decreasing even if 
              IUCN population trend was stable or unknown.
    
            '''
            # retrieve global assessment for species by id
            urlA = "http://apiv3.iucnredlist.org/api/v3/species/id/" + \
            str(intIucnID) + "?token=" + os.environ["IUCN_TOKEN"]
            jsonA = requests.get(urlA).json()
            iucnCom = xstr(jsonA["result"][0]["main_common_name"]).replace(u"\u2019", "'")
            #print(' GAPcom:  ' + strComName)
            #print(' iucnCom: ' + iucnCom)
            iucnSci = xstr(jsonA["result"][0]["scientific_name"])
            #print(' iucnSci: '+iucnSci)
            # extract threatened category
            iucnCat = xstr(jsonA["result"][0]["category"])
            #print(' iucnCat: ' + iucnCat)
            
            # retrieve global narrative for species by id
            urlN = "http://apiv3.iucnredlist.org/api/v3/species/narrative/id/" + \
            str(intIucnID) + "?token=" + os.environ["IUCN_TOKEN"]
            jsonN = requests.get(urlN).json()
            #print(IUCNjsonN)
            # extract population trend
            iucnTnd = xstr(jsonN["result"][0]["populationtrend"])
            #print(' iucnTnd: ' + iucnTnd)
            
            # combine strings and append to file
            rowStr = strUC + ',' + strSciName + ',' + strComName + ',' + str(intIucnID) + ',' + iucnSci + ',' + iucnCom + ',' \
            + iucnCat + ',' + iucnTnd
            # data record - append to file, add data
            tblIUCN = open(home + 'tblIUCN.csv', 'ab')
            # create the csv writer object
            csvwriter = csv.writer(tblIUCN)
            csvwriter.writerow(rowStr.split(','))
            #csvwriter.writerow(JD.split())
            tblIUCN.close()
            
            # count up on index value
            rowNum += 1
    
    # close file
    tblIUCN.close()
    
    print('Processed '+str(rowNum-1)+' records')
    
    return (tblIUCN)

# =======================================================================
# Evaluate existance of output table and replace option, then implement

if os.path.exists(home + 'tblIUCN.csv') == False:
    print('tblIUCN.csv does not exist - creating...')
    iucnTable = buildIUCN()
elif replaceTable == 'yes':
    print('tblIUCN.csv exists - replacing...')
    os.remove(home + 'tblIUCN.csv')
    iucnTable = buildIUCN()
else:
    print('tblIUCN.csv exists - not replacing.')

