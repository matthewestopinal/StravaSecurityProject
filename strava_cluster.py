import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN


def get_centroid(cluster):
    length = cluster.shape[0]
    sum_x = np.sum(cluster[:, 0])
    sum_y = np.sum(cluster[:, 1])
    return sum_x / length, sum_y / length


def dbscan_clustering(df, epsilon=0.8, min_samples=20):
    df = df.iloc[:, 1:]
    kms_per_radian = 6371.0088
    epsilon = epsilon / kms_per_radian
    db = DBSCAN(eps=epsilon, min_samples=min_samples, algorithm='ball_tree', metric='haversine').fit(
        np.radians(df.values))
    cluster_labels = db.labels_
    num_clusters = len(set(cluster_labels)) - 1
    clusters = pd.Series([df.values[cluster_labels == n] for n in range(num_clusters)])
    out = pd.DataFrame(columns=['Latitude', 'Longitude'])
    lat = []
    long = []
    for cluster in clusters:
        if np.size(cluster) != 0:
            i, j = get_centroid(cluster)
            lat.append(i)
            long.append(j)
    out['Latitude'] = lat
    out['Longitude'] = long
    print(out)
