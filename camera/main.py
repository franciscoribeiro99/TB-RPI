import os
import time
import threading
from datetime import datetime
import cv2

# Get environment variables
CAPTURE_INTERVAL = float(os.getenv("CAPTURE_INTERVAL", "0.2"))
MAX_CAMERAS = int(os.getenv("MAX_CAMERAS", "2"))
camera_resolution = os.getenv("CAMERA_RESOLUTION", "640x480")


def create_folder(folder_name):
    os.makedirs(folder_name, exist_ok=True)
    return folder_name


def save_image(frame, folder):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"image_{timestamp}.jpg"
    full_path = os.path.join(folder, filename)
    temp_latest = os.path.join(folder, "latest_tmp.jpg")
    final_latest = os.path.join(folder, "latest.jpg")

    cv2.imwrite(full_path, frame)
    cv2.imwrite(temp_latest, frame)
    os.replace(temp_latest, final_latest)

    print(f"Image saved: {full_path}")


def handle_usb_camera(folder, device_path):
    cap = cv2.VideoCapture(device_path)
    if not cap.isOpened():
        print(f"❌ Failed to open USB camera at {device_path}")
        return

    width, height = map(int, camera_resolution.split("x"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    print(f"✅ USB camera opened at {device_path}")

    failure_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                failure_count += 1
                print(f"Frame read failed from {device_path} ({failure_count})")
                if failure_count > 5:
                    print(f"Too many failures on {device_path}, stopping.")
                    break
                time.sleep(1)
                continue
            save_image(frame, folder)
            failure_count = 0
            time.sleep(CAPTURE_INTERVAL)
    except KeyboardInterrupt:
        print(f" Camera at {device_path} stopped.")
    finally:
        cap.release()


def find_working_cameras(max_devices=10, max_cameras=2):
    working_devices = []
    for i in range(max_devices):
        dev = f"/dev/video{i}"
        cap = cv2.VideoCapture(dev)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                print(f"Found usable camera at {dev}")
                working_devices.append(dev)
            else:
                print(f"Camera at {dev} opened but didn't deliver frames")
            cap.release()
        if len(working_devices) >= max_cameras:
            break
    return working_devices


def main():
    base_folder = "/app/images"
    create_folder(base_folder)

    devices = find_working_cameras(max_cameras=MAX_CAMERAS)

    threads = []
    for idx, dev in enumerate(devices):
        folder = create_folder(os.path.join(base_folder, f"usb_cam_{idx}"))
        t = threading.Thread(target=handle_usb_camera, args=(folder, dev))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
