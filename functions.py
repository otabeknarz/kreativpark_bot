import requests
import uuid
import os

from requests import Response

from settings import Settings
import qrcode


def get_req(url) -> Response:
    return requests.get(url)


def post_req(url, obj) -> Response:
    return requests.post(url, json=obj)


def make_qrcode(bot_settings: Settings) -> str:
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
