import tkinter as tk
from tkinter import scrolledtext
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
    email_listbox.bind("<ButtonRelease-1>", lambda event: show_email_func(email_listbox, emails, text_area, download_button))
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
    download_button = tk.Button(email_frame, text="Download Attachments", command=lambda: download_attachments_func(email_listbox, emails), state=tk.DISABLED)
    download_button.pack(pady=5)
