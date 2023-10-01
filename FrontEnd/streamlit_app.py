import streamlit as st
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import json
import folium
from streamlit_folium import st_folium

# Read the json file and return a dict of it
#@st.cache_data
def get_Reports():
    # Reads the reports that already saves in the database 
    with open('C:\\Users\\Amir\\development\\projects\\AINews\\Telegram\\AllNews.json') as f: 
        reportDict = json.load(f)
    return reportDict


allJson = get_Reports()
reports = allJson["Reports"]
# Creating a sidebar object
sideB = st.sidebar

israelView = (31.78847185,35.21879441094499)

# Creates the map
map = folium.Map(location=israelView,zoom_start=7,tiles="Cartodb dark_matter")

# Show reports on the map
for report in reports:
    if report['Coordinates'] != {}:
        location = report['Coordinates']['LAT'], report['Coordinates']['LON']
        folium.Marker(location,popup=report['Text'],icon=folium.Icon(color='red',prefix='fa',icon='star')).add_to(map)



# Side Bar
# Header
sideB.title('Recent Reports')
sideB.write('-----------------------------')

# Show reports 
for report in reports:
    sideB.header(report['Title'])
    sideB.info(report['Text'])
    sideB.write(report['PubilshTime'])
    sideB.write('-----------------------------')
st_folium(map,width=800,height=800)

