import csv
import random
import math
import sys


car_loc_ranges = [[(25, -30), (10, -16)],
                  [(113, 18), (49, -37)],
                  [(-14, 6), (-37, 27)],
                  [(-25, -95), (30, -47)]]


# Define the column names
columns = ['Episode', 
           'Car.001', 'Car.001_location_x', 'Car.001_location_y',
           'Car.002','Car.002_location_x', 'Car.002_location_y',
           'Car.003', 'Car.003_location_x','Car.003_location_y',
           'Car.004', 'Car.004_location_x','Car.004_location_y',
           'Car.002Motion', 'Car.004Motion']

# Generate random values for each column in subsequent rows
def generate_random_row(episode):
    row = [episode]
    values = ['Y', 'N'] * 3
    random.shuffle(values)

    for car_number in range(1, 5):
        row.append(values[0])  # Car column
        direction_x = car_loc_ranges[car_number - 1][1][0] - car_loc_ranges[car_number - 1][0][0]
        direction_y = car_loc_ranges[car_number - 1][1][1] - car_loc_ranges[car_number - 1][0][1]
        random_num = random.random()
        random_point_x = car_loc_ranges[car_number - 1][0][0] + direction_x * random_num
        random_point_y = car_loc_ranges[car_number - 1][0][1] + direction_y * random_num
        row.append(random_point_x)  # Car location_x
        row.append(random_point_y)  # Car location_y
        
    row.append(values[1])
    row.append(values[2])
    return row

# Generate the CSV file
def generate_csv_file(filename, num_episodes):
    is_empty = True
    num_rows = 0
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        num_rows = len(list(reader))

        if reader and num_rows > 1:
            is_empty = False
    if is_empty:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            for episode in range(1, num_episodes + 1):
                writer.writerow(generate_random_row(episode))
    else:
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            for episode in range(num_rows, num_rows + num_episodes):
                writer.writerow(generate_random_row(episode))



# read number of episodes from command line, default is 10
num_episodes = int(sys.argv[1] if len(sys.argv) > 1 else 10)
generate_csv_file('metadata_files/metadata.csv', num_episodes)  # Generate a CSV file with 10 episodes
