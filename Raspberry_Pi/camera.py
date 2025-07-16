import subprocess
import cv2

def capture_image(output_path="capture.jpg"):
    subprocess.run([
            "libcamera-still",
            "-o", output_path,
            "-n"  # no preview window
        ], check=True)
    image = cv2.imread(output_path)
    cv2.imwrite("test.jpg", image)
    # image = cv2.imread("wood.jpg")
    return image
