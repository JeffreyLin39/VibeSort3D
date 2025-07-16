from camera import capture_image
from detect import process_image
from communication import classify_crop
import os
import cv2
#hardcoding the bins for now
bins = {
    "red" : (0,0),
    "blue": (0,0),
    "yellow": (0,0),
}

default_bin_pos = (0,0)

def main():
    #Just for testing purposes

    image = capture_image()
    detections, crops = process_image(image)

    for i, center_x, center_y in detections:
        crop = crops[i]
        image_id = str(i)
        res = classify_crop(image_id,crop)
        print(res)
    # while True():
    #     image = capture_image()
    #     detections, crops = process_image(image)
    #     #send shit to steven's backend for classification
    #     #wait for response
    #     #response recieved, move arm accordingly
    
        
if __name__ == "__main__":
    main()