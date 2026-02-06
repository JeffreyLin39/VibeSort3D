import cv2
import numpy as np

X_MIN = 1200
X_MAX = 3400
Y_MIN = 300
Y_MAX = 1900
Y_OFFSET = 2300
X_OFFSET = 3425
def mask_lego_pixels(bgr):
    # Adaptive gamma correction on V channel only (preserves color relationships)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mean_v = hsv[..., 2].mean()
    gamma = np.clip(120.0 / mean_v, 0.6, 1.8)  # target mean ~120
    lut = np.array([((i / 255.) ** (1 / gamma)) * 255 for i in range(256)],
                   dtype=np.uint8)
    hsv[..., 2] = cv2.LUT(hsv[..., 2], lut)

    red1 = cv2.inRange(hsv, (0, 80, 50), (10, 255, 255))
    red2 = cv2.inRange(hsv, (165, 80, 50), (179, 255, 255))
    red = cv2.bitwise_or(red1, red2)

    orange = cv2.inRange(hsv, (10, 100, 80), (18, 255, 255))  
    yellow = cv2.inRange(hsv, (18, 80, 80), (35, 255, 255))
    green = cv2.inRange(hsv, (40, 50, 50), (75, 255, 255))    
    blue = cv2.inRange(hsv, (90, 60, 50), (130, 255, 255))
    brown = cv2.inRange(hsv, (8, 80, 40), (20, 200, 160))

    # White: high value, very low saturation (separated from glare suppression)
    white = cv2.inRange(hsv, (0, 0, 220), (179, 25, 255))

    # Combine all LEGO colors
    lego_colors = cv2.bitwise_or(red, orange)
    lego_colors = cv2.bitwise_or(lego_colors, yellow)
    lego_colors = cv2.bitwise_or(lego_colors, green)
    lego_colors = cv2.bitwise_or(lego_colors, blue)
    lego_colors = cv2.bitwise_or(lego_colors, brown)
    lego_colors = cv2.bitwise_or(lego_colors, white)

    # Suppress wood tones (tightened saturation to avoid removing saturated LEGOs)
    wood_mask1 = cv2.inRange(hsv, (10, 20, 100), (30, 90, 255))   # light wood
    wood_mask2 = cv2.inRange(hsv, (0, 0, 140), (25, 50, 255))     # pale beige
    wood_mask = cv2.bitwise_or(wood_mask1, wood_mask2)

    # Glare suppression (very bright, low saturation, but not as strict as white detection)
    glare_mask = cv2.inRange(hsv, (0, 0, 240), (179, 35, 255))

    # Combine suppression masks
    suppress_mask = cv2.bitwise_or(wood_mask, glare_mask)

    # Apply suppression (but preserve white LEGOs by not using low_sat blanket suppression)
    lego_mask = cv2.bitwise_and(lego_colors, cv2.bitwise_not(suppress_mask))

    # Morphological cleanup: remove noise and fill small holes
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    lego_mask = cv2.morphologyEx(lego_mask, cv2.MORPH_OPEN, kernel)   # remove noise
    lego_mask = cv2.morphologyEx(lego_mask, cv2.MORPH_CLOSE, kernel)  # fill holes

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


# def test_detection(image_path, output_folder="test_output", scale=0.5):
#     """
#     Test detection on a single image.
#     Saves crops and outlined image to output_folder.
#     """
#     import os

#     # Create output folder if it doesn't exist
#     os.makedirs(output_folder, exist_ok=True)

#     # Load image
#     image = cv2.imread(image_path)
#     if image is None:
#         print(f"Error: Could not load image '{image_path}'")
#         return

#     # Scale image
#     image_scaled = cv2.resize(image, (0, 0), fx=scale, fy=scale)

#     # Run detection
#     mask = mask_lego_pixels(image_scaled)
#     contours = find_lego_contours(mask)

#     # Draw red outlines and save crops
#     outlined = image_scaled.copy()
#     crop_id = 0
#     for cnt in contours:
#         x, y, w, h = cv2.boundingRect(cnt)
#         # Check if within ROI bounds
#         if x >= X_MIN * scale and x + w <= X_MAX * scale and y >= Y_MIN * scale and y + h <= Y_MAX * scale:
#             # Draw red rectangle
#             cv2.rectangle(outlined, (x, y), (x + w, y + h), (0, 0, 255), 2)
#             # Save crop
#             crop = image_scaled[y:y + h, x:x + w]
#             crop_path = os.path.join(output_folder, f"crop_{crop_id}.png")
#             cv2.imwrite(crop_path, crop)
#             crop_id += 1

#     # Draw ROI bounding box in green for verification
#     roi_x1, roi_y1 = int(X_MIN * scale), int(Y_MIN * scale)
#     roi_x2, roi_y2 = int(X_MAX * scale), int(Y_MAX * scale)
#     cv2.rectangle(outlined, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 3)

#     # Save outlined image
#     outlined_path = os.path.join(output_folder, "outlined.png")
#     cv2.imwrite(outlined_path, outlined)

#     # Also save the mask for debugging
#     mask_path = os.path.join(output_folder, "mask.png")
#     cv2.imwrite(mask_path, mask)

#     print(f"Saved {crop_id} crops to '{output_folder}/'")
#     print(f"Saved outlined image to '{outlined_path}'")
#     print(f"Saved mask to '{mask_path}'")


# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) < 2:
#         print("Usage: python detect.py <image_path> [output_folder]")
#         sys.exit(1)

#     image_path = sys.argv[1]
#     output_folder = sys.argv[2] if len(sys.argv) > 2 else "test_output"
#     test_detection(image_path, output_folder)