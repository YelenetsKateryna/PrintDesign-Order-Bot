from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from catalog import CALENDAR_TYPES, CALENDAR_DESIGNS, CALENDAR_PERIODS
from keyboards.navigation import nav_row


def calendar_type_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=v, callback_data=f"cal_type:{k}")] for k, v in CALENDAR_TYPES.items()]
    buttons.append(nav_row())  # перший крок — лише скасування
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def calendar_design_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=v, callback_data=f"cal_design:{k}")] for k, v in CALENDAR_DESIGNS.items()]
    buttons.append(nav_row("cal_back:type"))
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def calendar_period_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=v, callback_data=f"cal_period:{k}")] for k, v in CALENDAR_PERIODS.items()]
    buttons.append(nav_row("cal_back:design"))
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def calendar_photo_done_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="✅ Готово", callback_data="calendar_photos_done")]]
    buttons.append(nav_row())
    return InlineKeyboardMarkup(inline_keyboard=buttons)
