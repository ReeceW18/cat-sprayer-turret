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
    fps_sentry: int = 1
    fps_aiming: int = 10
    fps_recording: int = 30

@dataclass(frozen=True)
class NetworkConfig:
    port: int = 5555
    # if no ip set stream to default port, assuming not planning to view stream
    receiver_ip: str = os.getenv("RECEIVER_IP", "127.0.0.1")

@dataclass(frozen=True)
class CompressionConfig:
    stream_compression: int = 75
    recording_compression: int = 90

@dataclass(frozen=True)
class HardwareConfig:
    calibration_angle: float = 0
    aim_default_angle: float = 0
    trigger_default_angle: float = 90+45
    trigger_distance: float = 15
    # add gpio pins

@dataclass(frozen=True)
class YoloConfig:
    model_directory: str = "models/"
    model: str = model_directory + "11s_480p_halfprecision_ncnn_model"
    target_id: int = 0 # 0 = person, 15 = cat
    center_tolerance: float = 0
    confidence_threshold: float = .50

@dataclass(frozen=True)
class DurationsConfig:
    calibration_seconds: int = 3
    pre_roll_seconds: int = 10
    post_roll_seconds: int = 5
    cooldown_min_seconds: int = post_roll_seconds

@dataclass(frozen=True)
class SystemConfig:
    calibration_enabled: bool = True
    
# Main class
@dataclass(frozen=True)
class Config:
    camera: CameraConfig = field(default_factory=CameraConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    compression: CompressionConfig = field(default_factory=CompressionConfig)
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    yolo: YoloConfig = field(default_factory=YoloConfig)
    durations: DurationsConfig = field(default_factory=DurationsConfig)
    system: SystemConfig = field(default_factory=SystemConfig)
 
config = Config()


 
 
 