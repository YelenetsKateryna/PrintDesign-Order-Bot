from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.navigation import nav_row


def content_done_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="✅ Готово", callback_data="content_photos_done")]]
    buttons.append(nav_row())
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def article_material_skip_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text="⏭ Пропустити", callback_data="skip_article_material")]]
    buttons.append(nav_row())
    return InlineKeyboardMarkup(inline_keyboard=buttons)
