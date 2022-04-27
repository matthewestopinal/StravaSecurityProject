import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import argparse
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
    if circle:
        for cluster in clusters:
            circle_info.append(cf.least_squares_circle(cluster))
    
        for c in circle_info:
            circle_dict = {}
            circle_dict['Longitude'] = c[1]
            circle_dict['Latitude'] = c[0]
            circle_dict['Type'] = 'Circle'
            out = pd.concat([out, pd.DataFrame([circle_dict])], axis=0)
    return out

def main():
    args = parseCmdLineArgs()
    starts = pd.read_csv(args.input)
    print(starts)
    if args.privacy:
        tmp_list = []
        starts = starts.to_dict(orient='records')
        for start in starts:
            if start['Privacy']:
                tmp_list.append(start)

        starts = pd.DataFrame(tmp_list)

    print(starts.shape)
    clusters = dbscan_clustering(starts, min_samples=args.samples, epsilon=args.epsilon, circle=args.circle)
    clusters.to_csv(path_or_buf=args.output)


if __name__ == "__main__":
    main()