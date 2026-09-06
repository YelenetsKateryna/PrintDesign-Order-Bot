from aiogram.types import InlineKeyboardButton


def nav_row(back_callback: str | None = None) -> list[InlineKeyboardButton]:
    """Повертає рядок з кнопками [🔙 Назад] (якщо є попередній крок) та [❌ Скасувати замовлення]."""
    row = []
    if back_callback:
        row.append(InlineKeyboardButton(text="🔙 Назад", callback_data=back_callback))
    row.append(InlineKeyboardButton(text="❌ Скасувати замовлення", callback_data="cancel_order"))
    return row
