from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from catalog import CALENDAR_TYPES, CALENDAR_DESIGNS, CALENDAR_PERIODS


def calendar_type_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=v, callback_data=f"cal_type:{k}")] for k, v in CALENDAR_TYPES.items()]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def calendar_design_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=v, callback_data=f"cal_design:{k}")] for k, v in CALENDAR_DESIGNS.items()]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def calendar_period_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=v, callback_data=f"cal_period:{k}")] for k, v in CALENDAR_PERIODS.items()]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def calendar_photo_done_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="✅ Готово", callback_data="calendar_photos_done")]]
    )
