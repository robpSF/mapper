import streamlit as st
import pandas as pd
import folium
from folium.features import CustomIcon
from streamlit_folium import folium_static

# Function to load data
@st.cache_data
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
    # Initialize the map centered on the average location
    avg_lat = df['Latitude'].mean()
    avg_lon = df['Longitude'].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=2)
    
    # Add markers to the map
    for _, row in df.dropna(subset=['Latitude', 'Longitude']).iterrows():
        icon = CustomIcon(
            icon_image=row['Image'], 
            icon_size=(50, 50),  # Adjust the size as needed
        )
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"Name: {row['Name']}<br>Faction: {row['Faction']}",
            icon=icon
        ).add_to(m)
    
    return m

# Streamlit app
st.title("Excel GPS Data Analyzer")

uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    # Split GPS coordinates into Latitude and Longitude
    df[['Latitude', 'Longitude']] = df['GPS'].str.split(',', expand=True)
    df['Latitude'] = df['Latitude'].astype(float)
    df['Longitude'] = df['Longitude'].astype(float)
    
    st.subheader("Data Stats")
    display_stats(df)
    
    st.subheader("Map Visualization")
    factions = df['Faction'].unique()
    selected_faction = st.multiselect("Filter by Faction", options=factions, default=factions)
    
    filtered_df = df[df['Faction'].isin(selected_faction)]
    map_obj = create_map(filtered_df)
    folium_static(map_obj)
