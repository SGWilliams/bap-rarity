# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 12:00:17 2019

@author: sgwillia
=======================================================================
"""
# IMPORT PACKAGES
import sys
import socket
import pandas as pd
# import graphics components
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.core.properties import value
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

#####################################
# Figure3 - Ecoregion

# open ecoregional summary table
dfES = pd.read_csv(home + 'tblEcoSumm.csv')

# create taxa column
def setTaxa(row):
    if (row['gapSppCode'][:1] == 'a'):
        val = 'Amphibian'
    elif (row['gapSppCode'][:1] == 'b'):
        val = 'Bird'
    elif (row['gapSppCode'][:1] == 'm'):
        val = 'Mammal'
    elif (row['gapSppCode'][:1] == 'r'):
        val = 'Reptile'
    else:
        val = 'X'
    return val    
dfES['Taxa'] = dfES.apply(setTaxa, axis=1)

# subset Group TR and DD
dfES = dfES.loc[(dfES['Subgroup'] == 'TR') | (dfES['Subgroup'] == 'DD')]

# Create L2 Label column
dfES['L2'] = dfES['na_l2code'].astype(str) + ' - ' + dfES['na_l2name']

# sum by Subgroup
dfSG = dfES.groupby(['na_l2code', 'L2', 'Taxa', 'Subgroup']).size().reset_index(name='count')
maxCnt = dfSG['count'].max()

# pivot the table
dfSGp = pd.pivot_table(dfSG, values = 'count', index=['na_l2code', 'L2', 'Taxa'], columns = 'Subgroup').reset_index()
#dfSGp.to_csv(home + 'tmpSGp.csv', index=False)


output_file("fig3.html")

dfSGp['y'] = list(zip(dfSGp.L2, dfSGp.Taxa))
subgroups = ['DD', 'TR']
factors = dfSGp.y.unique()
source = ColumnDataSource(dfSGp)

p = figure(y_range=FactorRange(*factors), 
           plot_height=1000,
           plot_width=1200,
           toolbar_location=None, 
           tools="")

p.hbar_stack(subgroups, 
             y='y', 
             height=0.9, 
             alpha=0.5, 
             color=["blue", "red"], 
             source=source,
             legend=[value(y) for y in subgroups])

p.x_range.start = 0
p.x_range.end = maxCnt
p.y_range.range_padding = 0.1
#p.yaxis.major_label_orientation = 1
p.yaxis.group_label_orientation = 6
#p.yaxis.group_text = 'wrap'

p.ygrid.grid_line_color = None
p.legend.location = "center_right"
p.legend.orientation = "vertical"

show(p)
output_file("fig3.html")
