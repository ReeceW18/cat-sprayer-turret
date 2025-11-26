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
        xyxyn_boxes = self._yolo_results[0].boxes.xyxyn
        center_tolerance = 0.1

        target_xywhn_s = [normalized_boxes[i] for i in target_indexes]
        target_xyxyn_s = [xyxyn_boxes[i] for i in target_indexes]

        if not target_xyxyn_s:
            return TargetDirection.NONE
        if target_xyxyn_s[0][0] < 0.5 and target_xyxyn_s[0][2] > 0.5:
            return TargetDirection.CENTER
        if target_xyxyn_s[0][2] < 0.5:
            return TargetDirection.LEFT
        else:
            return TargetDirection.RIGHT


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

        h, w = annotated_frame.shape[:2]
        tol = 0.1
        left_x = int((0.5 - tol)*w)
        right_x = int((0.5 + tol)*w)
        center_x = int(0.5*w)

        line_color = (0,255,255)
        line_thickness = 2
        cv2.line(annotated_frame, (left_x, 0), (left_x, h), line_color, line_thickness)
        cv2.line(annotated_frame, (right_x, 0), (right_x, h), line_color, line_thickness)
        cv2.line(annotated_frame, (center_x, 0), (center_x, h), line_color, line_thickness)


        cv2.putText(annotated_frame, text, (text_x, text_y), font, 1, (255,255,255), 2, cv2.LINE_AA)

        overlay = annotated_frame.copy()
        cv2.rectangle(overlay, (left_x, 0), (right_x, h), (0, 255, 255), -1)
        alpha = 0.15
        annotated_frame = cv2.addWeighted(overlay, alpha, annotated_frame, 1 - alpha, 0)

        processed_frame = annotated_frame # TODO add overlay of state and fps
        return processed_frame
