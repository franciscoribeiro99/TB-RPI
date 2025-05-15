import os
import time
from datetime import datetime
from picamera2 import Picamera2
import cv2
import numpy as np

# Parameters
THRESHOLD_STD = 10.0  # seuil minimal de variation
CAPTURE_INTERVAL = float(os.getenv("CAPTURE_INTERVAL", "0.2"))  # en secondes

# Create folder for images
def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

# Camera initialization
def initialize_camera(IR_mode=True):
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration(main={"size": (640, 480)}))
    picam2.start()
    if IR_mode:
        picam2.set_controls({
            "AwbEnable": False,
            "AwbMode": 0,
            "AnalogueGain": 4.0,
            "ExposureTime": 10000
        })
    else:
        picam2.set_controls({
            "AwbEnable": True,
            "AwbMode": 1,
            "AnalogueGain": 1.0,
            "ExposureTime": 100000
        })
    return picam2

# Capture + analyse
def should_capture(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    std_dev = np.std(gray)
    return std_dev > THRESHOLD_STD

# Save image
def save_image(frame, folder):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = os.path.join(folder, f"image_{timestamp}.jpg")
    cv2.imwrite(path, frame)
    print(f"Image saved: {path}")

# Main function
def main():
    folder = create_folder("images")
    picam2 = initialize_camera(IR_mode=True)

    try:
        while True:
            frame = picam2.capture_array()
            if should_capture(frame):
                save_image(frame, folder)
            time.sleep(CAPTURE_INTERVAL)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        picam2.close()

if __name__ == "__main__":
    main()
