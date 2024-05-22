import re
import tkinter as tk
from tkinter import simpledialog, messagebox


class EmailManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Edit your emails whitelist")

        # Set window size
        self.master.geometry("600x400")

        # Create the listbox to display emails
        self.email_listbox = tk.Listbox(master, width=50, height=10, font=("Helvetica", 12))
        self.email_listbox.pack(pady=10)

        # Populate listbox with emails from whitelist file
        self.load_emails()

        # Buttons
        self.add_button = tk.Button(master, text="Add Email", command=self.add_email,
                                    font=("Helvetica", 12), bg="green", fg="white")
        self.add_button.pack(side=tk.LEFT, padx=10)
        self.edit_button = tk.Button(master, text="Edit Email", command=self.edit_email,
                                     font=("Helvetica", 12), bg="blue", fg="white")
        self.edit_button.pack(side=tk.LEFT, padx=10)
        self.delete_button = tk.Button(master, text="Delete Email", command=self.delete_email,
                                       font=("Helvetica", 12), bg="red", fg="white")
        self.delete_button.pack(side=tk.LEFT, padx=10)

    def load_emails(self):
        try:
            with open(r"C:\Users\Eitan\PycharmProjects\email\code\whitelist_file.txt", "r") as file:
                emails = file.readlines()
                for email in emails:
                    self.email_listbox.insert(tk.END, email.strip())
        except FileNotFoundError:
            messagebox.showerror("Error", "Whitelist file not found.")

    def add_email(self):
        email = simpledialog.askstring("Add Email", "Enter the email address:")
        if email:
            if is_valid_email(email):
                if not is_email_blacklisted(email):
                    self.email_listbox.insert(tk.END, email)
                    self.save_emails()
                else:
                    messagebox.showerror("Error",
                                         "This email address is blacklisted. Please remove this email address from the blacklist in order to add it to the whitelist")
            else:
                messagebox.showerror("Error", "Invalid email address.")

    def edit_email(self):
        selection = self.email_listbox.curselection()
        if selection:
            index = selection[0]
            old_email = self.email_listbox.get(index)
            new_email = simpledialog.askstring("Edit Email", "Edit email address:", initialvalue=old_email)
            if new_email:
                if is_valid_email(new_email):
                    if not is_email_blacklisted(new_email):
                        self.email_listbox.delete(index)
                        self.email_listbox.insert(index, new_email)
                        self.save_emails()
                    else:
                        messagebox.showerror("Error", "This email address is blacklisted. Please remove this email address from the blacklist in order to add it to the whitelist")
                else:
                    messagebox.showerror("Error", "Invalid email address.")
        else:
            messagebox.showwarning("Warning", "Please select an email to edit.")

    def delete_email(self):
        selection = self.email_listbox.curselection()
        if selection:
            index = selection[0]
            self.email_listbox.delete(index)
            self.save_emails()
        else:
            messagebox.showwarning("Warning", "Please select an email to delete.")

    def save_emails(self):
        with open(r"C:\Users\Eitan\PycharmProjects\email\code\whitelist_file.txt", "w") as file:
            emails = self.email_listbox.get(0, tk.END)
            for email in emails:
                file.write(email + "\n")


def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


def is_email_blacklisted(email):
    try:
        with open(r"C:\Users\Eitan\PycharmProjects\email\code\blacklist_file.txt", "r") as file:
            blacklisted_emails = file.readlines()
            for blacklisted_email in blacklisted_emails:
                if blacklisted_email.strip().lower() == email.strip().lower():
                    return True
        return False
    except FileNotFoundError:
        messagebox.showerror("Error", "Blacklist file not found.")
        return False


def main():
    root = tk.Tk()
    root.mainloop()


if __name__ == "__main__":
    main()
