import os
import queue
import threading
import time

import cv2

import core.state_manager as state_manager
import core.threads
from hardware.servo import Servo, setup_aiming, setup_trigger
from vision.camera import Camera


def calibrate(camera: Camera, aim: Servo, trigger: Servo):
    """
    Calibrate the hardware

    1. Capture an image and store it in camroll
    2. Move servos to calibration position to be screwed into the assembly
    3. Wait some number of seconds
    4. return servos to default position
    """
    # capture frame and save to camroll
    test_frame = camera.capture()

    camroll_dir = os.path.join(os.path.dirname(__file__), "camroll")
    os.makedirs(camroll_dir, exist_ok=True)
    save_path = os.path.join(camroll_dir, f"calibration-test_{int(time.time())}.png")

    cv2.imwrite(save_path, test_frame)
    
    # set motors to calibration position
    aim.calib_pos()
    trigger.calib_pos()

    # countdown until resetting position to default
    for i in range(3, -1, -1):
        print(f"{i}")
        time.sleep(1)

    # set motors to default position
    aim.default_pos()
    trigger.default_pos()


if __name__=="__main__":
    # initialize hardware
    print("initializing hardware")
    camera = Camera()
    aim_motor = setup_aiming()
    trigger_motor = setup_trigger()

    # initialize queues
    print("initializing queues")
    fps = 30
    pre_roll_seconds = 10
    pre_roll_size = fps*pre_roll_seconds
    frame_history = state_manager.RollingFrameBuffer(pre_roll_size) # pre_roll for saved video

    raw_queue = queue.Queue(2)
    stream_queue = queue.Queue(2)
    post_roll_queue = queue.Queue()
    metadata_queue = queue.Queue()
    hardware_command_queue = queue.Queue()

    # initialize system
    print("initializing system state")
    state = state_manager.SystemState()
    trigger_event = threading.Event()

    # calibrate
    print("starting calibration")
    calibrate(camera, aim_motor, trigger_motor)

    # create threads
    print("creating threads")
    capture_thread = threading.Thread(
        target=core.threads.capture_frames,
        args=(camera, raw_queue, state),
        daemon=True)

    stream_thread = threading.Thread(
        target=core.threads.stream_frames,
        args=(stream_queue, state),
        daemon=True)

    yolo_processing_thread = threading.Thread(
        target=core.threads.yolo_processing,
        args=(trigger_event, raw_queue, stream_queue, frame_history, post_roll_queue, metadata_queue, hardware_command_queue, state),
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
        t.start()

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
