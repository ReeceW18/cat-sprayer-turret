"""
Contains the functions with the core logic that are ran as concurrent threads

TODO:
- potentially set fps in SystemState
- implement YOLO, hardware, and video saving
"""
import configparser
import os
import queue
import time
from pathlib import Path

import cv2
import imagezmq

from core.state_manager import SystemMode, SystemState
from vision.camera import Camera

def capture_frames(camera: Camera, raw_queue: queue.Queue, state: SystemState):
    """
    Captures frames from camera and adds them to raw_queue. FPS depends on systemstate
    """
    while state.mode != SystemMode.SHUTDOWN:
        # set fps based on mode
        if state.mode == SystemMode.SENTRY:
            FPS = 1
        else:
            FPS = 30
        print(f"fps set to {FPS}")

        # capture frame
        frame = camera.capture()

        # get time
        timestamp = time.time()

        # add tuple(frame, time) to raw queue if space
        if not raw_queue.full():
            print("adding frame to raw queue")
            raw_queue.put((frame, timestamp))
        else:
            print("raw queue full")

        # sleep depending on mode
        time.sleep(1/FPS)

def stream_frames(stream_queue: queue.Queue, state: SystemState):
    """
    Stream frames from stream_queue to an external device identified by RECEIVER_IP in environment variables
    """
    # get port from config
    config = configparser.ConfigParser()
    root_dir = Path(__file__).resolve().parent.parent
    config_file_path = root_dir / 'config.ini'
    config.read(config_file_path)
    reciever_port = config.get('NETWORK', 'RECEIVER_PORT')

    # get ip of reciever from env variables
    reciever_ip = os.environ.get('RECEIVER_IP')

    # set up sender
    full_tcp_address = f"{reciever_ip}:{reciever_port}"
    print(f"connecting to {full_tcp_address}")
    sender = imagezmq.ImageSender(connect_to=f'tcp://{full_tcp_address}')
    rpi_name = "cat_sprayer"

    while state.mode != SystemMode.SHUTDOWN:
        # get frame from queue
        frame = stream_queue.get()

        # compress frame
        _, compressed_frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

        # send frame (blocks until frame is recieved)
        print("sending frame...")
        sender.send_image(rpi_name, compressed_frame)
        print("frame sent!")

def yolo_processing(raw_queue, stream_queue: queue.Queue, frame_history, post_roll_queue, metadata_queue, hardware_command_queue, state: SystemState):
    """
    Handles core computation on decision making. Uses computer vision to switch system states and give hardware instructions. Most data passes through here from one thread to another even if its unmodified.
    """
    while state.mode != SystemMode.SHUTDOWN:
        # TEMP TESTING
        frame, timestamp = raw_queue.get()
        stream_queue.put(frame)

def hardware_control(aim_motor, trigger_motor, hardware_command_queue, state: SystemState):
    """
    Receives commands through hardware_command_queue and calls functions to perform those actions.
    """
    while state.mode != SystemMode.SHUTDOWN:
        # UNIMPLEMENTED
        time.sleep(10)

def video_saver(frame_history, post_roll_queue, metadata_queue, state: SystemState):
    """
    Saves a video of event whenever event is trigger. Also saves the yolo metadata as json.
    """
    while state.mode != SystemMode.SHUTDOWN:
        # UNIMPLEMENTED
        time.sleep(10)

    # CLEAN UP WRITER

    return