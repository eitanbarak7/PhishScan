import tkinter as tk
import socket
from gui_setup import setup_gui
from email_operations import show_email, download_attachments, fetch_emails
import pickle

def start_program():
    # Create the main window
    window = tk.Tk()
    window.geometry("1300x800")
    window.title("Gmail Inbox")

    # Fetch unread messages
    emails = fetch_emails()

    # Setup GUI
    setup_gui(window, emails, show_email, download_attachments)

    # Start the Tkinter event loop
    window.mainloop()

start_program()
