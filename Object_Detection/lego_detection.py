import cv2
import numpy as np
import os
import csv
import argparse
import time

X_MIN = 700
X_MAX = 3700
Y_MIN = 300
Y_MAX = 2300

def mask_lego_pixels(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    colorful = cv2.inRange(hsv, (0, 60, 60), (179, 255, 255))
    white = cv2.inRange(hsv, (0, 0, 200), (179, 30, 255))
    wood_mask = cv2.inRange(hsv, (10, 30, 40), (25, 180, 180))
    not_wood = cv2.bitwise_not(wood_mask)

    lego_mask = cv2.bitwise_or(colorful, white)
    lego_mask = cv2.bitwise_and(lego_mask, not_wood)

    return lego_mask

def find_lego_contours(mask, min_area=2500):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

def draw_bounding_boxes(image, contours, scale=1):
    output = image.copy()
    detections = []

    os.makedirs("crops", exist_ok=True)

    for i, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)
        if x >= X_MIN * scale and x <= X_MAX * scale and y >= Y_MIN * scale and y <= Y_MAX * scale:
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 0, 255), 2)

            label = f"ID: {i}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.9
            thickness = 2
            text_x = x
            text_y = max(y - 10, 0)
            cv2.putText(output, label, (text_x, text_y), font, font_scale, (0, 0, 255), thickness)

            cx = x + w // 2
            cy = y + h // 2
            detections.append((i, cx, cy))

            # 🆕 Save cropped image
            crop = image[y:y + h, x:x + w]
            crop_filename = os.path.join("crops", f"lego_{i}.jpg")
            cv2.imwrite(crop_filename, crop)

    return output, detections

def find_and_crop_images():
    parser = argparse.ArgumentParser(description="LEGO detector")
    parser.add_argument("input_image", help="Path to input image")
    args = parser.parse_args()

    image = cv2.imread(args.input_image)
    if image is None:
        print(f"Error: Could not load image '{args.input_image}'")
        return

    scale = 0.5
    image = cv2.resize(image, (0, 0), fx=scale, fy=scale)

    mask = mask_lego_pixels(image)
    contours = find_lego_contours(mask)
    result_image, detections = draw_bounding_boxes(image, contours, scale)

    cv2.imwrite("output_compressed.jpg", result_image, [cv2.IMWRITE_JPEG_QUALITY, 70])

    with open("lego_detections.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "CenterX", "CenterY"])

        for det in detections:
            lego_id, cx, cy = det
            writer.writerow([lego_id, cx, cy])

find_and_crop_images()
