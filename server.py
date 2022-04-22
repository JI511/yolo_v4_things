import datetime
import io
import os
import socket
from PIL import Image
from yolo_predictions import YoloPredictions

yolo_model = YoloPredictions()
print('Performing test prediciton...')
yolo_model.predict_and_save_image('./img/street.jpeg')
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IP, SOCK_STREAM = TCP
server.bind(('localhost', 1002))  # 127.0.0.1
print('server bound to localhost at port 1002')
server.listen()
print('server listening...')
BUFFER_SIZE = 2048
client_socket, client_address = server.accept()
print('Client connected... client socket: %s, client address: %s' % (client_socket, client_address))

while True:
    # Wait for client to send
    packet = client_socket.recv(BUFFER_SIZE)
    if packet == b'client request':
        client_socket.send(b'server ready')
        print('server sent ready, waiting for image')

    file_stream = io.BytesIO()
    packet = client_socket.recv(BUFFER_SIZE)
    while packet:
        if packet == b'client complete':
            print('full image received')
            break
        else:
            file_stream.write(packet)
            packet = client_socket.recv(BUFFER_SIZE)

    image = Image.open(file_stream)
    image_name = 'temp_%s.jpeg' % datetime.datetime.now().microsecond
    image_path = './img_processed/%s' % image_name
    image.save(image_path, format='JPEG')
    # print('saved image at: %s' % image_path)
    time_taken = yolo_model.predict_and_save_image(image_path)
    print('process time: %s', time_taken)
    os.remove('./img_processed/%s' % image_name)
    client_socket.send(b'server complete')
    # print('temp image removed at: %s' % image_path)
