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
from math import pi
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.models import ColumnDataSource, LabelSet
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

# generate graphic
output_file("fig2.html")

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
        outer_radius=0.25,
        start_angle=cumsum('angle', include_zero=True), 
        end_angle=cumsum('angle'),
        line_color="color", 
        fill_color='color', 
        source=dfTG)

p.annular_wedge(x=0, y=1, 
        inner_radius=0.25,
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
                  angle=(cumsum('angle', include_zero=True)), 
                  source=source, 
                  render_mode='canvas')

p.add_layout(labels)

p.axis.axis_label=None
p.axis.visible=False
p.grid.grid_line_color = None

show(p)


output_file("fig2.html")
