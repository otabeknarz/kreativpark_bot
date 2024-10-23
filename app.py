import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

from aiogram.fsm.context import FSMContext

from aiogram import types
import datetime
import json

from aiogram.methods import DeleteWebhook

from modules.keyboards import Buttons, InlineButtons
from modules import functions
from modules.states import RegistrationState, SendPostState, LoginState
from modules.settings import get_settings
from modules import excelpy
from modules.filters import TextEqualsFilter

bot_settings = get_settings()

API_TOKEN = bot_settings.BOT_API_TOKEN

dp = Dispatcher()
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

buttons = Buttons()
inline_buttons = InlineButtons()


async def is_subscribed(bot, message: types.Message, state=None):
    """The function checks the did user subscribe the channel if so returns True else False"""
    is_subscribed_ = await bot.get_chat_member(
        chat_id=bot_settings.CHANNEL, user_id=message.from_user.id
    )
    if is_subscribed_.status == "left":
        await message.answer(
            "Botdan foydalanishingiz uchun birinchi navbatda bizning kanalga a'zo bo'lishingiz kerak",
            reply_markup=inline_buttons.subscribe_inline,
        )
        if state:
            await state.clear()

        return False
    return True


def debug_mode():
    def decorator(func):
        async def wrapper(message: types.Message, state: FSMContext, *args, **kwargs):
            # Check if debug mode is disabled
            if not bot_settings.DEBUG:
                return await func(message, state, *args, **kwargs)
            else:
                # If debug mode is enabled and the user is an admin, proceed
                if message.from_user.id in bot_settings.ignore_debug_users.values():
                    return await func(message, state, *args, **kwargs)
                # If not an admin, send a "maintenance" message
                await state.clear()
                await message.answer(
                    "Hozirda biz botga tuzatishlar kiritmoqdamiz iltimos kuting, "
                    "noqulayliklar uchun uzr so'raymiz"
                )

        return wrapper

    return decorator


@debug_mode()
@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    if not await is_subscribed(bot, message):
        return

    response = functions.get_req(
        bot_settings.CHECK_PEOPLE_URL + str(message.from_user.id) + "/"
    ).json()

    if message.from_user.id in bot_settings.admins.values():
        await message.reply(
            f"Assalomu alaykum <strong>{message.from_user.full_name}!</strong>",
            reply_markup=buttons.admin_main_keyboard,
            parse_mode="html",
        )
    elif response["status"] == "false":
        await message.reply(
            f"Assalomu alaykum!\nKreativ Parkga kirishdan oldin ro'yxatdan o'ting",
            reply_markup=buttons.registration,
        )
    else:
        await message.reply(
            f"Qaytganingiz bilan <strong>{response['people']['name']}!</strong>",
            reply_markup=buttons.main_keyboard,
            parse_mode="html",
        )


@debug_mode()
@dp.callback_query()
async def check_subs_callback(callback: types.CallbackQuery):
    if callback.data == "subscribed":
        is_subscribed = await bot.get_chat_member(
            chat_id=bot_settings.CHANNEL, user_id=callback.message.chat.id
        )
        if is_subscribed.status != "left":
            response = json.loads(
                functions.get_req(
                    bot_settings.CHECK_PEOPLE_URL + str(callback.message.chat.id) + "/"
                ).text
            )
            if response["status"] == "false":
                await callback.message.reply(
                    f"Assalomu alaykum\n"
                    f"Kreativ Parkga kirishdan oldin ro'yxatdan o'ting",
                    reply_markup=buttons.registration,
                )
            else:
                await callback.message.answer(
                    "Botdan foydalanishingiz mumkin.",
                    reply_markup=buttons.main_keyboard,
                )
        else:
            await bot.answer_callback_query(
                callback.id,
                "Botdan foydalanishingiz uchun birinchi navbatda bizning kanalga a'zo bo'lishingiz kerak",
                show_alert=True,
            )
            await callback.message.delete()
            await callback.message.answer(
                "Botdan foydalanishingiz uchun birinchi navbatda bizning kanalga a'zo bo'lishingiz kerak",
                reply_markup=inline_buttons.subscribe_inline,
            )


