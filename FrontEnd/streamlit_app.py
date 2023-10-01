import streamlit as st
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import json
import folium
from streamlit_folium import st_folium
from common import set_page_container_style


st.set_page_config(
    page_title='Israel Security Dashboard',
    layout='centered',
    page_icon=':shield:'
)


# Read the json file and return a dict of it
#@st.cache_data
def get_Reports():
    # Reads the reports that already saves in the database 
    with open('C:\\Users\\Amir\\development\\projects\\AINews\\Telegram\\AllNews.json') as f: 
        reportDict = json.load(f)
    return reportDict

st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)

# Creating a sidebar object
sideB = st.sidebar

# Gets the json file
allJson = get_Reports()
reports = allJson["Reports"]

# Maps default view point
israelView = (31.78847185,35.21879441094499)

# Creates the map
map = folium.Map(location=israelView,zoom_start=7,tiles="Cartodb dark_matter")

# Show reports on the map
for report in reports:
    if report['Coordinates'] != {}:
        location = report['Coordinates']['LAT'], report['Coordinates']['LON']
        folium.Marker(location,popup=report['Title'],icon=folium.Icon(color='red',prefix='fa',icon='star')).add_to(map)

text = report['Text']

# Side Bar
with sideB:     
    # Header
    
    st.title('Israel Security Dashboard')
    st.header('Recent Reports')
    st.write('-----------------------------')
    
    # Show reports 
    for report in reports:
        # Report Header
        st.header(report['Title'] + '🔸', anchor=str(report["Id"]))
        
        # Report first sentence
        splitReport = report['Text'].split('.')
        st.write(splitReport[0])
        
        # If Read more button pressed
        if st.button("Read More",key='b'+str(report["Id"])):
            st.write('more')
        
        # Publish Time
        st.write(report['PubilshTime'])
        st.write('-----------------------------')



# Print the map
st_folium(map,width=800,height=800)
