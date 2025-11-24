"""
TODO:
- setup functions
- actual servo interfacing
"""

class Servo():
    def __init__(self):
        # PLACEHOLDER VALUES
        self._calibration_angle = 0
        self._default_angle = 0
        return

    def release(self):
        return

    def calib_pos(self):
        self.move_to(self._calibration_angle)

    def default_pos(self):
        self.move_to(self._default_angle)

    def move_to(self, angle):
        # UNIMPLEMENTED
        print(f"moving to {angle}")
        return


def setup_aiming() -> Servo:
    # UNIMPLEMENTED
    return Servo()

def setup_trigger() -> Servo:
    #UNIMPLEMENTED
    return Servo()
