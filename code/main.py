import tkinter as tk
import threading
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
    display_image_fullscreen(r'C:\Users\Eitan\PycharmProjects\email\screens\welcome.png', on_button_click)
