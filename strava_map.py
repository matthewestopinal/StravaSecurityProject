import strava_data as sd
import pandas as pd
import argparse

def parseCmdLineArgs():
    parser = argparse.ArgumentParser(description='Draw Strava Coordinates on the Map.')
    
    parser.add_argument('-i', '--input', default = 'output_points.csv', help='Path of CSV file to get points from')
    parser.add_argument('-t', '--token', default="mapbox_token.txt", help='Location of Mapbox token, required for Default Layer')
    parser.add_argument('-l', '--layer', default="", help="Mapbox layer to draw. If no token, use open-street-map")
    parser.add_argument('-p', '--privacy', default="", help="Optional argument to plot Privacy Zone centers")
    parser.add_argument('-c', '--clusters', default="", help="Optional argument to plot clusters")
    
    return parser.parse_args()

def main():
    args = parseCmdLineArgs()
    starts = pd.read_csv(args.input)

    privacy_zones = pd.DataFrame()
    clusters = pd.DataFrame()

    #LOAD PRIVACY ZONES
    if args.privacy != "":
        privacy_zones = pd.read_csv(args.privacy)
        privacy_zones = sd.get_privacy_coords(privacy_zones)
        privacy_zones = pd.DataFrame(privacy_zones)

    #LOAD CLUSTERS
    if args.clusters != "":
        clusters = pd.read_csv(args.clusters)

    sd.draw_map(starts, privacy_zones=privacy_zones, clusters=clusters)

if __name__ == "__main__":
    main()