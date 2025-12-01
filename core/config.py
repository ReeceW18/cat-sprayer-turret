"""
Usage:
    from config import config

    foo = config.camera.fps_sentry
"""
import os
from dataclasses import dataclass, field
from typing import List
from pathlib import Path

@dataclass(frozen=True)
class CameraConfig:
    resolution: tuple[int, int] = (1080,1080)
    fps_sentry = 1
    fps_aiming = 10
    fps_recording = 30

@dataclass(frozen=True)
class NetworkConfig:
    port = 5555
    # if no ip set stream to default port, assuming not planning to view stream
    receiver_ip = os.getenv("RECEIVER_IP", "127.0.0.1")

@dataclass(frozen=True)
class CompressionConfig:
    stream_compression = 75
    recording_compression = 90

@dataclass(frozen=True)
class HardwareConfig:
    calibration_angle = 0
    aim_default_angle = 0
    trigger_default_angle = 90+45
    trigger_distance = 15
    # add gpio pins

@dataclass(frozen=True)
class YoloConfig:
    model_directory = "models/"
    model = model_directory + "11s_480p_halfprecision_ncnn_model"
    target_id = 0 # 0 = person, 15 = cat
    center_tolerance = 0
    confidence_threshold = .50

@dataclass(frozen=True)
class DurationsConfig:
    calibration_seconds = 3
    pre_roll_seconds = 10
    post_roll_seconds = 5
    cooldown_min_seconds = post_roll_seconds

@dataclass(Frozen=True)
class SystemConfig:
    calibration_enabled = True
    
# Main class
@dataclass(frozen=True)
class Config:
    camera = field(default_factory=CameraConfig)
    network = field(default_factory=NetworkConfig)
    compression = field(default_factory=CompressionConfig)
    hardware = field(default_factory=HardwareConfig)
    yolo = field(default_factory=YoloConfig)
    durations = field(default_factory=DurationsConfig)
    system = field(default_factory=SystemConfig)
 
config = Config()


 
 
 