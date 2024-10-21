import requests
import uuid
import os
import jwt
import time

from requests import Response
import qrcode
from dotenv import load_dotenv
from .settings import get_settings

bot_settings = get_settings()

load_dotenv()


class JWTManager:
    def __init__(self):
        self.token_url = bot_settings.ACCESS_TOKEN_URL
        self.refresh_url = bot_settings.REFRESH_TOKEN_URL
        self.username = "kreativpark_bot"
        self.password = os.getenv("PASSWORD")
        self.access_token = None
        self.refresh_token = None

        # Obtain tokens when the class is instantiated
        self.obtain_tokens()

    def obtain_tokens(self):
        """
        Obtain the access and refresh tokens by making an authentication request.
        """
        response = requests.post(
            url=self.token_url,
            json={"username": self.username, "password": self.password},
        )

        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens["access"]
            self.refresh_token = tokens["refresh"]
            print("Tokens obtained successfully.")
        else:
            raise Exception("Failed to obtain tokens.")

    def refresh_access_token(self):
        """
        Refresh the access token using the refresh token.
        """
        response = requests.post(self.refresh_url, json={"refresh": self.refresh_token})

        if response.status_code == 200:
            self.access_token = response.json()["access"]
            print("Access token refreshed successfully.")
        elif response.status_code == 401:
            print("Refresh token expired, obtaining new tokens...")
            self.obtain_tokens()
        else:
            raise Exception("Failed to refresh access token.")

    def is_token_expired(self):
        """
        Check if the access token is expired by decoding the 'exp' field.
        """
        try:
            decoded_token = jwt.decode(
                self.access_token, options={"verify_signature": False}
            )
            exp_timestamp = decoded_token.get("exp")

            if exp_timestamp:
                current_timestamp = time.time()
                if exp_timestamp < current_timestamp:
                    return True
            return False
        except jwt.DecodeError:
            return True

    def make_request(self, url, method="GET", data=None):
        """
        Make a request using the access token. Check if token is expired before the request.
        """
        if self.is_token_expired():
            print("Access token expired, refreshing token...")
            self.refresh_access_token()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }

        response = None
        if method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "GET":
            response = requests.get(url, headers=headers, params=data)

        return response


jwt_manager = JWTManager()


def get_req(url, data=None) -> Response:
    return jwt_manager.make_request(url, "GET", data)


def post_req(url, obj) -> Response:
    return jwt_manager.make_request(url, "POST", obj)


def make_qrcode() -> str:
    ID = uuid.uuid4()
    qr = qrcode.make(str(ID))
    qr.save(bot_settings.QRCODES_PATH + str(ID) + ".png")
    return str(ID)


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    else:
        return False
