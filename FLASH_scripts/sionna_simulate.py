import os # Configure which GPU 

gpu_num = 0 # Use "" to use the CPU
os.environ["CUDA_VISIBLE_DEVICES"] = f"{gpu_num}"

import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
    except RuntimeError as e:
        print(e) # Avoid warnings from TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

tf.random.set_seed(1) # Set global random seed for reproducibility

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import os
import csv

# Import Sionna
try:
    import sionna

except ImportError as e:
    # Install Sionna if package is not already installed
    os.system("pip install sionna")
    import sionna

# Import Sionna RT components
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, Camera
from sionna.rt import oriented_object

# For link-level simulations
from sionna.channel import cir_to_ofdm_channel, subcarrier_frequencies, OFDMChannel, ApplyOFDMChannel, CIRDataset
from sionna.nr import PUSCHConfig, PUSCHTransmitter, PUSCHReceiver
from sionna.utils import compute_ber, ebnodb2no, PlotBER
from sionna.ofdm import KBestDetector, LinearDetector
from sionna.mimo import StreamManagement
from sionna.mapping import Constellation
import pandas as pd
import argparse


def calculate_intermediate_points(start_loc, end_loc, time_stamps):
    # Calculate the time difference between start and end timestamps
    start_time = time_stamps.iloc[0]
    end_time = time_stamps.iloc[-1]
    time_diff = end_time - start_time

    # Initialize list to store intermediate points
    intermediate_points = []

    # Iterate over timestamps
    for timestamp in time_stamps:
        # Calculate the percentage of time elapsed
        time_elapsed = timestamp - start_time
        percentage = time_elapsed / time_diff

        # Interpolate intermediate point based on percentage
        intermediate_point = [(1 - percentage) * start_coord + percentage * end_coord
                              for start_coord, end_coord in zip(start_loc, end_loc)]

        # Append intermediate point to the list
        intermediate_points.append(intermediate_point)

    return intermediate_points



# Load integrated scene by configuring the Mitsuba XML scene path
parser = argparse.ArgumentParser(description='Process scene and episode files.')

# Add arguments
parser.add_argument('--scene_file', type=str, help='Path to the scene file')
parser.add_argument('--episode_file', type=str, help='Path to the episode file', default=None)

# Parse the command-line arguments
args = parser.parse_args()

# Extract the scene_file and episode_file values
scene_file = args.scene_file
episode_file = args.episode_file
category= None
speed = None
if episode_file != None:
    episode_df = pd.read_csv(episode_file)

    print(episode_file)
    if "Cat1" in episode_file:
        category = "LOS"
        if "10mph" in episode_file:
            speed = "10mph"
        elif "15mph" in episode_file:
            speed = "15mph"
        elif "20mph" in episode_file:
            speed = "20mph"
    elif "Cat3" in episode_file:
        category = "NLOS"
        if "15mph" in episode_file:
            speed = "15mph"
        elif "20mph" in episode_file:
            speed = "20mph"

    # Extract episode number from the episode file path
    episode_num = os.path.basename(os.path.dirname(episode_file)).split("_")[-1]

    # Generate directory path
    output_dir = os.path.join("test_rf", "sionna", category, speed, f"episode_{episode_num}")
    time_stamp_column = episode_df['time_stamp']
    start_loc = [-7.243222344953057,1.675,5.045067985371953]
    start_loc = [-19.332301207908067,1.675,-11.506852173831517]
    end_loc = [10.443302042895958,1.675,-14.986436063698633]
    tx_loc = [-7.243222344953057,0.95,5.045067985371953]
    intermediate_points = calculate_intermediate_points(start_loc, end_loc, time_stamp_column)
else:
    output_dir = os.path.join("test_rf", "sionna", "base")
print(output_dir)

os.makedirs(output_dir, exist_ok=True)
# Create directory if it doesn't exist

# Extract the "time_stamp" column
scene = load_scene(scene_file)
# locations are [X, Z, -Y] format
# print(intermediate_points)
scene.frequency = 60e9 # in Hz; implicitly updates RadioMaterials

