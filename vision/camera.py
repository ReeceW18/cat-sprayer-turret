from picamera2 import Picamera2
import numpy as np

class Camera():
    def __init__(self):
        self._cam = Picamera2()
        # ADD SETUP

    def stop(self):
        # CLEAN UP CAMERA

        return

    def capture(self):
        # RETURN AN IMAGE
        placeholder = np.full((100,100,3),128,dtype=np.uint8)

        return placeholder