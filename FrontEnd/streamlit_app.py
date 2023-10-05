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

def print_Report(block,feature_group):
    # Show reports 
    with st.container():
        
        time = block['PublishTime'].split(',')[0]
        HnM = time.split(':')[0] + ':' +time.split(':')[1]
        
        st.text(str(HnM))
        # Report Header
        if block['Coordinates']['LAT'] == 0:
            header = st.subheader('❕' + block['Title'] + '🔸', anchor=str(block["Id"]))
        elif block['Coordinates']['LAT'] != 0 and block['IsIsrael']:
            header = st.subheader('🔵 ' + block['Title'] + '🔸', anchor=str(block["Id"]))
        else:
            header = st.subheader('🔴 ' + block['Title'] + '🔸', anchor=str(block["Id"]))
       
        # Report first sentence
        splitReport = block['Text'].split('.')
        st.write(splitReport[0])
        restReport = ''
        # If Read more button pressed
        with st.expander("Full Report"):
            st.info(block['Text'])
            #map(location=(report['Coordinates']['LAT'], report['Coordinates']['LON']))
            st.write("[Resource↗️](https://web.telegram.org/k/#@hadshotabitahon)")
        # Publish Time
        
        st.write('---')
        # Puts the events on the map 
        if block['Coordinates'] != {} and block['Coordinates']['LAT'] != 0:
            location = block['Coordinates']['LAT'], block['Coordinates']['LON']
            if block['IsIsrael']: 
                folium.Marker(location,popup=HnM + ' ' + block['Title'],icon=folium.DivIcon(html=reportHtml)).add_to(feature_group)
            else:
                folium.Marker(location,popup=HnM + ' ' + block['Title'],icon=folium.DivIcon(html=alertHtml)).add_to(feature_group)

        return feature_group

def print_Alert(block,alertMarkers):
    # Show alert 
    # Report Header
        with st.container():
           
            # Publish Time
            time = block['PublishTime'].split(',')[0]
            HnM = time.split(':')[0] + ':' +time.split(':')[1]
            st.text(str(HnM))

            st.header('🚨' + f":red[{block['Title']}]" + '🔸', anchor=str(block["Id"]))
            

            st.write(block['Title'])
            

            st.write("[Resource↗️](https://web.telegram.org/k/#@CumtaAlertsEnglishChannel)")
           
           
            st.write('-----------------------------')
            
            # Puts the events on the map 
            if block['Places'] != []:
                for place in block['Places']:
                    location = place['LAT'],place['LON']
                    folium.Marker(location,popup=block['Title']+ '\n' + block['PublishTime'],icon=folium.DivIcon(html=alertHtml)).add_to(alertMarkers)
            return alertMarkers

def print_Feed(reports_cb,alerts_cb):
    # sort the blocks by date time
    sortedFeed = reversed(sorted(feed, key=lambda x: datetime.strptime(x['PublishTime'],'%H:%M:%S, %Y-%m-%d')))
    reportsMarkers = folium.FeatureGroup(name='Reports')
    alertMarkers = folium.FeatureGroup(name='Alerts')

    for block in sortedFeed:
        # CALCULATE THE DELTA TIME OF THE BLOCK
        # IF LESS THAN X PRINT ELSE: DON'T PRINT AND BREAK
        if block['Id'][0] == 'r' and reports_cb:
           reportsMarkers = print_Report(block, reportsMarkers)

           
        elif block['Id'][0] == 'a' and alerts_cb:
            alertMarkers = print_Alert(block,alertMarkers)
    reportsMarkers.add_to(map)
    alertMarkers.add_to(map)

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
        width: 25px;
        height: 25px;
        position: absolute;
        size: absolute;
        opacity: 0;
        animation: scaleIn 5s infinite cubic-bezier(.36, .11, .89, .32);
        }                                
        @keyframes scaleIn {
        from {
            transform: scale(.1, .1);
            opacity: .5;
        }
        to {
            transform: scale(2, 2);
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
            transform: scale(2, 2);
            opacity: 0;
        }
        } 
        
    </style>
    
    <div>  
        <div class="alert" style="animation-delay: -3s"></div>                                                                         
        <div class="alert" style="animation-delay: -2s"></div>
        <div class="alert" style="animation-delay: -1s"></div>
        <div class="alert" style="animation-delay: 0s"></div>                                                                                                           
    </div>
    """
eventHtml = """
    <style>
        .event {
        border-radius: 50%;
        background-color: orange;
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
            transform: scale(4, 4);
            opacity: 0;
        }
        } 
        
    </style>
    
    <div>  
        <div class="event" style="animation-delay: -3s"></div>                                                                         
        <div class="event" style="animation-delay: -2s"></div>
        <div class="event" style="animation-delay: -1s"></div>
        <div class="event" style="animation-delay: 0s"></div>                                                                                                           
    </div>
    """

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
# Get the time now
now = datetime.now()
# Side Bar
with sideB:     
    # Header🔸❕❗
    
    # Calculating How many miuntes ago the feed updated
    current_time = now.strftime("%H:%M")
    nowStr = datetime.strptime(current_time,"%H:%M")
    lastUpdate = datetime.strptime(allJson["LastUpdate"],'%H:%M')
    delta = nowStr - lastUpdate
    minsAgo = int(delta.total_seconds() / 60)
   
    # Ttle
    st.title('Israel Security Dashboard')
    
    # Choosing Feed Data
    reports_cb = st.checkbox('❕ Recent Reports',value=True)
    alerts_cb = st.checkbox('🚨 Red Alerts')
    
    with st.expander("Report Kinds"):
        st.text('❕ Report not on map')
        st.text('🚨 Red Alert')
        st.text('🔵 Israeli Operation on map')
        st.text('🔴 Terror Attack on map')
    # Print Last Update
    if minsAgo < 1:
        st.text('Just Updated Now')
    elif minsAgo > 60:
        st.text('Updated ' + str(int(minsAgo/60)) + 'h Ago')
    else:
        st.text('Updated ' + str(minsAgo) + 'm Ago')
    st.write('---------')
    
    #  Feed
    print_Feed(reports_cb,alerts_cb)
    #Print the map
st_folium(map,width=2600,height=790)
