from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.navigation import nav_row


def completeness_keyboard(has_critical: bool) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📤 Додати матеріали", callback_data="add_materials")],
        [InlineKeyboardButton(text="💬 Запитати адміністратора", callback_data="ask_admin")],
    ]
    if not has_critical:
        buttons.append(
            [InlineKeyboardButton(text="✅ Продовжити з попередженням", callback_data="continue_warning")]
        )
    buttons.append(nav_row())
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Підтвердити замовлення", callback_data="confirm_order")],
            [InlineKeyboardButton(text="✏️ Змінити дані", callback_data="edit_order")],
            nav_row(),
        ]
    )
