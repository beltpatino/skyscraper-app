"""
Name: Beltran Patino
CS230: Section 4
Data: Kaggle
URL:

Description:

This program...
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt

# Make the header of the tab, learned on a youtube video
st.set_page_config(
    page_title="US's Tallest Skyscrapers",
    page_icon="🏙️",
)
#Function to open the csv database
path = "C:\\Users\\beltr\\PycharmProjects\\Pythonskyscraperproject\\skyscrapers (1).csv"


#Load all of the data
def load_data(path):
    try:
        data = pd.read_csv(path)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Rename some columns to make coding easier/more legible
def clean_data(data):
    data.rename(columns = {"location.latitude" : "lat", "location.longitude" : "lon", "location.city" : "city", "location.country" : "country", "status.current" : "status", "statistics.height" : "height", "statistics.floors above" : "numfloor", "status.started.year" : "start_year"}, inplace = True)
    # Round the height so it's to 2dp
    data['height'] = data['height'].round(2)
    # Clean the data so that there are no points with 0 longitude and latitude (NOT BUILT BUILDINGS) as well as in start year as they haven't started yet, and no buildings with a eighto of 0
    data = data[(data['lon'] != 0) & (data['lat'] != 0) & (data['start_year'] != 0) & (data['height'] != 0)]
    return data

#Define the main page/home page, explains what the app is and the functionalities
def main_page(data):
    st.title("*Welcome to the Skyscraper Data Explorer*")
    st.header("Explore data about the tallest skyscrapers in the US!")
    st.write("""
    Explore the fascinating world of architecture across the United States!

*Interactive Map*: Navigate through a detailed map showcasing iconic buildings across various cities.

*City Insights*: Discover how cities compare with a bar graph of their average building heights.

*Material Breakdown*: Dive into the materials that shape our skylines with a colorful pie chart.

*Historical Trends*: Trace the evolution of architecture over the years with a dynamic line graph.
""")
    #Add an interesting facts section to the home page
    st.subheader("🏗️To start off here are some interesting Facts!🏗️")
    #Set theparameters
    min_height = data['height'].min()
    max_height = data['height'].max()
    #Join this to the buildings they belong to
    min_height_building = data.loc[data['height'] == min_height, ['name', 'city']].iloc[0]
    max_height_building = data.loc[data['height'] == max_height, ['name', 'city']].iloc[0]
    #Now find out the most common matrial used and in how many buildings
    most_used_material = data['material'].mode()[0]
    material_count = data['material'].value_counts().loc[most_used_material]
    #Now find the city with the most built builings
    city_with_most_buildings = data['city'].value_counts().idxmax()
    city_count = data['city'].value_counts().max()
    # Create a fact list
    st.markdown(
        f"""
            - **Tallest Building:** {max_height_building['name']} in {max_height_building['city']} ({max_height} meters)
            - **Shortest Building:** {min_height_building['name']} in {min_height_building['city']} ({min_height} meters)
            - **Most Used Material:** {most_used_material} (used in {material_count} skyscrapers)
            - **City with the Most Skyscrapers:** {city_with_most_buildings} ({city_count} skyscrapers)
            """
    )



#define a scatter map which gives the user options to pick what to see when you hover over the data
def scatter_map(data):
    st.title("Scatter Map of Skyscrapers")
    st.write("Hover over points to see details.")
    #Multi-select box for users to see what they want
    options = st.multiselect(
        "Select information to display on hover:",
        ["height", "material", "name", "city", "numfloor", "status"],
    )
    #Set up what the options of the scatter map are
    if options:
        data["tooltip"] = data.apply (
            lambda row : "<br>".join([f"<b>{opt.capitalize()}:</b> {row[opt]}" for opt in options]), axis = 1)
        #set up the map
        view_state = pdk.ViewState(
            latitude = data["lat"].mean(),
            longitude = data["lon"].mean(),
            zoom = 3,
            pitch = 0,
        )
        scatter_layer = pdk.Layer(
            type = 'ScatterplotLayer',
            data = data,
            get_position = '[lon, lat]',
            get_radius = 50,
            get_color = [0, 0, 128],
            pickable = True,
        )
        tool_tip = {
            "html" : "{tooltip}",
            "style" : {
                "backgroundColor" : "black",
                "color" : "white",
                "fontSize" : "14px",
                "padding" : "10px",
                "borderRadius" : "4px"
            },
        }
        map = pdk.Deck(
            map_style = 'mapbox://styles/mapbox/streets-v12',
            initial_view_state=view_state,
            layers = [scatter_layer],
            tooltip = tool_tip,
        )
        st.pydeck_chart(map)
    else:
        st.write("Please select at least one option to display on the map.")

# Define a bar-graph which will be able to compare different median heights per city
def bar_graph(data):
    st.title("Bar Graph: Median Height per City")
    #Create a multi-select box
    cities = data['city'].unique()
    selected_cities = st.multiselect("Select cities to display:", cities)
    if selected_cities:
        filtered_data = data[data['city'].isin(selected_cities)]
        # Calculate the height median of each city
        median_heights = filtered_data.groupby('city')['height'].median()
        # Create the bargraph
        fig, ax = plt.subplots()
        median_heights.plot(kind = 'bar', ax = ax, color = 'skyblue')
        ax.set_title("Median Height per City")
        ax.set_xlabel("City")
        ax.set_ylabel("Median Height (m)")
        st.pyplot(fig)
        #Have a pivot table to accompany the barchart, so the user can see the data in the bargraph
        st.subheader("City Insights: Pivot Table")
        pivot = filtered_data.pivot_table(values='height', index='city', aggfunc=['mean', 'count'])
        pivot.columns = ['Average Height (m)', 'Number of Skyscrapers']
        st.write("Here’s a detailed summary of the cities you selected:")
        st.dataframe(pivot)
    else:
        st.write("Please select at least one city to display the bar graph.")

# Define a piechart which shows the percentages of the materials used as a median
def pie_chart(data):
    st.title("Pie Chart: Distribution of Materials Used")
    #Add up all of the materials
    material_counts = data['material'].value_counts()
    #Plot the pie-chart
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(material_counts, labels = None, autopct = '%1.1f%%', startangle = 140, textprops = {'fontsize' : 8})
    #Make a legend
    ax.legend(wedges, material_counts.index, title = "Materials", loc = "center left", bbox_to_anchor = (1, 0, 0.5, 1), fontsize = 8)
    ax.set_title("Distribution of Materials")
    st.pyplot(fig)

# Define a linegraph which shows the years every building began to be built
def line_graph(data):
    st.title("Line Graph Showing the Construction Start Years")
    # Group by
    start_year_counts = data['start_year'].value_counts().sort_index()
    #Plot the linegraph
    fig, ax = plt.subplots()
    start_year_counts.plot(kind='line', ax=ax, marker='o', markersize = 1, color='red')
    ax.set_title("Number of Skyscrapers Built Each Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Skyscrapers")
    st.pyplot(fig)


#Side-bar set for navigation between all of the pages
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to:", ["🏠︎", "🗺️ Detailed", "📊 Heights", "🥧📊 Materials", "📈 Years They were built"])
#Clean the data and set where it should take the user
data = load_data(path)
if data is not None:
    data = clean_data(data)
if section == "🏠︎":
    main_page(data)
elif section == "🗺️ Detailed":
    scatter_map(data)
elif section == "📊 Heights":
    bar_graph(data)
elif section == "🥧📊 Materials":
    pie_chart(data)
elif section == "📈 Years They were built":
    line_graph(data)
