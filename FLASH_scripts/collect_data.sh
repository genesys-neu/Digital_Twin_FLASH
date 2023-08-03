#!/bin/bash
BLENSOR_FILES="blend_files/blend_files_blensor"
CAMERA_FILES="blend_files/blend_files_camera"

# Store file paths in an array variable
blensor_file_paths=()
while IFS= read -r -d '' file; do
  blensor_file_paths+=("$file")
done < <(find "$BLENSOR_FILES" -type f -name "*.blend" -print0)

# Store file paths in an array variable
camera_file_paths=()
while IFS= read -r -d '' file; do
  camera_file_paths+=("$file")
done < <(find "$CAMERA_FILES" -type f -name "*.blend" -print0)

for f in "${blensor_file_paths[@]}"; do
    echo "Performing Lidar scans $f"
    ./blender_builds/blensor/blender $f -b -P FLASH_scripts/lidar_scans.py 
done

for f in "${camera_file_paths[@]}"; do
    echo "Performing Camera scans $f";
    ./blender_builds/blender3.3.8/blender $f -b -P FLASH_scripts/cameraS_images.py
done
