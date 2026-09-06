from aiogram.fsm.state import State, StatesGroup


class AdminQuestion(StatesGroup):
    waiting_question = State()
