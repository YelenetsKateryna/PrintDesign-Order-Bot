from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_terms = State()
    waiting_name = State()
    waiting_phone = State()
