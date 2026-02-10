<!-- Notes to self to add:
- Ask mentors if I can mention them directly
-->

# Autonomous Cat Deterrent System
Why? Cats are intelligent enough to understand where they are not allowed to go, and also intelligent enough to know when nobody is around to stop them, so a 24/7 autonomous system is necessary to maintain boundaries.

What? Humane "turret" that sprays cats with water when in unauthorized areas. Identifies and aims using computer vision.

How? This project was completed as part of my Fall 2025 [EEP](https://www.uc.edu/campus-life/career-co-op-support/gain-experience/co-op/mandatory/experiential-explorations-programs.html), an alternative to industry co-op at the University of Cincinnati. I worked with industry mentors from Sensory Robotics and Microsoft AI to work through a full engineering prototyping lifecycle to obtain experience analogous to real world work.
## Demonstration
<video src="https://github.com/user-attachments/assets/720bba15-6034-4939-9861-61fa81a81528" autoplay loop muted playsinline style="max-width: 100%;">
</video>

## System
### Hardware
- Headless Raspberry Pi 4GB running Pi OS bookworm 64 bit lite (based on debian equivalent). 
- Arducam wide angle module 3 (SKU: B031202, uses IMX708 sensor)
- 2 ds3218 servos
- Standard consumer spray bottle
- 3d printed assembly

<table>
  <tr>
    <td><img src="https://github.com/ReeceW18/cat-sprayer-turret/blob/main/CAD%20renders%20(3).png" alt="Turret Angle 2" width="100%"></td>
	<td><img src="https://github.com/ReeceW18/cat-sprayer-turret/blob/main/CAD%20renders%20(2).png" alt="Turret Angle 1" width="100%"></td>
  </tr>
</table>

### Software
- A [main.py](main.py) file supported by several custom modules
- **most logic** is performed using instances of threads defined in **[threads.py](core/threads.py)**
	- Each "service" performed managed by a different thread, capturing frames, processing frames, streaming frames, controlling servos, and writing to storage.
- Uses ultralytics YOLO for live object detection. Primary implementation is a v11 small 320x320p frame input model converted to NCNN to leverage the Pi's arm architecture.
- Supporting programs
	- [model_creator.py](external/model_creator.py) - used to import and convert models to NCNN
	- [view-camera.py](external/view-camera.py) - run on other device on network to view live camera stream
	- [compiler.py](post-process/compiler.py) - compiled saved detection data and frames into watchable video
	- [yolo_test_images.py](testing/yolo_test_images.py) - test different models speed on saved images
- Camera transmission to device on local network supported via imagezmq imagehub.
- [Config.py](core/config.py) allows for rapid tweaking of parameters during testing.
## Technical overview
- The system operates under 4 different states: Sentry, Aiming, Firing, Cooldown.
1. Sentry: A frame is taken at a low fps defined in config, if the target object type is detected aiming is triggered.
2. Aiming: A frame is taken at a high fps defined in config, the device turns in the direction the target is detected, if the target is close to the middle of the frame firing is activated.
3. Firing: Pull the trigger on the spray bottle and switch to cooldown
4. Cooldown: Save frames and data collected of the event, reset buffers, and reset aiming position. Switch back to sentry

### Flow diagrams
State machine flow diagram:
<img width="1002" height="215" alt="image" src="https://github.com/user-attachments/assets/5ac4f3b4-e113-4c74-bd1f-b9e3a997669a" />
Threads flow diagram:
<img width="995" height="568" alt="image" src="https://github.com/user-attachments/assets/338e2b5f-ccff-4efc-b320-cb53c1e56ec6" />

## Deployment
Install Raspberry Pi OS Bookworm 64 bit lite (aka headless)

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

## Challenges 
- **Servo jitter**. Due to inherent electrical noise when using cheap servos, power, and breadboard prototyping servos experience substantial jitter. Solved via calculating the time it should take for a move and only instruct servo to be at the point for that time, then tell it to not move.
- **Aiming**. Due to aforementioned electrical unreliability as well as limited compute, consistent identification and aiming was a significant issue. Assigned all tunable variables (such as angle change increment and cooldown between commands) to do with aiming to config allowing for rapid tweaking and actual testing of different values.
## Avenues for improvement
- Solve root of servo jitter
	- More reliable servos
	- Higher spec power
	- Soldering not just breadboards
	- Try different pwm libraries
- Aiming
- Appearance
- Spraying reliably and professionally (not a off the shelf spray bottle jerry-rigged into assembly)
- Processing efficiency
	- move ai processing thread to its own process to fully utilize the Pi's multi core architecture
	- downgrade from a pi but use a edge AI computing device to boost AI performance
## More From Me
[Github Profile](https://github.com/ReeceW18)  
[LinkedIn](https://www.linkedin.com/in/reece-whitaker/)
## AI DISCLAIMER
AI was used throughout the project as an always available teacher. Some code blocks may be partially generated by AI. I tried my best to use it as a tool and teacher not a crutch. yolo_test_images.py is entirely AI generated as it was an auxiliary tool and not a critical feature of the final device.
