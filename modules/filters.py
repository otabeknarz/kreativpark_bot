from aiogram.filters import Filter
from aiogram.types import Message


class TextEqualsFilter(Filter):
    def __init__(self, message: str) -> None:
        self.message = message

    async def __call__(self, message: Message) -> bool:
        return message.text == self.message
