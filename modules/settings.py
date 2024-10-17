import requests
import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()


class Settings:
    """This module has any settings for kreativ park bot"""

    def __init__(self):
        # Settings for django apis (urls)

        # Base url
        self.BASE_URL = "https://api.otabek.me/"

        # Api endpoint
        self.API_ENDPOINT = "api/v2/"

        # Getting csrf_token from session
        self.CSRF_TOKEN_URL = self.BASE_URL + self.API_ENDPOINT + "get-csrf-token/"
        self.SESSION_ID = os.getenv("SESSION_ID")
        self.CSRF_TOKEN = requests.get(
            self.CSRF_TOKEN_URL, cookies={"sessionid": self.SESSION_ID}
        ).json()["csrf_token"]

        # Urls for people
        self.GET_PEOPLE_URL = self.BASE_URL + self.API_ENDPOINT + "people/?format=json"
        self.POST_PEOPLE_URL = self.BASE_URL + self.API_ENDPOINT + "people/add/"
        self.CHECK_PEOPLE_URL = self.BASE_URL + self.API_ENDPOINT + "people/check/"
        self.CHECK_PEOPLE_IDS = (
            self.BASE_URL + self.API_ENDPOINT + "people/IDs/?format=json"
        )
        self.CHECK_PEOPLE_HAS_QRCODE = (
            self.BASE_URL + self.API_ENDPOINT + "qrcode/people/check/"
        )

        # Urls for qrcode
        self.GET_QRCODES_URL = self.BASE_URL + self.API_ENDPOINT + "qrcode/?format=json"
        self.POST_QRCODE_URL = self.BASE_URL + self.API_ENDPOINT + "qrcode/add/"
        self.CHECK_QRCODE_URL = self.BASE_URL + self.API_ENDPOINT + "qrcode/check/"
        self.GET_QRCODES_DELETE_URL = (
            self.BASE_URL + self.API_ENDPOINT + "qrcode/delete/"
        )

        # This url to get qrcode and enter library
        self.LOGIN_LIBRARY = self.BASE_URL + self.API_ENDPOINT + "login-library/"
        self.GET_NUMBER_TOKEN = self.BASE_URL + self.API_ENDPOINT + "get-number-token/"

        # admins
        self.admins = {
            "Otabek": 5551503420,
            "Azizbek": 1251979840,
            "Iskandar": 228633803,
        }

        # admins urls
        self.STATS_URL = self.BASE_URL + self.API_ENDPOINT + "stats/"

        # Bot settings
        self.BOT_API_TOKEN = os.getenv("BOT_API_TOKEN")
        self.IBRAT_CHANNEL = "@kreativparkuz"
        self.QRCODES_PATH = "images/qr_codes/"

        # Commands
        self.COMMANDS = ("",)
        self.PURPOSES = (
            "Kutubxona",
            "Ibrat Farzandlari",
            "Kulolchilik akademiyasi",
            "Let's animate",
            "UVA",
            "Fitrat media",
            "Yoshlar ovozi",
        )


@lru_cache
def get_settings():
    return Settings()
