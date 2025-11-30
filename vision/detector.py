"""
Core inference and detection logic.

TODO:
    - Add class/method comments
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
    # TODO add to config
    TARGET_ID = 0

    def __init__(self, yolo_results: list[Results]):
        self._yolo_results = yolo_results

    def overlay(self, frame):
        annotated_frame = self._yolo_results[0].plot()
        return annotated_frame

    def has_target(self) -> bool:
        target_found = False

        detected_objects = self._yolo_results[0].boxes.cls.tolist()

        if DetectionResult.TARGET_ID in detected_objects:
            target_found = True

        return target_found

    def get_direction(self) -> TargetDirection:
        target_indexes = self._get_target_indexes()
        xyxyn_boxes = self._yolo_results[0].boxes.xyxyn
        center_tolerance = 0.1 #TODO add to config
        left_bound = 0.5 - center_tolerance
        right_bound = 0.5 + center_tolerance

        target_boxes = [xyxyn_boxes[i] for i in target_indexes]

        if not target_boxes:
            return TargetDirection.NONE
        elif target_boxes[0][2] < left_bound:
            return TargetDirection.LEFT
        elif target_boxes[0][0] > right_bound:
            return TargetDirection.RIGHT
        else:
            return TargetDirection.CENTER

    def _get_target_indexes(self) -> list[int]:
        target_indexes = []
        for i in range(0, len(self._yolo_results[0])):
            if self._yolo_results[0].boxes.cls.tolist()[i] == DetectionResult.TARGET_ID:
                target_indexes.append(i)
        return target_indexes

class ObjectDetector:
    def __init__(self):
        model_path = "models/11s_320p_halfprecision_ncnn_model" # TODO, define in config
        self._model = YOLO(model_path)

    def predict(self, frame) -> DetectionResult:
        results = DetectionResult(self._model.predict(frame, verbose=False))
        return results

    def overlay(self, frame, results: DetectionResult, state, fps):
        """

        Args:
            frame (_type_): _description_
            results (DetectionResult): _description_
            state (_type_): _description_
            fps (_type_): _description_

        Returns:
            _type_: _description_

        TODO:
            - Add overlay of system state and possible most recent hardware command
        """
        annotated_frame = results.overlay(frame)

        # add fps counter
        text = f'FPS: {fps:.0f}'
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1, 2)[0]
        text_x = annotated_frame.shape[1] - text_size[0] - 10
        text_y = text_size[1] + 10

        cv2.putText(annotated_frame, text, (text_x, text_y), font, 1, (255,255,255), 2, cv2.LINE_AA)

        # add a representation of center bounds
        h, w = annotated_frame.shape[:2]
        tol = 0.1 # TODO should pull center_tolerance from config
        left_x = int((0.5 - tol)*w)
        right_x = int((0.5 + tol)*w)
        center_x = int(0.5*w)

        line_color = (0,255,255)
        line_thickness = 2
        cv2.line(annotated_frame, (left_x, 0), (left_x, h), line_color, line_thickness)
        cv2.line(annotated_frame, (right_x, 0), (right_x, h), line_color, line_thickness)

        overlay = annotated_frame.copy()
        cv2.rectangle(overlay, (left_x, 0), (right_x, h), (0, 255, 255), -1)
        alpha = 0.15
        annotated_frame = cv2.addWeighted(overlay, alpha, annotated_frame, 1 - alpha, 0)

        # add center line
        cv2.line(annotated_frame, (center_x, 0), (center_x, h), (0,0,0), line_thickness)

        return annotated_frame
