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
pip install numpy==1.24.4
pip install opencv-python==4.8.0.74 picamera2 imagezmq
```