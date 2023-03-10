import json
import zipfile
import geopandas as gpd

import numpy as np
import pandas as pd

import plotly.express as px
import streamlit as st


data = pd.read_parquet("data.parquet.gzip")
codes = gpd.read_parquet("codes.parquet.gzip")

#Page config
st.set_page_config(
    page_title="Uber data interactive dashboard",
    page_icon="🚗",
    initial_sidebar_state="expanded"
)

#Title and header
st.header("Felipe Basurto Barrio")
st.markdown("#### Uber data interactive dashboard")
st.markdown("Interactive streamlit dashboard containing the data from all uber trips in Madrid, year 2020.")
st.markdown("--------------------------------------")


# Define the source and destination neighborhoods
source_neighborhood = st.sidebar.selectbox('Select source neighborhood', sorted(data['src_neigh_name'].unique()))
destination_neighborhood = st.sidebar.selectbox('Select destination neighborhood', sorted(data['src_neigh_name'].unique()))

# Filter the dataframe based on the user's selection
filtered_data = data[(data['src_neigh_name'] == source_neighborhood) & (data['dst_neigh_name'] == destination_neighborhood)]
source_neighborhood_data = codes[codes['DISPLAY_NAME'] == source_neighborhood]
destination_neighborhood_data = codes[codes['DISPLAY_NAME'] == destination_neighborhood]

# Calculating different metrics for our charts
mean_travel_time_per_day = filtered_data.groupby(["date"]).mean()["mean_travel_time"]
travel_by_time_and_day = filtered_data.groupby(["day_of_week_str","day_period"]).mean()["mean_travel_time"].unstack()
travel_by_time_and_day = travel_by_time_and_day.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

################################################# CHARTS #################################################


# CHART 1
st.markdown("**Mean travel time per day**")
tab1, tab2 = st.tabs(["📈 Chart", "📋 Data"])
tab1.plotly_chart(
    px.line(mean_travel_time_per_day, 
            labels={'x': 'Date', 'y': 'Mean travel time'})
    .update_layout(showlegend=False)
)
tab2.write(mean_travel_time_per_day)


# CHART 2

st.markdown("**Mean travel time time period, each day of the week**")
tab3, tab4 = st.tabs(["📈 Chart", "📋 Data"])
tab3.plotly_chart(
    px.bar(travel_by_time_and_day, 
           barmode = "group", 
           labels={'x':'Day of the week', 'y':'Mean travel time per period'}, 
           text_auto=True)
)
tab4.write(travel_by_time_and_day)

                      
                      
# CHART 3               
st.markdown("**Map of origin and destination neighbourhoods**")
# Create the Plotly figure
fig = px.choropleth(codes,
                    geojson = codes.geometry,
                    locations = codes.index,
                    projection="mercator",
                    hover_data=["DISPLAY_NAME"],
                    color_discrete_sequence=["#dedede"]
                    )

# Add source neighborhood
fig.add_trace(
    px.choropleth(source_neighborhood_data,
                  geojson = source_neighborhood_data.geometry,
                  locations = source_neighborhood_data.index,
                  projection="mercator",
                  color_discrete_sequence=["#5784ff"],
                  hover_data=["DISPLAY_NAME"]).data[0])

# Add destination neighborhood
fig.add_trace(
    px.choropleth(destination_neighborhood_data,
                  geojson = destination_neighborhood_data.geometry,
                  locations = destination_neighborhood_data.index,
                  projection="mercator",
                  color_discrete_sequence=["#ff943d"],
                  hover_data=["DISPLAY_NAME"],
                  title="Destination").data[0])

fig.data[1].name = 'Origin'
fig.data[2].name = 'Destination'

fig.update_geos(fitbounds="locations", visible=False).update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig)