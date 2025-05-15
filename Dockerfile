FROM dtcooper/raspberrypi-os:python3.9

# Install all dependencies for the project
RUN apt update && apt install -y \
    git \
    python3-pip \
    libcamera-apps \
    libcamera-dev \
    libglib2.0-0 \
    libjpeg-dev \
    libtiff-dev \
    libpng-dev \
    libexif-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libcap-dev \
    libboost-dev \
    libssl-dev \
    libudev-dev \
    libatlas-base-dev \
    python3-pyudev \
    python3-serial \
    python3-smbus \
    qtbase5-dev \
    qttools5-dev-tools \
    cmake \
    pkg-config \
    libevent-dev \
    pybind11-dev \
    libkms++-dev \
    libfmt-dev \
    libdrm-dev \
    && apt clean

# Install python libraries
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt

# Install meson and ninja for libcamera
RUN pip install meson ninja jinja2 pyyaml ply rpi-kms

# clone and install libcamera
RUN git clone https://github.com/raspberrypi/libcamera.git /opt/libcamera
WORKDIR /opt/libcamera
RUN meson setup build -Dpycamera=enabled && \
    ninja -C build install

# Install Picamera2
RUN git clone https://github.com/raspberrypi/picamera2.git /opt/picamera2
WORKDIR /opt/picamera2
RUN pip install .

# Environment variables for pycamera
ENV PYTHONPATH=/usr/local/lib/aarch64-linux-gnu/python3.9/site-packages:$PYTHONPATH

#copy the rest of the code
WORKDIR /app
COPY . .

# Run the main script
CMD ["python3", "main.py"]