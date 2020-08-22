from ring_doorbell import Ring, Auth # main Ring API (Unofficial)
from oauthlib.oauth2 import MissingTokenError # used for authentication 
from decouple import config # allows for the reading of user and password stored in the .env file
from time import sleep # used to check for 6-hour checks 

import logging
import smtplib # API used for sending emails

# debugging logger
def initialize_logger(): 
    logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M %p')
    logging.getLogger().setLevel(logging.INFO)

# asks for the Two-Factor Authentication Code
def otp_callback():
    auth_code = input("Two-Factor Authentication Code: ")
    return auth_code

def send_email(percent):
    # initialize sender credentials and receiver email
    sndr_user = config('gmail_user')
    sndr_pw = config('gmail_pw')
    rcv_eml = config('gmail_receiver')
    
    # creates SMTP session 
    conn = smtplib.SMTP('smtp.gmail.com', 587) 
    
    # start TLS for security 
    conn.starttls() 
    
    # login using the credentials
    conn.login(sndr_user, sndr_pw) 
    
    # email body
    txt = f'\nThe Front Door Ring Battery is at {percent}%. Charge it!'
    subj = "Ring Alert!"
    message = "From: %s\r\n" % sndr_user + "To: %s\r\n" % rcv_eml + "Subject: %s\r\n" % subj + "\r\n" + txt    
    
    # send mail and quit the connection
    conn.sendmail(sndr_user, rcv_eml, message) 
    conn.quit() 

def main(): 
    # initialize logger for debugging
    initialize_logger()

    # initialize ring account username and password
    username = config('user')
    password = config('pw')

    # use the Authenticator of the ring_doorbell API 
    # tries to fetch token for authentication 
    # requests user input for the code if necessary
    auth = Auth("MyProject/1.0", None, None)
    try:
        auth.fetch_token(username, password)
    except MissingTokenError:
        auth.fetch_token(username, password, otp_callback())

    ring = Ring(auth)
    ring.update_data()

    # filter the Ring Devices
    devices = ring.devices()
    front_door = devices['authorized_doorbots']

    threshold = input("Enter the percentage where-in you want to get reminders: ")
    # loop for checking battery life
    while True:
        battery_life = front_door[0].battery_life
        logging.info(f'The current battery life is {battery_life}')
        # if battery is less than threshold, send the e-mail
        if(battery_life <= int(threshold)):
            logging.info("Sending the email")
            send_email(battery_life)

        # loop sleeps for 6 hours 21600
        sleep(21600)

if __name__ == "__main__":
    main()