@debug_mode()
@dp.message(TextEqualsFilter("🔢 Kirish kodini olish"))
async def get_number_token(message: types.Message):
    if not await is_subscribed(bot, message):
        return

    response = functions.get_req(
        bot_settings.CHECK_PEOPLE_URL + str(message.from_user.id) + "/"
    ).json()

    if response["status"] == "false":
        await message.answer(
            "Ro'yxatdan topa olmadik avval ro'yxatdan o'ting",
            reply_markup=buttons.registration,
        )
        return

    res = functions.get_req(
        bot_settings.GET_NUMBER_TOKEN + str(message.chat.id) + "/"
    ).json()
    if res["status"] == "true":
        await message.reply(
            f"Sizning kirish uchun kodingiz: <code>{res['number_token']}</code>\nE'tibor bering kod faqat bir martalik va 1 daqiqa ichida amal qiladi",
            reply_markup=inline_buttons.web_login,
        )
    else:
        await message.reply("Qayta urinib ko'ring")


@debug_mode()
@dp.message(TextEqualsFilter("✍️ Ro'yxatdan o'tish"))
async def run_name_state(message: types.Message, state: FSMContext):
    if not await is_subscribed(bot, message):
        return

    await message.answer(
        "Ism familiyangizni to'liq yozing",
        reply_markup=buttons.remove_keyboard,
    )
    await state.set_state(RegistrationState.name)


@debug_mode()
@dp.message(RegistrationState.name)
async def name_state(message: types.Message, state: FSMContext):
    if not await is_subscribed(bot, message, state):
        return

    name = message.text
    await message.answer(
        "Endi shaxsiy ID kartangiz(passport)dan seriya va raqamni yuboring\nMisol uchun: AB1234567",
    )
    await state.update_data(name=name)
    await state.update_data(ID=str(message.from_user.id))
    await state.set_state(RegistrationState.passport_data)


@debug_mode()
@dp.message(RegistrationState.passport_data)
async def passport_data_state(message: types.Message, state: FSMContext):
    if not await is_subscribed(bot, message, state):
        return

    passport_data = message.text
    await message.answer(
        "Endi telefon raqamimni yuborish tugmasini bosing bu bilan siz bizga telefon raqamingizni yuborasiz",
        reply_markup=buttons.phone_number,
    )
    await state.update_data(passport_data=passport_data)
    await state.set_state(RegistrationState.phone_number)


@debug_mode()
@dp.message(RegistrationState.phone_number)
async def phone_number_state(message: types.Message, state: FSMContext):
    if not await is_subscribed(bot, message, state):
        return

    await state.update_data(phone_number=message.contact.phone_number)
    response = functions.post_req(bot_settings.POST_PEOPLE_URL, await state.get_data())
    print(response)
    print(response.text)
    if response.status_code == 201:
        await message.answer(
            "Siz ro'yxatdan o'tdingiz", reply_markup=buttons.main_keyboard
        )
    else:
        await message.answer(
            "Xatolik yuz berdi qaytadan urinib ko'ring",
            reply_markup=buttons.registration,
        )
    await state.clear()


@debug_mode()
@dp.message(TextEqualsFilter("🖼 Kirish uchun QR Code olish"))
async def purpose_state(message: types.Message, state: FSMContext):
    if not await is_subscribed(bot, message):
        return

    response = json.loads(
        functions.get_req(
            bot_settings.CHECK_PEOPLE_URL + str(message.from_user.id) + "/"
        ).text
    )

    if response["status"] == "false":
        await message.answer(
            "Ro'yxatdan topa olmadik avval ro'yxatdan o'ting",
            reply_markup=buttons.registration,
        )
        return

    check_people_has_qrcode = functions.get_req(
        bot_settings.CHECK_PEOPLE_HAS_QRCODE + str(message.chat.id) + "/"
    )
    if (
        check_people_has_qrcode.status_code == 200
        and json.loads(check_people_has_qrcode.text)["status"] == "true"
    ):
        response = functions.get_req(
            bot_settings.GET_QRCODES_DELETE_URL + str(message.chat.id) + "/"
        )
        if response.status_code == 200:
            if json.loads(response.text)["status"] == "true":
                await purpose_state(message, state)
        return

    await message.answer(
        "Quyidagi tugmalarda Kreativ Parkimizdagi manzillar bor va siz qayerga kirmoqchisiz?",
        reply_markup=buttons.purposes_btn,
    )
    await state.set_state(LoginState.purpose)


