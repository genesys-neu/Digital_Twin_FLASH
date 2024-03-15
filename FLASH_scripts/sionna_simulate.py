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

# Load integrated scene by configuring the Mitsuba XML scene path
scene_files = ['../blend_files/FLASH_open_los.xml',
               '../blend_files/FLASH_open_nlos.xml',
               '../blend_files/FLASH.xml',
               '../blend_files/FLASH_nlos.xml']
for scene_file in scene_files:
    scene = load_scene(scene_file)
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
            total_beam_df.to_csv('Twin-1_NLOS.csv')
        else:
            total_beam_df.to_csv('Twin-1_LOS.csv')


    # Iterate over locations along the vehicle's trajectory
    # Transmitter height is 95 cm
    # Receiver height is 167.5 cm
    #  Distance between transmitter and receiver 4.33 m apart
    # powers_db = pd.DataFrame()
    # orientation: have receiver and basestation look at each other, then change height of transmitter and receiver
    else:
        num_reflection_cases = [1, 3]
        for num_reflects in num_reflection_cases:
            receiver_locations = pd.read_csv('true_locs.csv', sep=',', header=0)
            for row in range(1, 201):
                scene.remove("tx")
                scene.remove("rx")
                tx = Transmitter(name="tx",
                            position=[receiver_locations.iloc[0]['X'], 0.95, -receiver_locations.iloc[0]['Y']],
                                    orientation = [0, 0, 0])
                scene.add(tx)
                rx = Receiver(name=f"rx",
                            position=[receiver_locations.iloc[row]['X'],
                                        1.675,
                                        -receiver_locations.iloc[row]['Y']],
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
                    total_beam_df.to_csv(f'Twin-2_NLOS.csv')
                else:
                    total_beam_df.to_csv(f'Twin-3_NLOS.csv')
            else:
                if num_reflects == 1:
                    total_beam_df.to_csv(f'Twin-2_LOS.csv')
                else:
                    total_beam_df.to_csv(f'Twin-3_LOS.csv')