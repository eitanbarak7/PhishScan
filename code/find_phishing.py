import socket

from email_operations import *
import json
from openai import OpenAI
import tkinter as tk
from tkinter import ttk

# Initialize OpenAI client
client = OpenAI()


def define_sender_email_score_with_ai(email):
    content_for_request = email.sender
    # Make a request to OpenAI's chat model
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": """

You will be my helper, I will send you: an email address + name of the sender who sent me an email.
In this format: (example@example.com <ExampleName>)

You will try to answer for me on a score scale of 1-10 how likely this email is trusted or maybe suspicious of a phishing attack.

REPLY IN THIS FORMAT, ONLY:
FINAL SCORE: #
COMMENT: #

Answer with the score you finally got to by the calculations (1 will be trusted, 10 will be very suspicious).

BEFORE YOU ANSWER:

Determine if the email is from a private person or a company.
Check if the domain is known and authentic.
Assess if the sender email and sender name are similar.
Look for any typos or mistakes in the address or name, especially if it's from a company.
If it's from a large company - check that the domain is authentic and connected with the company itself

IMPORTANT: Please provide only the score from 1 to 10 for the likelihood of trustworthiness or suspicion of the email after the calculations.

    """
            },
            {
                "role": "user",
                "content": content_for_request
            }
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    # sender_score =

    email_score = response.choices[0].message.content

    # Split the email_score string into lines
    lines = email_score.split('\n')

    # Initialize an empty dictionary to store the result
    result = {}

    # Iterate over each line to extract the score and comment
    for line in lines:
        if line.startswith("FINAL SCORE:"):
            # Extract the score by splitting the line and converting the score to an integer
            score = int(line.split(":")[1].strip())
            result["Score"] = score
        elif line.startswith("COMMENT:"):
            # Extract the comment by removing the "COMMENT:" prefix
            comment = line.replace("COMMENT:", "").strip()
            result["Comment"] = comment

    # Print the resulting dictionary
    return result


def check_if_sender_first_email(email):
    sender = email.sender

    if how_many_times_sender(sender) <= 1:
        return True
    else:
        return False


def check_if_in_white_list(email):
    sender = extract_email_from_sender(email.sender)

    if check_whitelist(sender):
        return True
    if not check_whitelist(sender):
        return False


def check_if_in_black_list(email):
    sender = extract_email_from_sender(email.sender)

    if check_blacklist(sender):
        return True
    if not check_blacklist(sender):
        return False


def check_sender(email):

    sender_status = {}
    if check_if_sender_first_email(email):
        sender_status["First_time_sender"] = True
    else:
        sender_status["First_time_sender"] = False

    if check_if_in_white_list(email):
        sender_status["Score"] = 1
        sender_status["Comment"] = "The email is likely trusted because the user added this email to it's white-list"
        return sender_status
    if check_if_in_black_list(email):
        sender_status["Score"] = 10
        sender_status[
            "Comment"] = "The email is very likely untrusted because the user added this email to it's black-list. This is the worst sender's score."
        return sender_status
    else:
        result = define_sender_email_score_with_ai(email)
        sender_status["Score"] = result["Score"]
        sender_status["Comment"] = "Based on AI's calculations: ", result["Comment"]
        return sender_status


def check_email_text(email, sender_status):
    sender_status_code = sender_status["Score"]

    insert_to_prompt = str(
        "Based on other checks, the sender (based on name and email address), received a score of " + str(
            sender_status_code) + ". (1-10 score, 1 is very trusted and safe, 10 is very suspicious and not safe. In addition, the comment that was added to summarize how this score was set is this: " + str(
            sender_status[
                "Comment"]) + " . Make sure to pay attention to that information and look at the email content based on this info too...")

    content_for_request = {"Sender Email and Name": email.sender,
                           "Sender Status from previous calculations": insert_to_prompt, "Email Subject": email.subject,
                           "Email plain text": email.plain}

    # Make a request to OpenAI's chat model
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": """

You are my AI agent who will help me to define if the email I received is safe based on its subject, plain text, and sender's trustworthiness.
Your goal is to decide if the email is a phishing (or other attacks) email, or a trusted email.

I will provide you that data, and you will reply to me with this layout of reply:
Phishing Detected Score: # (1-10 score: score of 1 is very safe, score of 10 is very untrusted and might be dangerous or suspicious!)
Safe: ### (write a text: explain here the safe things you found on the email)
Danger: ### (write a text: explain here the dangerous or suspicious things you found on the email)
Comment: #### (Here, add a comment explaining why you chose this specific score, explain your logic, and give me quotes from the texts to base your decision. give explanations. summarize the whole thing

Levels you MUST CHECK: check the email content properly:
1. Check the score for the email's sender that you've been given. check the rest of the email based on this, but don't put all of your trust in it, just get help with it. sometimes it's not that accurate, take that in charge. If the sender appears on white-list or black-list, make sure to pay attention!
2. Check the email subject. is it suspicious? does it contain promises or "clickbait"?
3. If there are URLs in the email, do they look safe? Are the domains authentic and trusted? - Fake URLs are highly suspicious!
4. Check the email content itself - based on your AI's training and the way you know to recognize cyber and phishing attacks, do you find the email text safe or not?
5. Any other methods if needed
6. If you think the email is safe, don't hesitate to give a score of 1-2...
7. Be informal. don't add tips regarding how to open and react to the email, just give me the score and comment. no need for user behavior tips! Don't tell me things like "take caution" or "pay attention"!
8. At last, make sure you chose the CORRECT score, if it's trusted it should be low, if its suspicious it should be a high scored. DO NOT MAKE MISTAKES WITH THAT.
9. If the sender identifies itself at some point on the email's plain text (usually at the end of it) - check that the sender's name and email matches this identity.
10. If the email is trying to show itself as an email from a known company, is the email address that sent the email - matches it? if not - it will be very suspicious because it might be disguise.

