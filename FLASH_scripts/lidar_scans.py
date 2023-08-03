import bpy
from bpy import data as D
from bpy import context as C
from mathutils import *
from math import *
import glob, os

import blensor
import re

def parse_episode_number(string):
    match = re.search(r"ep_(\d+)", string)
    if match:
        episode_number = int(match.group(1))
        return episode_number
    else:
        return None


def create_folder_if_not_exists(directory, folder_name):
    folder_path = os.path.join(directory, folder_name)
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

if __name__ == "__main__":

    destination_directory = "FLASH_TL/LIDAR"
    ep_num = parse_episode_number(bpy.data.filepath)

    # Get the source directory
    start = "category"
    index = bpy.path.abspath("//").find("category")
    source_directory = ""
    if index != -1:
        source_directory = bpy.path.abspath("//")[index:]
        print(source_directory)
    else:   
        print("Start pattern not found")

    # Parse folder names and create directories in the destination directory
    directories = source_directory.split(os.path.sep)
    print(directories)
    new_directory = os.path.join(destination_directory, *directories)

    os.makedirs(new_directory, exist_ok=True)
    destination_directory = new_directory
    create_folder_if_not_exists(destination_directory, f"episode_{ep_num}/")
    destination_directory += f"episode_{ep_num}/"
    print(f"Created directory: {destination_directory}")

    """If the scanner is the default camera it can be accessed for example by bpy.data.objects["Camera"]"""
    scanner = bpy.data.objects["Camera.001"]

    """Scan the scene with the Velodyne scanner and save it to the file "/tmp/scan.pcd"
        Note: The data will actually be saved to /tmp/scan00000.pcd and /tmp/scan_noisy00000.pcd
    """

    for i in range (0,191):
        bpy.context.scene.frame_set(i)
        bpy.context.scene.update()
        blensor.blendodyne.scan_advanced(scanner_object=scanner, 
                                        rotation_speed = 30.0, 
                                        simulation_fps=30, 
                                        angle_resolution = 0.1728, 
                                        max_distance = 120, 
                                        evd_file=f'{destination_directory}/lid_ep{ep_num}_fr{i}.pcd',
                                        noise_mu=0.0, 
                                        noise_sigma=0.03, 
                                        start_angle = 0.0, 
                                        end_angle = 360.0, 
                                        evd_last_scan=True, 
                                        add_blender_mesh = False, 
                                        add_noisy_blender_mesh = False, 
                                        frame_time = (1.0 / 30.0), 
                                        simulation_time = 0.0, 
                                        world_transformation=Matrix())
        os.remove(f'{destination_directory}/lid_ep{ep_num}_fr{i}')
        os.remove(f'{destination_directory}/lid_ep{ep_num}_fr{i}_noisy00000.pcd')
        os.rename(f'{destination_directory}/lid_ep{ep_num}_fr{i}00000.pcd', f'{destination_directory}/lid_ep{ep_num}_fr{i}.pcd')