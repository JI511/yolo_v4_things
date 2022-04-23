import socket
import time


BUFFER_SIZE = 2048

count = 1
while count < 100:
    # print("count: %s" % count)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IP, SOCK_STREAM = TCP
    client.connect(('localhost', 1002))  # 127.0.0.1

    packet = client.recv(BUFFER_SIZE)
    if packet == b'server ready':
        file = open('img/street.jpeg', 'rb')
        image_data = file.read(BUFFER_SIZE)

        packet_count = 1
        while image_data:
            client.send(image_data)
            image_data = file.read(BUFFER_SIZE)
            packet_count += 1
        file.close()
        count += 1
    else:
        print('packet didnt match')

    client.close()
