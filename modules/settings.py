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
        self.LOGIN_URL = "https://otabek.me/login/"

        # Api endpoint
        self.API_ENDPOINT = "api/v2/"

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

        # Urls for auth
        self.ACCESS_TOKEN_URL = self.BASE_URL + self.API_ENDPOINT + "auth/token/"
        self.REFRESH_TOKEN_URL = (
            self.BASE_URL + self.API_ENDPOINT + "auth/token/refresh/"
        )

        # This url to get qrcode and enter library
        self.LOGIN_LIBRARY = self.BASE_URL + self.API_ENDPOINT + "login-library/"
        self.GET_NUMBER_TOKEN = self.BASE_URL + self.API_ENDPOINT + "get-number-token/"

        # admins
        self.admins = {
            # "Otabek": 5551503420,
            "Azizbek": 1251979840,
            "Iskandar": 228633803,
        }

        self.ignore_debug_users = {"Otabek": 5551503420, **self.admins}

        # admins urls
        self.STATS_URL = self.BASE_URL + self.API_ENDPOINT + "stats/"

        # Bot settings
        self.BOT_API_TOKEN = os.getenv("API_TOKEN")
        self.CHANNEL = "@kreativparkuz"
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

        # Debug mode for there is a some bugs the bot answers everyone like currently bot is in debug mode
        self.DEBUG = os.getenv("DEBUG")


@lru_cache
def get_settings():
    return Settings()
