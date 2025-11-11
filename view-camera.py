import imagezmq
import cv2

# Initialize the ImageHub (server)
image_hub = imagezmq.ImageHub('tcp://*:5555') 

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
