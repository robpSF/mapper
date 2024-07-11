import streamlit as st
import pandas as pd
import folium
from folium.features import CustomIcon
from streamlit_folium import folium_static
from folium import IFrame
import matplotlib.pyplot as plt

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

# Function to create map with images
def create_map_with_images(df):
    avg_lat = df['Latitude'].mean()
    avg_lon = df['Longitude'].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=2)
    
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

# Function to create map with pins
def create_map_with_pins(df):
    avg_lat = df['Latitude'].mean()
    avg_lon = df['Longitude'].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=2)
    
    for _, row in df.dropna(subset=['Latitude', 'Longitude']).iterrows():
        html = f"""
        <h4>Name: {row['Name']}</h4>
        <h5>Faction: {row['Faction']}</h5>
        <img src="{row['Image']}" width="100" height="100">
        """
        iframe = IFrame(html, width=200, height=200)
        popup = folium.Popup(iframe, max_width=200)
        
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=popup
        ).add_to(m)
    
    return m

# Function to plot tag counts
def plot_tag_counts(df):
    tags_series = df['Tags'].str.split(',', expand=True).stack().str.strip()
    tag_counts = tags_series.value_counts().sort_index()
    
    # Split tag counts into groups based on the first letter
    tag_groups = {}
    for tag, count in tag_counts.items():
        if tag:  # Ensure tag is not empty
            first_letter = tag[0].upper()
            if first_letter not in tag_groups:
                tag_groups[first_letter] = []
            tag_groups[first_letter].append((tag, count))
    
    # Set font size
    plt.rcParams.update({'font.size': 12})
    
    # Create and display a chart for each group
    for letter in sorted(tag_groups.keys()):
        tags, counts = zip(*tag_groups[letter])
        plt.figure(figsize=(10, 6))
        plt.barh(tags, counts)
        plt.xlabel('Count')
        plt.ylabel('Tags')
        plt.title(f'Tag Counts ({letter})')
        plt.xticks(rotation=0)
        st.pyplot(plt)

# Function to plot faction counts
def plot_faction_counts(df):
    faction_counts = df['Faction'].value_counts().sort_index()
    
    # Set font size
    plt.rcParams.update({'font.size': 12})
    
    plt.figure(figsize=(10, 6))
    faction_counts.plot(kind='barh')
    plt.xlabel('Count')
    plt.ylabel('Faction')
    plt.title('Faction Counts')
    plt.xticks(rotation=0)
    st.pyplot(plt)

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

    # Extract unique tags
    df['Tags'] = df['Tags'].fillna('')  # Replace NaNs with empty strings
    all_tags = set(tag.strip() for tags in df['Tags'] for tag in tags.split(',') if tag)
    selected_tags = st.multiselect("Filter by Tags", options=list(all_tags), default=list(all_tags))
    
    display_option = st.radio("Display option", ("Pins", "Images"))
    show_as_table = st.checkbox("Show results as a table")

    # Filter data by faction and tags
    def filter_by_tags(tags, selected_tags):
        tags_list = [tag.strip() for tag in tags.split(',')]
        return any(tag in tags_list for tag in selected_tags)

    filtered_df = df[df['Faction'].isin(selected_faction)]
    if selected_tags:
        filtered_df = filtered_df[filtered_df['Tags'].apply(lambda x: filter_by_tags(x, selected_tags))]
    
    if show_as_table:
        st.subheader("Filtered Results")
        st.write(filtered_df[['Name', 'Handle', 'Faction', 'Tags', 'Bio', 'TwFollowers', 'TwFollowing']])
    else:
        if display_option == "Images":
            map_obj = create_map_with_images(filtered_df)
        else:
            map_obj = create_map_with_pins(filtered_df)
        
        folium_static(map_obj)
    
    st.subheader("Tag Counts")
    plot_tag_counts(df)
    
    st.subheader("Faction Counts")
    plot_faction_counts(df)
