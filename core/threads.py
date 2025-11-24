from core.state_manager import SystemState, SystemMode
from time import sleep

def capture_frames(camera, raw_queue, state: SystemState):
    while state.mode != SystemMode.SHUTDOWN:
        sleep(10)

def stream_frames(stream_queue, state: SystemState):
    while state.mode != SystemMode.SHUTDOWN:
        sleep(10)

def yolo_processing(raw_queue, stream_queue, frame_history, post_roll_queue, metadata_queue, hardware_command_queue, state: SystemState):
    while state.mode != SystemMode.SHUTDOWN:
        sleep(10)

def hardware_control(aim_motor, trigger_motor, hardware_command_queue, state: SystemState):
    while state.mode != SystemMode.SHUTDOWN:
        sleep(10)

def video_saver(frame_history, post_roll_queue, metadata_queue, state: SystemState):
    while state.mode != SystemMode.SHUTDOWN:
        print(f"video_saver: {state}")
        sleep(1)

    # CLEAN UP WRITER

    return