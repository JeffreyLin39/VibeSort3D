from camera import capture_image
from detect import process_image
from communication import classify_crop
from arm_movement import construct_serial_message, open_serial, send_and_wait
import os
import cv2
#hardcoding the bins for now
bins = {
    "red" : 10,
    "blue": 20,
    "yellow": 29,
}

default_bin = 0

def main():
    ser = open_serial()
    image = capture_image()
    detections, crops = process_image(image)
    for i, center_x, center_y in detections:
        crop = crops[i]
        image_id = str(i)
        id, color = classify_crop(image_id,crop)
        if color == "error":
            continue

        color = color.lower()
        print("Color of brick:", color)
        bin_position = bins.get(color.lower(), default_bin)
        message = construct_serial_message(center_x, center_y, bin_position)
        send_and_wait(ser, message)
    ser.close()
    # while True():
    #     image = capture_image()
    #     detections, crops = process_image(image)
    #     #send shit to steven's backend for classification
    #     #wait for response
    #     #response recieved, move arm accordingly

# def test_send_and_receive():
#     ser = open_serial()  # or your correct port

#     try:
#         msg = construct_serial_message(1000.0, 600.0, 15.24)
#         send_and_wait(ser, msg, expected_response="DONE")
#         print("✅ Test passed: received DONE from Arduino")
#     except Exception as e:
#         print("❌ Test failed:", e)
#     finally:
#         ser.close()
#         print("🔌 Serial connection closed")   
if __name__ == "__main__":
    main()