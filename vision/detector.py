"""
TODO: Everything
"""
from enum import StrEnum, auto
from ultralytics import YOLO
from ultralytics.engine.results import Results
import cv2

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
        model_path = "models/11s_320p_halfprecision_ncnn_model" # TODO, define in config
        model_path = "models/11n_320p_halfprecision_ncnn_model" # TODO, define in config
        self._model = YOLO(model_path)

    def predict(self, frame) -> DetectionResult:
        # TODO
        results = DetectionResult(self._model.predict(frame, verbose=False))
        return results

    def overlay(self, frame, results: DetectionResult, state, fps):
        # TODO
        annotated_frame = results.overlay(frame)
        text = f'FPS: {fps:.0f}'

        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1, 2)[0]
        text_x = annotated_frame.shape[1] - text_size[0] - 10
        text_y = text_size[1] + 10

        cv2.putText(annotated_frame, text, (text_x, text_y), font, 1, (255,255,255), 2, cv2.LINE_AA)

        processed_frame = annotated_frame # TODO add overlay of state and fps
        return processed_frame
