"""
Code for controlling hardware that is agnostic to specific hardware type
"""
from enum import StrEnum, auto

class HardwareCommand(StrEnum):
    AIM_LEFT = auto()
    AIM_RIGHT = auto()

    FIRE = auto()