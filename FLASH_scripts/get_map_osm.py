import bpy
import math

export_path = "FLASH_TL/MITSUBA"


bpy.ops.preferences.addon_enable(module="blender-osm")

bpy.context.preferences.addons["blender-osm"].preferences.dataDir = "blend_files/osm_terrains"
bpy.context.preferences.addons["blender-osm"].preferences.arcgisAccessToken = "AAPK2052bae790e04c7fb3443f14af8d422045sqSTneKr5VWPY7DWqw5AKqNEQ64F1TUVOs1akobd7iEgtBmvGwBskE5OUCou4J"
bpy.data.scenes["Scene"].blosm.maxLat = 42.36162
bpy.data.scenes["Scene"].blosm.minLon = -71.05745
bpy.data.scenes["Scene"].blosm.minLat = 42.35943
bpy.data.scenes["Scene"].blosm.maxLon = -71.05297

bpy.data.scenes["Scene"].blosm.dataType = "terrain"
bpy.ops.blosm.import_data()
bpy.data.scenes["Scene"].blosm.dataType = "osm"
bpy.data.scenes["Scene"].blosm.singleObject = False
bpy.ops.blosm.import_data()

center_lat = ((bpy.data.scenes["Scene"].blosm.maxLat + 
                        bpy.data.scenes["Scene"].blosm.minLat) / 2)

# Convert longitude to radians.
center_lon = ((bpy.data.scenes["Scene"].blosm.maxLon + 
                        bpy.data.scenes["Scene"].blosm.minLon) / 2)

print(center_lat, center_lon)

R=6378137

de = bpy.context.scene.cursor.location.x
dn = bpy.context.scene.cursor.location.y
dLon = de/(R*math.cos(math.pi * center_lat / 180))
dLat = dn/R

print(dLon)
lat0 = center_lat + dLat * 180/math.pi
lon0 = center_lon + dLon * 180/math.pi
print(lat0, lon0)

bpy.ops.export_scene.mitsuba(filepath=export_path + "/my_file.xml")

