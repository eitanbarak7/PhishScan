import tkinter as tk
from gui_setup import setup_gui
from email_operations import show_email, download_attachments, fetch_emails

# Create the main window
window = tk.Tk()
window.title("Gmail Inbox")

# Fetch unread messages
emails = fetch_emails()

# Setup GUI
setup_gui(window, emails, show_email, download_attachments)

# Start the Tkinter event loop
window.mainloop()