@debug_mode()
@dp.message(LoginState.purpose)
async def qrcode_make(message: types.Message, state: FSMContext):
    if not await is_subscribed(bot, message, state):
        return

    response = functions.get_req(
        bot_settings.CHECK_PEOPLE_URL + str(message.from_user.id) + "/"
    ).json()

    if response["status"] == "false":
        await message.answer(
            "Ro'yxatdan topa olmadik avval ro'yxatdan o'ting",
            reply_markup=buttons.registration,
        )
        return

    check_people_has_qrcode = functions.get_req(
        bot_settings.CHECK_PEOPLE_HAS_QRCODE + str(message.chat.id) + "/"
    )
    purpose = message.text
    if purpose not in bot_settings.PURPOSES:
        await message.reply("Quyidagi tugmalarda manzillar berilgan")
        await state.clear()
        await purpose_state(message, state)
        return

    if (
        json.loads(check_people_has_qrcode.text)["status"] == "false"
        and check_people_has_qrcode.status_code == 200
    ):
        req = functions.post_req(
            bot_settings.POST_QRCODE_URL,
            {"people_id": str(message.chat.id), "type": "IN", "purpose": purpose},
        )

        if req.status_code == 201:
            await message.answer(
                "QrCode ingiz tayyor uni web sahifamizga kirib 'Profil' bo'limidan olishingiz mumkin",
                reply_markup=inline_buttons.web_profile,
            )
            await message.answer("Unutmang, QrCode ni skaner qilganingizdan so'ng profilingizda avtomatik ravishda chiqish uchun QrCode beriladi", reply_markup=buttons.main_keyboard)
            # await bot.send_photo(
            #     message.chat.id,
            #     f"https://api.otabek.me/media/{req.json()['qr_code_image']}",
            #     caption="Sizning kirish uchun qr codeingiz",
            #     reply_markup=buttons.main_keyboard,
            # )
            await state.clear()


# @debug_mode()
# @dp.message(TextEqualsFilter("🖼 Chiqish uchun QR Code olish"))
# async def logout_qrcode(message: types.Message):
#     if not await is_subscribed(bot, message):
#         return
#
#     response = json.loads(
#         functions.get_req(
#             bot_settings.CHECK_PEOPLE_URL + str(message.from_user.id) + "/"
#         ).text
#     )
#
#     if response["status"] == "false":
#         await message.answer(
#             "Ro'yxatdan topa olmadik avval ro'yxatdan o'ting",
#             reply_markup=buttons.registration,
#         )
#         return
#
#     check_people_has_qrcode = functions.get_req(
#         bot_settings.CHECK_PEOPLE_HAS_QRCODE + str(message.chat.id) + "/"
#     )
#     if (
#         json.loads(check_people_has_qrcode.text)["status"] == "false"
#         and check_people_has_qrcode.status_code == 200
#     ):
#         req = functions.post_req(
#             bot_settings.POST_QRCODE_URL,
#             {"people_id": str(message.chat.id), "type": "OUT"},
#         )
#         if req.status_code == 201:
#             await bot.send_photo(
#                 message.chat.id,
#                 f"https://api.otabek.me/media/{req.json()['qr_code_image']}",
#                 caption="Sizning chiqish uchun qr codeingiz",
#                 reply_markup=buttons.main_keyboard,
#             )
#     elif (
#         json.loads(check_people_has_qrcode.text)["status"] == "true"
#         and check_people_has_qrcode.status_code == 200
#     ):
#         response = functions.get_req(
#             bot_settings.GET_QRCODES_DELETE_URL + str(message.chat.id) + "/"
#         )
#         if response.status_code == 200:
#             if json.loads(response.text)["status"] == "true":
#                 await logout_qrcode(message)


