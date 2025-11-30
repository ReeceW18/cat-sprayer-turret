"""
Run from receiving device to view camera feed

Usage:
    Set tcp receiver port in config to match that on sending device.
"""
import imagezmq
import cv2
import configparser
import os

config = configparser.ConfigParser()
config_file_path = os.path.join(os.path.dirname(__file__), 'config.ini')
try:
    config.read(config_file_path)
except Exception as e:
    print(f"Error reading config file: {e}\n Did you set up config file properly?")
receiver_port_str = config.get('NETWORK', 'RECEIVER_PORT')

image_hub = imagezmq.ImageHub(f'tcp://*:{receiver_port_str}') 

while True: 
    print("recieving..")
    rpi_name, frame = image_hub.recv_image()
    print("recieved!")
    
    cv2.imshow(rpi_name, frame)

    if cv2.waitKey(1) == ord('q'):
        break

    image_hub.send_reply(b'OK')
