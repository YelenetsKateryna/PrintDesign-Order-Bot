from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from catalog import JOURNAL_SUBCATEGORIES, JOURNAL_PAGE_OPTIONS, JOURNAL_ARTICLES


def subcategory_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=v, callback_data=f"journal_sub:{k}")]
        for k, v in JOURNAL_SUBCATEGORIES.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def pages_keyboard() -> InlineKeyboardMarkup:
    row = [
        InlineKeyboardButton(text=f"{p} сторінок", callback_data=f"journal_pages:{p}")
        for p in JOURNAL_PAGE_OPTIONS
    ]
    rows = [row[i:i + 2] for i in range(0, len(row), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def articles_keyboard(selected: set) -> InlineKeyboardMarkup:
    buttons = []
    for key, title in JOURNAL_ARTICLES.items():
        mark = "✅ " if key in selected else ""
        buttons.append([InlineKeyboardButton(text=f"{mark}{title}", callback_data=f"journal_article:{key}")])
    buttons.append([InlineKeyboardButton(text="➡️ Готово", callback_data="journal_articles_done")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
