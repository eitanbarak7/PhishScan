import os
import tkinter as tk
import threading

from email_scores import sync_email_scores
from screens import display_image_fullscreen, start_loading_screen
from gui_setup import setup_gui
from email_operations import show_email, download_attachments, fetch_emails
import queue


def start_program(done_queue):
    print("Starting program")

    # Fetch unread messages
    print("Fetching emails...")
    emails = fetch_emails()
    print(f"Fetched {len(emails)} emails")
    sync_email_scores(emails)  # Synchronize email scores after fetching emails

    # Signal that the loading is complete
    done_queue.put("done")

    # Create the main window
    # Create a Tkinter window
    window = tk.Tk()

    # Set the window title
    window.title("Gmail Inbox")

    # Set the window geometry to full screen
    window.attributes('-fullscreen', True)

    # Setup GUI
    setup_gui(window, emails, show_email, download_attachments)
    print("GUI setup complete")

    # Start the Tkinter event loop
    window.mainloop()


def on_button_click(root):
    root.destroy()

    # Create a queue to signal when the program has finished loading
    done_queue = queue.Queue()

    # Start the loading screen in a separate thread
    threading.Thread(target=start_loading_screen, args=(done_queue,)).start()

    # Run start_program in the main thread
    start_program(done_queue)


# Start the welcome screen
if __name__ == "__main__":
    # Construct the path to the 'welcome.png' image in the 'screens' directory
    image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'screens', 'welcome.png')

    # Check if the file exists
    if os.path.isfile(image_path):
        display_image_fullscreen(image_path, on_button_click)
    else:
        print(f"Error: The file does not exist at the path: {image_path}")
