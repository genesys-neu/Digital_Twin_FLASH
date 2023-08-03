#!/bin/bash

directory_path_blensor="blend_files/blend_files_blensor"
directory_path_camera="blend_files/blend_files_camera"

# Remove .blend files from the first directory and its subdirectories
find "$directory_path_blensor" -type f -name "*.blend" -exec rm -f {} +

# Remove .blend files from the second directory and its subdirectories
find "$directory_path_camera" -type f -name "*.blend" -exec rm -f {} +

./blender_builds/blensor/blender blend_files/template_files/blensor_template.blend -b -P FLASH_scripts/create_scene.py 
./blender_builds/blender3.3.8/blender blend_files/template_files/camera_template.blend -b -P FLASH_scripts/create_scene.py 