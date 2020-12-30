from ring_doorbell import Ring, Auth # main Ring API (Unofficial)
from oauthlib.oauth2 import MissingTokenError # used for authentication 
from decouple import config # allows for the reading of user and password stored in the .env file
from time import sleep # used to check for 6-hour checks 

import logging
import smtplib # API used for sending emails
from pathlib import Path 
import json 

import os.path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64

cache_file = Path("token.cache")
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

# debugging logger
def initialize_logger(): 
    logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M %p')
    logging.getLogger().setLevel(logging.INFO)

# asks for the Two-Factor Authentication Code
def otp_callback():
    auth_code = input("Two-Factor Authentication Code: ")
    return auth_code

# creates the message that is used to be sent for the email
def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

# resposible for sending the email notification
def send_email(percent):

    gmail_credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            gmail_credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not gmail_credentials or not gmail_credentials.valid:
        if gmail_credentials and gmail_credentials.expired and gmail_credentials.refresh_token:
            gmail_credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            gmail_credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(gmail_credentials, token)

    service = build('gmail', 'v1', credentials=gmail_credentials, cache_discovery=False)

    # initialize sender credentials and receiver email
    sndr_user = config('gmail_user')
    rcv_eml = config('gmail_receiver')
    
    # email body
    txt = f'\nThe Front Door Ring Battery is at {percent}%. Charge it!'
    subj = "Ring Alert!"  
    
    msg = create_message(sndr_user, rcv_eml, subj, txt)
    
    try:
        message = (service.users().messages().send(userId=sndr_user, body=msg)
                .execute())
        print('Message Id: %s' % message['id'])
        return message
    except HttpError:
        print(f'An error occurred: {HttpError}')


# updates the cache file with a refreshed token when necessary
def token_updated(token):
    cache_file.write_text(json.dumps(token))

def main(): 
    # initialize logger for debugging
    initialize_logger()

    if cache_file.is_file():
        auth = Auth("MyProject/1.0", json.loads(cache_file.read_text()), token_updated)
    else:
        # initialize ring account username and password
        username = config('user')
        password = config('pw')

        # use the Authenticator of the ring_doorbell API 
        # tries to fetch token for authentication 
        # requests user input for the code if necessary
        auth = Auth("MyProject/1.0", None, token_updated)
        try:
            auth.fetch_token(username, password)
        except MissingTokenError:
            auth.fetch_token(username, password, otp_callback())

    threshold = input("Enter the percentage where-in you want to get reminders: ")
    # loop for checking battery life
    while True:
        ring = Ring(auth)
        ring.update_data()
    
        # filter the Ring Devices
        devices = ring.devices()
        front_door = devices['authorized_doorbots']

        battery_life = front_door[0].battery_life
        logging.info(f'The current battery life is {battery_life}')
        # if battery is less than threshold, send the e-mail
        if(battery_life <= int(threshold)):
            logging.info("Sending the email")
            send_email(battery_life)

        # loop sleeps for 6 hours 21600
        sleep(3600)
    
    # test outside of the loop
    # ring = Ring(auth)
    # ring.update_data()

    # # filter the Ring Devices
    # devices = ring.devices()
    # front_door = devices['authorized_doorbots']

    # battery_life = front_door[0].battery_life
    # logging.info(f'The current battery life is {battery_life}')

    # send_email(battery_life)


if __name__ == "__main__":
    main()