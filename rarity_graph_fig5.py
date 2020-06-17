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
import math
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
# Figure5 - Ecoregion-Taxa-Protection

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

## subset potentially rare
#dfES = dfES.loc[(dfES['potRare'] == 1)]

# create <17% protection column
def set17(row):
    if (row['SppPercProt'] <= 17):
        val = 'Not Protected (<= 17%)'
    else:
        val = 'Protected (> 17%)'
    return val    
dfES['lt17'] = dfES.apply(set17, axis=1)

# Create L2 Label column
dfES['L2'] = dfES['na_l2code'].astype(str) + ' - ' + dfES['na_l2name']

# sum by lt17
dfSG = dfES.groupby(['na_l2code', 
                     'L2', 
                     'Taxa', 
                     'lt17']).size().reset_index(name='count')
# pivot the table
dfSGp = pd.pivot_table(dfSG, 
                       values = 'count', 
                       index=['na_l2code', 'L2', 'Taxa'], 
                       columns = 'lt17').reset_index()
# add zeros where Nan
dfSGp['Not Protected (<= 17%)'] = dfSGp['Not Protected (<= 17%)'].fillna(0)
dfSGp['Protected (> 17%)'] = dfSGp['Protected (> 17%)'].fillna(0)
#dfSGp.to_csv(home + 'tmpSGp.csv', index=False)

# sort by L2, Taxa
dfSGp = dfSGp.sort_values(by=['na_l2code', 'Taxa'], ascending=False)

# find upper limit of x-axis
dfSGp['max'] = dfSGp['Protected (> 17%)'] + dfSGp['Not Protected (<= 17%)']
def roundup(x):
    return int(math.ceil(x / 50.0)) * 50
maxCnt = roundup(dfSGp['max'].max())

# set colors for taxa
def setColor(row):
    if (row['Taxa'][:1] == 'A'):
        val = '#5b9bd5'
    elif (row['Taxa'][:1] == 'B'):
        val = '#ff9900'
    elif (row['Taxa'][:1] == 'M'):
        val = '#ff5050'
    elif (row['Taxa'][:1] == 'R'):
        val = '#00b050'
    else:
        val = '#000000'
    return val    
dfSGp['color'] = dfSGp.apply(setColor, axis=1)

# generate graphics
output_file("fig5.html")

dfSGp['y'] = list(zip(dfSGp.L2, dfSGp.Taxa))
subgroups = ['Protected (> 17%)', 'Not Protected (<= 17%)']
factors = dfSGp.y.unique()
source = ColumnDataSource(dfSGp)

p = figure(y_range=FactorRange(*factors), 
           plot_height=1200,
           plot_width=1000,
           toolbar_location=None, 
           tools="")

p.hbar_stack(subgroups, 
             y='y', 
             height=0.9, 
             alpha=1.0, 
             hatch_pattern=[" ", "\\"], 
             line_color="black", 
             fill_color='color', 
             source=source,
             legend=[value(y) for y in subgroups])

p.x_range.start = 0
p.x_range.end = maxCnt
p.y_range.range_padding = 0.1
#p.yaxis.major_label_orientation = 1
p.yaxis.group_label_orientation = 'horizontal'
p.yaxis.group_text_color = 'black'

p.ygrid.grid_line_color = None
p.legend.location = "top_center"
p.legend.orientation = "horizontal"


show(p)
output_file("fig5.html")
