import requests
import uuid
import os

from requests import Response
import qrcode
from dotenv import load_dotenv
from .settings import get_settings

bot_settings = get_settings()

load_dotenv()

cookies = {"sessionid": bot_settings.SESSION_ID, "csrftoken": bot_settings.CSRF_TOKEN}
headers = {
    "Content-Type": "application/json",
    "X-CSRFToken": bot_settings.CSRF_TOKEN,
}


def get_req(url) -> Response:
    return requests.get(url, cookies=cookies)


def post_req(url, obj) -> Response:
    return requests.post(url, json=obj, headers=headers, cookies=cookies)


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
