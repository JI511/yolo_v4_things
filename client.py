import argparse
import os
from queue import Queue
import socket
import time

import cv2

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


def process_webcam_video(send_rate):
    # Creating a VideoCapture object to read the webcam video
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if cap.isOpened():
        start_time = time.time()
        current_time = time.time()
        image_count = 0
        # Loop until the end of the video
        while cap.isOpened():
            image_name = str(cap.get(0)).replace('.', '_')
            # Capture frame-by-frame
            ret, frame = cap.read()
            frame = cv2.resize(frame, (540, 380), fx=0, fy=0,
                               interpolation=cv2.INTER_CUBIC)
            # send an image at desired rate
            if time.time() - current_time > (1 / send_rate):
                current_time = time.time()
                image_path = 'img_client/cli_%s.jpeg' % image_name
                cv2.imwrite(image_path, frame)
                send_image(image_path)
                image_count += 1
                if image_count % 25 == 0:
                    print('images: %s, time: %s' % (image_count, time.time() - start_time))

    # release the video capture object
    cap.release()
    # Closes all the windows currently opened.
    cv2.destroyAllWindows()
    print('Releasing the capture and destroying any windows.')


if __name__ == '__main__':
    client_send_rate = 1

    parser = argparse.ArgumentParser()
    parser.add_argument("--send_rate", help="The number of frames per second to send to the server"
                                            " for image processing. Default is 1 and max is 5.",
                        type=int)
    args = parser.parse_args()
    if args.send_rate:
        client_send_rate = args.send_rate
        print('Using specified send rate value of: %s' % args.send_rate)

    process_webcam_video(client_send_rate)
