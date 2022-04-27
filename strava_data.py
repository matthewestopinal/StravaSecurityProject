import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import fitparse
import gzip
import shutil
import os

import matplotlib.pyplot as plt
from geographiclib.geodesic import Geodesic
import googlemaps


#Accepts the filename of the activity.csv file
#Returns a list of the filenames for GPS Data
#TODO Edit to change to a tuple to save some important data (i.e. date)
def get_gps_filenames(activity_file):
    #Load csv
    df = pd.read_csv(activity_file)
    runs = df[df["Activity Type"] == "Run"]
    runs = runs.dropna(subset=['Filename'])

    gps_files = runs['Filename'].to_list()

    return gps_files

#Accepts a list of relative locations of gps files and extracts them
#dumps to the fit_file folder
#Returns the list of locations of these unzipped files
def unzip_gps_files(gps_locs, dest="fit_files"):
    fit_files = []

    #If the folder we are extracting to does not exist, make it
    if not os.path.exists(dest):
        os.makedirs(dest)

    for loc in gps_locs:
        #Get the location of the unzipped file
        #Get the actual filename instead of the whole path
        new_file = loc[0:len(loc)-3]
        #Assume there is a / since that is the format strava uses
        new_file = new_file.split("/")
        new_file = new_file[-1]

        #Get the path to save the new file at
        new_loc = os.path.join(dest, new_file)
        fit_files.append(new_loc)

        #Open the zipped file and write to the new location
        with gzip.open(loc, 'rb') as input_file:
            with open(new_loc, 'wb') as output_file:
                shutil.copyfileobj(input_file, output_file)

    return(fit_files)

#Gets the start locations from .fit files in a given folder
#Given a privacy zone will consider first ping outside privacy zone
#Returns a DataFrame
def get_start_locations(src, privacy_zones=None):
    count = 0
    start_locations = []
    for file in os.listdir(src):
        #If it is not a fit file, keep on going
        if not file.endswith(".fit"):
            continue
    
        count += 1

        #Import the fit file
        fitfile = fitparse.FitFile(os.path.join(src, file))

        start_found = False

        run_data = {}

        in_privacy_zone = False
        for record in fitfile.get_messages("record"):
            #Have we encountered a privacy zone?

            #Initialize our location as None
            latitude = None
            longitude = None
            distance = 10
            distance_unit ="NA"
            
            record_debug = []
            #Check all the values in the record
            for data in record:
                record_debug.append(f"Name: {data.name} Value: {data.value}")
                if data.name == "position_lat":
                    latitude = data.value
                if data.name == "position_long":
                    longitude = data.value
                if data.name == "distance":
                    distance = data.value
                    distance_unit = data.units

            #If our Latitude and Longitude have been found, try the point
            if latitude != None and longitude != None:
                #Must convert to degrees from FIT
                cur_loc = (float(latitude) / 11930465.0, float(longitude) / 11930465.0)
                if not check_in_privacy_zone(cur_loc, privacy_zones):
                    run_data["Latitude"] = cur_loc[0]
                    run_data["Longitude"] = cur_loc[1]
                    run_data["Distance"] = float(distance)
                    run_data["Privacy"] = in_privacy_zone
                    start_locations.append(run_data)
                    #Print out our distance into the run the first point is
                    #If we started in a privacy zone
                    if in_privacy_zone:
                        pass
                        #print(f"Distance {distance}")
                        #print(f"Units: {distance_unit}")
                    start_found = True
                    break
                else:
                    in_privacy_zone = True
            
        #Note activities with HR data will have fit files without location
        if not start_found:
            print(f"{file} has no valid locations outside of a privacy zone.")
            #print("Debug log:")
            #print(record_debug)

    print(f"{count} files checked.")

    #CAST TO DATAFRAME
    #Format the coordinates into the appropriate Dataframe
    start_df= pd.DataFrame(start_locations)
    #start_locations = [list(t) for t in start_locations]
    #start_df = pd.DataFrame(start_locations, columns = ['Latitude', 'Longitude'])

    return start_df

#Accepts a path to a google maps API key
#Returns string Key
def load_gmaps_key(key_loc = 'google_maps_token.txt'):
    with open(key_loc, 'r') as f:
        key = f.read()
        return key

#Checks if the location is within the privacy zone (or in any in the list)
#Takes loc, tuple of (lat, long) in degrees
#Takes zones, list of dictionaries
#Returns boolean, true if it is within a privacy zone
#TODO Actually implement this
def check_in_privacy_zone(loc, zones):
    for zone in zones:
        #GET coords from zone address
        zone_lat = zone['Latitude']
        zone_long = zone['Longitude']

        #Get distance in meters
        geod = Geodesic.WGS84
        g = geod.Inverse(loc[0], loc[1], zone_lat, zone_long)
        g_dist = g['s12']
        if  g_dist < zone['Radius'] * 1000:
            return True

    return False

