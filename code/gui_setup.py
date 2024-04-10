import tkinter as tk
from tkinter import scrolledtext, messagebox
from email_operations import show_email, download_attachments


def setup_gui(window, emails, show_email_func, download_attachments_func):
    # Define colors
    bg_color = "#f0f0f0"
    header_color = "#1e90ff"
    text_color = "#333333"
    # Define font sizes
    header_font = ("Arial", 16, "bold")
    sender_font = ("Arial", 12, "bold")
    subject_font = ("Arial", 12)
    date_font = ("Arial", 10, "italic")
    preview_font = ("Arial", 10)
    body_font = ("Arial", 12)

    # Create a frame for the sidebar
    sidebar_frame = tk.Frame(window, bg=bg_color)
    sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

    # Create a listbox to display email subjects and dates in the sidebar
    email_listbox = tk.Listbox(sidebar_frame, width=30, height=20, font=subject_font, bg=bg_color, fg=text_color)
    for email in emails:
        email_listbox.insert(tk.END, f"{email.subject} ({email.date})")
    email_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Bind click event to the listbox
    email_listbox.bind("<ButtonRelease-1>",
                       lambda event: show_email_func(email_listbox, emails, text_area, download_button))

    # Create a frame for the email display
    email_frame = tk.Frame(window, bg=bg_color)
    email_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a header label for the email title
    header_label = tk.Label(email_frame, text="Email Details", font=header_font, fg="white", bg=header_color, padx=10,
                            pady=5)
    header_label.pack(fill=tk.X)

    # Create a scrollable text area to display the selected email
    text_area = scrolledtext.ScrolledText(email_frame, width=80, height=30, font=body_font, bg=bg_color, fg=text_color)
    text_area.tag_config("header", font=header_font, foreground=header_color)
    text_area.tag_config("sender", font=sender_font, foreground=text_color)
    text_area.tag_config("subject", font=subject_font, foreground=text_color)
    text_area.tag_config("date", font=date_font, foreground=text_color)
    text_area.tag_config("preview", font=preview_font, foreground=text_color)
    text_area.tag_config("body", font=body_font, foreground=text_color)
    text_area.pack(expand=True, fill='both')

    # Disable text area for read-only mode
    text_area.config(state=tk.DISABLED)

    # Create a download button for attachments
    download_button = tk.Button(email_frame, text="Download Attachments",
                                command=lambda: download_attachments_func(email_listbox, emails), state=tk.DISABLED)
    download_button.pack(pady=5)

    # Create a Detect Phishing button
    detect_phishing_button = tk.Button(email_frame, text="Detect Phishing",
                                       command=lambda: detect_phishing_window(email_listbox, emails), bg="red",
                                       fg="white")
    detect_phishing_button.pack(pady=5)


def detect_phishing_window(email_listbox, emails):
    # Create a new window
    phishing_window = tk.Toplevel()
    phishing_window.title("Detect Phishing")
    phishing_window.geometry("600x400")

    # Get the index of the selected email in the listbox
    index = email_listbox.curselection()[0]
    email = emails[index]

    # Create and place labels for email content
    from_label = tk.Label(phishing_window, text=f"From: {email.sender}", font=("Arial", 14), padx=10, pady=5)
    from_label.grid(row=0, column=0, sticky="w")

    subject_label = tk.Label(phishing_window, text=f"Subject: {email.subject}", font=("Arial", 14), padx=10, pady=5)
    subject_label.grid(row=1, column=0, sticky="w")

    date_label = tk.Label(phishing_window, text=f"Date: {email.date}", font=("Arial", 14), padx=10, pady=5)
    date_label.grid(row=2, column=0, sticky="w")

    preview_label = tk.Label(phishing_window, text=f"Preview: {email.snippet}", font=("Arial", 14), padx=10, pady=5)
    preview_label.grid(row=3, column=0, sticky="w")

    body_label = tk.Label(phishing_window, text=f"Message Body:", font=("Arial", 14), padx=10, pady=5)
    body_label.grid(row=4, column=0, sticky="w")

    body_text = tk.Text(phishing_window, wrap="word", font=("Arial", 12), height=10, width=60)
    body_text.grid(row=5, column=0, padx=10, pady=5)
    body_text.insert("1.0", email.plain)
    body_text.config(state="disabled")

    pass
