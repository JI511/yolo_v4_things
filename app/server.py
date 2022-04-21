import datetime
import io
import socket
from PIL import Image

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IP, SOCK_STREAM = TCP
server.bind(('localhost', 1002))  # 127.0.0.1
print('server bound to localhost at port 1002')
server.listen()
print('server listening...')
BUFFER_SIZE = 4096

while True:
    client_socket, client_address = server.accept()
    print('Client connected... client socket: %s, client address: %s' % (client_socket, client_address))

    file_stream = io.BytesIO()
    packet = client_socket.recv(BUFFER_SIZE)

    while packet:
        file_stream.write(packet)
        packet = client_socket.recv(BUFFER_SIZE)

        # TODO send ack messages or image title?

    image = Image.open(file_stream)
    image_time = datetime.datetime.now().microsecond
    image.save('../img_processed/%s.jpeg' % image_time, format='JPEG')
    print('Image: %s saved' % image_time)
