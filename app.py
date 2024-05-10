import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import datetime
import json

from keyboards import Buttons, InlineButtons
import functions
from states import RegistrationState, SendPostState, LoginState
from settings import Settings
import excelpy

bot_settings = Settings()

API_TOKEN = bot_settings.BOT_API_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

buttons = Buttons()
inline_buttons = InlineButtons()


async def is_subscribed(bot, message: types.Message, state=None):
    """The function checks the did user subscribe the channel if so returns True else False"""
    is_subscribed_ = await bot.get_chat_member(
        chat_id=bot_settings.IBRAT_CHANNEL, user_id=message.from_user.id
    )
    if is_subscribed_["status"] == "left":
        await message.answer(
            "Botdan foydalanishingiz uchun birinchi navbatda bizning kanalga a'zo bo'lishingiz kerak",
            reply_markup=inline_buttons.subscribe_inline,
        )
        if state:
            await state.reset_state()

        return False
    return True


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    if not await is_subscribed(bot, message):
        return

    response = json.loads(
        functions.get_req(
            bot_settings.CHECK_PEOPLE_URL + str(message.from_user.id) + "/"
        ).text
    )
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
            parse_mode="html",
        )
    else:
        await message.reply(
            f"Qaytganingiz bilan <strong>{response['people']['name']}!</strong>{message.chat.id}",
            reply_markup=buttons.main_keyboard,
            parse_mode="html",
        )


@dp.callback_query_handler()
async def check_subs_callback(callback: types.CallbackQuery):
    if callback.data == "subscribed":
        is_subscribed = await bot.get_chat_member(
            chat_id=bot_settings.IBRAT_CHANNEL, user_id=callback.message.chat.id
        )
        if is_subscribed["status"] != "left":
            response = json.loads(
                functions.get_req(
                    bot_settings.CHECK_PEOPLE_URL + str(callback.message.chat.id) + "/"
                ).text
            )
            if response["status"] == "false":
                await callback.message.reply(
                    f"Assalomu alaykum <strong>{callback.message.chat.full_name}</strong>\n"
                    f"Kreativ Parkga kirishdan oldin ro'yxatdan o'ting",
                    reply_markup=buttons.registration,
                    parse_mode="html",
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


@dp.message_handler(text="✍️ Ro'yxatdan o'tish")
async def run_name_state(message: types.Message):
    if not await is_subscribed(bot, message):
        return
    # await bot.send_message(message.chat.id, message.text)

    await message.answer(
        "Ismingizni yozing",
        reply_markup=buttons.name_btn(message.from_user.full_name),
    )
    await RegistrationState.name.set()


@dp.message_handler(state=RegistrationState.name)
async def name_state(message: types.Message, state: FSMContext):
    if not await is_subscribed(bot, message, state):
        return

    name = message.text
    await message.answer(
        "Endi shaxsiy ID kartangiz(passport)dan seriya va raqamni yuboring\nMisol uchun: AB1234567",
        reply_markup=buttons.remove_keyboard,
    )
    await state.update_data(name=name)
    await state.update_data(ID=str(message.from_user.id))
    await RegistrationState.passport_data.set()


@dp.message_handler(state=RegistrationState.passport_data)
async def passport_data_state(message: types.Message, state: FSMContext):
    if not await is_subscribed(bot, message, state):
        return

    passport_data = message.text
    await message.answer(
        "Endi telefon raqamingizni yuboring\nTelefon raqamimni yuborish tugmasini bosing",
        reply_markup=buttons.phone_number,
    )
    await state.update_data(passport_data=passport_data)
    await RegistrationState.phone_number.set()


@dp.message_handler(content_types=["contact"], state=RegistrationState.phone_number)
async def phone_number_state(message: types.Message, state: FSMContext):
    if not await is_subscribed(bot, message, state):
        return

    await state.update_data(phone_number=message.contact["phone_number"])
    response = functions.post_req(bot_settings.POST_PEOPLE_URL, await state.get_data())
    if response.status_code == 201:
        await message.answer(
            "Siz ro'yxatdan o'tdingiz", reply_markup=buttons.main_keyboard
        )
    else:
        await message.answer(
            "Xatolik yuz berdi qaytadan urinib ko'ring",
            reply_markup=buttons.registration,
        )
    await state.reset_state()


@dp.message_handler(text="🖼 Kirish uchun QR Code olish")
async def purpose_state(message: types.Message):
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
                await purpose_state(message)
        return

    await message.answer(
        "Nima uchun Kreativ Parkga kirmoqchisiz yozing",
        reply_markup=buttons.purposes_btn,
    )
    await LoginState.purpose.set()


@dp.message_handler(state=LoginState.purpose)
async def qrcode_make(message: types.Message, state: FSMContext):
    if not await is_subscribed(bot, message, state):
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
    purpose = message.text
    if (
        json.loads(check_people_has_qrcode.text)["status"] == "false"
        and check_people_has_qrcode.status_code == 200
    ):
        ID = functions.make_qrcode(bot_settings)
        obj = {
            "ID": ID,
            "people": message.chat.id,
            "image_path": bot_settings.QRCODES_PATH + ID + ".png",
            "purpose": purpose,
            "type": "IN",
        }
        req = functions.post_req(bot_settings.POST_QRCODE_URL, obj)
        if req.status_code == 201:
            with open(obj["image_path"], "rb") as photo:
                await bot.send_photo(
                    message.chat.id,
                    photo,
                    caption="Sizning kirish uchun qr codeingiz",
                    reply_markup=buttons.main_keyboard,
                )
                if not functions.delete_file(json.loads(req.text)["image_path"]):
                    print(
                        "!!!!! Rasm o'chirilmadi !!!!!\nID: ",
                        json.loads(req.text)["image_path"],
                    )

            await state.reset_state()


@dp.message_handler(text="🖼 Chiqish uchun QR Code olish")
async def logout_qrcode(message: types.Message):
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
        json.loads(check_people_has_qrcode.text)["status"] == "false"
        and check_people_has_qrcode.status_code == 200
    ):
        ID = functions.make_qrcode(bot_settings)
        obj = {
            "ID": ID,
            "people": message.chat.id,
            "image_path": bot_settings.QRCODES_PATH + ID + ".png",
            "purpose": "",
            "type": "OUT",
        }
        req = functions.post_req(bot_settings.POST_QRCODE_URL, obj)
        if req.status_code == 201:
            with open(obj["image_path"], "rb") as photo:
                await bot.send_photo(
                    message.chat.id,
                    photo,
                    caption="Sizning chiqish uchun qr codeingiz",
                    reply_markup=buttons.main_keyboard,
                )
                if not functions.delete_file(json.loads(req.text)["image_path"]):
                    print(
                        "!!!!! Rasm o'chirilmadi !!!!!\nID: ",
                        json.loads(req.text)["image_path"],
                    )
    elif (
        json.loads(check_people_has_qrcode.text)["status"] == "true"
        and check_people_has_qrcode.status_code == 200
    ):
        response = functions.get_req(
            bot_settings.GET_QRCODES_DELETE_URL + str(message.chat.id) + "/"
        )
        if response.status_code == 200:
            if json.loads(response.text)["status"] == "true":
                await logout_qrcode(message)


