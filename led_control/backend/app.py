from flask import Flask, jsonify, request, send_from_directory
import psutil, os, subprocess, threading, time
from rpi_ws281x import Adafruit_NeoPixel, Color

LED_COUNT      = 58
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 65
LED_INVERT     = False
LED_CHANNEL    = 0

current_r = 0
current_g = 0
current_b = 0
current_brightness = 0

app = Flask(__name__, static_folder='static')

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                          LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

backup_status = {
    "running": False,
    "start_time": None,
    "end_time": None,
    "log": ""
}

def run_backup():
    global backup_status
    backup_status["running"] = True
    backup_status["start_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    backup_status["end_time"] = None
    backup_status["log"] = "Sauvegarde en cours..."
    try:
        result = subprocess.run(["/app/transfer_zips.sh", "--force"], capture_output=True, text=True)
        backup_status["log"] = result.stdout.strip()
        with open("static/last_upload.txt", "w") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as e:
        backup_status["log"] = f"Erreur: {str(e)}"
    finally:
        backup_status["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        backup_status["running"] = False

@app.route('/api/set-leds', methods=['POST'])
def set_leds():
    global current_r, current_g, current_b, current_brightness

    data = request.get_json()
    current_r = int(data.get('r', 0))
    current_g = int(data.get('g', 0))
    current_b = int(data.get('b', 0))
    current_brightness = int(data.get('brightness', LED_BRIGHTNESS))

    print(f"Set LEDs to RGB({current_r},{current_g},{current_b}) with brightness {current_brightness}")
    strip.setBrightness(current_brightness)
    color = Color(current_r, current_g, current_b)
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

    return jsonify({"status": "ok"})


@app.route('/api/stats')
def stats():
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu_temp = None

    # Lire la température CPU (Raspberry Pi)
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            cpu_temp = int(f.read()) / 1000.0  # convertit en °C
    except:
        cpu_temp = None

    return jsonify({
        "memory": {
            "used": mem.used // (1024**2),
            "total": mem.total // (1024**2),
            "percent": mem.percent
        },
        "sd": {
            "used": disk.used // (1024**2),
            "total": disk.total // (1024**2),
            "percent": disk.percent
        },
        "cpu": {
            "temperature_celsius": cpu_temp
        }
    })


@app.route('/api/latest-image')
def latest_image():
    path = os.path.join(app.static_folder, "images/usb_cam_0", "latest.jpg")
    if not os.path.exists(path):
        return jsonify({"image_url": ""})
    return jsonify({"image_url": "/images/usb_cam_0/latest.jpg"})

@app.route('/images/usb_cam_0/<filename>')
def serve_image(filename):
    folder = os.path.join(app.static_folder, "images/usb_cam_0")
    return send_from_directory(folder, filename)

@app.route('/api/last-upload')
def last_upload():
    try:
        with open("static/last_upload.txt", "r") as f:
            return jsonify({"last": f.read().strip()})
    except:
        return jsonify({"last": "Jamais effectué"})

@app.route('/api/manual-backup', methods=['POST'])
def manual_backup():
    if backup_status["running"]:
        return jsonify({"status": "running"})
    threading.Thread(target=run_backup).start()
    return jsonify({"status": "started"})

@app.route('/api/backup-status')
def get_backup_status():
    return jsonify(backup_status)

@app.route('/api/backup-log')
def backup_log():
    try:
        with open("static/zip_cron.log", "r") as f:
            return jsonify({"log": f.read()})
    except Exception as e:
        return jsonify({"log": f"Erreur lors de la lecture du log: {str(e)}"})

@app.route('/api/led-state')
def led_state():
    return jsonify({
        "r": current_r,
        "g": current_g,
        "b": current_b,
        "brightness": current_brightness
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)