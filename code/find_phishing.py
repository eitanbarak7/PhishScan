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
    # print("First Email? ", check_if_sender_first_email(email))
    # print("From WhiteList? ", check_if_in_white_list(email))
    # print("From Blacklist? ", check_if_in_black_list(email))
    # print("Respomse from AI:" , define_sender_email_score(email))

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
        sender_status["Comment"] = "The email is very likely untrusted because the user added this email to it's black-list. This is the worst sender's score."
        return sender_status
    else:
        result = define_sender_email_score_with_ai(email)
        sender_status["Score"] = result["Score"]
        sender_status["Comment"] = "Based on AI's calculations: ", result["Comment"]
        return sender_status

def check_email_text(email, sender_status):

    sender_status_code = sender_status["Score"]

    insert_to_prompt = str("Based on other checks, the sender (based on name and email address), received a score of " + str(sender_status_code) + ". (1-10 score, 1 is very trusted and safe, 10 is very suspicious and not safe. In addition, the comment that was added to summarize how this score was set is this: " + str(sender_status["Comment"]) + " . Make sure to pay attention to that information and look at the email content based on this info too...")

    content_for_request = {}
    content_for_request["Sender Email and Name"] = email.sender
    content_for_request["Sender Status from previous calculations"] = insert_to_prompt
    content_for_request["Email Subject"] = email.subject
    content_for_request["Email plain text"] = email.plain


    # Make a request to OpenAI's chat model
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": """

You are my AI agent who will help me to define if the email I received is safe based on its subject, plain text, and sender's trustworthiness.
Your goal is to decide if the email is a phishing (or other attacks) email, or a trusted email.

I will provide you that data, and you will reply to me with this layout of reply:
Phishing Detected Score: # (1-10 score: score of 1 is very safe, score of 10 is very untrusted and might be dangerous or suspicious!)
Safe: ### (explain here the safe things you found on the email)
Danger: ### (explain here the dangerous or suspicious things you found on the email)
Comment: #### (Here, add a comment explaining why you chose this specific score, explain your logic, and give me quotes from the texts to base your decision. give explanations. summarize the whole thing

Tips for you to check the email content properly:
1. Check the score for the email's sender that you've been given. check the rest of the email based on this, but don't put all of your trust in it, just get help with it. sometimes it's not that accurate, take that in charge. If the sender appears on white-list or black-list, make sure to pay attention!
2. Check the email subject. is it suspicious? does it contain promises or "clickbait"?
3. If there are URLs in the email, do they look safe? Are the domains authentic and trusted? - Fake URLs are highly suspicious!
4. Check the email content itself - based on your AI's training and the way you know to recognize cyber and phishing attacks, do you find the email text safe or not?
5. Any other methods if needed
6. If you think the email is safe, don't hesitate to give a score of 1-2...
7. Be informal. don't add tips regarding how to open and react to the email, just give me the score and comment. no need for user behavior tips! Don't tell me things like "take caution" or "pay attention"!
8. At last, make sure you chose the CORRECT score, if it's trusted it should be low, if its suspicious it should be a high scored. DO NOT MAKE MISTAKES WITH THAT.

By using these steps, you will be able to do it well.
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




def start_finding(email):
    print("Sender's details: ", email.sender)
    sender_status = check_sender(email)
    print(sender_status)
    print(check_email_text(email, sender_status))
    #print(check_email_attachments(email))
