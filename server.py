import argparse
import datetime
import io
import os
from queue import Queue
import socket
import threading
import time

import cv2
import numpy as np
from PIL import Image
from PIL import UnidentifiedImageError

from yolo_predictions import YoloPredictions

BUFFER_SIZE = 2048
images_to_process_queue = Queue()
processed_images = Queue()
SERVER_IP = '192.168.0.228'
SERVER_PORT = 10002


def collect_images(app_server, image_processing):
    received_images = 0
    current_time = time.time()
    while True:

        client_socket, client_address = app_server.accept()
        client_socket.send(b'server ready')

        file_stream = io.BytesIO()
        packet = client_socket.recv(BUFFER_SIZE)
        while packet:
            file_stream.write(packet)
            packet = client_socket.recv(BUFFER_SIZE)

        # Sometimes the last image gets corrupted?
        try:
            image = Image.open(file_stream)
            received_images += 1
            if image_processing:
                # todo get rid of this temp file creation
                image_name = 'temp_%s.jpeg' % datetime.datetime.now().microsecond
                image_path = './img_processed/%s' % image_name
                image.save(image_path, format='JPEG')
                images_to_process_queue.put((image_path, time.time()))
            else:
                img_arr = np.asarray(image)
                processed_images.put(img_arr)

        except UnidentifiedImageError:
            print('There was an issue processing image data. Ignoring image.')

        if received_images % 25 == 0:
            print('%s images received, %s' % (received_images, time.time() - current_time))
            current_time = time.time()


def perform_predictions(yolo_model):
    while True:
        while not images_to_process_queue.empty():
            image_pop = images_to_process_queue.get()
            image_path = image_pop[0]
            image_recv_time = image_pop[1]
            processed_array = yolo_model.predict_and_save_image(image_path)
            height = processed_array.shape[0]
            width = processed_array.shape[1]

            txt_img_a = cv2.putText(img=processed_array, text="avg predict time: %s" % yolo_model.average_predict_time,
                                    org=(5, (height - 5)), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1.0,
                                    color=(0, 0, 0), thickness=1)
            txt_img_b = cv2.putText(img=txt_img_a, text="time since recv: %s" % round(time.time() - image_recv_time, 3),
                                    org=(5, (height - 25)), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1.0,
                                    color=(0, 0, 0), thickness=1)
            processed_images.put(txt_img_b)
            os.remove(image_path)


def display_images():
    while True:
        if processed_images.empty():
            # put the thread to sleep so it doesnt take up processing time
            time.sleep(0.05)
        else:
            while not processed_images.empty():
                proc_pop = processed_images.get()
                cv2.imshow('Processed', proc_pop)

                # This escape sequence is needed for cv2.imshow() to work
                k = cv2.waitKey(20)
                # 113 is ASCII code for q key
                if k == 113:
                    break

                # if we fall too far behind, purge the queue (shouldn't happen?)
                if processed_images.qsize() > 20:
                    with processed_images.mutex:
                        processed_images.queue.clear()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--do_processing", help="True if you want to do object detection on the video stream.",
                        type=bool, default=False)
    args = parser.parse_args()

    do_image_processing = args.do_processing

    if do_image_processing:
        yv4_model = YoloPredictions()
        print('Performing test prediciton...')
        yv4_model.predict_and_save_image('./img/street.jpeg')
        predict_thread = threading.Thread(target=perform_predictions, args=(yv4_model,))
        predict_thread.start()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IP, SOCK_STREAM = TCP
    server.bind((SERVER_IP, SERVER_PORT))
    print('server bound to %s at port %s' % (SERVER_IP, SERVER_PORT))
    server.listen()
    print('server listening...')

    sock_thread = threading.Thread(target=collect_images, args=(server, do_image_processing))
    sock_thread.start()
    show_thread = threading.Thread(target=display_images, args=())
    show_thread.start()
