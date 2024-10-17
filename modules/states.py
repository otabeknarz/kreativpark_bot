from aiogram.filters.state import State, StatesGroup


class RegistrationState(StatesGroup):
    name = State()
    passport_data = State()
    phone_number = State()


class SendPostState(StatesGroup):
    post = State()


class LoginState(StatesGroup):
    purpose = State()
