import pandas as pd
import plotly.express as px
import numpy as np
import fitparse
import gzip
import shutil
import os

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
def get_start_locations(src, privacy_zones={}):
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

        for record in fitfile.get_messages("record"):
            #Initialize our location as None
            latitude = None
            longitude = None
            
            #Check all the values in the record
            for data in record:
                if data.name == "position_lat":
                    latitude = data.value
                if data.name == "position_long":
                    longitude = data.value

            #If our Latitude and Longitude have been found, try the point
            if latitude != None and longitude != None:
                #Must convert to degrees from FIT
                cur_loc = (float(latitude) / 11930465.0, float(longitude) / 11930465.0)
                if not check_in_privacy_zone(cur_loc, privacy_zones):
                    start_locations.append(cur_loc)
                    start_found = True
                    break
            
        #Should be unreached
        if not start_found:
            print(f"{file} has no valid locations outside of a privacy zone.")

    print(f"{count} files checked.")
    return start_locations

#Checks if the location is within the privacy zone (or in any in the list)
#Returns boolean, true if it is within a privacy zone
#TODO Actually implement this
def check_in_privacy_zone(loc, zones):
    return False


#Takes a list of coords and draws them on mapbox using the associated token
def draw_map(coords, token_path="mapbox_token.txt"):
    coords = [list(t) for t in coords]
    df = pd.DataFrame(coords, columns = ['latitude', 'longitude'])
    px.set_mapbox_access_token(open(token_path).read())
    fig = px.scatter_mapbox(data_frame=df, lat='latitude', lon='longitude', size_max=15, zoom=10)
    fig.update_layout(title= 'Map of Start Locations')
    fig.show()

#starts = get_start_locations('fit_files')
#draw_map(starts)
