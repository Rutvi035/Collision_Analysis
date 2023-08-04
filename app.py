import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px


DATA_URL = ("/Projects/Collision analysis/Motor_Vehicle_Collisions_-_Crashes.csv")

st.title("Motor vehical collision in New York city")
st.markdown("This application is a Streamlit dashboard used to analyze motor vehicle collisions in NYC 🗽💥🚗")


# checks function syntax
@st.cache_resource()

#----> load data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE','CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time':'date/time'}, inplace=True)
    return data

data = load_data(10000)
original_data = data

#----> visualizing data on map
st.header("Where are the most people injured in NYC?")
#0-29 displays range of 30 in the slider
injured_people = st.slider("Number of person(s) injured in vehicle collision", 0, 29)

#plot data on map
#returning two arguments latitude and longitude to plot on map

st.map(data.query("injured_persons >= @injured_people")[["latitude","longitude"]].dropna(how="any"))


#----> filtering data and interactive tables
#based on the hour select raw data table will change

st.header("How many collisions occur during given time of day?")
#dhour slider to select the particular hour of the day
hour = st.slider("Hour to look at", 0,23)
data = data[data['date/time'].dt.hour == hour]
#using hour slider subset hour day


#----> plotting filtered data on 3D interactive map
#collision between the chosen hour of the day
#pydeck used to intialize map at the provided latitutde and longitude based on the average of them
st.markdown("Vehicle collision between %i:00 & %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))
#3d plot... pitch key with 50 degrees
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch" : 50,
    },

    #making layers over map for better visualization
    layers = [
        pdk.Layer(
        "HexagonLayer",
        #specifying data
        data = data[['date/time','latitude','longitude']],
        get_position = ['longitude','latitude'],
        radius = 100, #in metres
        extruded = True,#for 3D
        pickable = True,
        elevation_scale = 4,
        elevation_range = [0,1000],
        ),
    ],
))


#----> charts and histograms
st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) %24))
filtered = data[(data['date/time'].dt.hour)& (data['date/time'].dt.hour < (hour + 1))]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute','crashes'], height=400)
st.write(fig)

#---> selecting data using dropdowns
st.subheader("Top 5 dangerous streets affected by collision through filters")
select = st.selectbox('Type of people affected',['Pedestrians','Cyclists','Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name","injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[:3])

elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name","injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[:5])

else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name","injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:9])



#>> checkbox to see the raw data
if st.checkbox("Display raw data", False):
    st.subheader('Raw Data')
    st.write(data)
