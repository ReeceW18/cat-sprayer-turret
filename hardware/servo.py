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
    def __init__(self, gpio_pin: int, 
                 default_angle = 0,
                 sec_per_60_deg = 0.16,
                 init_min_angle: int = config.hardware.init_min_angle, 
                 init_max_angle: int = config.hardware.init_max_angle, 
                 min_pulse_width = config.hardware.min_pulse_width, 
                 max_pulse_width = config.hardware.max_pulse_width
                 ):

        self._servo = AngularServo(gpio_pin, min_angle=init_min_angle, 
                                   max_angle=init_max_angle,
                                   min_pulse_width=min_pulse_width, 
                                   max_pulse_width=max_pulse_width)

        self._sec_per_deg = sec_per_60_deg/60
        self._current_angle = default_angle
        self._servo.angle = default_angle
        sleep(config.hardware.init_move_time)
        self._servo.angle = None
        return

    def release(self):
        self._servo.close()
        return

    def move_to(self, angle):
        if angle > self._servo.max_angle or angle < self._servo.min_angle:
            raise Exception("Attempting to move out of servo range")

        distance = abs(self._current_angle - angle)
        move_duration = (distance*self._sec_per_deg) + config.hardware.move_buffer_time

        self._servo.angle = angle
        sleep(move_duration)
        self._servo.angle = None

        self._current_angle = angle
        print(f"current angle: {self._current_angle}")

    def move_by(self, delta_angle) -> bool:
        '''
        Docstring for move_by
        
        :param self: Description
        :param delta_angle: Description
        :return: return false if trying to move out of range
        :rtype: bool
        '''
        target_angle = self._current_angle - delta_angle # TODO change stuff so that angles make sense (aiming should be inverted but not trigger)
        if target_angle > self._servo.max_angle or target_angle < self._servo.min_angle:
            return False
        self.move_to(target_angle)
        return True


def setup_aiming() -> Servo:
    return Servo(config.hardware.aim_pin, 
                 default_angle=config.hardware.aim_default_angle,
                 sec_per_60_deg=config.hardware.aim_sec_per_60_deg)

def setup_trigger() -> Servo:
    return Servo(config.hardware.trigger_pin, 
                 default_angle=config.hardware.trigger_default_angle,
                 sec_per_60_deg=config.hardware.trigger_sec_per_60_deg)
