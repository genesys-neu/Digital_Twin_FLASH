import math
import pandas as pd
import csv

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

    # Print the x, y coordinates
    # print("x:", x)
    # print("y:", y)

    return x, y

receiver_locations = pd.read_csv('../Richard_coords/opposite_lane_200_points_withHeights.csv', sep=',', header=0)
# print(receiver_locations)
receiver_locations_cart = [] 
center_cart = lat_lon_alt_to_cart(42.33785, -71.08655)
with open('true_locs.csv', 'w', newline='') as csvf:
    writer = csv.writer(csvf)
    writer.writerow(['X', 'Y', 'Z'])
    for i in range(0, len(receiver_locations)):
        rec_cart = lat_lon_alt_to_cart(\
            receiver_locations.iloc[i]['lat'],\
            -receiver_locations.iloc[i]['long'])
        map_cart = (rec_cart[0] - center_cart[0], rec_cart[1] - center_cart[1], receiver_locations.iloc[i]['Set Altitude'])
        # print(map_cart)
        writer.writerow([map_cart[0], map_cart[1], map_cart[2]])
    
# print(receiver_locations_cart)