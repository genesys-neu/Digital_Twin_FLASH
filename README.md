# This is repository to keep track of the Digital Twin project involving FLASH dataset and WI simulation.





# Synthetic Data Generation:

The synthetic data generation portion of this repository will allow us to create multiple scenarios of the ISEC building environment (and other road environments in the future) to allow us to train our ML models more effectively without necessarily needing to create scenarios in the real world. Using Transfer Learning could allow us to train a model using a synthetic dataset and apply it to the real dataset


## How to run synthetic data generation:


### Metadata file:

If a metadata file is not in the /metadata_files directory, or a new one must be created, run the command:

python3 FLASH_scripts/create_metadata.py <number of episodes per category>

The script will run and create a metadata file with the location information of the cars, whether they will/won't be in the scene for the corresponding episode, and for cars 2 and 4, whether they will/won't move (this feature may be added to every vehicle in the scene)

The metadata file will be used to create a blender environment for every episode row in the metadata file, for every category. There will be a default of 10 rows generated, for 10 episodes of data. This is computationally efficient, which is why it is the default, but should/when the need for more data arises, the number of rows in the metadata can be set by the user



### Blender environments:


#### Overview:
The synthetic data is generated using Blender, a 3D animation tool. With Blender, a real world scenario can be simulated in a virtual environment. The format that Blender files are written in is .blend. Essentially, there is one .blend file that simulates one real world scenario (Ex: Category 3, episode 1 would be one real world scenario, there would be a .blend file generated to match that)

There are two .blend files generated for each real world scenario. 1 that is compatible with Blender 3, one that is compatible with Blender 2.79. The former is used to generate image data, as Blender 3 has a rendering engine exclusive to that version that runs significantly faster than the rendering engines in Blender 2.79, allowing for image data creation to occur without the need of a GUI. Blender 2.79 is used to generate LIDAR data as the tool used to create LIDAR data, BlenSor, runs only on Blender 2.79. After contacting the developers, Making BlenSor compatible with Blender 3, or later versions of Blender in general, is not feasible in the short term. The current solution is to have two different blender builds in the repository and one for image data generation and the other for lidar data generation

#### Directory structure:
The .blend files are stored in /blend_files, where there are 3 subdirectories. The first one that should only be edited when making a scenario-agnostic change (building texture, car colors, tree placement, etc.) that you would want to have matched in every generated scenario. this is the /blend_files/template_files subdirectory. This has the template files where every generated .blend file works off of. If a change is needed, be sure to make changes in both template files for the two ?Blender versions

Then there are the /blend_files/blend_files_<modality> subdirectories that contain the scenarios for the two blender builds. In them there are subdirectories called /category_x that denote what category the scenario falls under.
Category 1: No obstacle in front of the basestation 
Category 2: Pedestrian in front of basestation. Also has 3 cases within the category: pedestrian not moving, moving left to right and moving right to left wrt basestation
Category 3: Stationary vehicle in front of basestation
Category 4: Moving vehicle in front of basestation. 2 cases within category: car moving in the same direction as receiver, car moving in opposite of receiver

In total, as of now, there are 7 unique "cases" that are generated. 1 case of cat 1, 3 for cat 2, 1 for cat 3, 2 for cat 4. 2N number of .blend will be generated per case (N being the number of episode rows in the metadata file, 2 because two .blend files must be generated for each build of blender). So if there are 20 episode rows in the metadata file, 140 .blend files would be generated for blender 3 (20, 60, 20 and 40 for cats 1,2,3 and 4, respectively), and the same would go for blender 2.79, leading to 280 .blend files created

#### Command to generate .blend files:
bash FLASH_scripts/create_blend_files.sh

### Image/Lidar generation:
#### Lidar:
For Lidar data generation, BlenSor, a Blender Lidar simulation tool, is used to get a lidar scan, with the receiver camera acting as the lidar sensor, from every frame in a give Blender animation.

#### Image:
For image data generation, a standard feature in Blender's rendering engine is used to render the animation and collect the image data from the receiver front and side view cameras

To get the image and lidar data from all the .blend files, run:
bash FLASH_scripts/collect_data.sh

The image and lidar .png and .pcd files will be saved in FLASH_TL

## Commands:
```
python3 FLASH_scripts/create_metadata.py <number of episodes per category>
bash FLASH_scripts/create_blend_files.sh
bash FLASH_scripts/collect_data.sh
```
