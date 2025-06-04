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
The sftp server is used to store the files when the Raspberry Pi is becoming full. Threshold is set to 40% of the disk space. If you want to change the threshold, edit the `led_control/backend/transfer_zips.sh` file. To set up the sftp server, you need to create a user and set up the environment variables. To do that add the the varibles to the .```env``` file and build the docker image.


## Build and run the docker image
```bash
docker compose up -d --build
```
