"""
Specific hardware control code.

TODO:
- setup functions (hardware initalization)
- actual servo interfacing
"""
from core.config import config
from gpiozero import AngularServo
from time import sleep

class Servo():
    def __init__(self, gpio_pin: int, min_angle: int = 0, max_angle: int = 270, 
                 min_pulse_width = 0.0005, max_pulse_width = 0.0025, 
                 default_angle = config.hardware.aim_default_angle):
        # PLACEHOLDER VALUES (TODO add to config?)
        self._servo = AngularServo(gpio_pin, min_angle=min_angle, max_angle=max_angle,
                                   min_pulse_width=min_pulse_width, max_pulse_width=max_pulse_width)
        self._calibration_angle = config.hardware.calibration_angle
        self._default_angle = default_angle
        self._current_angle = default_angle
        self._servo.angle = default_angle
        sleep(0.72)
        self._servo.angle = None
        return

    def release(self):
        # TODO release gpio pins
        self._servo.close()
        return

    def calib_pos(self):
        print("calib_pos: ", end="")
        self.move_to(self._calibration_angle)

    def default_pos(self):
        print("default_pos: ", end="")
        self.move_to(self._default_angle)

    def move_to(self, angle):
        # TODO
        if angle > self._servo.max_angle or angle < self._servo.min_angle:
            raise Exception("Attempting to move out of servo range")
        SEC_PER_60_DEG = 0.16
        SEC_PER_DEG = SEC_PER_60_DEG/60 # TODO move to better place

        distance = abs(self._current_angle - angle)
        move_duration = (distance*SEC_PER_DEG) + 0.05

        self._servo.angle = angle
        sleep(move_duration)
        self._servo.angle = None

        self._current_angle = angle

    def move_by(self, delta_angle) -> bool:
        '''
        Docstring for move_by
        
        :param self: Description
        :param delta_angle: Description
        :return: return false if trying to move out of range
        :rtype: bool
        '''
        target_angle = self._current_angle + delta_angle
        if target_angle > self._servo.max_angle or target_angle < self._servo.min_angle:
            return False
        self.move_to(target_angle)
        return True


def setup_aiming() -> Servo:
    # TODO
    return Servo(config.hardware.aim_pin, default_angle=config.hardware.aim_default_angle)

def setup_trigger() -> Servo:
    # TODO
    return Servo(config.hardware.trigger_pin, default_angle=config.hardware.trigger_default_angle)
