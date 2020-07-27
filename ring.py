from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError
from decouple import config
from pprint import pprint

def otp_callback():
    auth_code = input("2FA code: ")
    return auth_code

def return_battery(ring_obj): 
    return ring_obj.battery_life

def main(): 
    username = config('user')
    password = config('pw')
    auth = Auth("MyProject/1.0", None, None)

    try:
        auth.fetch_token(username, password)
    except MissingTokenError:
        auth.fetch_token(username, password, otp_callback())

    ring = Ring(auth)
    ring.update_data()

    devices = ring.devices()
    pprint(devices)


if __name__ == "__main__":
    main()