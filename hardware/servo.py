

class Servo():
    def __init__(self):
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
        # IMPLEMENT
        print(f"moving to {angle}")
        return


def setup_aiming() -> Servo:
    return Servo()

def setup_trigger() -> Servo:
    return Servo()
