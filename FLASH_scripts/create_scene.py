import bpy
import csv
import os
import math

car_objects = ["Car.001", "Car.002", "Car.003", "Car.004"]
pedestrian = "rp_eric_rigged_001"
ferrari = "Ferrari (2)"

def create_folder_if_not_exists(directory, folder_name):
    folder_path = os.path.join(directory, folder_name)
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def make_env_cat_1(header, rows):

    for index, episode in enumerate(rows):


        for car in car_objects:
            # Get the object by name
            obj = bpy.data.objects.get(car)

            if obj is not None:
                # Find the index of the header in the header row
                car_header_index = None
                car_movement_index = None
                car_loc_x = None
                car_loc_y = None
                for index, header_value in enumerate(header):
                    if car in header_value:
                        if car_header_index is None:
                            car_header_index = index
                        elif car_loc_x is None:
                            car_loc_x = index
                        elif car_loc_y is None:
                            car_loc_y = index
                    if car in header_value and "Motion" in header_value:
                        car_movement_index = index
                        print(episode[car_movement_index])
                        break
                
                print(episode[car_header_index])
                print(f"CAR {car} LOCATION: ({episode[car_loc_x]}, {episode[car_loc_y]})")

                # Set the current frame to the start frame
                bpy.context.scene.frame_set(0)

                # remove ferrari and pedestrian from env
                ped_obj = bpy.data.objects.get(pedestrian)
                ferrari_obj = bpy.data.objects.get(ferrari)
                ped_obj.location.z = -1000
                ferrari_obj.location.z = -1000

                # Set the new location for the object
                if episode[car_header_index] == 'Y':
                    print(type(episode[car_loc_x]))
                    obj.location.x = float(episode[car_loc_x])
                    obj.location.y = float(episode[car_loc_y])
                    obj.location.z = 0.5

                elif episode[car_header_index] == 'N':
                    obj.location.z = -100

                # Insert a keyframe for the location
                obj.keyframe_insert(data_path='location')
                ped_obj.keyframe_insert(data_path='location')
                ferrari_obj.keyframe_insert(data_path='location')

                # Set the current frame to the end frame
                bpy.context.scene.frame_set(190)

                # remove ferrari and pedestrian from env
                ped_obj.location.z = -1000
                ferrari_obj.location.z = -1000
                
                # Set the new location for the object
                if episode[car_header_index] == 'Y':
                    obj.location.x = float(episode[car_loc_x])
                    obj.location.y = float(episode[car_loc_y])
                    obj.location.z = 0.5
                    if car_movement_index is not None and episode[car_movement_index] == 'Y':
                        if car == "Car.002":
                            obj.location.x += -72
                            obj.location.y += -62
                        elif car == "Car.004":
                            obj.location.x += 59
                            obj.location.y += 50
                        
                elif episode[car_header_index] == 'N':
                    obj.location.z = -100

                # Insert a keyframe for the location
                obj.keyframe_insert(data_path='location')
                ped_obj.keyframe_insert(data_path='location')
                ferrari_obj.keyframe_insert(data_path='location')


                # Print the updated location
                print(f"The location of object '{obj.name}' has been changed to: {obj.location}")
            else:
                print(f"Object '{obj.name}' not found.")

        # Save the changes
        if "blender3.3.8" in (bpy.app.binary_path):
            episode_file_path = os.path.abspath(f'blend_files/blend_files_camera/category_1/ep_{episode[0]}.blend')
        elif "blensor" in (bpy.app.binary_path):
            episode_file_path = os.path.abspath(f'blend_files/blend_files_blensor/category_1/ep_{episode[0]}.blend')
        bpy.ops.wm.save_as_mainfile(filepath=episode_file_path)


