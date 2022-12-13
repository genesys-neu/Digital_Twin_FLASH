import numpy as np
import open3d as o3d
from pathlib import Path
import os

if __name__ == "__main__":
    #inputs for directories, don't forget "/" at the end of bin path
    pcd_data_path = input("Enter directory path of PCD data:")
    bin_data_path = input("Enter directory path for .bin data:")
    #create directory for binary data
    if not (os.path.isdir(bin_data_path)):
        os.makedirs(bin_data_path)
    #uses Path library to recursively iterate through pcd directory
    for path in Path(pcd_data_path).rglob('*.pcd'):
        #read and save pcd data as numpy array
        pcd_data = o3d.io.read_point_cloud(str(path), format='pcd')
        bin_data = np.asarray(pcd_data.points)
        #open and write to file
        bin_file = open(bin_data_path + os.path.splitext(path.name)[0] + ".bin", "w")
        bin_data.tofile(bin_file)
        bin_file.close()
    #TODO (?): ask Suyash if bin directory writing should be better
