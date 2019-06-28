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

'''
#####################################
# FIGURE 2 - NationalGroup Distribution

# open national summary table
dfNS = pd.read_csv(home + 'tblNatSumm.csv')

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
dfNS['Taxa'] = dfNS.apply(setTaxa, axis=1)

# remove Group X
dfNS = dfNS.loc[dfNS['Group'] != 'X']

# Create TG columns
dfNS['TG'] = dfNS['Taxa'] + '/Group ' + dfNS['Group']

# sum by Taxa/Group
dfTG = dfNS.groupby(['Taxa', 'Group', 'TG']).size().reset_index(name='Number')

# import graphics components
from math import pi
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.models import LabelSet, ColumnDataSource, FactorRange
from bokeh.core.properties import value

output_file("fig3.html")

# setup TG graphics
dfTG['angle'] = dfTG['Number']/dfTG['Number'].sum() * 2*pi
# set colors
def setColor(row):
    if (row['TG'][:1] == 'A'):
        val = '#5b9bd5'
    elif (row['TG'][:1] == 'B'):
        val = '#ff9900'
    elif (row['TG'][:1] == 'M'):
        val = '#ff5050'
    elif (row['TG'][:1] == 'R'):
        val = '#00b050'
    else:
        val = '#000000'
    return val    
dfTG['color'] = dfTG.apply(setColor, axis=1)

p = figure(plot_height=500, 
           title="Figure 3", 
           toolbar_location=None,
           tools="hover", 
           tooltips="@TG: @Number", 
           x_range=(-0.5, 1.0))

p.annular_wedge(x=0, y=1, 
        inner_radius=0.1,
        outer_radius=0.4,
        start_angle=cumsum('angle', include_zero=True), 
        end_angle=cumsum('angle'),
        line_color="white", 
        fill_color='color', 
        legend='Taxa', 
        source=dfTG)

dfTG['Group'] = dfTG['Group'].str.pad(33, side = 'left')
source = ColumnDataSource(dfTG)

labels = LabelSet(x=0, y=1, 
                  text='Group', 
                  level='annotation',
                  angle=cumsum('angle', include_zero=True), 
                  source=source, 
                  render_mode='canvas')

p.add_layout(labels)

p.axis.axis_label=None
p.axis.visible=False
p.grid.grid_line_color = None

show(p)
'''

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

# pivot the table
dfSGp = pd.pivot_table(dfSG, values = 'count', index=['na_l2code', 'L2', 'Taxa'], columns = 'Subgroup').reset_index()
#dfSGp.to_csv(home + 'tmpSGp.csv', index=False)

'''#####################################
# generate horizontal stacked bar chart

output_file("bar_stacked.html")

# create data
fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']
years = ["2015", "2016", "2017"]
colors = ["#c9d9d3", "#718dbf", "#e84d60"]

data = {'fruits' : fruits,
        '2015'   : [2, 1, 4, 3, 2, 4],
        '2016'   : [5, 3, 4, 2, 4, 6],
        '2017'   : [3, 2, 4, 4, 5, 3]}

source = ColumnDataSource(data)

p = figure(y_range=fruits, 
           plot_height=500,
           title="Fruit Counts by Year",
           toolbar_location=None,
           tools="hover",
           tooltips="name @fruites: @$name")

p.hbar_stack(years, y='fruits', height=0.9, source=source, color=colors)

show(p)
output_file("stacked.html")


################################
output_file("hierbars.html")

fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']
years = ['2015', '2016', '2017']

data = {'fruits' : fruits,
        '2015'   : [2, 1, 4, 3, 2, 4],
        '2016'   : [5, 3, 3, 2, 4, 6],
        '2017'   : [3, 2, 4, 4, 5, 3]}

# this creates [ ("Apples", "2015"), ("Apples", "2016"), ("Apples", "2017"), ("Pears", "2015), ... ]
y = [ (fruit, year) for fruit in fruits for year in years ]
counts = sum(zip(data['2015'], data['2016'], data['2017']), ()) # like an hstack

source = ColumnDataSource(data=dict(y=y, counts=counts))

p = figure(y_range=FactorRange(*y), plot_height=500, title="Fruit Counts by Year",
           toolbar_location=None, tools="")

p.hbar(y='y', right='counts', height=0.9, source=source)

p.x_range.start = 0
p.y_range.range_padding = 0.1
#p.yaxis.major_label_orientation = 1
p.ygrid.grid_line_color = None

show(p)

################################
output_file("bar_stacked_grouped.html")

#factors = [
#    ("Q1", "jan"), ("Q1", "feb"), ("Q1", "mar"),
#    ("Q2", "apr"), ("Q2", "may"), ("Q2", "jun"),
#    ("Q3", "jul"), ("Q3", "aug"), ("Q3", "sep"),
#    ("Q4", "oct"), ("Q4", "nov"), ("Q4", "dec"),
#]

regions = ['east', 'west']

#source = ColumnDataSource(data=dict(
#    y=factors,
#    east=[ 5, 5, 6, 5, 5, 4, 5, 6, 7, 8, 6, 9 ],
#    west=[ 5, 7, 9, 4, 5, 4, 7, 7, 7, 6, 6, 7 ],
#))

data=dict(
    qtr=[ 'Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2', 'Q3', 'Q3', 'Q3', 'Q4', 'Q4', 'Q4' ],
    mon=[ 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec' ],
    east=[ 5, 5, 6, 5, 5, 4, 5, 6, 7, 8, 6, 9 ],
    west=[ 5, 7, 9, 4, 5, 4, 7, 7, 7, 6, 6, 7 ]
)
dfData = pd.DataFrame.from_dict(data)
dfData['y'] = list(zip(dfData.qtr, dfData.mon))
factors = dfData.y.unique()
source = ColumnDataSource(dfData)


p = figure(y_range=FactorRange(*factors), plot_height=500,
           toolbar_location=None, tools="")

p.hbar_stack(regions, y='y', height=0.9, alpha=0.5, color=["blue", "red"], source=source,
             legend=[value(y) for y in regions])

p.x_range.start = 0
p.x_range.end = 18
p.y_range.range_padding = 0.1
p.yaxis.major_label_orientation = 1
p.ygrid.grid_line_color = None
p.legend.location = "center_right"
p.legend.orientation = "vertical"

show(p)
'''
############
# import graphics components
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.core.properties import value

output_file("bar_stacked_grouped.html")

dfSGp['y'] = list(zip(dfSGp.L2, dfSGp.Taxa))
subgroups = ['DD', 'TR']
factors = dfSGp.y.unique()
source = ColumnDataSource(dfSGp)

p = figure(y_range=FactorRange(*factors), 
           plot_height=1000,
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
p.x_range.end = 118
p.y_range.range_padding = 0.1
#p.yaxis.major_label_orientation = 1
p.ygrid.grid_line_color = None
p.legend.location = "center_right"
p.legend.orientation = "vertical"

show(p)
####################################
#listL2 = dfSGp.L2.unique()
#listTaxa = dfSGp.Taxa.unique()
#y = [ (L2, Taxa) for L2 in listL2 for Taxa in listTaxa ]
