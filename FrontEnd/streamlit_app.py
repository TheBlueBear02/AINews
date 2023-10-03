import streamlit as st
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import json
import folium
from streamlit_folium import st_folium
from common import set_page_container_style
from folium.plugins import HeatMap
from datetime import datetime


st.set_page_config(
    page_title='Israel Security Dashboard',
    layout='wide',
    page_icon=':shield:'
    
)


# Read the json file and return a dict of it
st.cache_data
def get_Reports():
    # Reads the reports that already saves in the database 
    with open('C:\\Users\\Amir\\development\\projects\\AINews\\Telegram\\AllNews.json') as f: 
        reportDict = json.load(f)
    return reportDict

def print_Reports():
    # Show reports 
    for report in reports:
        # Report Header
        st.header('❕' + report['Title'] + '🔸', anchor=str(report["Id"]))
        
        # Report first sentence
        splitReport = report['Text'].split('.')
        st.write(splitReport[0])
        
        # If Read more button pressed
        with st.expander("Read More"):
            st.info(report['Text'])
            #map(location=(report['Coordinates']['LAT'], report['Coordinates']['LON']))
            st.write("[Resource↗️](https://web.telegram.org/k/#@hadshotabitahon)")
        # Publish Time
        st.write(report['PubilshTime'])
        st.write('-----------------------------')
        
        # Puts the events on the map 
        if report['Coordinates'] != {}:
            location = report['Coordinates']['LAT'], report['Coordinates']['LON']
            folium.Marker(location,popup=report['Title'],icon=folium.DivIcon(html=reportHtml)).add_to(map)


def print_Alerts():
    # Show reports 
    for alert in alerts:
        # Report Header
        st.header('🚨' + alert['Title'] + '🔸', anchor=str(alert["Id"]))
        

        st.write(alert['Title'])
        

        st.write("[Resource↗️](https://web.telegram.org/k/#@CumtaAlertsEnglishChannel)")
        # Publish Time
        st.write(alert['Time'])
        st.write('-----------------------------')
        
        # Puts the events on the map 
        if alert['Places'] != []:
            for place in alert['Places']:
                location = place['LAT'],place['LON']
                folium.Marker(location,popup=alert['Type']+ '\n' + alert['Time'],icon=folium.DivIcon(html=alertHtml)).add_to(map)


st.markdown("""
        <style>
               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 0rem;
                    padding-right: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)
reportHtml = """
    <style>
        .report {
        border-radius: 50%;
        background-color: blue;
        width: 17px;
        height: 17px;
        position: absolute;
        opacity: 0;
        animation: scaleIn 5s infinite cubic-bezier(.36, .11, .89, .32);
        }                                
        @keyframes scaleIn {
        from {
            transform: scale(.1, .1);
            opacity: .5;
        }
        to {
            transform: scale(3, 3);
            opacity: 0;
        }
        } 
        
    </style>
    <div>  
        <div class="report" style="animation-delay: -3s"></div>                                                                         
        <div class="report" style="animation-delay: -2s"></div>
        <div class="report" style="animation-delay: -1s"></div>
        <div class="report" style="animation-delay: 0s"></div>      
                                                                                                                        
    </div>"""
alertHtml = """
    <style>
        .alert {
        border-radius: 50%;
        background-color: red;
        width: 10px;
        height: 10px;
        position: absolute;
        opacity: 0;
        animation: scaleIn 5s infinite cubic-bezier(.36, .11, .89, .32);
        }                                
        @keyframes scaleIn {
        from {
            transform: scale(.1, .1);
            opacity: .5;
        }
        to {
            transform: scale(3, 3);
            opacity: 0;
        }
        } 
        
    </style>
    <div>  
        <div class="alert" style="animation-delay: -3s"></div>                                                                         
        <div class="alert" style="animation-delay: -2s"></div>
        <div class="alert" style="animation-delay: -1s"></div>
        <div class="alert" style="animation-delay: 0s"></div>      
                                                                                                               
    </div>"""
# Creating a sidebar object
sideB = st.sidebar

# Gets the json file
allJson = get_Reports()
reports = allJson["Reports"]
alerts = allJson["Alerts"]
# Maps default view point
israelView = (31.78847185,38.21879441094499)

# Creates the map
map = folium.Map(location=israelView,zoom_start=7.5,tiles="Cartodb dark_matter")


now = datetime.now()

# Side Bar
with sideB:     
    # Header🔸❕❗
    st.title('Israel Security Dashboard')
    st.text(now.strftime("%H:%M:%S"))

    reports_cb = st.checkbox('❕ Recent Reports',value=True)
    Alerts_cb = st.checkbox('🚨 Red Alerts')

    st.text('Last Update: ' + allJson["LastUpdate"])
    st.write('-----------------------------')
    if reports_cb:
        print_Reports()
    if Alerts_cb:
        print_Alerts()
 # Print the map
st_folium(map,width=2600,height=790)
