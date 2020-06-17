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
# Figure7 - Ecoregion-Taxa-Protection Nationally

from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource
from bokeh.palettes import GnBu3, OrRd3
from bokeh.plotting import figure
from bokeh.transform import dodge

output_file("bar_stacked_split.html")
##############################################################################

from bokeh.models import FactorRange

output_file("bars.html")

fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']
years = ['2015', '2016', '2017']

data = {'fruits' : fruits,
        '2015'   : [2, 1, 4, 3, 2, 4],
        '2016'   : [5, 3, 3, 2, 4, 6],
        '2017'   : [3, 2, 4, 4, 5, 3]}

# this creates [ ("Apples", "2015"), ("Apples", "2016"), ("Apples", "2017"), ("Pears", "2015), ... ]
x = [ (fruit, year) for fruit in fruits for year in years ]
counts = sum(zip(data['2015'], data['2016'], data['2017']), ()) # like an hstack

source = ColumnDataSource(data=dict(x=x, counts=counts))

p = figure(x_range=FactorRange(*x), plot_height=250, title="Fruit Counts by Year",
           toolbar_location=None, tools="")

p.vbar(x='x', top='counts', width=0.9, source=source)

p.y_range.start = 0
p.x_range.range_padding = 0.1
p.xaxis.major_label_orientation = 1
p.xgrid.grid_line_color = None

show(p)

##############################################################################


fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']
years = ["2015", "2016", "2017"]

exports = {'fruits' : fruits,
           '2015'   : [20, 10, 40, 30, 20, 40],
           '2016'   : [50, 30, 40, 20, 40, 60],
           '2017'   : [30, 60, 20, 50, 40, 0]}
imports = {'fruits' : fruits,
           '2015'   : [10, 0, 10, 30, 20, 10],
           '2016'   : [20, 10, 30, 10, 20, 20],
           '2017'   : [70, 90, 60, 60, 60, 70]}

p = figure(y_range=fruits, plot_height=350, x_range=(0, 200), title="Fruit import/export, by year",
           toolbar_location=None)

p.hbar_stack(years, y='fruits', height=0.9, color=GnBu3, source=ColumnDataSource(exports),
             legend=["%s exports" % x for x in years])

p.hbar_stack(years, y='fruits', height=0.9, color=OrRd3, source=ColumnDataSource(imports),
             legend=["%s imports" % x for x in years])

p.y_range.range_padding = 0.1
p.ygrid.grid_line_color = None
p.legend.location = "top_right"
p.axis.minor_tick_line_color = None
p.outline_line_color = None

show(p)


##############################################################################
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
