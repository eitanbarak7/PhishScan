# Import necessary libraries
import socket
import sqlite3
import tkinter as tk
from tkinter import ttk
import threading
import re
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Generate server's key pair for encryption
server_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
server_public_key = server_private_key.public_key()

# Database setup: Creating SQLite database for storing email scores
db = sqlite3.connect('email_scores.db', check_same_thread=False)
cursor = db.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS email_scores (
        email TEXT PRIMARY KEY,
        sender_score_sum INTEGER,
        sender_score_count INTEGER,
        email_score_sum INTEGER,
        email_score_count INTEGER
    )
''')
db.commit()

# Server setup: Setting up socket for communication
host = 'localhost'
port = 5678

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)

print("Server is listening on: {}:{}".format(host, port))

# Function to escape string to avoid SQL injection


def escape_string(value):
    return str(sqlite3.Binary(value.encode()), 'utf-8')

# Function to update email scores in the database


def update_scores(email, sender_score, email_score):
    email = escape_string(email)
    cursor.execute('SELECT * FROM email_scores WHERE email=?', (email,))
    row = cursor.fetchone()

    if row:
        sender_score_sum = row[1] + sender_score
        sender_score_count = row[2] + 1
        email_score_sum = row[3] + email_score
        email_score_count = row[4] + 1
        query = '''
            UPDATE email_scores
            SET sender_score_sum=?, sender_score_count=?, email_score_sum=?, email_score_count=?
            WHERE email=?
        '''
        cursor.execute(query, (sender_score_sum, sender_score_count, email_score_sum, email_score_count, email))
    else:
        query = '''
            INSERT INTO email_scores (email, sender_score_sum, sender_score_count, email_score_sum, email_score_count)
            VALUES (?, ?, ?, ?, ?)
        '''
        cursor.execute(query, (email, sender_score, 1, email_score, 1))

    db.commit()
    update_treeview()

# Function to get average scores from the database


def get_average_scores():
    cursor.execute('''
        SELECT email,
               ROUND(sender_score_sum*1.0/sender_score_count, 2) as avg_sender_score,
               ROUND(email_score_sum*1.0/email_score_count, 2) as avg_email_score,
               sender_score_count
        FROM email_scores
    ''')
    return cursor.fetchall()

# Function to get email information from the database


def get_email_info(email):
    email = escape_string(email)
    query = '''
        SELECT email,
               ROUND(sender_score_sum*1.0/sender_score_count, 2) as avg_sender_score,
               ROUND(email_score_sum*1.0/email_score_count, 2) as avg_email_score,
               sender_score_count
        FROM email_scores
        WHERE email=?
    '''
    cursor.execute(query, (email,))
    return cursor.fetchone()

# Function to update the treeview with latest data


def update_treeview():
    for row in tree.get_children():
        tree.delete(row)
    for row in get_average_scores():
        displayed_email = extract_email(row[0])
        tree.insert('', 'end', values=(displayed_email, row[1], row[2], row[3]))

# Function to send email information to the client


def send_email_info(client_socket, email, cipher_suite):
    info = get_email_info(email)
    if info:
        message = (
            f"The email address: {info[0]}, has an average sender score of {info[1]}. "
            f"It has an average email score of {info[2]} (the email content score). "
            f"This email address has been checked by the server {info[3]} times till now."
        )
    else:
        message = (
            "This email address hasn't received an email score or sender score till now. "
            "It doesn't mean this isn't safe, this is just a parameter we can't use now. "
            "So check it as usual with the care needed."
        )
    encrypted_message = cipher_suite.encrypt(message.encode('utf-8'))
    client_socket.sendall(encrypted_message)

# Function to handle client requests


def handle_client(client_socket):
    try:
        # Receive client's public key
        client_public_key_pem = client_socket.recv(1024).decode()
        client_public_key = serialization.load_pem_public_key(
            client_public_key_pem.encode(),
            backend=default_backend()
        )
        print("Received client's public key.")

        # Send server's public key to the client
        server_public_key_pem = server_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        client_socket.send(server_public_key_pem.encode())
        print("Sent server's public key to the client.")

        # Generate a key for encryption
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        print("Generated encryption key.")

        # Send the encryption key to the client
        client_socket.send(key)
        print("Sent encryption key to the client.")

        while True:
            encrypted_data = client_socket.recv(100000)
            print("Received encrypted data from the client.")
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            print("Decrypted data:", decrypted_data)
            client_secret = decrypted_data.decode('utf-8')
            print("Email From: " + client_secret)
            email = client_secret
            send_email_info(client_socket, email, cipher_suite)
            break

        while True:
            encrypted_data = client_socket.recv(100000)
            print("Received encrypted data from the client.")
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            print("Decrypted data:", decrypted_data)
            client_secret = decrypted_data.decode('utf-8')
            print("Sender's Email Score: " + client_secret)
            sender_score = int(client_secret)
            break

        while True:
            encrypted_data = client_socket.recv(100000)
            print("Received encrypted data from the client.")
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            print("Decrypted data:", decrypted_data)
            client_secret = decrypted_data.decode('utf-8')
            print("Whole Email Score: " + client_secret)
            email_score = int(client_secret)
            break

        update_scores(email, sender_score, email_score)
        client_socket.close()
    except Exception as e:
        print("Error handling client:", str(e))
        client_socket.close()

# Function to accept incoming connections


def accept_connections():
    while True:
        client_socket, address = server_socket.accept()
        print("\nConnection from client: ", address)
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

# Tkinter setup:
# Setting up Tkinter GUI


root = tk.Tk()
root.title("Email Scores")

# Function to search for an email address in the database


def search_email():
    search_term = search_entry.get()
    for row in tree.get_children():
        tree.delete(row)
    query = '''
        SELECT email,
               ROUND(sender_score_sum*1.0/sender_score_count, 2) as avg_sender_score,
               ROUND(email_score_sum*1.0/email_score_count, 2) as avg_email_score,
               sender_score_count
        FROM email_scores
        WHERE email LIKE ?
    '''
    cursor.execute(query, ('%' + search_term + '%',))
    for row in cursor.fetchall():
        displayed_email = extract_email(row[0])
        tree.insert('', 'end', values=(displayed_email, row[1], row[2], row[3]))

# Function to extract email from the full email address


def extract_email(full_email):
    match = re.search(r'<(.+?)>', full_email)
    if match:
        return match.group(1)
    return full_email

# Function to sort the treeview columns


def sort_treeview(column, reverse):
    def convert(value):
        try:
            return float(value)
        except ValueError:
            return value

    data = [(convert(tree.set(child, column)), child) for child in tree.get_children('')]
    data.sort(reverse=reverse)
    for index, (value, child) in enumerate(data):
        tree.move(child, '', index)
    tree.heading(column, command=lambda: sort_treeview(column, not reverse))


# Creating Treeview widget to display email scores
tree = ttk.Treeview(root, columns=("Email", "Avg Sender Score", "Avg Email Score", "Count of Checks"), show='headings')
tree.heading("Email", text="Email", command=lambda: sort_treeview("Email", False))
tree.heading("Avg Sender Score", text="Avg Sender Score", command=lambda: sort_treeview("Avg Sender Score", False))
tree.heading("Avg Email Score", text="Avg Email Score", command=lambda: sort_treeview("Avg Email Score", False))
tree.heading("Count of Checks", text="Count of Checks", command=lambda: sort_treeview("Count of Checks", False))
tree.pack(fill=tk.BOTH, expand=True)

# Adding search functionality to the GUI
search_label = tk.Label(root, text="Search Email:")
search_label.pack(side=tk.LEFT, padx=10, pady=10)
search_entry = tk.Entry(root)
search_entry.pack(side=tk.LEFT, padx=10, pady=10)
search_button = tk.Button(root, text="Search", command=search_email)
search_button.pack(side=tk.LEFT, padx=10, pady=10)

# Start server in a new thread to handle incoming connections
server_thread = threading.Thread(target=accept_connections, daemon=True)
server_thread.start()

# Initial population of the treeview with existing data
update_treeview()

# Start Tkinter main loop
root.mainloop()

# Close the database connection when Tkinter window is closed
db.close()
