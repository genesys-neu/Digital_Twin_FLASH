import bpy

def populate(object_name, collection_names):
    fbx_filepath = f"blend_files/{object_name}.fbx"
    bpy.ops.import_scene.fbx(filepath=fbx_filepath)
    existing_object = bpy.data.objects.get(object_name)
    i = 0
    for collection in bpy.data.collections:
        print(collection.name)
        print(any(name in collection.name for name in collection_names))
        if any(name in collection.name for name in collection_names):
        # Loop through each object in the collection
            print(collection)
            for curve_obj in collection.objects:
                if curve_obj.type == 'CURVE':
                    # Create a new object
                    
                    curve_obj.data.path_duration = bpy.data.scenes["Scene"].frame_end
                    new_object = bpy.data.objects.new(existing_object.name + '_' + str(i), existing_object.data)
                    
                    i += 1

                    new_object.scale = existing_object.scale

                    # Link the new object to the current scene
                    bpy.context.collection.objects.link(new_object)
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.view_layer.objects.active = new_object
                    new_object.select_set(True)
                    
                    # Make the object follow the curve
                    follow_path = new_object.constraints.new(type='FOLLOW_PATH')
                    follow_path.target = curve_obj
                    follow_path.use_fixed_location = False  # Unlock the object's location
                    
                    # Set the animation path duration (adjust as needed)
                    follow_path.forward_axis = 'FORWARD_X'
                    follow_path.use_curve_follow = True
                    follow_path.use_curve_radius = True
                    follow_path.forward_axis = 'FORWARD_X'  # Adjust the axis as needed
                    
                    # Set the offset factor to control the position along the curve
                    follow_path.offset_factor = 1.0  # Adjust this value as needed
                    
                    # Keyframe the offset factor to animate the object along the curve
                    follow_path.keyframe_insert(data_path='offset_factor', frame=bpy.data.scenes["Scene"].frame_start)
                    follow_path.keyframe_insert(data_path='offset_factor', frame=bpy.data.scenes["Scene"].frame_end)
                    
                    bpy.ops.constraint.followpath_path_animate(constraint="Follow Path", owner='OBJECT')
                    # Update dependencies and apply the constraint
                    bpy.context.view_layer.update()

    # Set the animation frame range (adjust as needed)
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 250

    bpy.data.objects.remove(bpy.data.objects[object_name], do_unlink=True)

def remove_default_objs():
    default_objects = ['Cube', 'Camera', 'Light']

    # Loop through the default object names
    for obj_name in default_objects:
        # Check if the object exists in the current scene
        if obj_name in bpy.data.objects:
            # Get a reference to the object
            obj = bpy.data.objects[obj_name]

            # Unlink and remove the object
            bpy.data.objects.remove(obj, do_unlink=True)


if __name__ == "__main__":
    remove_default_objs()
    # Set the name of the collection containing the curves
    collection_road_names = ["osm_roads_service", "osm_roads_primary", "osm_roads_secondary", "osm_roads_unclassified"]
    collection_ped_names = ["osm_areas_pedestrian", "osm_paths_footway", "osm_paths_steps", "osm_roads_pedestrian"]
    populate("Car", collection_road_names)
    populate("pedestrian", collection_ped_names)