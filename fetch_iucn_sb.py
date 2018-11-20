# -*- coding: utf-8 -*-
"""
fetch_iucn_sb.py

enviroment: 2.7

Retrieves IUCN information from IUCN api to attach to SB Habitat Map item.

 
Created on Mon Nov 5 13:21:53 2018

@author: sgwillia
=======================================================================
"""
# Import gapconfig variables containing SB user/password
import sys
sys.path.append('C:/Code')
import gapconfig
# Import other packages
import requests
import pandas as pd
import pysb
from io import StringIO
import os

# =======================================================================
# LOCAL VARIABLES
home = "N:/Git_Repositories/fetchSppInfo/"
outDir = home + 'iucn'

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

    sb = pysb.SbSession()
    sb.login(username, password)
    return sb

## -------------------Attach file to ScienceBase Item---------------
def AttachFile(sppCode, itemID, filePath):
    '''
    Uploads a file to a species' habitat map ScienceBase item. Returns the
        ID of the item that it attached to. Replaces it if already present.
    
    Arguments:
    sppCode -- gap spp code
    itemID -- sciencebase item id
    filePath -- path to the file
    '''

    try:
        # Connect to ScienceBase
        #sb = ConnectToSB()
        
        # Get the species item
        sppItem = sb.get_item(itemID)
        
        # Establish if file present
        filePres = 0
        fileName = filePath[-16:]
        files = sppItem["files"]
        for f in files:
            if f["name"].find(fileName) > -1:
                filePres = 1
      
        # Upload the file
        if filePres == 1:
            print("file exists - replacing")
            sb.replace_file(filePath, sppItem)
        elif filePres == 0:
            print("file does not exists - creating")
            sb.upload_file_to_item(sppItem, filePath, scrape_file=False)
                
        # Return the SppCode and SbID
        sppID = sppCode + ' : ' + itemID
        return sppID
    
    except Exception as e:
        print(e)
        return False

## -------------------Add Title to Attached File---------------
def AddTitle(sppCode, itemID, fileName, fileTitle):
    '''
    Add a Title to a file attached to an SB Item.
    
    Arguments:
    sppCode -- gap spp code
    itemID -- sciencebase item id
    fileName -- name of file attached to item
    title -- title string
    '''

    try:
        # Connect to ScienceBase
        #sb = ConnectToSB()
        
        # Get the species item
        sppItem = sb.get_item(itemID)     

        # add title to itis json file
        files = sppItem["files"]
        for f in files:
            # update the description of the attached file
            if f["name"].find(fileName) > -1:
                #print('found: '+ fileName)
                f["title"] = fileTitle
            sb.update_item(sppItem)
                
        # Return the SppCode and SbID
        sppID = sppCode + ' : ' + itemID
        return sppID
    
    except Exception as e:
        print(e)
        return False
    
## -------------Replace null variables with empty string-----------------
def xstr(s):
    if s is None:
        return ''
    return str(s)

# =======================================================================
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
cols = cols.map(lambda x: x.replace(' ', '_') if isinstance(x, (str, unicode)) else x)
tbSpp.columns = cols
# =======================================================================
# SET UP LOOP ON SPECIES
# Iterate through table
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

    if strUC < 'aANAAx':  # reset sppCode if script fails along the way
        print('Working on '+strUC)
        
        # pull iucn data down, ?????????????????????, reformat and create json
        '''
        Red List
        Population Trend (decreasing, stable/increasing)
        Threatened Categories (critical CR, endangered EN, vulnerable VU) characterized as decreasing even if IUCN
          population trend was stable or unknown.
        Geographic Range (derived from AnalyticDB)
        Habitat Breadth (derived from AnalyticDB)
        {
         isocode: "US",
         country: "United States"
        }
        /api/v3/version                                             # api version
        /api/v3/country/getspecies/US?token='YOUR TOKEN'            # spp by US
        /api/v3/species/citation/:name?token='YOUR TOKEN'           # global spp citation
        /api/v3/species/id/:id?token='YOUR TOKEN'                   # global assessment via ID
        '''
        # retrieve global assessment for species by id
        urlA = "http://apiv3.iucnredlist.org/api/v3/species/id/"+str(intIucnID)+"?token="+os.environ["IUCN_TOKEN"]
        IUCNjsonA = requests.get(urlA).json()
        #print(IUCNjsonA)
        # extract species common name and compare to GAP common name
        IUCNcom = xstr(IUCNjsonA["result"][0]["main_common_name"])
        print(' GAPcom: '+strComName)
        print(' IUCNcom: '+IUCNcom)   
        # extract threatened category
        IUCNcat = xstr(IUCNjsonA["result"][0]["category"])
        print(' IUCNcat: '+IUCNcat)
        
        # retrieve global narrative for species by id
        urlN = "http://apiv3.iucnredlist.org/api/v3/species/narrative/id/"+str(intIucnID)+"?token="+os.environ["IUCN_TOKEN"]
        IUCNjsonN = requests.get(urlN).json()
        #print(IUCNjsonN)
        # extract population trend
        IUCNtnd = xstr(IUCNjsonN["result"][0]["populationtrend"])
        print(' IUCNtnd: '+IUCNtnd)
    
#    sppName = 'Trogon elegans'
#    url = "http://apiv3.iucnredlist.org/api/v3/species/"+sppName+"?token="+os.environ["IUCN_TOKEN"]
#    IUCNjson = requests.get(url).json()
#    taxonId = IUCNjson["result"][0]["taxonid"]
#    comName = IUCNjson["result"][0]["main_common_name"]
#    sciName = IUCNjson["result"][0]["scientific_name"]
#    authori = IUCNjson["result"][0]["authority"]
#    #print(IUCNjson)
#    print('')
#    print('taxonId: '+str(taxonId))
#    print('comName: '+comName)
#    print('sciName: '+sciName)
#    print('authority: '+authori)

    
    
