import socket

import cryptography

from email_operations import *
import json
from openai import OpenAI
import tkinter as tk
from tkinter import ttk
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Generate client's key pair
client_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
client_public_key = client_private_key.public_key()

# Initialize OpenAI client
clientOpenAI = OpenAI()


def define_sender_email_score_with_ai(email, response_text):
    content_for_request = email.sender + "\n" + response_text
    # Make a request to OpenAI's chat model
    response = clientOpenAI.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": """

You will be my helper, I will send you: an email address + name of the sender who sent me an email.
In this format: (example@example.com <ExampleName>)

I will also give you the sender average received score (checked by my server in recent checks) (1 is safe, 10 is very dangerous), use the average in order to improve your checks, but not as as a decision maker, if however you used it's result, mention it in the comment later.

You will try to answer for me on a score scale of 1-10 how likely this email is trusted or maybe suspicious of a phishing attack.

Answer with the score you finally got to by the calculations (1 will be trusted, 10 will be very suspicious).

BEFORE YOU ANSWER:

Determine if the email is from a private person or a company.
Check if the domain is known and authentic.
Assess if the sender email and sender name are similar.
Look for any typos or mistakes in the address or name, especially if it's from a company.
If it's from a large company - check that the domain is authentic and connected with the company itself

IMPORTANT: Please provide only the score from 1 to 10 for the likelihood of trustworthiness or suspicion of the email after the calculations.
Please respond in the following JSON format only:
{
    "Score": <integer from 1 to 10>,
    "Comment": "<your explanation>"
}
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

    try:
        result = response.choices[0].message.content.strip()
        result = json.loads(result)
        return result
    except (ValueError, json.JSONDecodeError):
        return {"Score": 5, "Comment": "Unable to parse the AI response."}


def check_if_sender_first_email(email):
    # Checks if it's the sender's first email
    sender = email.sender
    if how_many_times_sender(sender) <= 1:
        return True
    else:
        return False
    return False


def check_if_in_white_list(email):
    # Checks if the sender is in the whitelist file
    sender = extract_email_from_sender(email.sender)

    if check_whitelist(sender):
        return True
    if not check_whitelist(sender):
        return False


def check_if_in_black_list(email):
    # Checks if the sender is in the blacklist file
    sender = extract_email_from_sender(email.sender)

    if check_blacklist(sender):
        return True
    if not check_blacklist(sender):
        return False


def check_sender(email, response):
    # Dictionary to store sender status
    sender_status = {}

    try:
        # Check if email is in the whitelist
        if check_if_in_white_list(email):
            sender_status["Score"] = 1
            sender_status["Comment"] = "The email is likely trusted because the user added this email to its white-list"
            return sender_status
    except Exception as e:
        print(f"Error checking white list: {str(e)}")

    try:
        # Check if email is in the blacklist
        if check_if_in_black_list(email):
            sender_status["Score"] = 10
            sender_status[
                "Comment"] = "The email is very likely untrusted because the user added this email to its black-list. This is the worst sender's score."
            return sender_status
    except Exception as e:
        print(f"Error checking black list: {str(e)}")

    try:
        # Define sender email score with AI
        result = define_sender_email_score_with_ai(email, response)
        sender_status["Score"] = result['Score']
        sender_status["Comment"] = "Based on AI's calculations: " + result['Comment']
    except (KeyError, TypeError) as e:
        print(f"Error accessing result dictionary: {str(e)}")

    # Return sender status
    return sender_status


