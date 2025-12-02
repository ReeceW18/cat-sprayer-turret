"""
Threads and processes used for running system

Usage:
    create thread using each function and run all at once. All should be 
    daemons except for video_saver

TODO:
    - implement hardware, and video saving
    - see individual function todos
"""
import configparser
import os
import queue
import time
import threading
from pathlib import Path

import cv2
import imagezmq

from vision.detector import TargetDirection, ObjectDetector
from core.config import config
from core.state_manager import SystemMode, SystemState, ThreadingDeque
from hardware.hardware_control import HardwareCommand, HardwareQueue
from vision.camera import Camera

def capture_frames(camera: Camera, raw_queue: queue.Queue, frame_history: ThreadingDeque, post_roll_queue: queue.Queue, state: SystemState):
    """
    Captures frames from camera and adds to queues.

    Args:
        camera (Camera): The Camera object that handles image capture
        raw_queue (queue.Queue): The queue that raw frames are added to for 
        processing or streaming
        state (SystemState): The object that represents the state of the 
        system, vessel for all simple variables shared by threads

    TODO:
        - separate capture and process into separate threads
    """
    last_capture_time = time.time()
    while state.mode != SystemMode.SHUTDOWN:
        frame = camera.capture()

        debug_capture_time = False
        if debug_capture_time:
            this_capture_time = time.time()
            capture_fps = 1 / (this_capture_time - last_capture_time)
            last_capture_time = this_capture_time
            print(f"capture fps = {capture_fps}")

        _, compressed_frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), config.compression.recording_compression])
        timestamp = time.time()

        if state.mode == SystemMode.SENTRY or state.mode == SystemMode.AIMING:
            frame_history.append((compressed_frame, timestamp))
        elif state.mode == SystemMode.COOLDOWN:
            post_roll_queue.put((compressed_frame, timestamp)) #TODO double check adding properly when queue is full and when video recorder resets everything. check for timeout?

        if not raw_queue.full():
            raw_queue.put((frame, timestamp))
        
        time.sleep(1/config.camera.fps_recording)

        

def stream_frames(stream_queue: queue.Queue, state: SystemState):
    """
    Stream frames to recieving device on local network at tcp address 
    RECEIVER_IP:RECEIVER_PORT. ip in env variables, port in config.

    Args:
        stream_queue (queue.Queue): images to be streamed, this function reads 
        and sends from this queue one at a time
        state (SystemState): The object that represents the state of the 
        system, vessel for all simple variables shared by threads

    TODO:
    """
    receiver_port = config.network.port
    receiver_ip = config.network.receiver_ip
    full_tcp_address = f"{receiver_ip}:{receiver_port}"

    print(f"connecting to {full_tcp_address}")
    sender = imagezmq.ImageSender(connect_to=f'tcp://{full_tcp_address}')

    rpi_name = "cat_sprayer"

    while state.mode != SystemMode.SHUTDOWN:
        frame = stream_queue.get()

        # scale from 1-100, 100 being highest quality, default 95
        jpeg_quality = config.compression.stream_compression
        _, compressed_frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])

        # this blocks until image is received
        sender.send_image(rpi_name, compressed_frame)

def yolo_processing(trigger_event: threading.Event, raw_queue: queue.Queue, stream_queue: queue.Queue, metadata_queue: ThreadingDeque, hardware_command_queue: HardwareQueue, state: SystemState):
    """
    Run processing on images and make decisions for hardware commands

    Args:
        trigger_event (threading.Event): event object that tells video saver 
        to start saving video on spray trigger
        raw_queue (queue.Queue): quque that stores frames to be processed
        stream_queue (queue.Queue): queue that stores frames to be streamed
        frame_history (ThreadingDeque): deque that stores frame history to be 
        saved to event video
        post_roll_queue (queue.Queue): queue that stores post roll after 
        trigger to be saved to event video
        metadata_queue (ThreadingDeque): deque that stores object detection 
        data to be saved along with event video for later overlay
        hardware_command_queue (queue.Queue): queue that stores commands for 
        hardware to execute
        state (SystemState): The object that represents the state of the 
        system, vessel for all simple variables shared by threads

    TODO:
        - could make into a process to max speed, or even run yolo inference 
        only on its own process
        - create new special hardware queue class to make sure queue doesn't fill up
            - on add, delete all aim commands but keep fire command
            - shouldn't need to change logic in this function
    """
    object_detector = ObjectDetector()
    # used to determine processing fps for display when streaming frames
    last_frame_time = time.time()
    trigger_time = -1
    last_command = HardwareCommand.NULL

    while state.mode != SystemMode.SHUTDOWN:
        frame, timestamp = raw_queue.get()

        # if in a mode that needs inference to run
        if state.mode == SystemMode.SENTRY or state.mode == SystemMode.AIMING:
            predict_start = time.time()
            results = object_detector.predict(frame)
            predict_end = time.time()
            latency = predict_end-predict_start

            if state.mode == SystemMode.SENTRY:
                if results.has_target():
                    state.mode = SystemMode.AIMING
                    print("Switching to AIMING mode")
            else:
                direction = results.get_direction()
                if direction == TargetDirection.CENTER:
                    trigger_event.set()
                    trigger_time = time.time()
                    hardware_command_queue.put(HardwareCommand.FIRE)
                    #state.mode = SystemMode.COOLDOWN
                elif direction == TargetDirection.LEFT:
                    hardware_command_queue.put(HardwareCommand.AIM_LEFT)
                elif direction == TargetDirection.RIGHT:
                    hardware_command_queue.put(HardwareCommand.AIM_RIGHT)

            metadata_queue.append((results, timestamp))

            # calculate fps
            current_time = time.time()
            time_since_last_frame = current_time - last_frame_time
            fps = 1 / time_since_last_frame
            last_frame_time = current_time

            # print(f"FPS: {fps:.1f}")

            current_command = hardware_command_queue.current_status
            if current_command != HardwareCommand.NULL:
                last_command = current_command
            
            if not stream_queue.full():
                # generate and stream frame
                processed_frame = object_detector.overlay(frame, results, state, fps, last_command)
                stream_queue.put(processed_frame)

            if state.mode == SystemMode.SENTRY:
                time.sleep(1/config.camera.fps_sentry - latency)
            else:
                sleep_time = 1/config.camera.fps_aiming - latency
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
        else:
            time_since_trigger = time.time() - trigger_time 
            if not trigger_event.is_set() and time_since_trigger > config.durations.cooldown_min_seconds:
                state.mode = SystemMode.SENTRY
            else:
                time.sleep(.1)

def hardware_control(aim_motor, trigger_motor, hardware_command_queue, state: SystemState):
    """
    Receives commands through hardware_command_queue and calls functions to perform those actions.

    TODO:
    - All
    - add debug for sending commands to console when hardware isn't enabled
    """
    while state.mode != SystemMode.SHUTDOWN:
        # UNIMPLEMENTED
        time.sleep(10)

def video_saver(trigger_event, frame_history, post_roll_queue, metadata_queue, state: SystemState):
    """
    Saves a video of event whenever event is trigger. Also saves the yolo metadata as json.

    TODO:
    - All 
    """
    while state.mode != SystemMode.SHUTDOWN:
        # UNIMPLEMENTED
        time.sleep(10)

    # CLEAN UP WRITER

    return