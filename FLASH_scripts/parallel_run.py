import subprocess
import os
import csv
import time
from multiprocessing import Pool


def create_folder_if_not_exists(directory, folder_name):
    folder_path = os.path.join(directory, folder_name)
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def read_csv_file(file_path):
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)  # Read the header row
        
        rows = []
        for row in csv_reader:
            rows.append(row)
    
    return header, rows

def run_blender(header, row):
    subprocess.run(["blender_builds/blensor/blender",
                    "--enable-autoexec",
                    "-b",
                    "blend_files/template_files/blensor_template.blend",
                    "-P",
                    "FLASH_scripts/create_scene.py",
                    "--",
                    str(header),
                    str(row)])

start_time = time.time()
for i in range(1, 4):
    create_folder_if_not_exists("blend_files/blend_files_camera", f"category_{i}")
    create_folder_if_not_exists("blend_files/blend_files_blensor", f"category_{i}")
file_path = 'metadata_files/metadata.csv'
header, rows = read_csv_file(file_path)
with Pool(processes=len(rows)) as pool:    
        pool.starmap(run_blender, [(header, row) for row in rows])

print("--- %s seconds ---" % (time.time() - start_time))