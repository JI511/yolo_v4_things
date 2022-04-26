from io import BytesIO
import os
from queue import Queue
import socket
import time

import cv2
import numpy as np

BUFFER_SIZE = 2048
image_queue = Queue()


def send_image(im_path):
    """
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IP, SOCK_STREAM = TCP
    client.connect(('localhost', 1002))  # 127.0.0.1

    packet = client.recv(BUFFER_SIZE)
    if packet == b'server ready':
        file = open(im_path, 'rb')
        image_data = file.read(BUFFER_SIZE)

        packet_count = 1
        while image_data:
            client.send(image_data)
            image_data = file.read(BUFFER_SIZE)
            packet_count += 1
        file.close()
        # delete the image once we are done
        os.remove(im_path)
    else:
        print('packet didnt match')

    client.close()


def process_video():
    # Creating a VideoCapture object to read the video
    cap = cv2.VideoCapture('mp4/sparklers.mp4')
    if cap.isOpened():
        fps = int(cap.get(5))
        print("Frame Rate : ", fps, "frames per second")

        # Get frame count
        total_frame_count = int(cap.get(7))
        print("Frame count : ", total_frame_count)
        current_frame = 0
        start_time = time.time()
        # Loop until the end of the video
        while cap.isOpened():
            image_name = str(cap.get(0)).replace('.', '_')
            # Capture frame-by-frame
            ret, frame = cap.read()
            frame = cv2.resize(frame, (540, 380), fx=0, fy=0,
                               interpolation=cv2.INTER_CUBIC)
            if ret and current_frame % 5 == 0:
                image_path = 'img_client/cli_%s.jpeg' % image_name
                cv2.imwrite(image_path, frame)
                send_image(image_path)
                print('frame %s sent' % current_frame)

            current_frame += 1
            if current_frame % fps == 0:
                print('frame: %s, time: %s' % (current_frame, time.time() - start_time))
                start_time = time.time()

    # release the video capture object
    cap.release()
    # Closes all the windows currently opened.
    cv2.destroyAllWindows()
    print('Releasing the capture and destroying any windows.')


if __name__ == '__main__':
    process_video()
