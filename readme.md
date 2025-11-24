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
clone repository

set up virtual environment
```
python -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -r requirements.txt
export RECEIVER_IP = "192.168.X.X" # change to ip address of viewing device, add to end of .venv/bin/activate for persistence between restarts
```

# Use
run camera.py from a raspberry pi with a camera attached

run view-camera.py from another device (whose ip was added as environment variable) to display camera feed remotely
