import datetime
import queue
import subprocess
import threading
from tkinter import scrolledtext
import tkinter as tk
from find_phishing import start_finding
from screens import start_loading_screen


def setup_gui(window, emails, show_email_func, download_attachments_func):
    bg_color = "#f0f0f0"
    create_sidebar(window, bg_color, emails, show_email_func, download_attachments_func)


def create_sidebar(window, bg_color, emails, show_email_func, download_attachments_func):
    def create_listbox_with_scrollbar(parent_frame, emails):
        scrollbar = tk.Scrollbar(parent_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        email_listbox = create_email_listbox(parent_frame, emails)  # Utilize existing function
        email_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        email_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=email_listbox.yview)

        return email_listbox

    def manage_whitelist():
        try:
            # Execute the manage_whitelist.py file using subprocess
            subprocess.run(["python", "C:\\Users\\Eitan\\PycharmProjects\\PhishScan\\code\\lists\\manage_whitelist.py"])
        except Exception as e:
            print("Error executing manage_whitelist.py:", e)

    def manage_blacklist():
        try:
            # Execute the manage_blacklist.py file using subprocess
            subprocess.run(["python", "C:\\Users\\Eitan\\PycharmProjects\\PhishScan\\code\\lists\\manage_blacklist.py"])
        except Exception as e:
            print("Error executing manage_blacklist.py:", e)

    # Create a frame for the buttons
    buttons_frame = tk.Frame(window, bg=bg_color)
    buttons_frame.pack(side=tk.TOP, fill=tk.X)

    # 'Whitelist' button
    whitelist_button = tk.Button(buttons_frame, text="Manage Whitelist", bg="white", fg="black", width=15,
                                 command=lambda: manage_whitelist())
    whitelist_button.pack(side=tk.LEFT, padx=5, pady=5)

    # 'Blacklist' button
    blacklist_button = tk.Button(buttons_frame, text="Manage Blacklist", bg="black", fg="white", width=15,
                                 command=lambda: manage_blacklist())
    blacklist_button.pack(side=tk.LEFT, padx=5, pady=5)

    # Function to close the window
    def close_window():
        window.destroy()

    # 'X' button
    close_button = tk.Button(buttons_frame, text="X", bg="red", fg="white", width=3, command=close_window)
    close_button.pack(side=tk.RIGHT, padx=5, pady=5)

    # Add the sidebar frame for email list and title
    sidebar_frame = create_frame(window, bg_color)

    # Add a title for the unread emails list
    title_label = tk.Label(sidebar_frame, text="Your unread emails:", font=("Arial", 14, "bold"), bg=bg_color,
                           fg="black")
    title_label.pack(side=tk.TOP, pady=(10, 0))  # Adjust padding as needed

    email_listbox = create_listbox_with_scrollbar(sidebar_frame, emails)

    email_listbox.bind("<ButtonRelease-1>",
                       lambda event: (show_email_func(email_listbox, emails, text_area, download_button),
                                      ))  # Call both functions when the button is clicked

    email_frame = create_frame(window, bg_color)
    create_header_label(email_frame)
    text_area = create_text_area(email_frame)
    download_button = create_download_button(email_frame, download_attachments_func, email_listbox, emails)
    create_phishing_button(email_frame, email_listbox, emails)


def create_frame(window, bg_color):
    frame = tk.Frame(window, bg=bg_color)
    frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    return frame


def create_email_listbox(frame, emails):
    email_listbox = tk.Listbox(frame, width=50, height=20, font=("Arial", 10), bg=frame.cget("bg"), fg="#333333")

    for email in emails:
        # Format date
        email_date_string = email.date
        email_date = datetime.datetime.strptime(email_date_string, "%Y-%m-%d %H:%M:%S%z")
        date = email_date.strftime("%Y-%m-%d %H:%M")

        # Format subject
        subject = (email.subject[:47] + "..." if len(email.subject) > 50 else email.subject)

        email_listbox.insert(tk.END,
                             f"{date}{' ' * 5}{subject}")  # Display date, padding, and subject

    email_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    return email_listbox


def create_header_label(frame):
    header_label = tk.Label(frame, text="Click on an email in order to see more...", font=("Arial", 16, "bold"),
                            fg="white", bg="#1e90ff", padx=10,
                            pady=5)
    header_label.pack(fill=tk.X)


def create_text_area(frame):
    text_area = scrolledtext.ScrolledText(frame, width=80, height=30, font=("Arial", 12), bg=frame.cget("bg"),
                                          fg="#333333")
    text_area.tag_config("header", font=("Arial", 16, "bold"), foreground="#1e90ff")
    text_area.pack(expand=True, fill='both')
    text_area.config(state=tk.DISABLED)
    return text_area


def create_download_button(frame, download_func, listbox, emails):
    download_button = tk.Button(frame, text="Download Attachments", width=20, height=2,
                                command=lambda: download_func(listbox, emails), state=tk.DISABLED)
    download_button.pack(side=tk.LEFT, padx=5, pady=5)  # Adjust padding as needed
    return download_button


def create_phishing_button(frame, listbox, emails):
    detect_phishing_button = tk.Button(frame, text="Detect Phishing", width=20, height=2,
                                       command=lambda: find_phishing_in_message(listbox, emails), bg="red",
                                       fg="white")
    detect_phishing_button.pack(side=tk.LEFT, padx=5, pady=5)  # Adjust padding as needed


def find_phishing_in_message(email_listbox, emails):
    index = email_listbox.curselection()[0]
    email = emails[index]

    # Define the find_with_load function before calling it
    def find_with_load():
        # Create a queue to signal when the program has finished loading
        done_queue = queue.Queue()

        # Start the loading screen in a separate thread
        threading.Thread(target=start_loading_screen, args=(done_queue,)).start()

        # Run start_finding in the main thread
        start_finding(done_queue, email)

    # Call the find_with_load function
    find_with_load()
