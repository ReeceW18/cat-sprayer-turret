"""
TODO: Everything
"""
from enum import StrEnum, auto
from ultralytics import YOLO
from ultralytics.engine.results import Results

class TargetDirection(StrEnum):
    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()
    NONE = auto()

class DetectionResult:
    # NOTE should be moved to config, 0=person 15=cat see info/names.txt for all indexes
    TARGET_ID = 0

    def __init__(self, yolo_results: list[Results]):
        self._yolo_results = yolo_results

    def overlay(self, frame):
        annotated_frame = self._yolo_results[0].plot()
        return annotated_frame

    def has_target(self) -> bool:
        # TODO
        detected_objects = self._yolo_results[0].boxes.cls.tolist()
        target_found = False

        if DetectionResult.TARGET_ID in detected_objects:
            target_found = True

        return target_found

    def get_direction(self) -> TargetDirection:
        # TODO
        target_indexes = self._get_target_indexes()
        normalized_boxes = self._yolo_results[0].boxes.xyxyn

        target_xywhn_s = [normalized_boxes[i] for i in target_indexes]

        if not target_xywhn_s:
            return TargetDirection.NONE
        if target_xywhn_s[0][0] < 0.5:
            return TargetDirection.LEFT
        if target_xywhn_s[0][0] > 0.5:
            return TargetDirection.RIGHT
        if target_xywhn_s[0][0] == 0.5:
            return TargetDirection.CENTER

        return TargetDirection.NONE

    def _get_target_indexes(self) -> list[int]:
        target_indexes = []
        for i in range(0, len(self._yolo_results[0])):
            if self._yolo_results[0].boxes.cls.tolist()[i] == DetectionResult.TARGET_ID:
                target_indexes.append(i)
        return target_indexes

class ObjectDetector:
    def __init__(self):
        model_path = "models/yolov8n.pt" # TODO, define in config
        self._model = YOLO(model_path)

    def predict(self, frame) -> DetectionResult:
        # TODO
        imgSize = 640 # TODO, define in config, must match exported model
        results = DetectionResult(self._model.predict(frame, imgsz = imgSize, classes=[0]))
        return results

    def overlay(self, frame, results: DetectionResult, state, fps):
        # TODO
        annotated_frame = results.overlay(frame)
        processed_frame = annotated_frame # TODO add overlay of state and fps
        return processed_frame
