import streamlit as st
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import json
import folium
from streamlit_folium import st_folium
from streamlit_gsheets import GSheetsConnection
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

def print_Report(block):
    # Show reports 
    with st.container():
        # Report Header
        st.header('❕' + block['Title'] + '🔸', anchor=str(block["Id"]))
        
        # Report first sentence
        splitReport = block['Text'].split('.')
        st.write(splitReport[0])
        
        # If Read more button pressed
        with st.expander("Read More"):
            st.info(block['Text'])
            #map(location=(report['Coordinates']['LAT'], report['Coordinates']['LON']))
            st.write("[Resource↗️](https://web.telegram.org/k/#@hadshotabitahon)")
        # Publish Time
        st.write(block['PublishTime'])
        st.write('-----------------------------')
        # Puts the events on the map 
        if block['Coordinates'] != {}:
            location = block['Coordinates']['LAT'], block['Coordinates']['LON']
            folium.Marker(location,popup=block['Title'],icon=folium.DivIcon(html=reportHtml)).add_to(map)

def print_Alert(block):
    # Show alert 
    # Report Header
        with st.container():
            st.header('🚨' + block['Title'] + '🔸', anchor=str(block["Id"]))
            

            st.write(block['Title'])
            

            st.write("[Resource↗️](https://web.telegram.org/k/#@CumtaAlertsEnglishChannel)")
            # Publish Time
            st.write(block['PublishTime'])
            st.write('-----------------------------')
            
            # Puts the events on the map 
            if block['Places'] != []:
                for place in block['Places']:
                    location = place['LAT'],place['LON']
                    folium.Marker(location,popup=block['Type']+ '\n' + block['PublishTime'],icon=folium.DivIcon(html=alertHtml)).add_to(map)

def print_Feed(reports_cb,alerts_cb):
    # sort the blocks by date time
    sortedFeed = reversed(sorted(feed, key=lambda x: datetime.strptime(x['PublishTime'],'%H:%M:%S, %Y-%m-%d')))

    for block in sortedFeed:
        if block['Id'][0] == 'r' and reports_cb:
           print_Report(block)
           
        elif block['Id'][0] == 'a' and alerts_cb:
            print_Alert(block)
        

# HTML 
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


# Creates connection with the google sheets database
#conn = st.experimental_connection("gsheets", type=GSheetsConnection)
# Reads from the DB
#df = conn.read()



# Creating a sidebar object
sideB = st.sidebar

# Gets the json file
allJson = get_Reports()
feed = allJson["Reports"] + allJson["Alerts"]

# Maps default view point
israelView = (31.78847185,38.21879441094499)

# Creates the map
map = folium.Map(location=israelView,zoom_start=7.5,tiles="Cartodb dark_matter")

# Get the time
now = datetime.now()

# Side Bar
with sideB:     
    # Header🔸❕❗
    st.title('Israel Security Dashboard')
    st.text(now.strftime("%H:%M:%S"))

    reports_cb = st.checkbox('❕ Recent Reports',value=True)
    alerts_cb = st.checkbox('🚨 Red Alerts',value=True)

    st.text('Last Update: ' + allJson["LastUpdate"])
    st.write('-----------------------------')
    
    #  Feed
    print_Feed(reports_cb,alerts_cb)
    #Print the map
st_folium(map,width=2600,height=790)