scene.synthetic_array = False # If set to False, ray tracing will be done per antenna element (slower for large arrays)

#Load sampled points along vehicle's trajectory

# Create transmitter
Optimal_Beam = []
total_beam_df = pd.DataFrame()
scene.remove("tx")
scene.remove("rx")
antennas = list(range(1, 32))
antennas.extend([61, 62, 63])
if 'open' in scene_file:
    tx = Transmitter(name="tx",
                    position=[-7.243, 0.95, 5.045],
                            orientation = [0, 0, 0])
    scene.add(tx)
    rx = Receiver(name=f"rx",
                position=[-3.76,
                            1.675,
                            7.51],
                orientation=[10,3.5,10])
    scene.add(rx)
    beam_power = {f"Legacy_{i:02}": -250 for i in antennas}
    for antenna in antennas:
        scene.tx_array = PlanarArray(num_rows=1, 
                                        num_cols=1,
                                        vertical_spacing=1,
                                        horizontal_spacing=1,
                                        pattern="legacy_tx", 
                                        number = antenna,
                                        polarization="V")
            
        # Beam.append("Legacy_" + str(antenna))
        # print("Scanning Pattern " + str(antenna))

        # Configure antenna array for all receivers
        scene.rx_array = PlanarArray(num_rows=1,
                                    num_cols=1,
                                    vertical_spacing=1,
                                    horizontal_spacing=1,
                                    pattern="legacy_rx",
                                    polarization="V")

        # Compute propagation paths
        paths = scene.compute_paths(max_depth=3,
                                    method="fibonacci", # For small scenes the method can be also set to "exhaustive"
                                    num_samples=1e6)     # Number of rays shot into random directions, too few rays can lead to missing paths)          
        
        # Convert paths to Channel Impulse Response
        a, tau = paths.cir()
        received_power = 10 * np.log10(tf.reduce_sum(tf.abs(a)**2, axis=(1, 2, 4, 5))) 
        if received_power < -250:
            beam_power[f"Legacy_{antenna:02}"] = -250

        else:
            beam_power[f"Legacy_{antenna:02}"] = received_power[0][0][0]
        max_beam = max(beam_power, key=lambda x: beam_power[x])
        max_P = beam_power[max_beam]
        # print("Optimal Beam -> ", max_beam, " , Corresponding Power = ", max_P)
        Optimal_Beam.append(max_beam)
        sorted_beams = dict(sorted(beam_power.items(), key=lambda item: item[1], reverse=True))
        # print(sorted_beams)

    # Store beam search results
    sorted_beam_list = [{f"Antenna": key, f"Max Propogated Power(dBm)": value} for key, value in sorted_beams.items()]
    beam_search_df = pd.DataFrame(sorted_beam_list)
    # print(beam_search_df)
    total_beam_df = pd.concat([total_beam_df, beam_search_df], axis=1)
    # Store beam labels for trajectory/episode
    label_df = pd.DataFrame({'Beam Label': Optimal_Beam})
    if "nlos" in scene_file:
        total_beam_df.to_csv(output_dir + 'Twin-1_NLOS.csv')
    else:
        total_beam_df.to_csv(output_dir + 'Twin-1_LOS.csv')


