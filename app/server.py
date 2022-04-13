import socket


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IP, SOCK_STREAM = TCP
server.bind(('localhost', 1002))  # 127.0.0.1
print('server bound to localhost:1002')
server.listen()
print('server listening...')

client_socket, client_address = server.accept()
print('Client connected... client socket: %s, client address: %s' % (client_socket, client_address))

file = open('server_image.jpg', "wb")
image_chunk = client_socket.recv(2048)  # stream-based protocol

while image_chunk:
    file.write(image_chunk)
    image_chunk = client_socket.recv(2048)

file.close()
client_socket.close()
