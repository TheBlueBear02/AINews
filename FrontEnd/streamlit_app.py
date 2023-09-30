import streamlit as st
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim

# Initialize Nominatim API
geolocator = Nominatim(user_agent="MyApp")

location = geolocator.geocode("Tel Aviv")

lat = location.latitude
lot = location.longitude

df = pd.DataFrame({
    "col1": lat,
    "col2": lot,
    "col3": 200,
    "col4": np.random.rand(1000, 4).tolist(),
})

st.map(df,
    latitude='col1',
    longitude='col2',
    size='col3',
    #color='col4'
    )
# Add a selectbox to the sidebar:
st.sidebar.write('Hello')

