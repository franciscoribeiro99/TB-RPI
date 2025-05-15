import os
import time
import threading
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

# Capture + analyse
def should_capture(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Calculate standard deviation of pixel values
    std_dev = np.std(gray)
    return std_dev > THRESHOLD_STD

# Save image
def save_image(frame, folder):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = os.path.join(folder, f"image_{timestamp}.jpg")
    cv2.imwrite(path, frame)
    print(f"Image saved: {path}")

# Camera initialization
def initialize_picamera(IR_mode=True):
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration(main={"size": (2592, 1944)}))
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

# Handle PiCamera thread
def handle_picamera(folder):
    picam2 = initialize_picamera(IR_mode=True)
    try:
        while True:
            frame = picam2.capture_array()
            if should_capture(frame):
                save_image(frame, folder)
            time.sleep(CAPTURE_INTERVAL)
    except KeyboardInterrupt:
        print("PiCamera stopped.")
    finally:
        picam2.close()


# Handle USB camera thread
def handle_usb_camera(index, folder):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print(f"Failed to open USB camera {index}")
        return
    try:
        while True:
            ret, frame = cap.read()
            if ret and should_capture(frame):
                save_image(frame, folder)
            time.sleep(CAPTURE_INTERVAL)
    except KeyboardInterrupt:
        print(f"USB camera {index} stopped.")
    finally:
        cap.release()


# Main function
def main():
    folder_picam = create_folder("images_picam")
    folder_usb = create_folder("images_usb")

    thread_picam = threading.Thread(target=handle_picamera, args=(folder_picam,))
    thread_usb = threading.Thread(target=handle_usb_camera, args=(0, folder_usb))  # USB cam index 0

    thread_picam.start()
    thread_usb.start()

    thread_picam.join()
    thread_usb.join()

if __name__ == "__main__":
    main()
