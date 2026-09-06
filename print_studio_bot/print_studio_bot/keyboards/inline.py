from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 Журнал", callback_data="product_journal")],
            [InlineKeyboardButton(text="📅 Календар", callback_data="product_calendar")],
        ]
    )
