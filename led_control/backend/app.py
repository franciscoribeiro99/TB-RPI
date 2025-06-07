from flask import Flask, jsonify, request, send_from_directory
import psutil
import os
import subprocess
import threading
import time
import board
import neopixel

# Init GPIO18 LED strip
LED_COUNT = 58  # Nombre de LEDs connectées à GPIO18
LED_BRIGHTNESS = 1.0  # 0.0 à 1.0
PIXEL_ORDER = neopixel.GRB

current_r = 0
current_g = 0
current_b = 0
current_brightness = 100

app = Flask(__name__, static_folder="static")

pixels = neopixel.NeoPixel(
    board.D18,
    LED_COUNT,
    brightness=LED_BRIGHTNESS,
    pixel_order=PIXEL_ORDER,
    auto_write=False,
)


def send_color(r, g, b):
    for i in range(LED_COUNT):
        pixels[i] = (r, g, b)
    pixels.show()


def clear_strip():
    for i in range(LED_COUNT):
        pixels[i] = (0, 0, 0)
    pixels.show()


# Backup logic
backup_status = {"running": False, "start_time": None, "end_time": None, "log": ""}


def run_backup():
    global backup_status
    backup_status["running"] = True
    backup_status["start_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    backup_status["end_time"] = None
    backup_status["log"] = "Sauvegarde en cours..."
    try:
        result = subprocess.run(
            ["/app/transfer_zips.sh", "--force"], capture_output=True, text=True
        )
        backup_status["log"] = result.stdout.strip()
        with open("static/last_upload.txt", "w") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as e:
        backup_status["log"] = f"Erreur: {str(e)}"
    finally:
        backup_status["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        backup_status["running"] = False


@app.route("/api/set-leds", methods=["POST"])
def set_leds():
    global current_r, current_g, current_b, current_brightness
    data = request.get_json()
    current_r = int(data.get("r", 0))
    current_g = int(data.get("g", 0))
    current_b = int(data.get("b", 0))
    current_brightness = int(data.get("brightness", 100))

    scale = current_brightness / 100.0
    r = min(max(int(current_r * scale), 0), 255)
    g = min(max(int(current_g * scale), 0), 255)
    b = min(max(int(current_b * scale), 0), 255)

    send_color(r, g, b)
    return jsonify({"status": "ok"})


@app.route("/api/led-blink")
def led_blink():
    for _ in range(3):
        send_color(255, 0, 0)
        time.sleep(1)
        clear_strip()
        time.sleep(1)
    return jsonify({"status": "blinked"})


@app.route("/api/led-state")
def led_state():
    return jsonify(
        {
            "r": current_r,
            "g": current_g,
            "b": current_b,
            "brightness": current_brightness,
        }
    )


@app.route("/api/stats")
def stats():
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            cpu_temp = int(f.read()) / 1000.0
    except Exception:
        cpu_temp = None

    return jsonify(
        {
            "memory": {
                "used": mem.used // (1024**2),
                "total": mem.total // (1024**2),
                "percent": mem.percent,
            },
            "sd": {
                "used": disk.used // (1024**2),
                "total": disk.total // (1024**2),
                "percent": disk.percent,
            },
            "cpu": {"temperature_celsius": cpu_temp},
        }
    )


@app.route("/api/latest-image")
def latest_image():
    path = os.path.join(app.static_folder, "images/usb_cam_0", "latest.jpg")
    if not os.path.exists(path):
        return jsonify({"image_url": ""})
    return jsonify({"image_url": "/images/usb_cam_0/latest.jpg"})


@app.route("/images/usb_cam_0/<filename>")
def serve_image(filename):
    folder = os.path.join(app.static_folder, "images/usb_cam_0")
    return send_from_directory(folder, filename)


@app.route("/api/last-upload")
def last_upload():
    try:
        with open("static/last_upload.txt", "r") as f:
            return jsonify({"last": f.read().strip()})
    except Exception:
        return jsonify({"last": "No picture uploaded yet"})


@app.route("/api/manual-backup", methods=["POST"])
def manual_backup():
    if backup_status["running"]:
        return jsonify({"status": "running"})
    threading.Thread(target=run_backup).start()
    return jsonify({"status": "started"})


@app.route("/api/backup-status")
def get_backup_status():
    return jsonify(backup_status)


@app.route("/api/backup-log")
def backup_log():
    try:
        with open("static/zip_cron.log", "r") as f:
            return jsonify({"log": f.read()})
    except Exception as e:
        return jsonify({"log": f"Error reading the log: {str(e)}"})


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    finally:
        clear_strip()
