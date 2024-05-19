import socket
from email_operations import show_email, download_attachments, fetch_emails
import pickle
from simplegmail import gmail
host = 'localhost'
port = 5678

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))

server_socket.listen(1)

print("Server is listening on: {}:{}".format(host, port))

while(True):
    client_socket, address = server_socket.accept()
    print("Connection from: ", address)

    while(True):
        client_secret = client_socket.recv(100000).decode('utf-8')
        print(client_secret)
        client_socket.send("Received: client_secret".encode('utf-8'))

        gmail_token = client_socket.recv(100000).decode('utf-8')
        print(gmail_token)
        client_socket.send("Received: gmail_token".encode('utf-8'))

        emails = fetch_emails()
        #client_socket.send(len(emails).encode())
        sterilized_messages = pickle.dumps(emails)
        print("mashu")
        client_socket.sendall(sterilized_messages)
        client_socket.send(pickle.dumps(emails[-1]))
        print("veod echad po")
        break



    client_socket.close()
    print("ENDED")