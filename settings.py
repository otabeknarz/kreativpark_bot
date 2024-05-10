class Settings:
    """This module has any settings for kreativ park bot"""

    def __init__(self):
        # Settings for django apis (urls)

        # Base url
        self.BASE_URL = "http://127.0.0.1:8000/"

        # Api endpoint
        self.API_ENDPOINT = "api/v1/"

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

        # admins
        self.admins = {
            "Otabek": 5551503420,
            "Azizbek": 1251979840,
            "Iskandar": 228633803,
        }

        # admins urls
        self.STATS_URL = self.BASE_URL + self.API_ENDPOINT + "stats/"

        # Bot settings
        self.BOT_API_TOKEN = "6354164020:AAGFYlDZAU7AOMbn1bp4FrJsVSJP1Od69Y8"
        self.IBRAT_CHANNEL = "@ibratdebate"
        self.QRCODES_PATH = "images/qr_codes/"
