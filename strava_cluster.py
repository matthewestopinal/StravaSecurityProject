from distutils.command.install_egg_info import safe_name
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import argparse
import math
import circle_fit as cf

def parseCmdLineArgs():
    parser = argparse.ArgumentParser(description='Draw Strava Coordinates on the Map.')
    
    parser.add_argument('-i', '--input', default = 'output_points.csv', help='Path of CSV file to get points from')
    parser.add_argument('-o', '--output', default='clusters.csv', help='Path of output CSV file containing cluster coords')
    parser.add_argument('-e', '--epsilon', default=0.8, type=float, help='Epsilon value for DBScan')
    parser.add_argument('-n', '--samples', default=20, type=int, help='Number of minimum samples for DBScan')
    parser.add_argument('-p', '--privacy', action='store_true', help='Flag to cluster only points modified due to a privacy zone.')
    parser.add_argument('-c', '--circle', action='store_true', help='Fit circle to points in clusters')

    return parser.parse_args()

def get_centroid(cluster):
    length = cluster.shape[0]
    sum_x = np.sum(cluster[:, 0])
    sum_y = np.sum(cluster[:, 1])
    return sum_x / length, sum_y / length


def dbscan_clustering(df, epsilon=0.8, min_samples=20, circle=False):
    df = df.iloc[:, 1:3]
    #print(df)
    kms_per_radian = 6371.0088
    epsilon = epsilon / kms_per_radian
    db = DBSCAN(eps=epsilon, min_samples=min_samples, algorithm='ball_tree', metric='haversine').fit(
        np.radians(df.values))
    cluster_labels = db.labels_
    #print(cluster_labels)
    num_clusters = len(set(cluster_labels)) - 1
    clusters = pd.Series([df.values[cluster_labels == n] for n in range(num_clusters)])
    out = pd.DataFrame(columns=['Latitude', 'Longitude', 'Type'])
    lat = []
    long = []
    type_list = []
    print(clusters)
    for cluster in clusters:
        #Get the 'Midpoint' of a cluster
        min_vals = cluster.min(axis=0)
        max_vals = cluster.max(axis=0)
        mid_lat = (min_vals[0] + max_vals[0]) / 2
        mid_long = (min_vals[1] + max_vals[1]) / 2
        lat.append(mid_lat)
        long.append(mid_long)
        type_list.append('Mid_Point')

        if np.size(cluster) != 0:
            i, j = get_centroid(cluster)
            lat.append(i)
            long.append(j)
            type_list.append('Cluster')
    out['Latitude'] = lat
    out['Longitude'] = long
    out['Type'] = type_list

    circle_info = []

    #Contain 0s for circles unused, 1s if they have
    #Used to combine overlapping circles like a big-brain
    circles_used = []
    if circle:
        for cluster in clusters:
            circle_info.append(cf.least_squares_circle(cluster))
            circles_used.append(0)

        #Want to combine circles within a certain range
        trimmed_circles = []
        #loop through first circle to compare
        for index, circle_1 in enumerate(circle_info):
            close_circles = []
            max_dist = 0

            if circles_used[index] == 1:
                continue
            else:
                circles_used[index] = 1
                close_circles.append(circle_1)

                #Loop through neighbors that have not already been checked
                for index2 in range(index+1, len(circle_info)):
                    if circles_used[index2] == 1:
                        continue
                    circle_2 = circle_info[index2]

                    #Check if circles are mutually visible
                    P = [circle_1[0], circle_1[1]]
                    Pr = circle_1[2]
                    Q = [circle_2[0], circle_2[1]]
                    Qr = circle_2[3]

                    circle_dist = math.dist(P, Q)
                    if circle_dist <= Pr and circle_dist <= Qr:
                        #keep track of the maximum distance
                        if circle_dist > max_dist:
                            max_dist = circle_dist
                        print('Close circles found!')
                    close_circles.append(circle_2)
                    
                    #Mark Circle 2 as used
                    circles_used[index2] = 1

            #Now we need to combine the circles
            #Take average of the locations
            #Take radius as max radius + max distance between center points
            circle_count = len(close_circles)
            sumX = 0
            sumY = 0
            maxR = 0
            for circle in close_circles:
                sumX = sumX + circle[0]
                sumY = sumY + circle[1]
                if circle[3] > maxR:
                    maxR = circle[3]
            
            new_circle = [sumX / circle_count, sumY / circle_count, maxR + max_dist]
            trimmed_circles.append(new_circle)
            #[X,Y, R, variance]

        for c in trimmed_circles:
            circle_dict = {}
            circle_dict['Longitude'] = c[1]
            circle_dict['Latitude'] = c[0]
            circle_dict['Type'] = 'Circle'
            out = pd.concat([out, pd.DataFrame([circle_dict])], axis=0)
    return out

def main():
    args = parseCmdLineArgs()
    starts = pd.read_csv(args.input)
    #print(starts)
    if args.privacy:
        tmp_list = []
        starts = starts.to_dict(orient='records')
        for start in starts:
            if start['Privacy']:
                tmp_list.append(start)

        starts = pd.DataFrame(tmp_list)

    #print(starts.shape)
    clusters = dbscan_clustering(starts, min_samples=args.samples, epsilon=args.epsilon, circle=args.circle)
    clusters.to_csv(path_or_buf=args.output)


if __name__ == "__main__":
    main()