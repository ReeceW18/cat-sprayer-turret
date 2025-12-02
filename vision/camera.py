"""
Code for controlling specific camera.

TODO:
- review camera configuration
- handling for if no camera is connected
    - error handling in general
"""
import numpy as np

from picamera2 import Picamera2
from libcamera import Transform

from core.config import config

class Camera():
    def __init__(self):
        self._cam = Picamera2()
        # TODO add create video configuration for best video performance
        self._cam.preview_configuration.main.size = config.camera.resolution
        self._cam.preview_configuration.main.format = "RGB888"
        self._cam.preview_configuration.align()
        self._cam.preview_configuration.transform = Transform(hflip=True, vflip=True)
        self._cam.configure("preview")
        self._cam.start()


    def stop(self):
        self._cam.stop()

    def capture(self):
        frame = self._cam.capture_array()

        return frame