# Iterate over locations along the vehicle's trajectory
# Transmitter height is 95 cm
# Receiver height is 167.5 cm
#  Distance between transmitter and receiver 4.33 m apart
# powers_db = pd.DataFrame()
# orientation: have receiver and basestation look at each other, then change height of transmitter and receiver
else:
    num_reflection_cases = [1, 3]
    for num_reflects in num_reflection_cases:
        total_beam_df = pd.DataFrame()
        receiver_locations = pd.read_csv('true_locs.csv', sep=',', header=0)
        for row in range(len(intermediate_points)):
            # print(intermediate_points[row])
            scene.remove("tx")
            scene.remove("rx")
            tx = Transmitter(name="tx",
                        position=tx_loc,
                                orientation = [0, 0, 0])
            scene.add(tx)
            rx = Receiver(name=f"rx",
                        position=intermediate_points[row],
                        orientation=[10,3.5,10])
            scene.add(rx)
            # Update receiver location
            # print("Current Receiver Location : ", rx.position)

            rx.look_at(tx)
            rx.orientation.y = 0
            # print(rx.orientation)
            scene.preview( show_devices=True, show_paths=True) # Use the mouse to focus on the visualized paths
            # continue

            # Scan beams at each location and record received power
            Beam = []
            power = []
            antennas = list(range(1, 32))
            antennas.extend([61, 62, 63])
            if 'open' in scene_file:
                beam_power = {f"Legacy_{i}": -250 for i in antennas}
            else:
                beam_power = {f"Legacy_{i:02}": -250 for i in antennas}
            for antenna in antennas:
                #The number parameter is used to scan 34 Talon antenna patterns on transmitter side

                scene.tx_array = PlanarArray(num_rows=1, 
                                            num_cols=1,
                                            vertical_spacing=1,
                                            horizontal_spacing=1,
                                            pattern="legacy_tx", 
                                            number = antenna,
                                            polarization="V")
                
                # Beam.append("Legacy_" + str(antenna))
                # print("Scanning Pattern " + str(antenna))

                # Configure antenna array for all receivers
                scene.rx_array = PlanarArray(num_rows=1,
                                            num_cols=1,
                                            vertical_spacing=1,
                                            horizontal_spacing=1,
                                            pattern="legacy_rx",
                                            polarization="V")

                # Compute propagation paths
                paths = scene.compute_paths(max_depth=num_reflects,
                                            method="fibonacci", # For small scenes the method can be also set to "exhaustive"
                                            num_samples=1e6)     # Number of rays shot into random directions, too few rays can lead to missing paths)          

                scene.preview(paths=paths,show_orientations=True, show_devices=True, show_paths=True) # Use the mouse to focus on the visualized paths

                # Convert paths to Channel Impulse Response
                a, tau = paths.cir()

                # Compute Received Power for optimal path
                # Ask suyash about how sionna beam pattern compares to WI
                # confirm the similarities between the WI and Sionna paths
                # Beam forming path similarities
                
                received_power = 10 * np.log10(tf.reduce_sum(tf.abs(a)**2, axis=(1, 2, 4, 5))) 
                # Mimimum Threshold Exception
                if received_power < -250:
                    if 'open' in scene_file:
                        beam_power[f"Legacy_{antenna}"] = -250
                    else:
                        beam_power[f"Legacy_{antenna:02}"] = -250

                else:
                    if 'open' in scene_file:
                        beam_power[f"Legacy_{antenna}"] = received_power[0][0][0]
                    else: 
                        beam_power[f"Legacy_{antenna:02}"] = received_power[0][0][0]

            # Identify optimal beam for current positioning
            # print(beam_power)
            max_beam = max(beam_power, key=lambda x: beam_power[x])
            max_P = beam_power[max_beam]
            # print("Optimal Beam -> ", max_beam, " , Corresponding Power = ", max_P)
            Optimal_Beam.append(max_beam)
            sorted_beams = dict(sorted(beam_power.items(), key=lambda item: item[1], reverse=True))
            # print(sorted_beams)

            # Store beam search results
            sorted_beam_list = [{f"Antennas-{row}": key, f"Power-{row} (dBm)": value} for key, value in sorted_beams.items()]
            beam_search_df = pd.DataFrame(sorted_beam_list)
            # print(beam_search_df)
            total_beam_df = pd.concat([total_beam_df, beam_search_df], axis=1)
            # print(total_beam_df)
            # print(total_beam_df)
        if "nlos" in scene_file:
            if num_reflects == 1:
                total_beam_df.to_csv(output_dir + "Twin-2_NLOS.csv")
            else:
                total_beam_df.to_csv(output_dir + 'Twin-3_NLOS.csv')
        else:
            if num_reflects == 1:
                total_beam_df.to_csv(output_dir + 'Twin-2_LOS.csv')
            else:
                total_beam_df.to_csv(output_dir + 'Twin-3_LOS.csv')