import os
from simplegmail import Gmail
import tkinter as tk
from tkinter import messagebox

def fetch_emails():
    # Create Gmail object
    gmail = Gmail()
    # Fetch unread messages
    return gmail.get_unread_inbox()

def show_email(email_listbox, emails, text_area, download_button):
    # Get the index of the selected email in the listbox
    index = email_listbox.curselection()[0]
    # Clear the text area
    text_area.config(state=tk.NORMAL)
    text_area.delete('1.0', tk.END)
    # Display the selected email in the text area
    email = emails[index]
    text_area.insert(tk.END, f"\n", "header")  # Empty line for spacing
    text_area.insert(tk.END, f"From: {email.sender}\n", "sender")
    text_area.insert(tk.END, f"Subject: {email.subject}\n", "subject")
    text_area.insert(tk.END, f"Date: {email.date}\n", "date")
    text_area.insert(tk.END, f"Preview: {email.snippet}\n\n", "preview")
    text_area.insert(tk.END, f"Message Body: {email.plain}\n\n", "body")
    text_area.config(state=tk.DISABLED)
    # Check if the email has attachments
    if email.attachments:
        download_button.config(state=tk.NORMAL)
    else:
        download_button.config(state=tk.DISABLED)

def download_attachments(email_listbox, emails):
    # Get the index of the selected email in the listbox
    index = email_listbox.curselection()[0]
    # Get the selected email
    email = emails[index]
    # Directory to save attachments
    save_dir = r"C:\Users\Eitan\PycharmProjects\email\files_from_emails"
    # Download attachments
    try:
        for attachment in email.attachments:
            filename = os.path.join(save_dir, attachment.filename)
            attachment.save(filename, overwrite=True)
        messagebox.showinfo("Download Complete", "Attachments downloaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download attachments: {e}")


def how_many_times_sender(sender):

    emails = fetch_emails()  # Assuming fetch_emails() fetches all emails
    sender_count = 0
    for email in emails:
        if email.sender == sender:
            sender_count += 1
    return sender_count

def check_whitelist(sender_email):
    whitelist_file = r"C:\Users\Eitan\PycharmProjects\email\code\whitelist_file.txt"
    with open(whitelist_file, 'r') as file:
        whitelist_emails = file.read().splitlines()

    # Check if the sender email is in the whitelist
    if sender_email in whitelist_emails:
        return True
    else:
        return False

def check_blacklist(sender_email):
    blacklist_file = r"C:\Users\Eitan\PycharmProjects\email\code\blacklist_file.txt"
    # Read the blacklist file and extract email addresses
    with open(blacklist_file, 'r') as file:
        blacklist_file = file.read().splitlines()

    # Check if the sender email is in the blacklist
    if sender_email in blacklist_file:
        return True
    else:
        return False


def extract_email_from_sender(sender):
    # Find the index of "<" and ">" to extract the email address
    email_start_index = sender.find("<") + 1
    email_end_index = sender.find(">", email_start_index)

    # Extract the email substring
    email = sender[email_start_index:email_end_index]
    return email