# @dp.message_handler(text="❌ Kirish uchun QR Codeni o'chirish")
# async def qrcode_make(message: types.Message):
#     is_subscribed = await bot.get_chat_member(
#         chat_id=bot_settings.IBRAT_CHANNEL, user_id=message.from_user.id
#     )
#     if is_subscribed["status"] == "left":
#         await message.answer(
#             "Botdan foydalanishingiz uchun birinchi navbatda bizning kanalga a'zo bo'lishingiz kerak",
#             reply_markup=inline_buttons.subscribe_inline,
#         )
#         return
#
#     check_people_has_qrcode = functions.get_req(
#         bot_settings.CHECK_PEOPLE_HAS_QRCODE + str(message.chat.id)
#     )
#     if check_people_has_qrcode.status_code == 200:
#         if json.loads(check_people_has_qrcode.text)["status"] == "true":
#             response = functions.get_req(
#                 bot_settings.GET_QRCODES_DELETE_URL + str(message.chat.id)
#             )
#             if response.status_code == 200:
#                 if json.loads(response.text)["status"] == "true":
#                     if not functions.delete_file(
#                         json.loads(response.text)["image_path"]
#                     ):
#                         print(
#                             "!!!!! Rasm o'chirilmadi !!!!!\nID: ",
#                             json.loads(response.text)["image_path"],
#                         )
#                     await message.answer(
#                         "O'chirildi", reply_markup=keyboards.main_keyboard
#                     )
#         elif json.loads(check_people_has_qrcode.text)["status"] == "false":
#             await message.answer("Sizda QR Code yo'q")


# Admins commands


@dp.message_handler(text="📮 Yangi post yuborish")
async def send_post_activate(message: types.Message):
    if message.chat.id not in bot_settings.admins.values():
        return
    await message.answer("Postingizni yuboring", reply_markup=buttons.cancel_btn)
    await SendPostState.post.set()


@dp.message_handler(state=SendPostState.post, content_types=["text", "photo"])
async def send_post(message: types.Message, state: FSMContext):
    if message.chat.id not in bot_settings.admins.values():
        return
    text = message.text
    if text == "❌ Bekor qilish":
        await state.reset_state()
        await message.answer("Bekor qilindi", reply_markup=buttons.admin_main_keyboard)

        return
    people_IDs = json.loads(functions.get_req(bot_settings.CHECK_PEOPLE_IDS).text)[
        "IDs"
    ]
    unregistered_people_count = 0

    try:
        for people in people_IDs:
            await bot.send_message(people, text)
    except:
        unregistered_people_count += 1

    await message.answer("Post jo'natildi")
    if unregistered_people_count:
        await message.answer(
            f"{unregistered_people_count} ta ro'yxatdan o'tgan foydalanuvchi hozir botni ishlatmayapti"
        )
    await state.reset_state()


