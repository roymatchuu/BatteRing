# BatteRing
BatteRing is Battery Health checker for your Ring Doorbell. BatteRing offers dynamic e-mail notifications and percentage threshold for when you want to be notfied about your Ring's battery life. 

## Installation 
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install following APIs used for BatteRing.

BatteRing aims to promote personal security by utilizing environment variables to store the credentials on the user's local machine. Install python-decouple in order to extract the credentials from a .env file.

```bash
pip install python-decouple
```

BatteRing utilizes the Unofficial Ring API [ring_doorbell](https://github.com/tchellomello/python-ring-doorbell). 

```bash
pip install ring_doorbell
```

## Usage 
Create a local .env file that would store your credentials with the local variable names
- user and pw for your credentials for www.ring.com
- gmail_user and gmail_pw for your credentials for www.gmail.com
- gmail_receiver for the gmail account that you want to be notified in 

Note: BatteRing currently does not support OAuth 2.0 authorization for gmail which means that in order for BatteRing to access the gmail account the user will be sending from, the "Enable third-party apps" option must be enabled. Enable this option at your own risk. 

Run BatteRing on your terminal by either specifying the path where ring.py is in or by navigating to the BatteRing directory 

```bash 
python ring.py
```

BatteRing will then ask for the two-factor authentication code from Ring.com that the user receives either through text or e-mail. Lastly, BatteRing asks the user for input for what percentage the user wants to be notified for. 

For more information about the Unofficial API used in the production of battering. Refer to the documentation: http://python-ring-doorbell.readthedocs.io/.