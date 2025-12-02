"""
Top level file for autonomous spraying system.

This module initializes all hardware components and launches the concurrent 
processing units required for real-time detection and actuation. It manages 
the lifecycle of the application, including graceful shutdown procedures and 
resource cleanup.

Usage:
    Run this script directly from the project root to start the system:
    
    $ python3 main.py

    Ensure that the 'config.ini' file is present (and properly conifgured) in 
    the root directory before execution.

TODO:
    - make processing thread a process to improve performance
    - change hardware queue size to match what final implementation necessitates
"""
import os
import queue
import threading
import time

import cv2

import core.state_manager as state_manager
import core.threads
from core.config import config
from hardware.servo import Servo, setup_aiming, setup_trigger
from vision.camera import Camera


def calibrate(camera: Camera, aim: Servo, trigger: Servo):
    """
    Calibrate the hardware.

    1. Capture an image and store it in camroll
    2. Move servos to calibration position to be screwed into the assembly
    3. Wait some number of seconds
    4. return servos to default position
    """
    print("capturing test frame")
    test_frame = camera.capture()

    camroll_dir = os.path.join(os.path.dirname(__file__), "camroll")
    os.makedirs(camroll_dir, exist_ok=True)
    save_path = os.path.join(camroll_dir, f"calibration-test_{int(time.time())}.png")

    cv2.imwrite(save_path, test_frame)
    
    print("moving motors to calibration position")
    aim.calib_pos()
    trigger.calib_pos()

    # countdown waiting for servos to be fully mounted
    print("attach servo horns")
    for i in range(config.durations.calibration_seconds, -1, -1): 
        print(f"Waiting for {i} seconds")
        time.sleep(1)

    # set motors to default position
    print("returning to default position")
    aim.default_pos()
    trigger.default_pos()


if __name__=="__main__":
    """
    Initialize hardware and variables, run concurrent threads, listen for stop 
    and orchestrate graceful shutdown.
    """
    # initialize hardware
    print("initializing hardware")
    camera = Camera()
    aim_motor = setup_aiming()
    trigger_motor = setup_trigger()

    # initialize queues
    print("initializing queues")
    fps = config.camera.fps_recording 
    pre_roll_seconds = config.durations.pre_roll_seconds
    post_roll_seconds = config.durations.post_roll_seconds

    pre_roll_size = fps*pre_roll_seconds
    post_roll_size = fps*post_roll_seconds

    frame_history = state_manager.ThreadingDeque(pre_roll_size) # pre_roll for saved video
    metadata_queue = state_manager.ThreadingDeque(pre_roll_size+post_roll_size)
    post_roll_queue = queue.Queue(post_roll_size)

    raw_queue = queue.Queue(2)
    stream_queue = queue.Queue(2)
    hardware_command_queue = queue.Queue(10)

    # initialize system
    print("initializing system state")
    state = state_manager.SystemState()
    trigger_event = threading.Event()

    if config.system.calibration_enabled:
        print("starting calibration")
        calibrate(camera, aim_motor, trigger_motor)
    else:
        print("skipping calibration")

    # create threads
    print("creating threads")
    capture_thread = threading.Thread(
        target=core.threads.capture_frames,
        args=(camera, raw_queue, frame_history, post_roll_queue, state),
        daemon=True)

    stream_thread = threading.Thread(
        target=core.threads.stream_frames,
        args=(stream_queue, state),
        daemon=True)

    yolo_processing_thread = threading.Thread(
        target=core.threads.yolo_processing,
        args=(trigger_event, raw_queue, stream_queue, metadata_queue, hardware_command_queue, state),
        daemon=True)

    hardware_control_thread = threading.Thread(
        target=core.threads.hardware_control,
        args=(aim_motor, trigger_motor, hardware_command_queue, state),
        daemon=True)

    video_saver_thread = threading.Thread(
        target=core.threads.video_saver,
        args=(trigger_event, frame_history, post_roll_queue, metadata_queue, state),
        daemon=False)

    # start threads
    print("entering sentry mode and starting threads")
    state.mode = state_manager.SystemMode.SENTRY
    threads = [capture_thread, stream_thread, yolo_processing_thread, hardware_control_thread, video_saver_thread]
    for t in threads:
        print(f"starting thread...", end="")
        t.start()
        print(" thread started")

    # listen for keyboard interrupt for graceful shutdown
    print("threads running, listening for interrupt (ctrl c) for controlled shutdown")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # indicate that system is in shutdown
        print("shutting down")
        state.mode = state_manager.SystemMode.SHUTDOWN

        # release threads that have special ending behavior
        print("waiting for video saver thread to stop")
        video_saver_thread.join()

        # clean up/release hardware
        print("releasing hardware")
        camera.stop()
        aim_motor.release()
        trigger_motor.release()

        print("program done")
