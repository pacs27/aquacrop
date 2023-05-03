import sys
import json
import datetime
import pandas as pd

PARENT_DIRECTORY_PATH = "/home/pi/aquacrop_cameras"
AQUACROP_WRAPPER_DIRECTORY_PATH = PARENT_DIRECTORY_PATH + "/aquacrop_wrapper"
AQUACROP_DIRECTORY_PATH = AQUACROP_WRAPPER_DIRECTORY_PATH + "/aquacrop"
OWN_UTILS_PATH = AQUACROP_WRAPPER_DIRECTORY_PATH + "/own_utils_py"
DATA_PATH = AQUACROP_WRAPPER_DIRECTORY_PATH + "/data"


sys.path.append(OWN_UTILS_PATH)


from utils.image_procesing.canopeo import Canopeo
from utils.image_procesing.crop_image import crop_image
# read json file 
with open('/home/pi/aquacrop_cameras/aquacrop_wrapper/data/canopy_cover_test.json') as json_file:
    images = json.load(json_file)
    # pandas dataframe
    images_df = pd.DataFrame(images)

images_df["date"] = pd.to_datetime(images_df["timeStamp"], unit='ms')

# select images between 15 and 16

images_between_15_16 = images_df[(images_df["date"].dt.hour > 15)]
images_between_15_16 = images_between_15_16[(images_between_15_16["date"].dt.hour < 17)]

# add column with day-month-year with minimun 2 digits
images_between_15_16["day-month-year"] = images_between_15_16["date"].dt.strftime('%d-%m-%Y')

# delete images with the same dt.day
images_between_15_16 = images_between_15_16.drop_duplicates(subset=['day-month-year'], keep='last')

# delete days before 15-03-2023
images_between_15_16 = images_between_15_16[(images_between_15_16["date"] > datetime.datetime(2023, 3, 15))]

        
    
    

image_fodler_path  = '/home/pi/nfsServer/client1'

for index, image in enumerate(images_between_15_16["imageName"]):

    image_path = image_fodler_path + "/" + image
    # image_path_raspberry_m_3 = './images\image_20230227-093043.jpeg'
    x1 = 1056
    y1 = 0
    x2 = 2200
    y2 = 1500

    canopeo = Canopeo(image_path=image_path,
                      x1=x1, y1=y1, x2=x2,y2=y2
                    )

    # canopeo.show_original_image()

    # canopeo.show_bands_histogram()

    canopeo.calculate_canopeo(param1=0.96, param2=0.96, param3=20)
    
    canopeo_value = canopeo.canopeo_value*100
    
    #update pandas dataframe
    images_between_15_16["canopyCover"].iloc[index] = canopeo_value
    

# save pandas dataframe in json file
images_between_15_16.to_json(DATA_PATH + f"/canopy_cover_{x1}_{y1}_{x2}_{y2}.json", orient="records")

# # canopeo.show_original_and_classified_image()
# image_path = DATA_PATH + "/procesed" + images_between_15_16["imageName"].iloc[0]
# canopeo.save_processed_image(image_path)


    
print("end tests")


# ------------