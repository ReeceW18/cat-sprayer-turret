# ==IN PROGRESS==

# Description
A spray bottle turret that detects and spray cats using YOLO object detection.

Hardware documentation to be made. Uses:
- 3d printed frame
- arducam wide angle comera module 3 for raspberry pi, SKU: B031202
- raspberry pi 5 4gb
- 2 ds3218 servos
- an off the shelf spray bottle

# Software Setup
create new pi os image using pi os legacy (bookworm) 64 bit lite

If using exact same camera module, edit /boot/firmware/config.txt
- change camera_auto_detect=1 to camera_auto_detect=0
- add `dtoverlay=imx708` at end

reboot

check if camera is recognized

```
rpicam-still --list-cameras
```

clone repository
```
sudo apt install git
git clone git@github.com:ReeceW18/cat-sprayer-turret.git
```

make sure picamera2 and libcam are installed
```
pip install -U pip
sudo apt install python3-picamera2
```

set up virtual environment and libraries
```
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
sudo apt install libcap-dev python3-dev
pip install -r requirements_pi.txt
export RECEIVER_IP = "192.168.X.X" # change to ip address of viewing device, add to end of .venv/bin/activate for persistence between restarts
```

configure variables in config.py as needed


# Use
run main.py

run view-camera.py from another device (whose ip was added as environment variable) to display camera feed remotely
