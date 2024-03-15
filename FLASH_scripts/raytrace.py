# %%

colab_compat = True # activate preview

resolution = [480,320] # increase for higher quality of renderings

class ExitCell(Exception):
    def _render_traceback_(self):
        pass

# Configure the notebook to use only a single GPU and allocate only as much memory as needed
# For more details, see https://www.tensorflow.org/guide/gpu

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
import pandas as pd

# %%
# Load integrated scene by configuring the Mitsuba XML scene path
scene = load_scene('blend_files/FLASH_open_nlos.xml')

 # Open 3D preview (only works in Jupyter notebook)
colab_compat = True
'''if colab_compat:
    scene.render(camera="preview", num_samples=512)
    raise ExitCell'''
print(scene.get("_unnamed_5"))
# scene.add()
# scene.remove("_unnamed_5")
# scene.remove("_unnamed_4")
# scene.remove("_unnamed_3")

scene.preview()

# %%
import math
scene.frequency = 60e9 # in Hz; implicitly updates RadioMaterials

scene.synthetic_array = False # If set to False, ray tracing will be done per antenna element (slower for large arrays)
print(scene.objects)


scene.preview( show_devices=True) # Use the mouse to focus on the visualized paths

# %%
import math
# import convert_latlon_to_cart as LL2C

#Load sampled points along vehicle's trajectory

## Create transmitter
receiver_locations = pd.read_csv('true_locs.csv', sep=',', header=0)

scene.remove("tx")
tx = Transmitter(name="tx",
                position=[receiver_locations.iloc[0]['X'],
                        4,
                        -receiver_locations.iloc[0]['Y']],
                          orientation = [0, 0, 0])
scene.add(tx)

Optimal_Beam = []
total_beam_df = pd.DataFrame()
# Iterate over locations along the vehicle's trajectory

# powers_db = pd.DataFrame()
for row in range(1, 201):

    # Update receiver location
    scene.remove("rx")
    X_rx = receiver_locations.iloc[row]['X']
    Y_rx = receiver_locations.iloc[row]['Y']
    rx = Receiver(name=f"rx",
                position=[X_rx,
                            4,
                            -Y_rx],
                orientation=[10,3.5,10])
    print("Current Receiver Location : ", rx.position)

    scene.add(rx)

    scene.preview( show_devices=True, show_paths=True) # Use the mouse to focus on the visualized paths
    # continue

    # Scan beams at each location and record received power
    Beam = []
    power = []
    antennas = list(range(1, 32))
    antennas.extend([61, 62, 63])
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
        paths = scene.compute_paths(max_depth=3,
                                    method="fibonacci", # For small scenes the method can be also set to "exhaustive"
                                    num_samples=1e6)     # Number of rays shot into random directions, too few rays can lead to missing paths)          
        # Visualize paths in the 3D preview
        if not colab_compat:
            scene.render("preview", camera='birds_view', paths=paths, show_devices=True, show_paths=True, resolution=resolution)
            raise ExitCell
        scene.preview(paths=paths, show_devices=True, show_paths=True) # Use the mouse to focus on the visualized paths

        # Convert paths to Channel Impulse Response
        a, tau = paths.cir()

        # Compute Received Power for optimal path
        # Ask suyash about how sionna beam pattern compares to WI
        # confirm the similarities between the WI and Sionna paths
        # Beam forming path similarities
        
        received_power = 10 * np.log10(tf.reduce_sum(tf.abs(a)**2, axis=(1, 2, 4, 5))) 

        # Mimimum Threshold Exception
        if received_power < -250:
            beam_power[f"Legacy_{antenna:02}"] = -250

        else:
            beam_power[f"Legacy_{antenna:02}"] = received_power

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

# Store beam labels for trajectory/episode
label_df = pd.DataFrame({'Beam Label': Optimal_Beam})
total_beam_df.to_csv('Twin_open_nlos.csv' )

# %%
 # Open 3D preview (only works in Jupyter notebook)
colab_compat = True
scene.preview(paths)

# %%
# Select an example object from the scene
so = scene.get("itu_concrete")
print(so.name)

