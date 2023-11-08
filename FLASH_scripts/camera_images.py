import os
import bpy
import multiprocessing
import re
import time


def parse_episode_number(string):
    match = re.search(r"ep_(\d+)", string)
    if match:
        episode_number = int(match.group(1))
        return episode_number
    else:
        return None

def parse_category_number(string):
    match = re.search(r"category_(\d+)", string)
    if match:
        episode_number = int(match.group(1))
        return episode_number
    else:
        return None



def render_frame(camera_object_name, output_directory):
    # Set the rendering engine to Cycles
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'

    # devices = bpy.context.preferences.addons['cycles'].preferences['devices']

    # for dev in devices:
    #     dev['use'] = 1
    # get_devices() to let Blender detects GPU device
    # print("started")
    # Get the camera object by name
    camera_object = bpy.data.objects.get(camera_object_name)
    # print(camera_object)
    if camera_object is not None:        
        # Check if the camera object is already in the scene collection
        # Set the active camera
        bpy.context.scene.camera = camera_object

        # Set the output properties
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.filepath = output_directory
        
        # Render the current frame with the active camera
        print("rendering")
        bpy.ops.render.render(animation=True)
    else:
        print(f"Camera object '{camera_object_name}' not found.")


def create_folder_if_not_exists(directory, folder_name):
    folder_path = os.path.join(directory, folder_name)
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

if __name__ == "__main__":

    start_time = time.time()
    camera_object_names = ["Camera.001", "Camera.003"]
    destination_directory = "FLASH_TL/IMAGE"
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
    new_directory = os.path.join(destination_directory, *directories)

    os.makedirs(new_directory, exist_ok=True)
    destination_directory = new_directory + f"episode_{ep_num}/"
    print(f"Created directory: {destination_directory}")
    
    output_directories = [f"{destination_directory}/front/img_ep{ep_num}_fr", 
                        f"{destination_directory}/side/img_ep{ep_num}_fr"]

    # Set the frame range for the animation
    start_frame = 0
    end_frame = 190
   

    create_folder_if_not_exists(destination_directory, 'front/')
    create_folder_if_not_exists(destination_directory, 'side/')

    pool = multiprocessing.Pool(processes=len(camera_object_names))

    # Render frames from "Camera.001" perspective for the "front" output
    front_render_args = [("Camera.001", output_directories[0])]
    # Render frames from "Camera.003" perspective for the "side" output
    side_render_args = [("Camera.003", output_directories[1])]

    # Use the worker processes to render frames in parallel
    pool.starmap(render_frame, front_render_args + side_render_args)

    # Close the worker processes pool
    pool.close()
    pool.join()
    print(f"Execution time = {time.time() - start_time}")
