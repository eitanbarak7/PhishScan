from email_operations import *
import json
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

def define_sender_email_score(email):

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
    print (response)
   # sender_score =

    #email_score = response.choices[0].message.content
    #return response_message

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
    print("First Email? ", check_if_sender_first_email(email))
    print("From WhiteList? ", check_if_in_white_list(email))
    print("From Blacklist? ", check_if_in_black_list(email))
    print("Respomse from AI:" , define_sender_email_score(email))



def start_finding(email):
    print("SENDER ", email.sender)
    check_sender(email)