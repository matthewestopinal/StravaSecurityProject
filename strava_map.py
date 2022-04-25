import strava_data as sd
import pandas as pd
import argparse

def parseCmdLineArgs():
    parser = argparse.ArgumentParser(description='Draw Strava Coordinates on the Map.')
    
    parser.add_argument('-i', '--input', default = 'output_points.csv', help='Path of CSV file to get points from')
    parser.add_argument('-t', '--token', default="mapbox_token.txt", help='Location of Mapbox token, required for Default Layer')
    parser.add_argument('-l', '--layer', default="", help="Mapbox layer to draw. If no token, use open-street-map")
    
    return parser.parse_args()

def main():
    args = parseCmdLineArgs()
    starts = pd.read_csv(args.input)
    sd.draw_map(starts)

if __name__ == "__main__":
    main()