import socket

host = 'localhost'
port = 5678

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))

server_socket.listen(1)

print("Server is listening on: {}:{}".format(host, port))

while True:
    client_socket, address = server_socket.accept()
    print("Connection from client: ", address)

    while True:
        client_secret = client_socket.recv(100000).decode('utf-8')
        print("Email From: " + client_secret)
        break

    while True:
        client_secret = client_socket.recv(100000).decode('utf-8')
        print("Sender's Email Score: " + client_secret)
        break

    while True:
        client_secret = client_socket.recv(100000).decode('utf-8')
        print("Whole Email Score: " + client_secret)
        break

    client_socket.close()
