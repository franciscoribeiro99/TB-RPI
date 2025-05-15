import os
import time
import threading
from datetime import datetime
from picamera2 import Picamera2
import cv2
import numpy as np

# Parameters
THRESHOLD_STD = 10.0
CAPTURE_INTERVAL = float(os.getenv("CAPTURE_INTERVAL", "0.2"))

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def save_image(frame, folder):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = os.path.join(folder, f"image_{timestamp}.jpg")
    cv2.imwrite(path, frame)
    print(f"Image saved: {path}")

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

def handle_picamera(folder):
    picam2 = initialize_picamera(IR_mode=True)
    try:
        while True:
            frame = picam2.capture_array()
            save_image(frame, folder)
            time.sleep(CAPTURE_INTERVAL)
    except KeyboardInterrupt:
        print("PiCamera stopped.")
    finally:
        picam2.close()


def handle_usb_camera(folder):
    device_path = '/dev/video1'
    cap = cv2.VideoCapture(device_path)
    if not cap.isOpened():
        print(f"❌ Failed to open USB camera at {device_path}")
        return
    print(f"✅ USB camera opened at {device_path}")
    try:
        while True:
            ret, frame = cap.read()
            if ret:
                save_image(frame, folder)
            time.sleep(CAPTURE_INTERVAL)
    except KeyboardInterrupt:
        print("USB camera thread interrupted.")
    finally:
        cap.release()


def main():
    base_folder = "/app/images"
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    print(f"Base folder created: {base_folder}")
    
    folder_picam = create_folder(os.path.join(base_folder, "images_picam"))
    folder_usb = create_folder(os.path.join(base_folder, "images_usb"))

    thread_picam = threading.Thread(target=handle_picamera, args=(folder_picam,))
    thread_usb = threading.Thread(target=handle_usb_camera, args=(folder_usb,))

    thread_picam.start()
    thread_usb.start()

    thread_picam.join()
    thread_usb.join()

if __name__ == "__main__":
    main()
