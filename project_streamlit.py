#***********************************************************************************
#************************* Importation of librairies *******************************
#***********************************************************************************

# cd C:\Users\Hugo\Documents\7 S7\Project 1
# streamlit run Project_streamlit.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import streamlit as st

# Feature 1 

import geopy
from geopy.point import Point
from geopy.geocoders import Nominatim

# Feature 2

import openrouteservice
from openrouteservice import convert
import folium
from streamlit_folium import folium_static
import json
import datetime

# Feature 3
import plotly.express as px

#***********************************************************************************
#********************************* Reading of data *********************************
#***********************************************************************************
st.video('video.mp4')

df_bis = pd.read_csv("50_files.csv",sep=',')
#df_bis = pd.read_csv("roads_10_files.csv",sep=',')
df_bis["date_time"] = pd.to_datetime(df_bis["date_time"])

#***********************************************************************************
#************************************ Feature 1 ************************************
#***********************************************************************************

st.title("Data camp project")
st.subheader("Feature 1 : Streets with the highest congestion rate")

#Top 10 streets with the highest congestion rate
st.write("Top 10 streets with the highest congestion rate")
st.write(df_bis['road'].value_counts().head(10))

#Top 10 streets with the highest congestion rate at a given time
st.write("Top 10 streets with the highest congestion rate at a given time")
with st.form(key='Feature_1_1'):
    date = st.date_input('Date',value=pd.to_datetime('2008-02-02'))
    time = st.time_input('Time',value=pd.to_datetime('14:19:00'))
    final_date = datetime.datetime.combine(date, time)
    final_date = pd.to_datetime(final_date)
    # add one minute to the time
    date_bis = final_date + pd.Timedelta(minutes=1)
    submit_button = st.form_submit_button(label='Submit')

if submit_button:
    st.write(df_bis[(df_bis['date_time'] > final_date) & (df_bis['date_time'] < date_bis)]['road'].value_counts().head(10))

#The 10 streets with the highest congestion rate at a given time interval
st.write("The 10 streets with the highest congestion rate at a given time interval")
with st.form(key='Feature_1_2'):
    date = st.date_input('Date',value=pd.to_datetime('2008-02-02'))
    time = st.time_input('Time',value=pd.to_datetime('14:19:00'))
    date2 = st.date_input('Date',value=pd.to_datetime('2008-02-03'))
    time2 = st.time_input('Time',value=pd.to_datetime('11:20:00'))
    final_date = datetime.datetime.combine(date, time)
    final_date = pd.to_datetime(final_date)
    final_date2 = datetime.datetime.combine(date2, time2)
    final_date2 = pd.to_datetime(final_date2)
    submit_button = st.form_submit_button(label='Submit')

if submit_button:
    st.write(df_bis[(df_bis['date_time'] > final_date) & (df_bis['date_time'] < final_date2)]['road'].value_counts().head(10))


#***********************************************************************************
#************************************ Feature 2 ************************************
#***********************************************************************************

st.subheader("Feature 2 : The average time needed to reach from point A to point B")

with st.form(key='Feature_2'):
    a_longitude = st.number_input("Longitude of point A",-180.0,180.0,step=1e-10,format="%.9f",value = 116.33772)
    a_latitude = st.number_input("Latitude of point A",-90.0,90.0,step=1e-10,format="%.9f",value = 39.92724)
    b_longitude = st.number_input("Longitude of point B",-180.0,180.0,step=1e-10,format="%.9f",value = 116.37429)
    b_latitude = st.number_input("Latitude of point B",-90.0,90.0,step=1e-10,format="%.9f",value = 39.97052)
    date = st.date_input('Date',value=pd.to_datetime('2008-02-02'))
    time = st.time_input('Time',value=pd.to_datetime('14:19:00'))
    submit_button2 = st.form_submit_button(label='Submit')

