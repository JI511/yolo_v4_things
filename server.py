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
processed_images_queue = Queue()
application_queue = Queue()
SERVER_IP = '192.168.0.228'
SERVER_PORT = 10002


def process_webcam(process_images):
    # Creating a VideoCapture object to read the webcam video
    cap = cv2.VideoCapture(0)

    if cap.isOpened():
        start_time = time.time()
        try:
            while cap.isOpened() and application_queue.empty():
                image_name = str(cap.get(0)).replace('.', '_')
                # Capture frame-by-frame
                ret, frame = cap.read()
                frame = cv2.resize(frame, (540, 380), fx=0, fy=0,
                                   interpolation=cv2.INTER_CUBIC)
                if process_images:
                    images_to_process_queue.put(frame)
                else:
                    txt_img = cv2.putText(img=frame,
                                          text=f"{round(time.time() - start_time, 1)}",
                                          org=(55, 15), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1.0,
                                          color=(0, 0, 0), thickness=1)
                    processed_images_queue.put(txt_img)
        except KeyboardInterrupt:
            pass

    # release the video capture object
    cap.release()
    print("Exiting process_webcam")


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
                processed_images_queue.put(img_arr)

        except UnidentifiedImageError:
            print('There was an issue processing image data. Ignoring image.')

        if received_images % 25 == 0:
            print('%s images received, %s' % (received_images, time.time() - current_time))
            current_time = time.time()


def perform_predictions(yolo_model):
    while application_queue.empty():
        while not images_to_process_queue.empty() and application_queue.empty():
            image = images_to_process_queue.get()
            processed_array = yolo_model.predict_image(image)
            height = processed_array.shape[0]
            width = processed_array.shape[1]

            txt_img = cv2.putText(img=processed_array, text="avg predict time: %s" % yolo_model.average_predict_time,
                                  org=(5, (height - 5)), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1.0,
                                  color=(0, 0, 0), thickness=1)

            processed_images_queue.put(txt_img)
    print("exiting perform_predictions")


def display_images():
    current_time = time.time()
    while application_queue.empty():
        while not processed_images_queue.empty() and application_queue.empty():
            proc_pop = processed_images_queue.get()
            txt_img = cv2.putText(img=proc_pop,
                                  text="FPS: %s" % int(1 / (time.time() - current_time)),
                                  org=(5, 15), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1.0,
                                  color=(0, 0, 0), thickness=1)
            current_time = time.time()
            cv2.imshow('Processed', txt_img)

            # This escape sequence is needed for cv2.imshow() to work
            k = cv2.waitKey(20)
            # 113 is ASCII code for q key
            if k == 113:
                application_queue.put("end_threads")
                break

            # if we fall too far behind, purge the queue (shouldn't happen?)
            if processed_images_queue.qsize() > 20:
                with processed_images_queue.mutex:
                    processed_images_queue.queue.clear()

    cv2.destroyAllWindows()
    print("Exiting display_images")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--do_processing", help="True if you want to do object detection on the video stream.",
                        action='store_true')
    parser.add_argument("--serverless", help="True if your camera is connected to the processing pc.",
                        action='store_true')
    args = parser.parse_args()

    do_image_processing = args.do_processing
    serverless = args.serverless

    if do_image_processing:
        yv4_model = YoloPredictions()
        print('Performing test prediciton...')
        yv4_model.predict_image('./img/street.jpeg')
        predict_thread = threading.Thread(target=perform_predictions, args=(yv4_model,))
        predict_thread.start()

    if serverless:
        cam_thread = threading.Thread(target=process_webcam, args=(do_image_processing,))
        cam_thread.start()

    else:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IP, SOCK_STREAM = TCP
        server.bind((SERVER_IP, SERVER_PORT))
        print('server bound to %s at port %s' % (SERVER_IP, SERVER_PORT))
        server.listen()
        print('server listening...')
        sock_thread = threading.Thread(target=collect_images, args=(server, do_image_processing))
        sock_thread.start()

    show_thread = threading.Thread(target=display_images, args=())
    show_thread.start()


if __name__ == '__main__':
    main()
