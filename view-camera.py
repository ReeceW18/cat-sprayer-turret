import imagezmq
import cv2
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

# Initialize the ImageHub (server)
image_hub = imagezmq.ImageHub('tcp://*:{receiver_port_str}') 

while True: 
    # Receive the sender's name and the frame
    print("recieving..")
    rpi_name, frame = image_hub.recv_image()
    print("recieved")
    
    print("displaying")
    cv2.imshow(rpi_name, frame)
    if cv2.waitKey(1) == ord('q'):
        break
    
    # Send a reply back (important for ZMQ to work correctly)
    image_hub.send_reply(b'OK')
