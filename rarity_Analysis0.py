# -*- coding: utf-8 -*-
"""
rarity_Analysis.py

enviroment: base 2.7

Output are ...
 
Created on 19dec2018

@author: sgwillia
=======================================================================
"""
# IMPORT PACKAGES
import sys
import socket
import pandas as pd
import pandas.io.sql as psql
import numpy as np
import os.path

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

tblAmph = home + 'tblRarityAmph.csv'
tblBird = home + 'tblRarityBird.csv'
tblMamm = home + 'tblRarityMamm.csv'
tblRept = home + 'tblRarityRept.csv'

# =======================================================================
# Open rarity_GapAnalyticDB.py output
dfSql = pd.read_csv(tblAmph, dtype=str)
dtypes = {"hucPix": np.int64,
          "ecoPix": np.int64, 
          "gs1SppPix": np.int64, 
          "gs2SppPix": np.int64, 
          "gs3SppPix": np.int64, 
          "gs4SppPix": np.int64, 
          "totalSppPix": np.int64}
for col, col_type in dtypes.items():
    dfSql[col] = dfSql[col].astype(col_type)

# Calc percent use for spp/huc combinations
dfSql['percUse'] = (dfSql['totalSppPix']/dfSql['hucPix'])*100





dfSql.iloc[100]