def make_env_cat_2(header, rows):

    # positions of the pedestrian in the 3 cases
    pedestrian_pos_list = [[(-1.05, -5.8, 0), (-1.05, -5.8, 0), 'static'],
                            [(3.53, -9.17, 0), (-4.96, -2.04, 0), 'right_to_left'],
                            [(-4.96, -2.04, 0), (3.53, -9.17, 0), 'left_to_right']]
    for case in pedestrian_pos_list:
        for index, episode in enumerate(rows):


            for car in car_objects:
                # Get the object by name
                obj = bpy.data.objects.get(car)

                if obj is not None:
                    # Find the index of the header in the header row
                    car_header_index = None
                    car_movement_index = None
                    car_loc_x = None
                    car_loc_y = None
                    for index, header_value in enumerate(header):
                        if car in header_value:
                            if car_header_index is None:
                                car_header_index = index
                            elif car_loc_x is None:
                                car_loc_x = index
                            elif car_loc_y is None:
                                car_loc_y = index
                        if car in header_value and "Motion" in header_value:
                            car_movement_index = index
                            print(episode[car_movement_index])
                            break
                    
                    print(episode[car_header_index])

                    # Set the current frame to the start frame
                    bpy.context.scene.frame_set(0)

                    # remove ferrari from env
                    ped_obj = bpy.data.objects.get(pedestrian)
                    ferrari_obj = bpy.data.objects.get(ferrari)
                    ped_obj.location = case[0]
                    ferrari_obj.location.z = -1000

                    # Set the new location for the object
                    if episode[car_header_index] == 'Y':
                        obj.location.x = float(episode[car_loc_x])
                        obj.location.y = float(episode[car_loc_y])
                        obj.location.z = 0.5

                    elif episode[car_header_index] == 'N':
                        obj.location.z = -100

                    # Insert a keyframe for the location
                    obj.keyframe_insert(data_path='location')
                    ped_obj.keyframe_insert(data_path='location')
                    ferrari_obj.keyframe_insert(data_path='location')

                    # Set the current frame to the end frame
                    bpy.context.scene.frame_set(190)

                    # remove ferrari and pedestrian from env
                    ped_obj.location = case[1]
                    ferrari_obj.location.z = -1000
                    
                    # Set the new location for the object
                    if episode[car_header_index] == 'Y':
                        obj.location.x = float(episode[car_loc_x])
                        obj.location.y = float(episode[car_loc_y])
                        obj.location.z = 0.5
                        if car_movement_index is not None and episode[car_movement_index] == 'Y':
                            if car == "Car.002":
                                obj.location.x += -72
                                obj.location.y += -62
                            elif car == "Car.004":
                                obj.location.x += 59
                                obj.location.y += 50
                            
                    elif episode[car_header_index] == 'N':
                        obj.location.z = -100

                    # Insert a keyframe for the location
                    obj.keyframe_insert(data_path='location')
                    ped_obj.keyframe_insert(data_path='location')
                    ferrari_obj.keyframe_insert(data_path='location')


                    # Print the updated location
                    print(f"The location of object '{obj.name}' has been changed to: {obj.location}")
                else:
                    print(f"Object '{obj.name}' not found.")

            # Save the changes
            create_folder_if_not_exists('blend_files/blend_files_camera/category_2', case[2])
            create_folder_if_not_exists('blend_files/blend_files_blensor/category_2', case[2])

            if "blender3.3.8" in (bpy.app.binary_path):
                episode_file_path = os.path.abspath(f'blend_files/blend_files_camera/category_2/{case[2]}/ep_{episode[0]}.blend')
            elif "blensor" in (bpy.app.binary_path):
                episode_file_path = os.path.abspath(f'blend_files/blend_files_blensor/category_2/{case[2]}/ep_{episode[0]}.blend')
            bpy.ops.wm.save_as_mainfile(filepath=episode_file_path)

