from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)

from .settings import get_settings

bot_settings = get_settings()


class Buttons:
    """Reply keyboard buttons"""

    def __init__(self):
        # Keyboards for only admins
        self.admin_main_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📮 Yangi post yuborish")],
                [KeyboardButton(text="📈 Bugungi Ma'lumotlar")],
                [KeyboardButton(text="7️⃣ Haftalik Ma'lumotlar")],
                [KeyboardButton(text="🌘 Oylik Ma'lumotlar")],
                [KeyboardButton(text="📊 Barcha Ma'lumotlar")],
            ],
            resize_keyboard=True,
        )

        # Keyboards for everyone
        self.main_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🖼 Kirish uchun QR Code olish")],
                [KeyboardButton(text="🖼 Chiqish uchun QR Code olish")],
                [KeyboardButton(text="👤 Ma'lumotlarim")],
            ],
            resize_keyboard=True,
        )
        self.registration = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="✍️ Ro'yxatdan o'tish")]],
            resize_keyboard=True,
        )

        self.phone_number = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="📱 Telefon raqamimni yuborish", request_contact=True
                    )
                ]
            ],
            resize_keyboard=True,
        )

        self.remove_keyboard = ReplyKeyboardRemove()

        self.cancel_btn = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Bekor qilish")]], resize_keyboard=True
        )

        self.purposes_btn = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Kutubxona")],
                [KeyboardButton(text="Ibrat Farzandlari")],
                [KeyboardButton(text="Kulolchilik akademiyasi")],
                [KeyboardButton(text="Let's animate")],
                [KeyboardButton(text="UVA")],
                [KeyboardButton(text="Fitrat media")],
                [KeyboardButton(text="Yoshlar ovozi")],
            ]
        )


class InlineButtons:
    def __init__(self):
        # INLINE Keyboards
        ibrat_inline_btn = InlineKeyboardButton(
            text="Kreativ Park kanaliga obuna bo'lish",
            url="https://t.me/" + bot_settings.CHANNEL[1:],
        )
        ive_subscribed_btn = InlineKeyboardButton(
            text="A'zo bo'ldim", callback_data="subscribed"
        )
        self.subscribe_inline = InlineKeyboardMarkup(
            inline_keyboard=[[ibrat_inline_btn], [ive_subscribed_btn]]
        )

        self.web_login = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔗 Web saytga kirish", url=bot_settings.LOGIN_URL
                    )
                ]
            ]
        )