@debug_mode()
@dp.message(TextEqualsFilter("👤 Ma'lumotlarim"))
async def dashboard(message: types.Message):
    if not await is_subscribed(bot, message):
        return
    response = functions.get_req(
        bot_settings.CHECK_PEOPLE_URL + str(message.chat.id) + "/"
    ).json()
    if response["status"] == "true":
        people = (
            f"Ism Familiyangiz: {response['people']['name']}\n"
            f"Telefon raqamingiz: {response['people']['phone_number']}"
        )
        await message.answer(people)
    else:
        await message.reply(
            f"Assalomu alaykum!\nKreativ Parkga kirishdan oldin ro'yxatdan o'ting",
            reply_markup=buttons.registration,
        )


# Admins commands


@dp.message(TextEqualsFilter("📮 Yangi post yuborish"))
async def send_post_activate(message: types.Message, state: FSMContext):
    if message.chat.id not in bot_settings.admins.values():
        return
    await message.answer("Postingizni yuboring", reply_markup=buttons.cancel_btn)
    await state.set_state(SendPostState.post)


@dp.message(SendPostState.post)
async def send_post(message: types.Message, state: FSMContext):
    if message.chat.id not in bot_settings.admins.values():
        return
    text = message.text
    if text == "❌ Bekor qilish" or text == "📮 Yangi post yuborish":
        await state.clear()
        await message.answer("Bekor qilindi", reply_markup=buttons.admin_main_keyboard)
        return

    people_IDs = json.loads(functions.get_req(bot_settings.CHECK_PEOPLE_IDS).text)
    unregistered_people_count = 0
    posted_people_count = 0
    await message.answer("Post yuborilyabdi...")
    for people in people_IDs:
        try:
            await message.send_copy(people["ID"])
            posted_people_count += 1
        except:
            unregistered_people_count += 1

    await message.answer("Post jo'natildi", reply_markup=buttons.admin_main_keyboard)
    if unregistered_people_count:
        await message.answer(
            f"{posted_people_count} ta foydalanuvchiga post jo'natildi\n"
            f"{unregistered_people_count} ta ro'yxatdan o'tgan foydalanuvchi hozir botni ishlatmayapti"
        )
    await state.clear()


@dp.message(TextEqualsFilter("📈 Bugungi Ma'lumotlar"))
async def todays_stats(message: types.Message):
    if message.chat.id not in bot_settings.admins.values():
        return
    response = functions.get_req(bot_settings.STATS_URL + "1/").json()
    answer = ""
    answer += (
        "🆕 Yangi ro'yxatdan o'tganlar soni: "
        + f"<strong>{response['people_count']}</strong>"
        + "\n"
    )
    answer += (
        "📥 Kreativ Parkga kirganlar soni: "
        + f"<strong>{response['data_count_IN']}</strong>"
        + "\n"
    )
    answer += (
        "📤 Kreativ Parkdan chiqganlar soni: "
        + f"<strong>{response['data_count_OUT']}</strong>"
        + "\n"
    )
    answer += "Odamlar qayerga kirishyapti: " + "\n"
    for key, value in response["purposes"].items():
        answer += key + ": " + f"<strong>{value}</strong>" + "\n"

    await message.answer(answer, parse_mode="html")
    document_name = excelpy.make_stats(response["people"], response["purposes"], 1)

    await bot.send_document(
        message.chat.id,
        types.FSInputFile(path=document_name, filename=document_name.split("/")[-1]),
    )


