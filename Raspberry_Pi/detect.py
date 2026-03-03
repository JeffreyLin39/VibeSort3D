import cv2
import numpy as np
import os
from datetime import datetime

X_MIN = 1200
X_MAX = 3400
Y_MIN = 300
Y_MAX = 1900
Y_OFFSET = 2300
X_OFFSET = 3425
def mask_lego_pixels(bgr):
    # === COLOR-BASED DETECTION FOR BLACK BACKGROUND ===
    
    # Gamma correction to normalize brightness
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mean_v = hsv[..., 2].mean()
    gamma = np.clip(120.0 / mean_v, 0.6, 1.8)
    lut = np.array([((i / 255.) ** (1 / gamma)) * 255 for i in range(256)], dtype=np.uint8)
    hsv[..., 2] = cv2.LUT(hsv[..., 2], lut)
    
    # Specific LEGO color ranges
    # Higher saturation + value thresholds to reject dark mat texture
    red1 = cv2.inRange(hsv, (0, 120, 100), (10, 255, 255))
    red2 = cv2.inRange(hsv, (160, 120, 100), (179, 255, 255))
    red = cv2.bitwise_or(red1, red2)
    
    yellow = cv2.inRange(hsv, (15, 120, 120), (35, 255, 255))
    orange = cv2.inRange(hsv, (10, 120, 120), (20, 255, 255))
    
    # Green: raised thresholds to avoid dark mat (mat has H ~90-110, low S/V)
    green = cv2.inRange(hsv, (35, 100, 100), (85, 255, 255))
    
    # Blue: expanded range but higher V to catch bright blue, reject dark mat
    blue = cv2.inRange(hsv, (85, 80, 100), (135, 255, 255))
    
    # White LEGOs
    white = cv2.inRange(hsv, (0, 0, 200), (179, 40, 255))
    
    # Combine all colors
    lego_mask = cv2.bitwise_or(red, yellow)
    lego_mask = cv2.bitwise_or(lego_mask, green)
    lego_mask = cv2.bitwise_or(lego_mask, blue)
    lego_mask = cv2.bitwise_or(lego_mask, orange)
    lego_mask = cv2.bitwise_or(lego_mask, white)

    # Larger kernel to remove mat texture noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    lego_mask = cv2.morphologyEx(lego_mask, cv2.MORPH_OPEN, kernel)
    lego_mask = cv2.morphologyEx(lego_mask, cv2.MORPH_CLOSE, kernel)

    return lego_mask


def find_lego_contours(mask, min_area=2000):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

def process_image(image, scale=0.5, debug_output_folder="test_output"):
    """
    Run detection on an in-memory image and, by default, save crops/mask/outlined
    to a debug folder (test_output by default). Returns (detections, crops) as before.
    """
    # Resize and run the core detection pipeline (same as before)
    image = cv2.resize(image, (0, 0), fx=scale, fy=scale)
    mask = mask_lego_pixels(image)
    contours = find_lego_contours(mask)

    crops = {}
    detections = []
    crop_id = 0
    for _, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)
        if x >= X_MIN * scale and x + w <= X_MAX * scale and y >= Y_MIN * scale and y + h <= Y_MAX * scale:
            crop = image[y:y + h, x:x + w]
            crops[crop_id] = crop
            # We scaled the image down by a certain amount, so to record the true coordinates we divide by the scale
            center_x = int((x + w // 2) / scale)
            center_y = int((y + h // 2) / scale)
            detections.append((crop_id, X_OFFSET - center_x, Y_OFFSET - center_y))
            crop_id += 1

    # --- Debug output: save crops/mask/outlined/original to a folder, but only if we found any crops ---
    if len(crops) > 0:
        # Create a unique subfolder per call, e.g. test_output/2026-02-28_15-30-12
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        out_dir = os.path.join(debug_output_folder, timestamp)
        os.makedirs(out_dir, exist_ok=True)

        # Save original (resized) image
        original_path = os.path.join(out_dir, "original.png")
        cv2.imwrite(original_path, image)

        # Save crops
        for cid, crop_img in crops.items():
            crop_path = os.path.join(out_dir, f"crop_{cid}.png")
            cv2.imwrite(crop_path, crop_img)

        # Save outlined image with detections and ROI
        outlined = image.copy()
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if x >= X_MIN * scale and x + w <= X_MAX * scale and y >= Y_MIN * scale and y + h <= Y_MAX * scale:
                cv2.rectangle(outlined, (x, y), (x + w, y + h), (0, 0, 255), 2)

        roi_x1, roi_y1 = int(X_MIN * scale), int(Y_MIN * scale)
        roi_x2, roi_y2 = int(X_MAX * scale), int(Y_MAX * scale)
        cv2.rectangle(outlined, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 3)

        outlined_path = os.path.join(out_dir, "outlined.png")
        cv2.imwrite(outlined_path, outlined)

        # Save mask
        mask_path = os.path.join(out_dir, "mask.png")
        cv2.imwrite(mask_path, mask)

    return detections, crops


def test_detection(image_path, output_folder="test_output", scale=0.5):
    """
    Test detection on a single image.
    Saves crops and outlined image to output_folder.
    """
    import os

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image '{image_path}'")
        return

    # Scale image
    image_scaled = cv2.resize(image, (0, 0), fx=scale, fy=scale)

    # Run detection
    mask = mask_lego_pixels(image_scaled)
    contours = find_lego_contours(mask)

    # Draw red outlines and save crops
    outlined = image_scaled.copy()
    crop_id = 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Check if within ROI bounds
        if x >= X_MIN * scale and x + w <= X_MAX * scale and y >= Y_MIN * scale and y + h <= Y_MAX * scale:
            # Draw red rectangle
            cv2.rectangle(outlined, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # Save crop
            crop = image_scaled[y:y + h, x:x + w]
            crop_path = os.path.join(output_folder, f"crop_{crop_id}.png")
            cv2.imwrite(crop_path, crop)
            crop_id += 1

    # Draw ROI bounding box in green for verification
    roi_x1, roi_y1 = int(X_MIN * scale), int(Y_MIN * scale)
    roi_x2, roi_y2 = int(X_MAX * scale), int(Y_MAX * scale)
    cv2.rectangle(outlined, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 3)

    # Save outlined image
    outlined_path = os.path.join(output_folder, "outlined.png")
    cv2.imwrite(outlined_path, outlined)

    # Also save the mask for debugging
    mask_path = os.path.join(output_folder, "mask.png")
    cv2.imwrite(mask_path, mask)

    print(f"Saved {crop_id} crops to '{output_folder}/'")
    print(f"Saved outlined image to '{outlined_path}'")
    print(f"Saved mask to '{mask_path}'")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python detect.py <image_path> [output_folder]")
        sys.exit(1)

    image_path = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else "test_output"
    test_detection(image_path, output_folder)