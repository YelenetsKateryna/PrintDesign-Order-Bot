from aiogram.fsm.state import State, StatesGroup


class CalendarOrder(StatesGroup):
    choosing_type = State()
    choosing_design = State()
    choosing_period = State()
    collecting_photo = State()
    review = State()