@dp.message(TextEqualsFilter("7️⃣ Haftalik Ma'lumotlar"))
async def weeks_stats(message: types.Message):
    if message.chat.id not in bot_settings.admins.values():
        return
    response = functions.get_req(bot_settings.STATS_URL + "7/").json()
    answer = ""
    answer += (
        "🆕 Yangi ro'yxatdan o'tganlar soni: "
        + f"<strong>{response['people_count']}</strong>"
        + "\n"
    )
    answer += (
        "📥 Kreativ Parkga kirganlar soni: "
        + f"<strong>{response['data_count_IN']}</strong>"
        + "\n"
    )
    answer += (
        "📤 Kreativ Parkdan chiqganlar soni: "
        + f"<strong>{response['data_count_OUT']}</strong>"
        + "\n"
    )
    answer += "Odamlar qayerga kirishyapti: " + "\n"
    for key, value in response["purposes"].items():
        answer += key + ": " + f"<strong>{value}</strong>" + "\n"

    await message.answer(answer, parse_mode="html")
    document_name = excelpy.make_stats(response["people"], response["purposes"], 7)

    await bot.send_document(
        message.chat.id,
        document=types.FSInputFile(
            path=document_name, filename=document_name.split("/")[-1]
        ),
    )


@dp.message(TextEqualsFilter("🌘 Oylik Ma'lumotlar"))
async def months_stats(message: types.Message):
    if message.chat.id not in bot_settings.admins.values():
        return
    response = functions.get_req(bot_settings.STATS_URL + "30/").json()
    answer = ""
    answer += (
        "🆕 Yangi ro'yxatdan o'tganlar soni: "
        + f"<strong>{response['people_count']}</strong>"
        + "\n"
    )
    answer += (
        "📥 Kreativ Parkga kirganlar soni: "
        + f"<strong>{response['data_count_IN']}</strong>"
        + "\n"
    )
    answer += (
        "📤 Kreativ Parkdan chiqganlar soni: "
        + f"<strong>{response['data_count_OUT']}</strong>"
        + "\n"
    )
    answer += "Odamlar qayerga kirishyapti: " + "\n"
    for key, value in response["purposes"].items():
        answer += key + ": " + f"<strong>{value}</strong>" + "\n"

    await message.answer(answer, parse_mode="html")
    document_name = excelpy.make_stats(response["people"], response["purposes"], 30)

    await bot.send_document(
        message.chat.id,
        types.FSInputFile(path=document_name, filename=document_name.split("/")[-1]),
    )


@dp.message(TextEqualsFilter("📊 Barcha Ma'lumotlar"))
async def all_time_stats(message: types.Message):
    if message.chat.id not in bot_settings.admins.values():
        return
    response = functions.get_req(bot_settings.STATS_URL + "0/").json()
    answer = ""
    answer += (
        "Jami ro'yxatdan o'tganlar soni: "
        + f"<strong>{response['people_count']}</strong>"
        + "\n"
    )
    answer += (
        "Kreativ Parkga kirganlar soni: "
        + f"<strong>{response['data_count_IN']}</strong>"
        + "\n"
    )
    answer += (
        "Kreativ Parkdan chiqganlar soni: "
        + f"<strong>{response['data_count_OUT']}</strong>"
        + "\n"
    )
    answer += "Odamlar qayerga kirishyapti: " + "\n"
    for key, value in response["purposes"].items():
        answer += key + ": " + f"<strong>{value}</strong>" + "\n"

    await message.answer(answer, parse_mode="html")
    document_name = excelpy.make_stats(response["people"], response["purposes"], 0)

    await bot.send_document(
        message.chat.id,
        types.FSInputFile(path=document_name, filename=document_name.split("/")[-1]),
    )


async def on_startup_notify(arg):
    for admin in bot_settings.admins.values():
        try:
            await bot.send_message(
                admin,
                f"Bot has been ran successfully\n{datetime.datetime.now().strftime('%H:%M %d/%m/%Y')}",
            )
        except:
            pass


async def main() -> None:
    # And the run events dispatching
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot, on_startup_notify=on_startup_notify)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
