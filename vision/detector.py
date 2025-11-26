"""
TODO: Everything
"""
from enum import StrEnum, auto

class TargetDirection(StrEnum):
    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()
    NONE = auto()

class DetectionResult:
    pass

    def has_target(self) -> bool:
        # TODO
        return None

    def get_direction(self) -> TargetDirection:
        # TODO
        return None

class ObjectDetector:
    pass

    def predict(self, frame) -> DetectionResult:
        # TODO
        return None

    def overlay(self, frame, results, state, fps):
        # TODO
        pass
