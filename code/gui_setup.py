import os
import sys
import tkinter as tk
from tkinter import scrolledtext
from find_phishing import start_finding


def setup_gui(window, emails, show_email_func, download_attachments_func):
    bg_color = "#f0f0f0"
    create_sidebar(window, bg_color, emails, show_email_func, download_attachments_func)


def create_sidebar(window, bg_color, emails, show_email_func, download_attachments_func):
    sidebar_frame = create_frame(window, bg_color)
    email_listbox = create_email_listbox(sidebar_frame, emails)
    email_listbox.bind("<ButtonRelease-1>",
                       lambda event: show_email_func(email_listbox, emails, text_area, download_button))

    create_refresh_button(sidebar_frame)  # Add a refresh button

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
    email_listbox = tk.Listbox(frame, width=30, height=20, font=("Arial", 12), bg=frame.cget("bg"), fg="#333333")
    for email in emails:
        email_listbox.insert(tk.END, f"{email.subject} ({email.date})")
    email_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    return email_listbox


def create_header_label(frame):
    header_label = tk.Label(frame, text="Email Details", font=("Arial", 16, "bold"), fg="white", bg="#1e90ff", padx=10,
                             pady=5)
    header_label.pack(fill=tk.X)


def create_text_area(frame):
    text_area = scrolledtext.ScrolledText(frame, width=80, height=30, font=("Arial", 12), bg=frame.cget("bg"),
                                           fg="#333333")
    text_area.tag_config("header", font=("Arial", 16, "bold"), foreground="#1e90ff")
    text_area.pack(expand=True, fill='both')
    text_area.config(state=tk.DISABLED)
    return text_area

def create_refresh_button(frame):
    refresh_button = tk.Button(frame, text="Refresh", command=restart_program)
    refresh_button.pack(pady=5)
    return refresh_button

def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)


def create_download_button(frame, download_func, listbox, emails):
    download_button = tk.Button(frame, text="Download Attachments",
                                command=lambda: download_func(listbox, emails), state=tk.DISABLED)
    download_button.pack(pady=5)
    return download_button


def create_phishing_button(frame, listbox, emails):
    detect_phishing_button = tk.Button(frame, text="Detect Phishing",
                                       command=lambda: find_phishing_in_message(listbox, emails), bg="red",
                                       fg="white")
    detect_phishing_button.pack(pady=5)

def find_phishing_in_message(email_listbox, emails):
    index = email_listbox.curselection()[0]
    email = emails[index]
    start_finding(email)


def detect_phishing_window(email_listbox, emails):
    phishing_window = tk.Toplevel()
    phishing_window.title("Detect Phishing")
    phishing_window.geometry("600x400")
    phishing_window.configure(bg="#f0f0f0")

    index = email_listbox.curselection()[0]
    email = emails[index]

    from_label = tk.Label(phishing_window, text=f"From: {email.sender}", font=("Arial", 14), bg="#f0f0f0", padx=10, pady=5)
    from_label.grid(row=0, column=0, sticky="w")

    subject_label = tk.Label(phishing_window, text=f"Subject: {email.subject}", font=("Arial", 14), bg="#f0f0f0", padx=10, pady=5)
    subject_label.grid(row=1, column=0, sticky="w")

    date_label = tk.Label(phishing_window, text=f"Date: {email.date}", font=("Arial", 14), bg="#f0f0f0", padx=10, pady=5)
    date_label.grid(row=2, column=0, sticky="w")

    body_label = tk.Label(phishing_window, text=f"Message Body:", font=("Arial", 14), bg="#f0f0f0", padx=10, pady=5)
    body_label.grid(row=3, column=0, sticky="w")

    body_text = tk.Text(phishing_window, wrap="word", font=("Arial", 12), height=10, width=60)
    body_text.grid(row=4, column=0, padx=10, pady=5)
    body_text.insert("1.0", email.plain)
    body_text.config(state="disabled")

    bottom_padding = tk.Label(phishing_window, text="", bg="#f0f0f0", pady=10)
    bottom_padding.grid(row=5, column=0)

    phishing_window.update_idletasks()
    width = phishing_window.winfo_width()
    height = phishing_window.winfo_height()
    x_coordinate = (phishing_window.winfo_screenwidth() // 2) - (width // 2)
    y_coordinate = (phishing_window.winfo_screenheight() // 2) - (height // 2)
    phishing_window.geometry(f"+{x_coordinate}+{y_coordinate}")

    pass
