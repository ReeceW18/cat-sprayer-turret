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
    resolution: tuple[int, int] = (1536,864)
    fps_sentry: int = 1
    fps_aiming: int = 10
    fps_recording: int = 15

@dataclass(frozen=True)
class NetworkConfig:
    port: int = 5555
    # if no ip set stream to default port, assuming not planning to view stream
    receiver_ip: str = os.getenv("RECEIVER_IP", "127.0.0.1")

@dataclass(frozen=True)
class CompressionConfig:
    stream_compression: int = 75
    recording_compression: int = 50

@dataclass(frozen=True)
class HardwareConfig:
    # servo initialization (based off data sheet)
    init_min_angle = 0
    init_max_angle = 270
    min_pulse_width = 0.0005
    max_pulse_width = 0.0025
    # 
    calibration_angle: float = 0
    aim_default_angle: float = 270/2
    trigger_default_angle: float = 90+80
    aim_sec_per_60_deg: float = 0.20
    trigger_sec_per_60_deg: float = 0.50   
    init_move_time: float = 0.72 # how long servo has to move to default angle on init
    move_buffer_time: float = 0.2

    aim_increment: int = 10
    command_cooldown: float = 0.5

    aiming_min: int = 0
    aiming_max: int = 270
    trigger_distance: float = -40
    # add gpio pins
    aim_pin: int = 18
    trigger_pin: int = 19

@dataclass(frozen=True)
class YoloConfig:
    models_directory: str = "models/"
    model: str = models_directory + "11s_320p_halfprecision_ncnn_model"
    target_id: int = 0 # 0 = person, 15 = cat
    center_tolerance: float = .05
    confidence_threshold: float = .50

@dataclass(frozen=True)
class DurationsConfig:
    calibration_seconds: int = 5
    pre_roll_seconds: int = 5
    post_roll_seconds: int = 5
    cooldown_min_seconds: int = post_roll_seconds
    max_aiming_seconds: int = 10

@dataclass(frozen=True)
class SystemConfig:
    calibration_enabled: bool = False
    virtual_hardware: bool = False # give console outputs instead of trying to move servos
    
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


 
 
 