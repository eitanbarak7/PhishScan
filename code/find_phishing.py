from email_operations import *
import json
from openai import OpenAI

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
    #print("First Email? ", check_if_sender_first_email(email))
    #print("From WhiteList? ", check_if_in_white_list(email))
    #print("From Blacklist? ", check_if_in_black_list(email))
    #print("Respomse from AI:" , define_sender_email_score(email))

    sender_status = {}
    if check_if_sender_first_email(email):
        sender_status["Activity"] = "New Sender"
    else:
        sender_status["Activity"] = "Not a first time Sender, sent: " + str(how_many_times_sender(email.sender)) + " emails"

    if check_if_in_white_list(email):
        sender_status["Score"] = 1
        sender_status["Comment"] = "The sender email is appearing on the user's White List"
        return sender_status
    if check_if_in_black_list(email):
        sender_status["Score"] = 10
        sender_status["Comment"] = "The sender email is appearing on the user's Black List"
        return sender_status
    else:
        result = define_sender_email_score_with_ai(email)
        sender_status["Score"] = result["Score"]
        sender_status["Comment"] = "Based on AI's calculations: ", result["Comment"]
        return sender_status




def start_finding(email):
    print("SENDER ", email.sender)
    print(check_sender(email))
