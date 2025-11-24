import threading, time, queue
from vision.camera import Camera
from hardware.servo import setup_aiming, setup_trigger
import core.state_manager as state_manager
import core.threads
from hardware.servo import Servo

def calibrate(camera: Camera, aim: Servo, trigger:Servo):
    test_frame = camera.capture()
    # save test frame to camroll/

    # set motors to calibration position
    aim.calib_pos()
    trigger.calib_pos()
    for i in range(3, -1, -1):
        print(f"{i}")
        time.sleep(1)

    # set motors to default position
    aim.default_pos()
    trigger.default_pos()


if __name__=="__main__":
    print("initializing hardware")
    camera = Camera()
    aim_motor = setup_aiming()
    trigger_motor = setup_trigger()

    print("initializing queues")
    fps = 30
    pre_roll_seconds = 10
    pre_roll_size = fps*pre_roll_seconds
    frame_history = state_manager.RollingFrameBuffer(pre_roll_size)

    raw_queue = queue.Queue(2)
    stream_queue = queue.Queue(2)
    post_roll_queue = queue.Queue()
    metadata_queue = queue.Queue()
    hardware_command_queue = queue.Queue()

    print("initializing system state")
    state = state_manager.SystemState()

    print("starting calibration")
    calibrate(camera, aim_motor, trigger_motor)

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
        args=(raw_queue, stream_queue, frame_history, post_roll_queue, metadata_queue, hardware_command_queue, state),
        daemon=True)

    hardware_control_thread = threading.Thread(
        target=core.threads.hardware_control,
        args=(aim_motor, trigger_motor, hardware_command_queue, state),
        daemon=True)

    video_saver_thread = threading.Thread(
        target=core.threads.video_saver,
        args=(frame_history, post_roll_queue, metadata_queue, state),
        daemon=False)

    print("entering sentry mode and starting threads")
    state.mode = state_manager.SystemMode.SENTRY
    threads = [capture_thread, stream_thread, yolo_processing_thread, hardware_control_thread, video_saver_thread]
    for t in threads:
        t.start()

    print("threads running, listening for interrupt (ctrl c) for controlled shutdown")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("shutting down")
        state.mode = state_manager.SystemMode.SHUTDOWN
        print("waiting for video saver thread to stop")
        video_saver_thread.join()

        print("releasing hardware")
        camera.stop()
        aim_motor.release()
        trigger_motor.release()

        print("program done")
