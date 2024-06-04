import unittest
import socket
import threading
import time

# Import the setup_server function from the original location
from code.server import setup_server


def server_program():
    setup_server()  # Call your server setup function

    conn, _ = server_socket.accept()
    while True:
        data = conn.recv(1024).decode()
        print("CLIENT:", data)

        if data == "EXIT":
            break

        # Echo the received message back to the client
        conn.send("B".encode())

    conn.close()


def client_program():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 5678))

    messages = ["A", "C", "EXIT"]
    for message in messages:
        client_socket.send(message.encode())
        print("SERVER:", client_socket.recv(1024).decode())
        time.sleep(1)  # Add a delay to ensure messages are printed sequentially

    client_socket.close()


class TestCommunication(unittest.TestCase):

    def test_client_server_communication(self):
        global server_socket  # Define server_socket as global variable
        server_thread = threading.Thread(target=server_program)
        server_thread.start()

        client_program()

        server_thread.join()


if __name__ == '__main__':
    unittest.main()
