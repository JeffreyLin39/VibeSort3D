import cv2
import numpy as np

X_MIN = 1200
X_MAX = 3400
Y_MIN = 300
Y_MAX = 1900
Y_OFFSET = 2300
X_OFFSET = 3425
def mask_lego_pixels(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mean_v = hsv[..., 2].mean()
    gamma = np.clip(120.0 / mean_v, 0.6, 1.8)   # target mean ~120
    lut = np.array([((i / 255.) ** (1 / gamma)) * 255 for i in range(256)],
                   dtype=np.uint8)
    bgr = cv2.LUT(bgr, lut)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    ranges = [
        ((0,   55, 45), (10, 255, 255)),   # red 1
        ((170, 55, 45), (179,255, 255)),   # red 2
        ((18,  40, 45), (40, 255, 255)),   # yellow
        ((45,  35, 40), (90, 255, 255)),   # green
        ((95,  35, 40), (135,255, 255)),   # blue
        ((0,   0, 210), (179,40, 255)),    # white
        ((6,   70, 30), (22, 200, 170)),   # brown (optional)
    ]
    lego_colors = None
    for lo, hi in ranges:
        m = cv2.inRange(hsv, lo, hi)
        lego_colors = m if lego_colors is None else cv2.bitwise_or(lego_colors, m)

    # Low saturation stuff = wood/background
    low_sat = cv2.inRange(hsv, (0, 0, 0), (179, 60, 255))
    wood = cv2.inRange(hsv, (10, 0, 40), (32, 180, 255))  # hue of the board
    glare = cv2.inRange(hsv, (0, 0, 235), (179, 60, 255))
    suppress = cv2.bitwise_or(wood, glare)
    suppress = cv2.bitwise_or(suppress, low_sat)
    lego_mask = cv2.bitwise_and(lego_colors, cv2.bitwise_not(suppress))

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