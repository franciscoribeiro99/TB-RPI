# Hardware setup
Using RPI imager create a bootable SD card with the latest version of Raspberry Pi OS and enable SSH.
Connect this bootable SD card to the Raspberry Pi and boot it up.

# Software setup
## Install dependencies
```bash
sudo apt update
sudo apt install -y git
```
## Install docker
```bash
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker $USER
restart terminal
```
## Clone the repository
```bash
git clone https://github.com/franciscoribeiro99/TB-RPI.git
cd TB-RPI
```
## Build the docker image
```bash
docker build -t tb-rpi .
```
## Run the docker container
```bash
docker run -d \
    --name tb-rpi \
    --restart unless-stopped \
    --network host \
    -v /etc/localtime:/etc/localtime:ro \
    -v /etc/timezone:/etc/timezone:ro \
    -v /home/pi/TB-RPI/config:/config \
    tb-rpi
```