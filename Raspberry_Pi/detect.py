import cv2
import numpy as np

X_MIN = 1200
X_MAX = 3400
Y_MIN = 300
Y_MAX = 1900
Y_OFFSET = 1900
def mask_lego_pixels(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    colorful = cv2.inRange(hsv, (0, 60, 60), (179, 255, 255))
    white = cv2.inRange(hsv, (0, 0, 200), (179, 30, 255))
    wood_mask = cv2.inRange(hsv, (10, 30, 40), (25, 180, 180))
    not_wood = cv2.bitwise_not(wood_mask)

    lego_mask = cv2.bitwise_or(colorful, white)
    lego_mask = cv2.bitwise_and(lego_mask, not_wood)

    return lego_mask

def find_lego_contours(mask, min_area=2000):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

def process_image(image, scale=0.5):
    image = cv2.resize(image, (0, 0), fx=scale, fy=scale)
    mask = mask_lego_pixels(image)
    contours = find_lego_contours(mask)

    crops = {}
    detections = []
    crop_id = 0
    for _, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)
        if X_MIN * scale <= x <= X_MAX * scale and Y_MIN * scale <= y <= Y_MAX * scale:
            crop = image[y:y + h, x:x + w]
            crops[crop_id] = crop
            #We scaled the image down by a certain amount, so to record the true coordinates we divide by the scale
            center_x = int((x + w // 2) / scale)
            center_y = int((y + h // 2) / scale)
            detections.append((crop_id, center_x-X_MIN, Y_OFFSET-center_y))
            crop_id+=1

    return detections, crops