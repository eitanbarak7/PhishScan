import socket
import sqlite3
import tkinter as tk
from tkinter import ttk
import threading

# Database setup
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

# Server setup
host = 'localhost'
port = 5678

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)

print("Server is listening on: {}:{}".format(host, port))

def update_scores(email, sender_score, email_score):
    cursor.execute('SELECT * FROM email_scores WHERE email=?', (email,))
    row = cursor.fetchone()

    if row:
        sender_score_sum = row[1] + sender_score
        sender_score_count = row[2] + 1
        email_score_sum = row[3] + email_score
        email_score_count = row[4] + 1
        cursor.execute('''
            UPDATE email_scores 
            SET sender_score_sum=?, sender_score_count=?, email_score_sum=?, email_score_count=?
            WHERE email=?
        ''', (sender_score_sum, sender_score_count, email_score_sum, email_score_count, email))
    else:
        cursor.execute('''
            INSERT INTO email_scores (email, sender_score_sum, sender_score_count, email_score_sum, email_score_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, sender_score, 1, email_score, 1))

    db.commit()
    update_treeview()

def get_average_scores():
    cursor.execute('''
        SELECT email, 
               ROUND(sender_score_sum*1.0/sender_score_count, 2) as avg_sender_score, 
               ROUND(email_score_sum*1.0/email_score_count, 2) as avg_email_score,
               sender_score_count
        FROM email_scores
    ''')
    return cursor.fetchall()

def get_email_info(email):
    cursor.execute('''
        SELECT email, 
               ROUND(sender_score_sum*1.0/sender_score_count, 2) as avg_sender_score, 
               ROUND(email_score_sum*1.0/email_score_count, 2) as avg_email_score,
               sender_score_count
        FROM email_scores
        WHERE email=?
    ''', (email,))
    return cursor.fetchone()

def update_treeview():
    for row in tree.get_children():
        tree.delete(row)
    for row in get_average_scores():
        tree.insert('', 'end', values=row)

def send_email_info(client_socket, email):
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
    client_socket.sendall(message.encode('utf-8'))

def handle_client(client_socket):
    while True:
        client_secret = client_socket.recv(100000).decode('utf-8')
        print("Email From: " + client_secret)
        email = client_secret
        send_email_info(client_socket, email)
        break

    while True:
        client_secret = client_socket.recv(100000).decode('utf-8')
        print("Sender's Email Score: " + client_secret)
        sender_score = int(client_secret)
        break

    while True:
        client_secret = client_socket.recv(100000).decode('utf-8')
        print("Whole Email Score: " + client_secret)
        email_score = int(client_secret)
        break

    update_scores(email, sender_score, email_score)
    client_socket.close()

def accept_connections():
    while True:
        client_socket, address = server_socket.accept()
        print("Connection from client: ", address)
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

# Tkinter setup
root = tk.Tk()
root.title("Email Scores")

def search_email():
    search_term = search_entry.get()
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute('''
        SELECT email, 
               ROUND(sender_score_sum*1.0/sender_score_count, 2) as avg_sender_score, 
               ROUND(email_score_sum*1.0/email_score_count, 2) as avg_email_score,
               sender_score_count
        FROM email_scores
        WHERE email LIKE ?
    ''', ('%' + search_term + '%',))
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)

def sort_treeview(column, reverse):
    data = [(tree.set(child, column), child) for child in tree.get_children('')]
    data.sort(reverse=reverse)
    for index, (value, child) in enumerate(data):
        tree.move(child, '', index)
    tree.heading(column, command=lambda: sort_treeview(column, not reverse))

tree = ttk.Treeview(root, columns=("Email", "Avg Sender Score", "Avg Email Score", "Count of Checks"), show='headings')
tree.heading("Email", text="Email", command=lambda: sort_treeview("Email", False))
tree.heading("Avg Sender Score", text="Avg Sender Score", command=lambda: sort_treeview("Avg Sender Score", False))
tree.heading("Avg Email Score", text="Avg Email Score", command=lambda: sort_treeview("Avg Email Score", False))
tree.heading("Count of Checks", text="Count of Checks", command=lambda: sort_treeview("Count of Checks", False))
tree.pack(fill=tk.BOTH, expand=True)

search_label = tk.Label(root, text="Search Email:")
search_label.pack(side=tk.LEFT, padx=10, pady=10)
search_entry = tk.Entry(root)
search_entry.pack(side=tk.LEFT, padx=10, pady=10)
search_button = tk.Button(root, text="Search", command=search_email)
search_button.pack(side=tk.LEFT, padx=10, pady=10)

# Start server in a new thread
server_thread = threading.Thread(target=accept_connections, daemon=True)
server_thread.start()

# Initial population of the treeview
update_treeview()

# Start Tkinter main loop
root.mainloop()

# Close the database connection when Tkinter window is closed
db.close()
