from camera import capture_image
from detect import process_image
import os
import cv2
def main():
    #Just for testing purposes

    # os.makedirs("crops", exist_ok=True)
    # image = capture_image()
    # detections, crops = process_image(image)
    # for id, crop in crops.items():
    #     filename = f"crops/crop_{id}.jpg"
    #     cv2.imwrite(filename, crop)
    # print(f"Saved {len(crops)} crops.")

    while True():
        image = capture_image()
        detections, crops = process_image(image)
        #send shit to steven's backend for classification
        #wait for response
        #response recieved, move arm accordingly
    
        
if __name__ == "__main__":
    main()