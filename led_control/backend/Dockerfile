FROM dtcooper/raspberrypi-os:python3.11

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libjpeg-dev libtiff-dev libturbojpeg0 \
    libcap-dev git wget build-essential \
    cron python3-dev i2c-tools \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Blinka and RPi5 Neopixel support
RUN pip install --no-cache-dir Adafruit-Blinka Adafruit-Blinka-Raspberry-Pi5-Neopixel

# Copy app files
COPY . .

# Make scripts executable
RUN chmod +x /app/transfer_zips.sh /app/start.sh

EXPOSE 5000

CMD ["/bin/bash", "./start.sh"]
