import imagezmq
import cv2
from picamera2 import Picamera2

picam2 = Picamera2()
picam2.preview_configuration.main.size = (240,240)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

sender = imagezmq.ImageSender(connect_to='tcp://[REDACTED_IP]:5555')

rpi_name = "Pi_YOLO"

while True:
    frame = picam2.capture_array()
    cv2.imwrite("image.png", frame)

    print("sending image...")
    sender.send_image(rpi_name, frame)

