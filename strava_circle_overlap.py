import pandas as pd
import numpy as np
import argparse
import math
import haversine as hs
from haversine import Unit
import matplotlib.pyplot as plt

#pip install haversine
#Used to calculate distance between points

#Accepts a dataframe of start points and a center point
#Uses coordinates then casts to meters
#Distance is given in km
def overlap_grid(input_points, center, granularity = 0.0002):
    #Keep only input points relatively close to center

    #Initialize grid
    #Want our grid to correspond to coords
    #lets try radius of 0.04
    width = 0.04
    cols = int(width / granularity)
    my_grid = np.zeros((cols, cols))
    
    #I will be lat
    #J will be long
    for i in range(cols):
        for j in range(cols):
            lat = center[0] - (width / 2) + i * granularity
            long = center[1] - (width / 2) + j * granularity

            loc1 = (lat, long)
            #Compare to each points in input points
            for index, row in input_points.iterrows():
                loc2 = (float(row['Latitude']), float(row['Longitude']))
                #print(loc2)
                radius = float(row['Distance']) / 1000

                #Calculate distance. If they are within range, increment counter
                dist = hs.haversine(loc1, loc2, unit=Unit.KILOMETERS)

                if dist <= radius:
                    my_grid[i,j] = my_grid[i,j] + 1

    return my_grid

def main():
    starts = pd.read_csv('pesto_starts_caleb_privacy_NEW.csv')
    starts = starts[starts['Privacy'] == True]

    #Example
    center = (36.1420859192645, -86.8083079450525)

    og = overlap_grid(starts, center)

    plt.imshow(og, interpolation='none')
    
    plt.title("Heat Map of Start Radii")
    #plt.xlabel('Latitude')
    #plt.ylabel('Longitude')
    plt.show()
if __name__ == "__main__":
    main()