@dp.message_handler(text="📈 Bugungi Ma'lumotlar")
async def todays_stats(message: types.Message):
    if message.chat.id not in bot_settings.admins.values():
        return
    response = functions.get_req(bot_settings.STATS_URL + "1/").json()
    answer = ""
    answer += (
        "🆕 Yangi ro'yxatdan o'tganlar soni: "
        + f"<strong>{response["people_count"]}</strong>"
        + "\n"
    )
    answer += (
        "📥 Kreativ Parkga kirganlar soni: "
        + f"<strong>{response["data_count_IN"]}</strong>"
        + "\n"
    )
    answer += (
        "📤 Kreativ Parkdan chiqganlar soni: "
        + f"<strong>{response["data_count_OUT"]}</strong>"
        + "\n"
    )
    answer += "Odamlar qayerga kirishyapti: " + "\n"
    for key, value in response["purposes"].items():
        answer += key + ": " + f"<strong>{value}</strong>" + "\n"

    await message.answer(answer, parse_mode="html")
    document_name = excelpy.make_stats(response["people"], response["purposes"], 1)
    with open(document_name, "rb") as excel:
        await bot.send_document(message.chat.id, excel)


@dp.message_handler(text="7️⃣ Haftalik Ma'lumotlar")
async def weeks_stats(message: types.Message):
    if message.chat.id not in bot_settings.admins.values():
        return
    response = functions.get_req(bot_settings.STATS_URL + "7/").json()
    answer = ""
    answer += (
        "🆕 Yangi ro'yxatdan o'tganlar soni: "
        + f"<strong>{response["people_count"]}</strong>"
        + "\n"
    )
    answer += (
        "📥 Kreativ Parkga kirganlar soni: "
        + f"<strong>{response["data_count_IN"]}</strong>"
        + "\n"
    )
    answer += (
        "📤 Kreativ Parkdan chiqganlar soni: "
        + f"<strong>{response["data_count_OUT"]}</strong>"
        + "\n"
    )
    answer += "Odamlar qayerga kirishyapti: " + "\n"
    for key, value in response["purposes"].items():
        answer += key + ": " + f"<strong>{value}</strong>" + "\n"

    await message.answer(answer, parse_mode="html")
    document_name = excelpy.make_stats(response["people"], response["purposes"], 7)
    with open(document_name, "rb") as excel:
        await bot.send_document(message.chat.id, excel)


@dp.message_handler(text="🌘 Oylik Ma'lumotlar")
async def months_stats(message: types.Message):
    if message.chat.id not in bot_settings.admins.values():
        return
    response = functions.get_req(bot_settings.STATS_URL + "30/").json()
    answer = ""
    answer += (
        "🆕 Yangi ro'yxatdan o'tganlar soni: "
        + f"<strong>{response["people_count"]}</strong>"
        + "\n"
    )
    answer += (
        "📥 Kreativ Parkga kirganlar soni: "
        + f"<strong>{response["data_count_IN"]}</strong>"
        + "\n"
    )
    answer += (
        "📤 Kreativ Parkdan chiqganlar soni: "
        + f"<strong>{response["data_count_OUT"]}</strong>"
        + "\n"
    )
    answer += "Odamlar qayerga kirishyapti: " + "\n"
    for key, value in response["purposes"].items():
        answer += key + ": " + f"<strong>{value}</strong>" + "\n"

    await message.answer(answer, parse_mode="html")
    document_name = excelpy.make_stats(response["people"], response["purposes"], 30)
    with open(document_name, "rb") as excel:
        await bot.send_document(message.chat.id, excel)


@dp.message_handler(text="📊 Barcha Ma'lumotlar")
async def all_time_stats(message: types.Message):
    if message.chat.id not in bot_settings.admins.values():
        return
    response = functions.get_req(bot_settings.STATS_URL + "0/").json()
    answer = ""
    answer += (
        "Jami ro'yxatdan o'tganlar soni: "
        + f"<strong>{response["people_count"]}</strong>"
        + "\n"
    )
    answer += (
        "Kreativ Parkga kirganlar soni: "
        + f"<strong>{response["data_count_IN"]}</strong>"
        + "\n"
    )
    answer += (
        "Kreativ Parkdan chiqganlar soni: "
        + f"<strong>{response["data_count_OUT"]}</strong>"
        + "\n"
    )
    answer += "Odamlar qayerga kirishyapti: " + "\n"
    for key, value in response["purposes"].items():
        answer += key + ": " + f"<strong>{value}</strong>" + "\n"

    await message.answer(answer, parse_mode="html")
    document_name = excelpy.make_stats(response["people"], response["purposes"], 0)
    with open(document_name, "rb") as excel:
        await bot.send_document(message.chat.id, excel)


async def on_startup_notify(arg):
    for admin in bot_settings.admins.values():
        try:
            await bot.send_message(
                admin,
                f"Bot has been ran successfully\n{datetime.datetime.now().strftime("%H:%M %d/%m/%Y")}",
            )
        except:
            pass


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup_notify)
