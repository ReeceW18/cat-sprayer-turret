"""
Specific hardware control code.

TODO:
- setup functions (hardware initalization)
- actual servo interfacing
"""
from core.config import config

class Servo():
    def __init__(self, default_angle = config.hardware.aim_default_angle):
        # PLACEHOLDER VALUES (TODO add to config?)
        self._calibration_angle = config.hardware.calibration_angle
        self._default_angle = default_angle
        return

    def release(self):
        # TODO release gpio pins
        return

    def calib_pos(self):
        print("calib_pos: ", end="")
        self.move_to(self._calibration_angle)

    def default_pos(self):
        print("default_pos: ", end="")
        self.move_to(self._default_angle)

    def move_to(self, angle):
        # TODO
        print(f"moving to {angle}")
        return


def setup_aiming() -> Servo:
    # TODO
    return Servo()

def setup_trigger() -> Servo:
    # TODO
    return Servo()
