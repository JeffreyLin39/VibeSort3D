import cv2
import numpy as np

X_MIN = 1200
X_MAX = 3400
Y_MIN = 300
Y_MAX = 1900
Y_OFFSET = 2100
X_OFFSET = 3600
def mask_lego_pixels(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    # LEGO color masks
    red1 = cv2.inRange(hsv, (0, 100, 50), (10, 255, 255))
    red2 = cv2.inRange(hsv, (160, 100, 50), (179, 255, 255))
    red = cv2.bitwise_or(red1, red2)

    blue = cv2.inRange(hsv, (90, 80, 50), (130, 255, 255))
    green = cv2.inRange(hsv, (40, 50, 50), (85, 255, 255))
    yellow = cv2.inRange(hsv, (20, 100, 100), (35, 255, 255))
    brown = cv2.inRange(hsv, (10, 100, 30), (20, 255, 180))

    # Tighter white range: reduce false positives from bright wood/glare
    white = cv2.inRange(hsv, (0, 0, 210), (179, 25, 255))

    lego_colors = cv2.bitwise_or(red, blue)
    lego_colors = cv2.bitwise_or(lego_colors, green)
    lego_colors = cv2.bitwise_or(lego_colors, yellow)
    lego_colors = cv2.bitwise_or(lego_colors, white)
    lego_colors = cv2.bitwise_or(lego_colors, brown)

    # Suppress light beige/wood tones
    wood_mask1 = cv2.inRange(hsv, (10, 20, 160), (30, 100, 255))
    wood_mask2 = cv2.inRange(hsv, (0, 0, 180), (30, 40, 255))
    wood_mask = cv2.bitwise_or(wood_mask1, wood_mask2)

    # Additional suppression for glare (very bright and low saturation)
    glare_mask = cv2.inRange(hsv, (0, 0, 230), (179, 40, 255))

    suppress_mask = cv2.bitwise_or(wood_mask, glare_mask)
    not_suppress = cv2.bitwise_not(suppress_mask)

    lego_mask = cv2.bitwise_and(lego_colors, not_suppress)

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
        if x >= X_MIN * scale and x + w <= X_MAX * scale and y >= Y_MIN * scale and y+h <= Y_MAX * scale:
            crop = image[y:y + h, x:x + w]
            crops[crop_id] = crop
            #We scaled the image down by a certain amount, so to record the true coordinates we divide by the scale
            center_x = int((x + w // 2) / scale)
            center_y = int((y + h // 2) / scale)
            detections.append((crop_id, X_OFFSET-center_x, Y_OFFSET-center_y))
            crop_id+=1

    return detections, crops