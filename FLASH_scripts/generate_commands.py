import os

# Define the directory to search for episode files
flash_directory = "../flash/flash"

# Function to find all "Synchornized_data_with_SNR.csv" files and their relative directories
def find_episode_files(directory):
    episode_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "Synchornized_data_with_SNR.csv":
                episode_files.append(os.path.join(root, file))
    return episode_files

# Write the commands to a text file
with open("commands.txt", "w") as f:
    # Write the first two commands with only scene_file specified
    f.write("python3 sionna_simulate.py --scene_file=../blend_files/FLASH_open_nlos.xml\n")
    f.write("python3 sionna_simulate.py --scene_file=../blend_files/FLASH_open_los.xml\n")
    
    # Find and write the episode_file for each "Synchornized_data_with_SNR.csv" file
    episode_files = find_episode_files(flash_directory)
    for episode_file in episode_files:
        relative_path = os.path.relpath(episode_file, flash_directory)
        print(relative_path)
        f.write(f"python3 sionna_simulate.py --scene_file=../blend_files/FLASH_open_nlos.xml --episode_file={relative_path}\n")
