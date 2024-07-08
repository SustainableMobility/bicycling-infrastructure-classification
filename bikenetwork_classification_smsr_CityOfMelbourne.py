# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 11:34:28 2023

@author: dbho0002
"""

#%% Step: Import modules
import geopandas as gpd
import osmnx as ox
import networkx as nx
from shapely.geometry import shape
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points
import geojson
import pandas as pd
import numpy as np
import math
import time
from pathlib import Path
# from gpx_converter import Converter
from leuvenmapmatching.util.gpx import gpx_to_path
import pyproj
# import functions
pd.set_option('display.max_columns', 500)
import warnings
warnings.filterwarnings('ignore')
import ast

import sys, os, os.path
os.environ['HTTP_PROXY'] = 'serp-proxy.erc.monash.edu:3128'

#%% Step: Import boundary data
#Convert study area polygon to shapely multipolygon
# with open('GreaterMelbourne_polygon.geojson') as f:
#     gj = geojson.load(f)
with open('CityOfMelbourne_municipal-boundary.geojson') as f:
    gj = geojson.load(f)
# polygon = shape(gj)
# polygon = shape(gj['geometries'][0]) ##varies across sources from where boundary file is obtained
polygon = shape(gj['features'][0]['geometry']) ##varies across sources from where boundary file is obtained

#%% Step: Import graphs and join

bike_filter_1 = '[~"highway"~"cycleway|trunk|primary|secondary|tertiary|unclassified|residential|primary_link|secondary_link|tertiary_link|living_street|trailhead|service"]["access"!~"no|private"]["bicycle"!~"no"]["area"!~"yes"]'
G1 = ox.graph.graph_from_polygon(polygon, custom_filter = bike_filter_1, simplify = False, retain_all=True)
# G_nodes, G_edges = ox.graph_to_gdfs(G)

bike_filter_2 = '[~"highway"~"footway|pedestrian|path"]["bicycle"~"yes|designated|dismount"]["area"!~"yes"]'
G2 = ox.graph.graph_from_polygon(polygon, custom_filter = bike_filter_2, simplify = False, retain_all=True)

G = nx.compose(G1, G2)
G_nodes, G_edges = ox.graph_to_gdfs(G, nodes=True, edges=True)

#%% Modified SMSR classification

G_edges['bike_inf_smsr'] = '1. mixed traffic'

###BICYCLISTS DISMOUNT
G_edges.loc[G_edges['bicycle'].isin(['dismount']) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '0a. bicyclists dismount'  

###BIKEPATH
##comment out following 1 line for City of Melbourne
# G_edges.loc[G_edges['route'].isin(['mtb']) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '9. dedicated bikepath'
G_edges.loc[G_edges['highway'].isin(['cycleway']) & G_edges['foot'].isin(['no']) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '9. dedicated bikepath'
G_edges.loc[G_edges['highway'].isin(['path']) & G_edges['bicycle'].isin(['yes','designated']) & G_edges['foot'].isin(['no']) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '9. dedicated bikepath'    

###SHARED PATH
G_edges.loc[G_edges['highway'].isin(['cycleway']) & ~G_edges['foot'].isin(['no']) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '8b. shared bikepath'
G_edges.loc[G_edges['highway'].isin(['path']) & G_edges['bicycle'].isin(['yes','designated']) & ~G_edges['foot'].isin(['no']) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '8b. shared bikepath' 

###PEDESTRIAN PATH WITH CYCLING ALLOWED   
G_edges.loc[G_edges['highway'].isin(['footway','pedestrian']) & G_edges['bicycle'].isin(['yes','designated']) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '8a. pedestrian path/street with cycling allowed'    

###PEDESTRIAN PATH WITH CYCLING NOT ALLOWED
G_edges.loc[G_edges['highway'].isin(['footway','pedestrian','path']) & ~G_edges['bicycle'].isin(['yes','designated']) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '0b. pedestrian path/street with cycling not allowed'  

###PROTECTED BIKELANE
G_edges.loc[~G_edges['highway'].isin(['cycleway']) & (G_edges['cycleway'].isin(['track','opposite_track']) | G_edges['cycleway:left'].isin(['track']) | G_edges['cycleway:right'].isin(['track']) | G_edges['cycleway:both'].isin(['track'])) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '7. protected bikelane'
#added for st kilda rd protected lanes
G_edges.loc[G_edges['highway'].isin(['cycleway']) & (G_edges['name'].str.contains("Road|Street")==True), 'bike_inf_smsr'] = '7. protected bikelane'


###BUFFERED BIKELANE (BOTH SIDES)
G_edges.loc[G_edges['cycleway:both'].isin(['lane'])
            & (G_edges['cycleway:both:lane'].isin(['exclusive']) | G_edges['cycleway:left:lane'].isin(['exclusive']))
            & ((~G_edges['cycleway:left:buffer:both'].isna() | ~G_edges['cycleway:both:buffer:both'].isna()) | (~G_edges['cycleway:left:buffer:left'].isna() & ~G_edges['cycleway:left:buffer:right'].isna())
            | (~G_edges['cycleway:both:buffer:left'].isna() & ~G_edges['cycleway:both:buffer:right'].isna())) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '6c. buffered lane (both sides)'

G_edges.loc[G_edges['cycleway:left'].isin(['lane']) & G_edges['cycleway:left:lane'].isin(['exclusive'])
            & ((~G_edges['cycleway:left:buffer:left'].isna() & ~G_edges['cycleway:left:buffer:right'].isna()) | ~G_edges['cycleway:left:buffer:both'].isna())
            & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '6c. buffered lane (both sides)'

###BUFFERED BIKELANE (KERB-SIDE)
G_edges.loc[G_edges['cycleway:both'].isin(['lane'])
            & (G_edges['cycleway:both:lane'].isin(['exclusive']) | G_edges['cycleway:left:lane'].isin(['exclusive']))
            & (~G_edges['cycleway:left:buffer:left'].isna() | ~G_edges['cycleway:both:buffer:left'].isna())
            & ~(~G_edges['cycleway:left:buffer:right'].isna() | ~G_edges['cycleway:both:buffer:right'].isna()) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '6a. buffered bikelane (kerb-side)'

G_edges.loc[G_edges['cycleway:left'].isin(['lane'])
            & G_edges['cycleway:left:lane'].isin(['exclusive']) & ~G_edges['cycleway:left:buffer:left'].isna()
            & G_edges['cycleway:left:buffer:right'].isna() & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '6a. buffered bikelane (kerb-side)'

###BUFFERED BIKELANE (ROAD-SIDE)
G_edges.loc[G_edges['cycleway:both'].isin(['lane'])
            & (G_edges['cycleway:both:lane'].isin(['exclusive']) | G_edges['cycleway:left:lane'].isin(['exclusive']))
            & (~G_edges['cycleway:left:buffer:right'].isna() | ~G_edges['cycleway:both:buffer:right'].isna())
            & ~(~G_edges['cycleway:left:buffer:left'].isna() | ~G_edges['cycleway:both:buffer:left'].isna()) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '6b. buffered bikelane (road-side)'

G_edges.loc[G_edges['cycleway:left'].isin(['lane'])
            & G_edges['cycleway:left:lane'].isin(['exclusive']) & ~G_edges['cycleway:left:buffer:right'].isna()
            & G_edges['cycleway:left:buffer:left'].isna() & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '6b. buffered bikelane (road-side)'


###PAINTED BIKELANE
G_edges.loc[~G_edges['highway'].isin(['cycleway']) & (G_edges['cycleway'].isin(['lane','opposite_lane']) | G_edges['cycleway:left'].isin(['lane'])
                                                      | G_edges['cycleway:right'].isin(['lane']) | G_edges['cycleway:both'].isin(['lane'])) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '5e. painted bikelane'

###PAINTED BIKELANE (SINGLE SIDE)
G_edges.loc[((G_edges['cycleway:left'].isin(['lane']) & G_edges['cycleway:right'].isin(['no']))
            | (G_edges['cycleway:right'].isin(['lane']) & G_edges['cycleway:left'].isin(['no']))) & G_edges['bike_inf_smsr'].isin(['5e. painted bikelane']), 'bike_inf_smsr'] = '5d. painted bikelane (single side)'

###ADVISORY BIKELANE
G_edges.loc[G_edges['cycleway:both'].isin(['lane']) & (G_edges['cycleway:both:lane'].isin(['advisory']) | G_edges['cycleway:left:lane'].isin(['advisory'])) & G_edges['bike_inf_smsr'].isin(['5e. painted bikelane','5d. painted bikelane (single side)']), 'bike_inf_smsr'] = '5c. advisory bikelane'
G_edges.loc[G_edges['cycleway:left'].isin(['lane']) & G_edges['cycleway:left:lane'].isin(['advisory']) & G_edges['bike_inf_smsr'].isin(['5e. painted bikelane','5d. painted bikelane (single side)']), 'bike_inf_smsr'] = '5c. advisory bikelane'

###ADVISORY BIKELANE (SINGLE SIDE)
G_edges.loc[G_edges['cycleway:left'].isin(['lane']) & G_edges['cycleway:right'].isin(['no']) & G_edges['cycleway:left:lane'].isin(['advisory']) & G_edges['bike_inf_smsr'].isin(['5c. advisory bikelane']), 'bike_inf_smsr'] = '5b. advisory bikelane (single side)' 

###PEAK HOUR BIKELANE
##comment out following 4 lines for City of Melbourne
# G_edges.loc[(~G_edges['cycleway:both:conditional'].isna() | ~G_edges['cycleway:left:conditional'].isna() | ~G_edges['cycleway:both:lane:conditional'].isna() | ~G_edges['cycleway:left:lane:conditional'].isna()) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic','5e. painted bikelane']), 'bike_inf_smsr'] = '5a. peak hour painted bikelane'
# G_edges.loc[(~G_edges['cycleway:both:conditional'].isna() | ~G_edges['cycleway:left:conditional'].isna() | ~G_edges['cycleway:both:lane:conditional'].isna() | ~G_edges['cycleway:left:lane:conditional'].isna()) & G_edges['bike_inf_smsr'].isin(['5d. painted bikelane (single side)']), 'bike_inf_smsr'] = '5a. peak hour painted bikelane (single side)'
# G_edges.loc[(~G_edges['cycleway:both:conditional'].isna() | ~G_edges['cycleway:left:conditional'].isna() | ~G_edges['cycleway:both:lane:conditional'].isna() | ~G_edges['cycleway:left:lane:conditional'].isna()) & G_edges['bike_inf_smsr'].isin(['5c. advisory bikelane']), 'bike_inf_smsr'] = '5a. peak hour advisory bikelane'
# G_edges.loc[(~G_edges['cycleway:both:conditional'].isna() | ~G_edges['cycleway:left:conditional'].isna() | ~G_edges['cycleway:both:lane:conditional'].isna() | ~G_edges['cycleway:left:lane:conditional'].isna()) & G_edges['bike_inf_smsr'].isin(['5b. advisory bikelane (single side)']), 'bike_inf_smsr'] = '5a. peak hour advisory bikelane (single side)'
##comment out following 4 lines for Greater Melbourne
G_edges.loc[(~G_edges['cycleway:left:conditional'].isna() | ~G_edges['cycleway:left:lane:conditional'].isna()) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic','5e. painted bikelane']), 'bike_inf_smsr'] = '5a. peak hour painted bikelane'
G_edges.loc[(~G_edges['cycleway:left:conditional'].isna() | ~G_edges['cycleway:left:lane:conditional'].isna()) & G_edges['bike_inf_smsr'].isin(['5d. painted bikelane (single side)']), 'bike_inf_smsr'] = '5a. peak hour painted bikelane (single side)'
G_edges.loc[(~G_edges['cycleway:left:conditional'].isna() | ~G_edges['cycleway:left:lane:conditional'].isna()) & G_edges['bike_inf_smsr'].isin(['5c. advisory bikelane']), 'bike_inf_smsr'] = '5a. peak hour advisory bikelane'
G_edges.loc[(~G_edges['cycleway:left:conditional'].isna() | ~G_edges['cycleway:left:lane:conditional'].isna()) & G_edges['bike_inf_smsr'].isin(['5b. advisory bikelane (single side)']), 'bike_inf_smsr'] = '5a. peak hour advisory bikelane (single side)'


###SHARROW
G_edges.loc[~G_edges['highway'].isin(['cycleway']) & G_edges['cycleway'].isin(['shared_lane']) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '4b. sharrow'
G_edges.loc[G_edges['cycleway:both'].isin(['shared_lane']) & (G_edges['cycleway:both:lane'].isin(['pictogram']) | G_edges['cycleway:left:lane'].isin(['pictogram'])) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '4b. sharrow'
G_edges.loc[G_edges['cycleway:left'].isin(['shared_lane']) & G_edges['cycleway:left:lane'].isin(['pictogram']) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '4b. sharrow'
G_edges.loc[G_edges['cycleway:right'].isin(['shared_lane']) & G_edges['cycleway:left'].isin(['no']) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '4b. sharrow'

###SHARED ZONE  
G_edges.loc[G_edges['highway'].isin(['living_street']) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '4a. shared zone'

###SHARED BUS LANE
G_edges.loc[(G_edges['cycleway:both'].isin(['share_busway','opposite_share_busway']) | G_edges['cycleway:left'].isin(['share_busway','opposite_share_busway'])) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '3. bus lane with cycling allowed'

###SHOULDER CYCLABLE
G_edges.loc[G_edges['cycleway:both'].isin(['shoulder']) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '2. shoulder cyclable'
G_edges.loc[G_edges['cycleway:left'].isin(['shoulder']) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '2. shoulder cyclable'

###OTHERS
## roads which have associated bike lanes (usually protected) which are mapped separately, should not be classified as mixed traffic.
## However, it is not trivial to detect the associated bike lane/infrastructure type.
## Also, given that infrastructure is separately mapped and is classified already, it could cause duplication issues.
## Thus, we have decided to classify roads with associated bike infra mapped separately in a new category '0b. Associated bike infrastructure separately mapped'

G_edges.loc[G_edges['cycleway'].isin(['separate']) & G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_smsr'] = '0b. Associated bike infrastructure separately mapped'

print()
print('Number of edges by infrastructure type')
print(G_edges['bike_inf_smsr'].value_counts().sort_index())
print()
print('Total length in kms by infrastructure type')
print(G_edges[['length','bike_inf_smsr']].groupby(['bike_inf_smsr']).sum()/1000)
#%%
###ASSIGN BIKE INFRA SUPERCLASS

G_edges['bike_inf_superclass'] = ''

G_edges.loc[G_edges['bike_inf_smsr'].isin(['9. dedicated bikepath']), 'bike_inf_superclass'] = 'dedicated bikepath'
G_edges.loc[G_edges['bike_inf_smsr'].isin(['8b. shared bikepath']), 'bike_inf_superclass'] = 'shared bikepath'
G_edges.loc[G_edges['bike_inf_smsr'].isin(['8a. pedestrian path/street with cycling allowed']), 'bike_inf_superclass'] = 'pedestrian path/street with cycling allowed'
G_edges.loc[G_edges['bike_inf_smsr'].isin(['7. protected bikelane']), 'bike_inf_superclass'] = 'protected bikelane'
G_edges.loc[G_edges['bike_inf_smsr'].isin(['6a. buffered bikelane (kerb-side)','6b. buffered bikelane (road-side)','6c. buffered lane (both sides)']), 'bike_inf_superclass'] = 'buffered bikelane'
G_edges.loc[G_edges['bike_inf_smsr'].isin(['5d. painted bikelane (single side)','5e. painted bikelane']), 'bike_inf_superclass'] = 'painted bikelane'
G_edges.loc[G_edges['bike_inf_smsr'].isin(['5b. advisory bikelane (single side)','5c. advisory bikelane']), 'bike_inf_superclass'] = 'advisory bikelane'
G_edges.loc[G_edges['bike_inf_smsr'].isin(['5a. peak hour advisory bikelane','5a. peak hour advisory bikelane (single side)','5a. peak hour painted bikelane','5a. peak hour painted bikelane (single side)']), 'bike_inf_superclass'] = 'peak hour bikelane'
G_edges.loc[G_edges['bike_inf_smsr'].isin(['4b. sharrow']), 'bike_inf_superclass'] = 'sharrow'
G_edges.loc[G_edges['bike_inf_smsr'].isin(['4a. shared zone']), 'bike_inf_superclass'] = 'shared zone'
G_edges.loc[G_edges['bike_inf_smsr'].isin(['3. bus lane with cycling allowed']), 'bike_inf_superclass'] = 'bus lane with cycling allowed'
G_edges.loc[G_edges['bike_inf_smsr'].isin(['2. shoulder cyclable']), 'bike_inf_superclass'] = 'shoulder cyclable'
G_edges.loc[G_edges['bike_inf_smsr'].isin(['0a. bicyclists dismount','0b. pedestrian path/street with cycling not allowed']), 'bike_inf_superclass'] = 'bicycling not allowed'
G_edges.loc[G_edges['bike_inf_smsr'].isin(['1. mixed traffic']), 'bike_inf_superclass'] = 'mixed traffic'
G_edges.loc[G_edges['bike_inf_smsr'].isin(['0b. Associated bike infrastructure separately mapped']), 'bike_inf_superclass'] = 'Associated bike infrastructure separately mapped'

print()
print('Number of edges by infrastructure type')
print(G_edges['bike_inf_superclass'].value_counts().sort_index())
print()
print('Total length in kms by infrastructure type')
print(G_edges[['length','bike_inf_superclass']].groupby(['bike_inf_superclass']).sum()/1000)
#%%

# test = G_edges[G_edges['name'].str.contains("St Kilda Road")==True]

#%% Step: Compose graph from modified geodataframes, project graph if necessary (for mapmatching) and save in desired format 
      
G = ox.utils_graph.graph_from_gdfs(G_nodes, G_edges)

att_list = ['geometry']
for n1, n2, d in G.edges(data=True):
    for att in att_list:
        d.pop(att, None)

##Simplify graph if necessary
# G_simplified = ox.simplification.simplify_graph(G)
# G_simp_nodes, G_simp_edges = ox.graph_to_gdfs(G_simplified, nodes=True, edges=True)

##Project graph if necessary
# G_proj = ox.project_graph(G, to_crs={'init':'epsg:32755'})

##Save in desired format
# G_edges.to_csv('COM_edges_with_bike_infra_class_dtp_smsr_ecf.csv')
G_edges.to_csv('COM_edges_with_bike_infra_class_smsr_v2.csv')
# ox.io.save_graph_geopackage(G, filepath = 'GMEL_bikeinfra_smsr_dtp_ecf.gpkg', directed=True)
# ox.io.save_graph_geopackage(G_proj, filepath = 'GMEL_bikeinfra_smsr_dtp_ecf_32755.gpkg')
ox.io.save_graph_geopackage(G, filepath = 'COM_bikeinfra_smsr_v2.gpkg', directed=True)
# ox.io.save_graph_geopackage(G_proj, filepath = 'COM_bikeinfra_smsr_dtp_ecf_32755.gpkg')
# ox.osm_xml.save_graph_xml(G_simplified, filepath = 'graph_used.osm')
# ox.osm_xml.save_graph_xml(G_proj, filepath = 'graph_used_projected.osm')
# ox.io.save_graph_shapefile(G_simplified, filepath = 'graph_used_shapefile_simplified_latest')
# ox.io.save_graph_shapefile(G_proj, filepath = 'graph_used_shapefile_simplified_latest_projected')

#%%

stats = G_edges[['length','bike_inf_smsr']].groupby(['bike_inf_smsr']).sum()/1000
stats['percentage'] = 100*stats['length']/(stats['length'].sum())
stats['length'] = stats['length'].round(0)
stats['percentage'] = stats['percentage'].round(2)
stats.to_csv('COM_stats_length_by_infra_v2.csv')

stats = G_edges[['length','bike_inf_superclass']].groupby(['bike_inf_superclass']).sum()/1000
stats['percentage'] = 100*stats['length']/(stats['length'].sum())
stats['length'] = stats['length'].round(0)
stats['percentage'] = stats['percentage'].round(2)
stats.to_csv('COM_stats_length_by_superclass_v2.csv')

#%%

