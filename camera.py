import imagezmq
import cv2
from picamera2 import Picamera2
import configparser
import os

# pull config values
config = configparser.ConfigParser()
config_file_path = os.path.join(os.path.dirname(__file__), 'config.ini')
try:
    config.read(config_file_path)
except Exception as e:
    print(f"Error reading config file: {e}\n Did you set up config file properly?")
receiver_port_str = config.get('NETWORK', 'RECEIVER_PORT')

# pull env variables
receiver_ip = os.environ.get('RECEIVER_IP')

# initialize camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (240,240)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

# initialize connection
sender = imagezmq.ImageSender(connect_to=f'tcp://{receiver_ip}:{receiver_port_str}')

rpi_name = "Pi_YOLO"

# continuously send images
while True:
    frame = picam2.capture_array()
    cv2.imwrite(os.path.join(os.path.dirname(__file__), "camroll/image.png"), frame)

    print("sending image...")
    sender.send_image(rpi_name, frame)