By using these steps (levels), you will be able to do it well. Make sure you checked ALL LEVELS.
Make sure to reply to me with the template I asked for.

REPLY IN ENGLISH ONLY. In a DICT json format!
   """
            },
            {
                "role": "user",
                "content": str(content_for_request)
            }
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    email_score = response.choices[0].message.content

    return email_score


def start_finding(done_queue, email):
    host = 'localhost'
    port = 5678

    print("Sender's details: ", email.sender)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    email_from_to_socket = email.sender
    client_socket.send(email_from_to_socket.encode('utf-8'))

    sender_status = check_sender(email)
    print(sender_status)

    sender_status_to_socket_ = str(sender_status["Score"])
    client_socket.send(sender_status_to_socket_.encode('utf-8'))

    email_status_str = check_email_text(email, sender_status)
    email_status = json.loads(email_status_str)
    print(email_status)

    email_status_to_socket_ = str(email_status["Phishing Detected Score"])
    client_socket.send(email_status_to_socket_.encode('utf-8'))

    done_queue.put("done")

    show_sender_screen(email, sender_status, email_status)


def show_sender_screen(email, sender_status, email_status):
    root = tk.Tk()
    root.title("Email Details and Status")
    root.geometry("1200x700")  # Set initial size of the window

    # Create a Canvas widget to hold the content
    canvas = tk.Canvas(root)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add a scrollbar to the canvas
    scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to hold the content
    main_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=main_frame, anchor="nw")

    # Bind the canvas to scroll with the mouse wheel
    def on_mousewheel(event):
        canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # Frame for sender/email status
    status_frame = tk.Frame(main_frame, padx=10, pady=10)
    status_frame.grid(row=0, column=0, sticky="nsew")

    # Determine sender score color and comment
    sender_score = sender_status["Score"]
    if sender_score <= 3:
        sender_color = "green"
        sender_comment = "Safe"
    elif sender_score <= 6:
        sender_color = "orange"
        sender_comment = "Probably Safe"
    else:
        sender_color = "red"
        sender_comment = "Unsafe"

    # Sender status
    sender_label = tk.Label(status_frame, text="Sender Status:", font=("Arial", 14, "bold"))
    sender_label.grid(row=0, column=0, sticky="w")

    sender_score_label = tk.Label(status_frame, text=f"Score: {sender_score} ({sender_comment})",
                                  font=("Arial", 12, "bold"), fg=sender_color)
    sender_score_label.grid(row=1, column=0, sticky="w")

    sender_comment_label = tk.Label(status_frame, text=sender_status["Comment"], font=("Arial", 12), wraplength=300,
                                    justify="left")
    sender_comment_label.grid(row=2, column=0, sticky="w")

    # Determine email score color and comment
    email_score = int(email_status["Phishing Detected Score"])
    if email_score <= 3:
        email_color = "green"
        email_comment = "Safe"
    elif email_score <= 6:
        email_color = "orange"
        email_comment = "Probably Safe"
    else:
        email_color = "red"
        email_comment = "Unsafe"

    # Email status
    email_label = tk.Label(status_frame, text="Email Status:", font=("Arial", 14, "bold"))
    email_label.grid(row=3, column=0, sticky="w")

    email_score_label = tk.Label(status_frame, text=f"Score: {email_score} ({email_comment})",
                                 font=("Arial", 20, "bold"), fg=email_color)
    email_score_label.grid(row=4, column=0, sticky="w")

    email_safe_label = tk.Label(status_frame, text=email_status["Safe"], font=("Arial", 10), wraplength=300,
                                justify="left")
    email_safe_label.grid(row=5, column=0, sticky="w")

    email_danger_label = tk.Label(status_frame, text=email_status["Danger"], font=("Arial", 12, "bold"), fg="red",
                                  wraplength=300, justify="left")
    email_danger_label.grid(row=6, column=0, sticky="w")

    email_final_label = tk.Label(status_frame, text=email_status["Comment"], font=("Arial", 10), wraplength=300,
                                 justify="left")
    email_final_label.grid(row=7, column=0, sticky="w")

    details_frame = tk.Frame(main_frame, padx=10, pady=10)
    details_frame.grid(row=0, column=1, sticky="nsew")

    # Email subject
    subject_label = tk.Label(details_frame, text="Subject:", font=("Arial", 14, "bold"))
    subject_label.grid(row=0, column=0, sticky="w")

    subject_text = tk.Label(details_frame, text=email.subject, font=("Arial", 12, "bold"), wraplength=400,
                            justify="left")
    subject_text.grid(row=0, column=1, sticky="w")

    # Email plain text
    plain_label = tk.Label(details_frame, text="Email Content:", font=("Arial", 14, "bold"))
    plain_label.grid(row=1, column=0, sticky="w")

    plain_text = tk.Label(details_frame, text=email.plain, font=("Arial", 10), wraplength=400, justify="left")
    plain_text.grid(row=2, column=0, columnspan=2, sticky="w")

    # Change background color of the column with scores to very light gray
    for label in status_frame.winfo_children():
        if label.grid_info()["column"] == 0:  # Assuming score labels are in the first column
            label.config(bg="#ffffff")  # Use a very light gray color

    # Update the canvas scroll region when the size of the main_frame changes
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    main_frame.bind("<Configure>", on_frame_configure)

    root.mainloop()