#Accepts Dataframe of Privacy Zones
#Returns List of Dictionaries with addres, lat, long, radius
def get_privacy_coords(zones):
    if not isinstance(zones, pd.DataFrame):
        print("Not a DataFrame, returing []")
        return []
    
    privacy_zones = []
    gmaps_key = load_gmaps_key()
    gmaps = googlemaps.Client(key=gmaps_key)
    for index, zone in zones.iterrows():
        my_zone = {}
        my_zone["Address"] = zone["Address"]
        zone_maps = gmaps.geocode(zone["Address"])
        zone_maps = zone_maps[0]
        zone_geometry = zone_maps['geometry']
        zone_loc = zone_geometry['location']

        #Actually get the radius value as a flaot
        radius = zone["Radius"]
        radius = radius.split(" ")
        radius = float(radius[0])
        my_zone["Radius"] = radius

        my_zone["Latitude"] = zone_loc['lat']
        my_zone['Longitude'] = zone_loc['lng']

        
        privacy_zones.append(my_zone)

    return privacy_zones


#Accepts start points and optionally privacy and cluster dataframes
#Outputs dataframe to be mapped
def merge_dataframes(starts, privacy=pd.DataFrame(), clusters=pd.DataFrame()):
    start_list = starts.to_dict(orient='records')
    privacy_list = []
    cluster_list = []
    result = []

    if not privacy.empty:
        privacy_list = privacy.to_dict(orient='records')
    if not clusters.empty:
        cluster_list = clusters.to_dict(orient='records')

    #Add tags to our starts then add to list
    for start in start_list:
        #Apply Proper Type
        if start['Privacy']:
            start['Type'] = 'Private Start'
            start['Size'] = float(start['Distance']) / 111
            if start['Size'] > 1600 / 111:
                start['Size'] = 1600 / 111
        else:
            start['Type'] = 'Public Start'
            start['Size'] = 100
        start['Text'] = ''
        result.append(start)

    #add tags to privacy zones and add to list
    for zone in privacy_list:
        zone['Type'] = 'Privacy_Zone'
        zone['Text'] = f"Radius: {zone['Radius']}km"
        zone['Size'] = 100
        result.append(zone)

    #Add our clusters to list
    for cluster in cluster_list:
        cluster['Text'] = ''
        cluster['Size'] = 100
        result.append(cluster)

    result = pd.DataFrame(result)
    return result

#Takes a list of coords and draws them on mapbox using the associated token
#Takes Starts, Privacy Zones, Clusters, as DataFrames with Latitude, Longitude, Type, and Text Columns
#Privacy Zones must also have a radius Column
#TODO TAKE COORDS AS DF
def draw_map(start_df, privacy_zones=None, clusters=None, token_path="mapbox_token.txt", layer =""):
    map_df = merge_dataframes(start_df, privacy_zones, clusters)

    px.set_mapbox_access_token(open(token_path).read())
    fig = px.scatter_mapbox(
        data_frame=map_df,
        lat='Latitude',
        lon='Longitude',
        text='Text',
        color='Type',
        #size='Size',
        #size_max=1600/111,
        size='Size',
        size_max=20,
        zoom=7)

    #Want this so that we do not need a token
    if layer != "":
        fig.update_layout(mapbox_style='open-street-map')

    fig.update_layout(title= 'Map of Start Locations')
    fig.show()

#Accepts Dataframe
#Saves a csv file
def save_points(points, path='output_points.csv'):
    points.to_csv(path_or_buf=path)
    return

#This will be a class to manage the activity file
#Will handle importing data from a folder
#Also want to have maps from an activity file
class Activity_Manager:

    #Loads in and stores the Dataframe from the activity path
    def __init__(self, activity_path):
        self.activity_df = pd.read_csv(activity_path)

    #Returns DataFrame containing only activities of a specified type,
    #setting gps to true gives only activities with an associated FIT file 
    def get_activities_of_type(self, activity_type, gps=False):
        activities = [self.activity_df["Activity Type"] in activity_type]

        #Drop non-mapped activities
        if gps:
            activities = activities.dropna(subset=['Filename'])

        return activities

'''
privacy_zone = pd.read_csv('caleb_privacy_zones.csv')
privacy_coords = get_privacy_coords(privacy_zone)

#starts = get_start_locations('fit_files', privacy_zones=privacy_coords)
starts = pd.read_csv('output_points.csv')
draw_map(starts, privacy_zones = privacy_coords)
'''