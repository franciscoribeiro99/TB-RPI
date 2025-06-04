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
## Setup config for the sftp server
The sftp server is used to store the files when the Raspberry Pi is becoming full. Threshold is set to 40% of the disk space. If you want to change the threshold, edit the `led_control/backend/transfer_zips.sh` file.
```bash
cp config
chmod +x setup_sftp.sh
./setup_sftp.sh
source ~/.sftp_env
```

## Build and run the docker image
```bash
docker compose up -d --build
```