def check_email_text(email, sender_status, response):
    # Extract sender status code from the sender_status dictionary
    sender_status_code = sender_status["Score"]

    # Create a prompt message to include sender status information
    insert_to_prompt = str(
        "Based on other checks, the sender (based on name and email address), received a score of " + str(
            sender_status_code) + ". (1-10 score, 1 is very trusted and safe, 10 is very suspicious and not safe. In addition, the comment that was added to summarize how this score was set is this: " + str(
            sender_status[
                "Comment"]) + " . Make sure to pay attention to that information and look at the email content based on this info too...")

    # Prepare content for the request, including sender information, email subject, plain text, and response score
    content_for_request = {
        "Sender Email and Name": email.sender,
        "Sender Status from previous calculations": insert_to_prompt,
        "Email Subject": email.subject,
        "Email plain text": email.plain,
        "Email Address average score": response
    }

    # Make a request to OpenAI's chat model
    response = clientOpenAI.chat.completions.create(
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

THE MOST DANGEROUS RISKS ARE: FAKE URLs, URGENCY, PRIVATE DETAILS SHARING REQUEST, AND ALL PHISHING AND SPAM EMAILS SIGNS.
CHECK EVEN THE TRUSTED URLs, are they authentic? SOMETIMES THEY CHANGE o to 0 or other similar things.... DOUBLE CHECK IT!!!
Levels you MUST CHECK: check the email content properly:
1. Check the score for the email's sender that you've been given. check the rest of the email based on this, but don't put all of your trust in it, just get help with it. sometimes it's not that accurate, take that in charge. If the sender appears on white-list or black-list, make sure to pay attention!
2. Check the email subject. is it suspicious? does it contain promises or "clickbait"?
3. If there are URLs in the email, do they look safe? Are the domains authentic and trusted? - Fake URLs are highly suspicious! check if they are the original URL's of the brand or company, if not - it's very bad.
4. Check the email content itself - based on your AI's training and the way you know to recognize cyber and phishing attacks, do you find the email text safe or not?
5. Any other methods if needed
6. If you think the email is safe, don't hesitate to give a score of 1-2...
7. Be informal. don't add tips regarding how to open and react to the email, just give me the score and comment. no need for user behavior tips! Don't tell me things like "take caution" or "pay attention"!
8. At last, make sure you chose the CORRECT score, if it's trusted it should be low, if its suspicious it should be a high scored. DO NOT MAKE MISTAKES WITH THAT.
9. If the sender identifies itself at some point on the email's plain text (usually at the end of it) - check that the sender's name and email matches this identity.
10. If the email is trying to show itself as an email from a known company, is the email address that sent the email - matches it? if not - it will be very suspicious because it might be disguise.
11. Look at the average email's sender score and average email's score that you received before, they shouldn't decide it all, but pay attention, they might show trust or show dangerous patterns. mention it in the comments later if you used it. (it's the average till now from other previous email checks)
12. CHECK EVEN THE TRUSTED URLs, are they authentic? SOMETIMES THEY CHANGE o to 0 or other similar things.... DOUBLE CHECK IT!!!
13. EXAMPLES: Double check imposters: Is Google: Google or Go0gle? (zero instead of o), is Apple: Apple or App1e? (1 instead of l)
14. Double check the letters that can be spoofed: o-0, l-1, L-1, e-3, S-5, G-9, z-2, etc.!!!
15 Email that contains spoofed links - will be highly suspicious.

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

    # Extract the email score from the response object
    email_score = response.choices[0].message.content

    # Return the email score
    return email_score