if submit_button2:

    #****************** Obtain map information with coords from the API ****************

    # Connexion to the API with the key
    client = openrouteservice.Client(key='5b3ce3597851110001cf6248b32018d70bf542d6bcb8f811f562cb17')

    #Add coordinates
    #coords = ((116.33772,39.92724),(116.37429,39.97052))
    coords = ((a_longitude,a_latitude),(b_longitude,b_latitude))


    res = client.directions(coords)

    # As our purpose is to draw the route between the given points, 
    # we could use the routes’s geometry attribute. By default, 
    # the directions API returns encoded polylines. 
    geometry = client.directions(coords)['routes'][0]['geometry']
    #GeoJSON geometry object that we can use in the visualization part.
    decoded = convert.decode_polyline(geometry)

    #****************** Calculation of the time route ****************

    #creation of an array of dictionaries
    #each dictionary contains the distance and the road name
    # We have to do the sum of the distances for each road name because 
    # the API gives us the same road name with several distances

    itinerary = []
    for i in range(len(res["routes"][0]["segments"][0]["steps"])):

        if (res["routes"][0]["segments"][0]["steps"][i]["name"] != '-'):
            new_dict = {"distance":res["routes"][0]["segments"][0]["steps"][i]["distance"], "name":res["routes"][0]["segments"][0]["steps"][i]["name"]}
            itinerary.append(new_dict)

        else:
            if (len(itinerary)!=0):
                itinerary[len(itinerary)-1]["distance"] = itinerary[len(itinerary)-1]["distance"] + res["routes"][0]["segments"][0]["steps"][i]["distance"]

    final_date = datetime.datetime.combine(date, time)
    final_date = pd.to_datetime(final_date)
    next_date = final_date + pd.Timedelta(hours=5) 

    for i in range(len(itinerary)):
        
        road = itinerary[i]["name"]

        #calculatation the number of the same road in the df_bis to know the density of each road
        df_road = df_bis[df_bis['road'] == road]
        road_density = df_road[(df_road['date_time'] > final_date) & (df_road['date_time'] < next_date)].shape[0]
        #Give speed in fuction of the density of the road
        if (road_density < 5):
            speed = 35
        elif (road_density < 10):
            speed = 27
        else : 
            speed = 22
        
        #Calculation of the time needed for each road
        itinerary[i]["time"] = (itinerary[i]["distance"]*3600)/(speed*1000)

    #Calculation of the total time needed
    total_time = 0
    for i in range(len(itinerary)):
        total_time = total_time + itinerary[i]["time"]

    #st.write("total_time : ", int(total_time/3600), "h ",str(int(total_time/60)), "min ",str(int(total_time%60)), "s")


    #****************** Display the map with the route on it ****************

    distance_txt = "<h5> <b>Distance :&nbsp" + "<strong>"+str(round(res['routes'][0]['summary']['distance']/1000,1))+" Km </strong>" +"</h5></b>"
    duration_txt = "<h5> <b>Duration :&nbsp" + "<strong>"+str(int(total_time/60)) +" Min </strong>" +"</h5></b>"

    m = folium.Map(location=[39.9075,116.39723],zoom_start=10, control_scale=True,tiles="cartodbpositron")

    # add itinerary and distance to the map
    #folium.GeoJson(decoded).add_child(folium.Popup(distance_txt,max_width=200)).add_to(m)
    folium.GeoJson(decoded).add_child(folium.Popup(distance_txt+duration_txt,max_width=200)).add_to(m)

    #creation of start and end points
    folium.Marker(
        location=list(coords[0][::-1]),
        popup="Galle fort",
        icon=folium.Icon(color="green"),
    ).add_to(m)

    folium.Marker(
        location=list(coords[1][::-1]),
        popup="Jungle beach",
        icon=folium.Icon(color="red"),
    ).add_to(m)
    #m.save('map.html')

    #show map on the streamlit app
    folium_static(m)


#***********************************************************************************
#************************************ Feature 3 ************************************
#***********************************************************************************

st.subheader("Feature 3 : The average car density of the city")

# ********* Top 10 streets with the highest congestion rate at a given time ********
st.write("Density of the city at a given time")
with st.form(key='Feature_2_1'):
    date = st.date_input('Date',value=pd.to_datetime('2008-02-02'))
    time = st.time_input('Time',value=pd.to_datetime('14:19:00'))
    final_date = datetime.datetime.combine(date, time)
    final_date = pd.to_datetime(final_date)
    # add one minute to the time
    date_bis = final_date + pd.Timedelta(minutes=1)
    submit_button = st.form_submit_button(label='Submit')

if submit_button:
    st.write("The number of vehicules in Benjing at this time is equal to", df_bis[(df_bis['date_time'] > final_date) & (df_bis['date_time'] < date_bis)].shape[0])

# ********************* Average car density of the city by hour ********************

# create a column with the hour of the day
df_bis['hour'] = df_bis['date_time'].dt.hour
# create a column with the day of the week
df_bis['day'] = df_bis['date_time'].dt.day
df_bis['month'] = df_bis['date_time'].dt.month
df_bis['year'] = df_bis['date_time'].dt.year

#list with the average car density by hour
average_list=[0]*24

for i in range(0,24):
    # sort by hour i 
    df_2 = df_bis[(df_bis['hour'] == i)]

    #nb_cars = number of cars at i hour
    nb_cars = df_2.shape[0]
    df_2 = df_2.drop_duplicates(subset=['day','month','year'], keep='first')

    #nb_of_days = number of days where at least one car drive at i hour
    nb_of_days = len(df_2)
    
    average = nb_cars/nb_of_days
    average_list[i] = average

# graph of the average car density of the city by hour 
st.write("Average car density of the city by hour")
st.bar_chart(average_list)

