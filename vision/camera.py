"""
TODO:
- proper camera configuration
- handling for if no camera is connected
    - error handling in general
"""
import numpy as np

from picamera2 import Picamera2

class Camera():
    def __init__(self):
        # REVISIT CONFIGURATION SPECIFICS
        self._cam = Picamera2()
        self._cam.preview_configuration.main.size = (1080,1080)
        self._cam.preview_configuration.main.format = "RGB888"
        self._cam.preview_configuration.align()
        self._cam.configure("preview")
        self._cam.start()

    def stop(self):
        # CLEAN UP CAMERA
        self._cam.stop()

    def capture(self):
        # RETURN AN IMAGE
        frame = self._cam.capture_array()

        return frame