def start_finding(done_queue, email):
    max_retries = 2
    retry_count = 0

    while retry_count <= max_retries:
        try:
            # Server details
            host = '10.0.0.8'  # Server's IP
            port = 5678

            # Print sender's details
            print("Sender's details: ", email.sender)

            # Create client socket
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except socket.error as e:
                print(f"Error creating socket: {str(e)}")
                retry_count += 1
                continue

            # Connect to the server
            try:
                client_socket.connect((host, port))
            except socket.error as e:
                print(f"Error connecting to the server: {str(e)}")
                retry_count += 1
                continue

            print("Connected to the server.")

            # Send client's public key to the server
            try:
                client_public_key_pem = client_public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode()
            except ValueError as e:
                print(f"Error encoding public key: {str(e)}")
                retry_count += 1
                continue

            try:
                client_socket.send(client_public_key_pem.encode())
            except socket.error as e:
                print(f"Error sending public key to the server: {str(e)}")
                retry_count += 1
                continue

            print("Sent client's public key to the server.")

            # Receive server's public key
            try:
                server_public_key_pem = client_socket.recv(1024).decode()
            except socket.error as e:
                print(f"Error receiving server's public key: {str(e)}")
                retry_count += 1
                continue

            try:
                server_public_key = serialization.load_pem_public_key(
                    server_public_key_pem.encode(),
                    backend=default_backend()
                )
            except ValueError as e:
                print(f"Error loading server's public key: {str(e)}")
                retry_count += 1
                continue

            print("Received server's public key.")

            # Receive the encryption key from the server
            try:
                key = client_socket.recv(100000)
            except socket.error as e:
                print(f"Error receiving encryption key from the server: {str(e)}")
                retry_count += 1
                continue

            try:
                cipher_suite = Fernet(key)
            except ValueError as e:
                print(f"Error creating cipher suite: {str(e)}")
                retry_count += 1
                continue

            print("Received encryption key from the server.")

            # Encrypt email data and send it to the server
            email_from_to_socket = email.sender
            try:
                encrypted_email = cipher_suite.encrypt(email_from_to_socket.encode('utf-8'))
            except cryptography.fernet.InvalidToken as e:
                print(f"Error encrypting email data: {str(e)}")
                retry_count += 1
                continue

            print("Original email data:", email_from_to_socket)
            print("Encrypted email data:", encrypted_email)

            try:
                client_socket.send(encrypted_email)
            except socket.error as e:
                print(f"Error sending encrypted email data to the server: {str(e)}")
                retry_count += 1
                continue

            print("Sent encrypted email data to the server.")

            # Receive encrypted response from the server
            try:
                encrypted_response = client_socket.recv(100000)
            except socket.error as e:
                print(f"Error receiving encrypted response from the server: {str(e)}")
                retry_count += 1
                continue

            print("Encrypted response received:", encrypted_response)

            # Decrypt response from the server
            try:
                response = cipher_suite.decrypt(encrypted_response).decode('utf-8')
            except cryptography.fernet.InvalidToken as e:
                print(f"Error decrypting response: {str(e)}")
                retry_count += 1
                continue

            print("Decrypted response:", response)

            # Check sender status
            try:
                sender_status = check_sender(email, response)
            except ValueError as e:
                print(f"Error checking sender status (ValueError): {str(e)}")
                retry_count += 1
                continue
            except TypeError as e:
                print(f"Error checking sender status (TypeError): {str(e)}")
                retry_count += 1
                continue
            except Exception as e:
                print(f"Error checking sender status (other exception): {str(e)}")
                retry_count += 1
                continue

            print("Sender status:", sender_status)

            # Encrypt sender status and send it to the server
            sender_status_to_socket_ = str(sender_status["Score"])
            try:
                encrypted_sender_status = cipher_suite.encrypt(sender_status_to_socket_.encode('utf-8'))
            except cryptography.fernet.InvalidToken as e:
                print(f"Error encrypting sender status: {str(e)}")
                retry_count += 1
                continue

            print("Encrypted sender status:", encrypted_sender_status)

            try:
                client_socket.send(encrypted_sender_status)
            except socket.error as e:
                print(f"Error sending encrypted sender status to the server: {str(e)}")
                retry_count += 1
                continue

            print("Sent encrypted sender status to the server.")

            # Check email status
            email_status_str = check_email_text(email, sender_status, response)
            try:
                email_status = json.loads(email_status_str)
            except ValueError as e:
                print(f"Error parsing email status JSON: {str(e)}")
                retry_count += 1
                continue

            print("Email status:", email_status)

            # Encrypt email status and send it to the server
            email_status_to_socket_ = str(email_status["Phishing Detected Score"])
            try:
                encrypted_email_status = cipher_suite.encrypt(email_status_to_socket_.encode('utf-8'))
            except cryptography.fernet.InvalidToken as e:
                print(f"Error encrypting email status: {str(e)}")
                retry_count += 1
                continue

            print("Encrypted email status:", encrypted_email_status)

            try:
                client_socket.send(encrypted_email_status)
            except socket.error as e:
                print(f"Error sending encrypted email status to the server: {str(e)}")
                retry_count += 1
                continue

            print("Sent encrypted email status to the server.")

            # Put "done" in the done_queue
            done_queue.put("done")

            # Close client socket
            client_socket.close()

            # Show sender screen with email, sender status, email status, and response
            show_sender_screen(email, sender_status, email_status, response)

            break  # Exit the loop if the analysis is successful

        except Exception as e:
            # Handle any errors during email analysis
            print("Error during email analysis:", str(e))
            retry_count += 1

    if retry_count > max_retries:
        print("Max retries exceeded. Email analysis failed.")

        # Display a message box indicating the failure
        messagebox.showerror("Error", "Email analysis failed. Please try again.")

        # Put "done" in the done_queue to end the loading screen
        done_queue.put("done")


def show_sender_screen(email, sender_status, email_status, response):
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

    # Frame for response, sender, and email status
    response_frame = tk.Frame(main_frame, padx=10, pady=10)
    response_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

    if (response == "This email address hasn't received an email score or sender score till now. "
                    "It doesn't mean this isn't safe, this is just a parameter we can't use now. "
                    "So check it as usual with the care needed."):
        response = "This email address doesn't have average scores, since it's hasn't been checked till now."

    # Response label
    response_label = tk.Label(response_frame, text=response, font=("Arial", 10, "italic"), fg="blue", wraplength=700,
                              justify="left")
    response_label.grid(row=0, column=0, sticky="w")

    # Frame for sender/email status
    status_frame = tk.Frame(main_frame, padx=10, pady=10)
    status_frame.grid(row=1, column=0, sticky="nsew")

    # Determine sender score color and comment
    sender_score = sender_status["Score"]
    if sender_score <= 3:
        sender_color = "green"
        sender_comment = "Safe"
    elif sender_score <= 5:
        sender_color = "orange"
        sender_comment = "Probably Safe"
    elif sender_score <= 7:
        sender_color = "orange"
        sender_comment = "Pay Attention"
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
    details_frame.grid(row=1, column=1, sticky="nsew")

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
