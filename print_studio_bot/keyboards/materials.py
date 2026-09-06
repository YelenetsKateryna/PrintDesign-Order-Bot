from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def content_done_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="✅ Готово", callback_data="content_photos_done")]]
    )


def article_material_skip_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⏭ Пропустити", callback_data="skip_article_material")]]
    )