# Print name of assigned radio material for different frequenies
for f in [3.5e9, 2.14e9]: # Print for differrent frequencies
    scene.frequency = f   
    print(f"\nRadioMaterial: {so.name} @ {scene.frequency/1e9:.2f}GHz")
    print("Conductivity:", so.conductivity.numpy())
    print("Complex relative permittivity:", so.complex_relative_permittivity.numpy())
    print("Relative permeability:", so.relative_permeability.numpy())
    # print("Trainable:", so.trainable)

# %%
# We can now access for every path the resulting transfer matrices, the propagation delay,
# as well as the angles of departure and arrival, respectively (zenith and azimuth). 
mat_t, tau, theta_t, phi_t, theta_r, phi_r = paths.as_tuple()

print("Shape of mat_t:", mat_t.shape)
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, Camera, Paths2CIR
# Let us inspect a specific path in detail
path_idx = 1

# The dimensions are batch_size, num_rx, num_tx, max_num_paths, 2, 2] where the transfer matrices have an additional 2x2 dimension
print(f"\n--- Detailed results for path {path_idx} ---\n")
print(f"Transfer matrix:\n{mat_t[0,0,0,path_idx,...]}")
print(f"\nPropagation delay: {tau[0,0,0,path_idx]*1e6:.5f} us\n")
print(f"Zenith angle of departure: {theta_t[0,0,0,path_idx]:.4f} rad")
print(f"Azimuth angle of departure: {phi_t[0,0,0,path_idx]:.4f} rad")
print(f"Zenith angle of arrival: {theta_r[0,0,0,path_idx]:.4f} rad")
print(f"Azimuth angle of arrival: {phi_r[0,0,0,path_idx]:.4f} rad")

# %%
# Default parameters in the PUSCHConfig
subcarrier_spacing = 15e3
fft_size = 48

# %%
# Configure a Paths2CIR instance
p2c = Paths2CIR(sampling_frequency=subcarrier_spacing, # Set to 15e3 Hz
                tx_velocities=[3.,0,0], # We can set additional tx speeds
                rx_velocities=[0,7.,0], # Or rx speeds
                num_time_steps=14, # Number of OFDM symbols
                scene=scene)

# Transform paths into channel impulse responses
a, tau = p2c(paths.as_tuple())

print("Shape of a: ", a.shape)
print("Shape of tau: ", tau.shape)

# %%
t = tau[0,0,0,:]/1e-9 # Scale to ns
a_abs = np.abs(a)[0,0,0,0,0,:,0]
a_max = np.max(a_abs)
# Add dummy entry at start/end for nicer figure
t = np.concatenate([(0.,), t, (np.max(t)*1.1,)])
a_abs = np.concatenate([(np.nan,), a_abs, (np.nan,)])

# And plot the CIR
plt.figure()
plt.title("Channel impulse response realization")

#plt.stem(t, a_abs)
plt.stem(t, -20*np.log10(np.squeeze(np.abs(a))));
plt.xlim([0, np.max(t)])
plt.ylim([-2e-6, a_max*1.1])
plt.xlabel(r"$\tau$ [ns]")
plt.ylabel(r"$|a|$");

# %%
p2c = Paths2CIR(sampling_frequency=1e6, scene=scene)
a, tau = p2c(paths.as_tuple())
print(a)

P_Tx = 0
print("Received Power:", max(P_Tx - (-20*np.log10(np.squeeze(np.abs(a)))) + 30))  #P_Tx = 0

# Visualize channel impulse response
'''order=plt.figure()
plt.stem(np.squeeze(tau)/1e-9, -20*np.log10(np.squeeze(np.abs(a))));
plt.xlabel(r"$\tau$ [ns]")
plt.ylabel(r"Path loss [dB]")
plt.title("Channel impulse response")'''

# %%
max_depths = 3 # evaluate performance up to 15 reflections
depths = range(1,max_depths+1)
ts = []
pl_avg = []
for d in depths:
    # save start time
    t = time.time() 
    # run the ray tracer 
    paths = scene.compute_paths(max_depth=d, method="stochastic")
    # and measure the required time interval
    ts.append(time.time()-t)     

# %%
# and plot results
plt.figure()
plt.plot(depths, ts, color="b")
plt.xlabel("Max. depth")
plt.ylabel("Runtime (s)", color="b")
plt.grid(which="both")
plt.xlim([1, max_depths])


