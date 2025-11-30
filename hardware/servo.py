"""
Specific hardware control code.

TODO:
- setup functions (hardware initalization)
- actual servo interfacing
"""

class Servo():
    def __init__(self):
        # PLACEHOLDER VALUES (TODO add to config?)
        self._calibration_angle = 0
        self._default_angle = 0
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
