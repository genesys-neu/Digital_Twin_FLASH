import math
import pandas as pd
import csv
import os

minLon = -71.0874
maxLon = -71.0857
minLat = 42.3372
maxLat = 42.3385


def lat_lon_alt_to_cart(targetLat, targetLon):
    """Converts latitude, longitude, and altitude to cartesian coordinates.

    Args:
    lat: The latitude in degrees.
    lon: The longitude in degrees.

    Returns:
    A tuple of (x, y, z) cartesian coordinates.
    """

    # Define the Earth's radius
    R = 6378137

    # Convert the latitude and longitude of the center point to radians
    centerLat = math.radians((minLat + maxLat) / 2)
    centerLon = math.radians((minLon + maxLon) / 2)

    # Convert target latitude and longitude to radians
    targetLat = math.radians(targetLat)
    targetLon = math.radians(targetLon)

    # Calculate the x and y coordinates
    dLon = targetLon - centerLon
    dLat = targetLat - centerLat

    x = R * dLon * math.cos(centerLat) 
    y = R * dLat 

    # print(x)
    # Print the x, y coordinates
    # print("x:", x)
    # print("y:", y)

    return x, y

center_cart = lat_lon_alt_to_cart(42.33785, -71.08655)
# print(center_cart)
directories = ['../flash/flash/Cat1/opposite/Extract/Cat1_10mph_lr_opposite/',
               '../flash/flash/Cat1/opposite/Extract/Cat1_15mph_lr_opposite/',
               '../flash/flash/Cat1/opposite/Extract/Cat1_20mph_lr_opposite/',
               '../flash/flash/Cat3/static_in_front/Extract/Cat3_15mph_lr_opposite/',
               '../flash/flash/Cat3/static_in_front/Extract/Cat3_20mph_lr_opposite/']

for directory in directories:
    # print("Processing directory:", directory)
    subdirectories = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    for subdir in subdirectories:
        subdir_path = os.path.join(directory, subdir)
        # print("Subdirectory:", subdir_path)
        # Check if 'Synchornized_data_with_SNR.csv' file exists in the subdirectory
        snr_file = os.path.join(subdir_path, 'GPS_data.csv')
        if os.path.exists(snr_file):
            print(snr_file)
            # print("Opening 'Synchornized_data_with_SNR.csv'")
            # df = pd.read_csv('../Richard_coords/opposite_lane_200_points_withHeights.csv')
            df = pd.read_csv(snr_file)
            # Select only the 'lat' and 'long' columns
            receiver_locations = df[['lat', 'long']]
            print(receiver_locations)
            # Append the selected columns to the combined DataFrame
            with open('test.csv', 'w', newline='') as csvf:
                writer = csv.writer(csvf)
                writer.writerow(['X', 'Y', 'Z'])
                for i in range(0, len(receiver_locations)):
                    rec_cart = lat_lon_alt_to_cart(\
                        receiver_locations.iloc[i]['lat'],\
                        receiver_locations.iloc[i]['long'])
                    print(rec_cart)
                    map_cart = (rec_cart[0] - center_cart[0], rec_cart[1] - center_cart[1], 4.95)
                    # print(map_cart)
                    writer.writerow([map_cart[0] +13, map_cart[1] -12, map_cart[2]])
                quit()
    
        else:
            print("'Synchornized_data_with_SNR.csv' does not exist in this subdirectory")