def make_env_cat_3(header, rows):

    ferrari_loc = (-2, -5, 0.5)

    for index, episode in enumerate(rows):


        for car in car_objects:
            # Get the object by name
            obj = bpy.data.objects.get(car)

            if obj is not None:
                # Find the index of the header in the header row
                car_header_index = None
                car_movement_index = None
                car_loc_x = None
                car_loc_y = None
                for index, header_value in enumerate(header):
                    if car in header_value:
                        if car_header_index is None:
                            car_header_index = index
                        elif car_loc_x is None:
                            car_loc_x = index
                        elif car_loc_y is None:
                            car_loc_y = index
                    if car in header_value and "Motion" in header_value:
                        car_movement_index = index
                        print(episode[car_movement_index])
                        break
                
                print(episode[car_header_index])

                # Set the current frame to the start frame
                bpy.context.scene.frame_set(0)

                # remove ferrari and pedestrian from env
                ped_obj = bpy.data.objects.get(pedestrian)
                ferrari_obj = bpy.data.objects.get(ferrari)
                ped_obj.location.z = -1000
                ferrari_obj.location = ferrari_loc

                # Set the new location for the object
                if episode[car_header_index] == 'Y':
                    obj.location.x = float(episode[car_loc_x])
                    obj.location.y = float(episode[car_loc_y])
                    obj.location.z = 0.5

                elif episode[car_header_index] == 'N':
                    obj.location.z = -100

                # Insert a keyframe for the location
                obj.keyframe_insert(data_path='location')
                ped_obj.keyframe_insert(data_path='location')
                ferrari_obj.keyframe_insert(data_path='location')

                # Set the current frame to the end frame
                bpy.context.scene.frame_set(190)

                # remove ferrari and pedestrian from env
                ped_obj.location.z = -1000
                ferrari_obj.location = ferrari_loc               
                # Set the new location for the object
                if episode[car_header_index] == 'Y':
                    obj.location.x = float(episode[car_loc_x])
                    obj.location.y = float(episode[car_loc_y])
                    obj.location.z = 0.5
                    if car_movement_index is not None and episode[car_movement_index] == 'Y':
                        if car == "Car.002":
                            obj.location.x += -72
                            obj.location.y += -62
                        elif car == "Car.004":
                            obj.location.x += 59
                            obj.location.y += 50
                        
                elif episode[car_header_index] == 'N':
                    obj.location.z = -100

                # Insert a keyframe for the location
                obj.keyframe_insert(data_path='location')
                ped_obj.keyframe_insert(data_path='location')
                ferrari_obj.keyframe_insert(data_path='location')


                # Print the updated location
                print(f"The location of object '{obj.name}' has been changed to: {obj.location}")
            else:
                print(f"Object '{obj.name}' not found.")

        # Save the changes
        if "blender3.3.8" in (bpy.app.binary_path):
            episode_file_path = os.path.abspath(f'blend_files/blend_files_camera/category_3/ep_{episode[0]}.blend')
        elif "blensor" in (bpy.app.binary_path):
            episode_file_path = os.path.abspath(f'blend_files/blend_files_blensor/category_3/ep_{episode[0]}.blend')
        bpy.ops.wm.save_as_mainfile(filepath=episode_file_path)

