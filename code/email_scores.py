import json
import os

EMAIL_SCORES_FILE = "email_scores.json"


def store_email_score(email_identifier, score):
    email_scores = load_email_scores()
    email_scores[email_identifier] = score
    save_email_scores(email_scores)


def get_email_score(email_identifier):
    email_scores = load_email_scores()
    return email_scores.get(email_identifier)


def load_email_scores():
    if os.path.exists(EMAIL_SCORES_FILE):
        with open(EMAIL_SCORES_FILE, "r") as file:
            return json.load(file)
    else:
        return {}


def save_email_scores(email_scores):
    with open(EMAIL_SCORES_FILE, "w") as file:
        json.dump(email_scores, file)


def sync_email_scores(emails):
    email_scores = load_email_scores()
    updated_scores = {}

    for email in emails:
        email_identifier = f"{email.subject}_{email.date}"
        if email_identifier in email_scores:
            updated_scores[email_identifier] = email_scores[email_identifier]

    save_email_scores(updated_scores)
