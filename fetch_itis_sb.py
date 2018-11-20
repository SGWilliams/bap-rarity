# -*- coding: utf-8 -*-
"""
fetch_itis_sb.py

enviroment: bis

Retrieves information from ITIS api to attach to SB Habitat Map item
   for species.
 
Created on Wed Oct 24 17:07:53 2018

@author: sgwillia
=======================================================================
"""
# Import gapconfig variables containing SB user/password
import sys
sys.path.append('C:/Code')
import gapconfig
# Import other packages
import bis
import requests
import json
import pandas as pd
import pysb
from io import StringIO

# =======================================================================
# LOCAL VARIABLES
home = "N:/Git_Repositories/fetchSppInfo/"
outDir = home + 'itis'

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

# =======================================================================
# GET SPP TABLE FROM SB HABMAP ITEM
sb = ConnectToSB()
habItem = sb.get_item("527d0a83e4b0850ea0518326")
for file in habItem["files"]:
    if file["name"] == "ScienceBaseHabMapCSV_20180713.csv":
        tbSpp = pd.read_csv(StringIO(sb.get(file["url"])))
   
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
        
    #print(strUC)
    #print('  ' + strSciName)
    #print('  ' + strComName)
    #print('  ' + str(intITIScode))
    #print('  ' + strSbHabID)

    if strUC == 'aFBSAx':  # set single or multiple spp to work on
        print('Working on '+strUC)
    
        # pull itis data down, 
        ITISstring = "http://services.itis.gov/?wt=json&q=tsn:{0}".format(intITIScode)
        url = bis.itis.getITISSearchURL(ITISstring,False,False)
        ITISjson = requests.get(url).json()
        # write to local file
        outJson = strUC + '_ITIS.json'
        pthJson = outDir + '/' + outJson       
        with open(pthJson, 'w') as jf:
            json.dump(ITISjson, jf)
        
        # attach json file to SB habitat item
        AttachFile(strUC, strSbHabID, pthJson)
        
        # add file title
        title = "ITIS Information"
        AddTitle(strUC, strSbHabID, outJson, title)
    
