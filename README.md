# PhishScan - Email Phishing Detection System

PhishScan is an advanced system for detecting phishing attempts in email messages using AI-based analysis. This README provides instructions for setting up and using the PhishScan system.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Server-side Database Management](#server-side-database-management)

## System Requirements

To run PhishScan, ensure that your system meets the following requirements:

- Python 3.12 or higher
- Windows operating system
- Internet connection

## Installation

1. Clone the PhishScan repository from GitHub:

    git clone https://github.com/eitanbarak7/PhishScan.git

2. Navigate to the project directory: 

    cd PhishScan

3. Install the required packages listed in the `requirements.txt` file:

    pip install -r requirements.txt


## Configuration

Before running PhishScan, you need to configure the following:

1. OpenAI API Key:
- Sign in to your account on the OpenAI website
- Obtain an API key (or use an existing one if you have it)
- Save the secret API key securely
- Set the API key as a local environment variable in the `main.py` file or through your IDE
- Ensure that the variable is stored as an environment variable and not uploaded to GitHub or other public locations to maintain security and privacy

2. Gmail API Credentials:
- Create a new Gmail account if you don't have one
- Set up a project in the Google Cloud Console
- Enable the Gmail API for your project
- Create OAuth 2.0 credentials and download the `client_secret.json` file
- The `gmail_token.json` file will be automatically created when using the `simplegmail` library for the first time (complete the authorization process during the first run)
- Place the `client_secret.json` and `gmail_token.json` files in the root directory of the project, alongside files like `main.py`

## Usage

To start using PhishScan, follow these steps:

1. Run the server:
    
    python code/server.py

2. Run the client:
    
    python code/main.py


3. Wait for the loading screen to finish and the email inbox to be displayed

4. Select an email from the inbox

5. Click the "DETECT PHISHING" button to start the phishing detection process for the selected email

6. Wait for the analysis to complete

7. View the risk scores for the email address and email content in the displayed window

Additionally, you can manage the blacklist and whitelist of email addresses from the email inbox interface. You can also download attachments from emails, which will be saved in the local `files_from_emails` directory.

## Server-side Database Management

For system administrators running the server, the database table can be managed as follows:

- Browse the database table
- Sort the table by numerical order or ABC order
- Search for an email address using free text

These features are useful for managing a large number of email addresses and organizing the data. Note that these operations are only relevant for system administrators running the server, not for end-users (clients).


