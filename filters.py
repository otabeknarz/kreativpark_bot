from aiogram.filters import Filter
from aiogram.types import Message


class TextFilter(Filter):
    def __init__(self, text) -> None:
        self.text = text

    def __call__(self, message: Message) -> bool:
        return message.text == self.text
