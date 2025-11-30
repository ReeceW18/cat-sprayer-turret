"""
Code for controlling specific camera.

TODO:
- review camera configuration
- handling for if no camera is connected
    - error handling in general
"""
import numpy as np

from picamera2 import Picamera2

class Camera():
    def __init__(self):
        self._cam = Picamera2()
        # TODO add create video configuration for best video performance
        # TODO flip camera
        self._cam.preview_configuration.main.size = (1080,1080) # TODO add to config
        self._cam.preview_configuration.main.format = "RGB888"
        self._cam.preview_configuration.align()
        self._cam.configure("preview")
        self._cam.start()

    def stop(self):
        self._cam.stop()

    def capture(self):
        frame = self._cam.capture_array()

        return frame