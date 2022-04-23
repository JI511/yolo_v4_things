import socket
import time

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IP, SOCK_STREAM = TCP
client.connect(('localhost', 1002))  # 127.0.0.1
BUFFER_SIZE = 2048

count = 1
while count < 10:
    client.send(b'client request')
    print('client request sent, waiting for Ready reply')
    packet = client.recv(BUFFER_SIZE)
    while packet:
        if packet == b'server ready':
            print('client acknowledges server ready, sending image, count: %s' % count)
            file = open('img/street.jpeg', 'rb')
            image_data = file.read(BUFFER_SIZE)

            packet_count = 1
            while image_data:
                client.send(image_data)
                image_data = file.read(BUFFER_SIZE)
                packet_count += 1
            file.close()
            time.sleep(1)
            print('client image sent, packets: %s' % packet_count)
            client.send(b'client complete')
            print('send client complete')

            # wait for server to acknowledge completion
            packet = client.recv(BUFFER_SIZE)
            if packet == b'server complete':
                packet = False
            count += 1
        else:
            packet = client.recv(BUFFER_SIZE)

client.close()
