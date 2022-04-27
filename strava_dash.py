import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

data = pd.read_csv('pesto_starts_caleb_privacy_NEW.csv')
data = data.to_dict(orient='records')


lats = []
lons = []
radii = []
for point in data:
    point_dict = {}
    if point['Privacy']:
        lats.append(point['Latitude'])
        lons.append(point['Longitude'])
        radii.append(point['Distance'] * 22)
 
figure, axes = plt.subplots()

for i in range(len(lats)):
    cc = plt.Circle((lons[i], lats[i]), radii[i] / 11100000 * 4, alpha=1, edgecolor='black', fill=None)
    #print(lons[i])
    #print(lats[i])
    axes.add_artist(cc)
    #break

plt.xlim(-86.69,-86.925)
plt.ylim(36.03, 36.25)
plt.title( 'Possible Starting Points' ) 
plt.show()

'''
plt.scatter(lons,lats, s=radii ,  facecolors='none', edgecolors='blue' ) 
 
plt.show()
'''