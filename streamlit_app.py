import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# Function to load data
@st.cache
def load_data(file):
    return pd.read_excel(file)

# Function to display stats
def display_stats(df):
    total_rows = df.shape[0]
    missing_gps = df['GPS'].isnull().sum()
    st.write(f"Total rows: {total_rows}")
    st.write(f"Rows without GPS coordinates: {missing_gps}")

# Function to create map
def create_map(df):
    m = folium.Map(location=[df['GPS'].dropna().iloc[0].split(", ")[0], df['GPS'].dropna().iloc[0].split(", ")[1]], zoom_start=2)
    
    for _, row in df.dropna(subset=['GPS']).iterrows():
        folium.Marker(
            location=[float(coord) for coord in row['GPS'].split(", ")],
            popup=f"Name: {row['Name']}<br>Faction: {row['Faction']}"
        ).add_to(m)
    
    return m

# Streamlit app
st.title("Excel GPS Data Analyzer")

uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    st.subheader("Data Stats")
    display_stats(df)
    
    st.subheader("Map Visualization")
    factions = df['Faction'].unique()
    selected_faction = st.multiselect("Filter by Faction", options=factions, default=factions)
    
    filtered_df = df[df['Faction'].isin(selected_faction)]
    map_obj = create_map(filtered_df)
    folium_static(map_obj)
