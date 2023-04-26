# AQUACROP CAMERA APP
This app is used to calculate aquacrop for the cameras

The library will have its own architecture to allow using others libraries in the future

## aquacrop wrapper
Aquacrop wrapper have the following classes:
* Crop
* Soil
* Irrigation 
* Weather 
* AquacropWrapp

## TODO

Next step:

1. Add the python library to the node server
2. connect NodeJS to it
3. Use the canopy cover to update the aquacrop model
4. Create a page to show the aquacrop results

**NODE SERVER**
We have to addapt the node server to allow the user to see the aquacrop results.

The node server only will call the python algorith via the console. A good approach will be to create a venv inside the python part and uses this python interpreter to run the algorith.

**PYTHON PART**
The algorith have to work inside the main server (In the raspberry PI). This is the best approach as we will have direct access to all the images. 
* Create a class that read the images and get the canopy cover. Also the class should have a canopeo algorith to get the canopy in a specific image portion. 
* Create an algorith that calculate all the canopy cover of all the images and store it in a binary file. After do that it is necessary to create a backup of the images.

**REACT PART**
Now we have the algorithm that is working (However I dont have the part that update the algorithm based in the sensor, this will come later)
* Create a page inside the react app that show the canopy cover of the images.


**FUTURE WORK:**
it could be a better option to access the weather station that is in the field. Maybe in the future. I don have time now
