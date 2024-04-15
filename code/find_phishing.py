from email_operations import *


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


def start_finding(email):
    print("SENDER ", email.sender)
    check_sender(email)