def make_env_cat_4(header, rows):


    ferrari_loc_list = ['same_direction',
                        'opp_direction']

    for case in ferrari_loc_list:
        for index, episode in enumerate(rows):


            for car in car_objects:
                # Get the object by name
                obj = bpy.data.objects.get(car)

                if obj is not None:
                    # Find the index of the header in the header row
                    car_header_index = None
                    car_movement_index = None
                    car_loc_x = None
                    car_loc_y = None
                    for index, header_value in enumerate(header):
                        if car in header_value:
                            if car_header_index is None:
                                car_header_index = index
                            elif car_loc_x is None:
                                car_loc_x = index
                            elif car_loc_y is None:
                                car_loc_y = index
                        if car in header_value and "Motion" in header_value:
                            car_movement_index = index
                            print(episode[car_movement_index])
                            break
                    
                    print(episode[car_header_index])

                    # Set the current frame to the start frame
                    bpy.context.scene.frame_set(0)

                    # remove ferrari and pedestrian from env
                    ped_obj = bpy.data.objects.get(pedestrian)
                    ferrari_obj = bpy.data.objects.get(ferrari)
                    ped_obj.location.z = -1000
                    car_1_x = bpy.data.objects.get("Car.001").location.x
                    car_1_y = bpy.data.objects.get("Car.001").location.y
                    car_3_x = bpy.data.objects.get("Car.003").location.x
                    car_3_y = bpy.data.objects.get("Car.003").location.y
                    if 'same' in case:
                        ferrari_obj.location.x = car_3_x + 4
                        ferrari_obj.location.y = car_3_y - 4
                    if 'opp' in case:
                        ferrari_obj.rotation_euler.z = math.radians(180)
                        ferrari_obj.location.x = car_1_x - 4
                        ferrari_obj.location.y = car_1_y + 4

                    # Set the new location for the object
                    if episode[car_header_index] == 'Y':
                        obj.location.x = float(episode[car_loc_x])
                        obj.location.y = float(episode[car_loc_y])
                        obj.location.z = 0.5

                    elif episode[car_header_index] == 'N':
                        obj.location.z = -100

                    # Insert a keyframe for the location
                    obj.keyframe_insert(data_path='location')
                    ped_obj.keyframe_insert(data_path='location')
                    ferrari_obj.keyframe_insert(data_path='location')

                    # Set the current frame to the end frame
                    bpy.context.scene.frame_set(190)

                    # remove ferrari and pedestrian from env
                    ped_obj.location.z = -1000
                    if 'same' in case:
                        ferrari_obj.location.x = car_1_x - 4
                        ferrari_obj.location.y = car_1_y + 4
                    if 'opp' in case:
                        ferrari_obj.rotation_euler.z = math.radians(180)
                        ferrari_obj.location.x = car_3_x + 4
                        ferrari_obj.location.y = car_3_y - 4

                    # Set the new location for the object
                    if episode[car_header_index] == 'Y':
                        obj.location.x = float(episode[car_loc_x])
                        obj.location.y = float(episode[car_loc_y])
                        obj.location.z = 0.5
                        if car_movement_index is not None and episode[car_movement_index] == 'Y':
                            if car == "Car.002":
                                obj.location.x += -72
                                obj.location.y += -62
                            elif car == "Car.004":
                                obj.location.x += 59
                                obj.location.y += 50
                            
                    elif episode[car_header_index] == 'N':
                        obj.location.z = -100

                    # Insert a keyframe for the location
                    obj.keyframe_insert(data_path='location')
                    ped_obj.keyframe_insert(data_path='location')
                    ferrari_obj.keyframe_insert(data_path='location')


                    # Print the updated location
                    print(f"The location of object '{obj.name}' has been changed to: {obj.location}")
                else:
                    print(f"Object '{obj.name}' not found.")

            # Save the changes
            create_folder_if_not_exists('blend_files/blend_files_camera/category_4', case)
            create_folder_if_not_exists('blend_files/blend_files_blensor/category_4', case)

            if "blender3.3.8" in (bpy.app.binary_path):
                episode_file_path = os.path.abspath(f'blend_files/blend_files_camera/category_4/{case}/ep_{episode[0]}.blend')
            elif "blensor" in (bpy.app.binary_path):
                episode_file_path = os.path.abspath(f'blend_files/blend_files_blensor/category_4/{case}/ep_{episode[0]}.blend')
            bpy.ops.wm.save_as_mainfile(filepath=episode_file_path)

# def make_env
def read_csv_file(file_path):
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)  # Read the header row
        
        rows = []
        for row in csv_reader:
            rows.append(row)
    
    return header, rows

if __name__ == '__main__':
    
    for i in range(1, 4):
        create_folder_if_not_exists("blend_files/blend_files_camera", f"category_{i}")
        create_folder_if_not_exists("blend_files/blend_files_blensor", f"category_{i}")
    file_path = 'metadata_files/metadata.csv'
    header, rows = read_csv_file(file_path)
    make_env_cat_1(header, rows)
    make_env_cat_2(header, rows)
    make_env_cat_3(header, rows)
    make_env_cat_4(header, rows)