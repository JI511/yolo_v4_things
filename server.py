import datetime
import io
import os
from queue import Queue
import socket
import threading
import time

from PIL import Image
from PIL import UnidentifiedImageError

from yolo_predictions import YoloPredictions

BUFFER_SIZE = 2048
image_queue = Queue()


def collect_images(app_server):
    while True:

        client_socket, client_address = app_server.accept()
        print('Client connected... client socket: %s, client address: %s' % (client_socket, client_address))
        # Wait for client to send
        client_socket.send(b'server ready')

        file_stream = io.BytesIO()
        packet = client_socket.recv(BUFFER_SIZE)
        while packet:
            file_stream.write(packet)
            packet = client_socket.recv(BUFFER_SIZE)

        # Sometimes the last image gets corrupted?
        try:
            image = Image.open(file_stream)
            image_name = 'temp_%s.jpeg' % datetime.datetime.now().microsecond
            image_path = './img_processed/%s' % image_name
            # image.save(image_path, format='JPEG')
            image_queue.put(image_path)
            print('image saved')

        except UnidentifiedImageError:
            print('There was an issue processing image data. Ignoring image.')


def perform_predictions(yolo_model):
    while True:
        while not image_queue.empty():
            image_pop = image_queue.get()
            time_taken = yolo_model.predict_and_save_image(image_pop)
            print('process time: %s', time_taken)
            os.remove(image_pop)


if __name__ == '__main__':
    yv4_model = YoloPredictions()
    print('Performing test prediciton...')
    yv4_model.predict_and_save_image('./img/street.jpeg')

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IP, SOCK_STREAM = TCP
    server.bind(('localhost', 1002))  # 127.0.0.1
    print('server bound to localhost at port 1002')
    server.listen()
    print('server listening...')

    sock_thread = threading.Thread(target=collect_images, args=(server,))
    sock_thread.start()
    predict_thread = threading.Thread(target=perform_predictions, args=(yv4_model,))
    predict_thread.start()
