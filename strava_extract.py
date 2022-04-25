import strava_data as sd
import pandas as pd
import argparse

#Extracts Strava Data and outputs CSV of Start Points
#Optionally Takes Privacy Zones To Consider
#Given Locations to compressed files, will extract them
#MUST BE GIVEN RELATIVE PATHS (I know that's bad)

def parseCmdLineArgs():
    parser = argparse.ArgumentParser(description='Extract Strava start points')
    
    parser.add_argument('-o', '--output', default = 'output_points.csv', help='Path of CSV file to save points to')
    parser.add_argument('-p', '--privacy', default=None, help = 'Optional path of Privacy Zone CSV to consider')
    parser.add_argument('-e', '--extract', help='Boolean to check whether we want to extract FIT files or if we have their location', action='store_true')
    parser.add_argument('-a', '-activity', default='activities.csv', help='Path of Strava activities CSV file.')
    parser.add_argument('-f', '--fit', default='fit_files', help='Location of Fit Files, and or location to extract them to.')
    parser.add_argument('-g', '--googlekey', default="google_maps_token.txt", help='Location of Google Maps Key, REQUIRED FOR PRIVACY ZONES')

    return parser.parse_args()

def main():
    args = parseCmdLineArgs()
    if args.extract:
        gps_files = sd.get_gps_filenames(args.activity)
        sd.unzip_gps_files(gps_files, args.fit)

    privacy_zones = []
    if args.privacy != None:
        zones = pd.read_csv(args.privacy)
        privacy_zones = sd.get_privacy_coords(zones)

    #Load and extract starts
    starts = sd.get_start_locations(args.fit, privacy_zones)
    sd.save_points(starts, args.output)
        

if __name__ == "__main__":
    main()