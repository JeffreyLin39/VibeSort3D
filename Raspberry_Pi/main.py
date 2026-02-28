from camera import capture_image
from detect import process_image
from communication import classify_crop
from arm_movement import (
    construct_serial_message, 
    send_and_wait, 
    identify_arduinos,
    motor_on,
    motor_off
)
import time

# Hardcoding the bins for now
bins = {
    "1": 10,
    "2": 20,
    "3": 29,
}

default_bin = 0

# How long to wait after stopping motor before processing (seconds)
SETTLE_TIME = 2


def main():
    # Identify and connect to both Arduinos
    print("🔍 Searching for Arduinos...")
    gantry_ser, motor_ser = identify_arduinos()
    
    if not gantry_ser:
        print("❌ ERROR: Could not find GANTRY Arduino!")
        return
    if not motor_ser:
        print("❌ ERROR: Could not find MOTOR Arduino!")
        return
    
    print("✅ Both Arduinos connected successfully")
    
    try:
        # # Start with motor ON (vibrating to feed pieces)
        # motor_on(motor_ser)
        
        # Main loop - runs continuously
        while True:
            # Capture and detect
            image = capture_image()
            detections, crops = process_image(image)
            
            if detections:
                print(f"🧱 Detected {len(detections)} piece(s)")
                
                # # Stop motor and wait for pieces to settle
                motor_off(motor_ser)
                print(f"⏳ Waiting {SETTLE_TIME}s for pieces to settle...")
                time.sleep(SETTLE_TIME)
                
                # Take a fresh image after settling
                print("📸 Capturing settled image...")
                image = capture_image()
                detections, crops = process_image(image)
                
                if not detections:
                    print("⚠️ No pieces detected after settling, resuming motor")
                    motor_on(motor_ser)
                    continue
                
                print(f"🧱 Processing {len(detections)} piece(s)")
                
                # Process each detected piece
                for i, center_x, center_y in detections:
                    crop = crops[i]
                    image_id = str(i)
                    id, color = classify_crop(image_id, crop)
                    
                    if color == "error":
                        print(f"⚠️ Classification error for piece {i}, skipping")
                        continue
                    
                    color = color.lower()
                    print(f"🎨 Piece {i}: color = {color}")
                    
                    bin_position = bins.get(color, default_bin)
                    message = construct_serial_message(center_x, center_y, bin_position)
                    send_and_wait(gantry_ser, message)
                
                # All pieces processed, turn motor back on
                motor_on(motor_ser)
            else:
                # No pieces detected, keep vibrating and check again
                # Small delay to avoid hammering the camera
                time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        # Cleanup
        motor_off(motor_ser)
        gantry_ser.close()
        motor_ser.close()
        print("🔌 Serial connections closed")


if __name__ == "__main__":
    main()