from aiogram import Bot

from database.models import OrderFile
from utils.order_data import get_answers
from catalog import (
    JOURNAL_SUBCATEGORIES, JOURNAL_ARTICLES,
    CALENDAR_TYPES, CALENDAR_DESIGNS, CALENDAR_PERIODS,
)
from config import ADMIN_ID


async def send_order_report(bot: Bot, order):
    client = order.client
    answers = get_answers(order)
    files = list(OrderFile.select().where(OrderFile.order == order))

    lines = [
        "🆕 Нове замовлення",
        f"Клієнт: {client.full_name or '—'}",
        f"Телефон: {client.phone or '—'}",
        f"Telegram ID: {client.telegram_id}",
        f"Продукт: {'Журнал' if order.product_type == 'journal' else 'Календар'}",
    ]

    if order.product_type == "journal":
        lines.append(f"Підкатегорія: {JOURNAL_SUBCATEGORIES.get(order.subcategory, order.subcategory)}")
        lines.append(f"Кількість сторінок: {answers.get('pages', '—')}")
        articles = answers.get("selected_articles", [])
        lines.append(f"Статті: {', '.join(JOURNAL_ARTICLES.get(a, a) for a in articles) or '—'}")
    else:
        lines.append(f"Тип: {CALENDAR_TYPES.get(order.subcategory, order.subcategory)}")
        lines.append(f"Дизайн: {CALENDAR_DESIGNS.get(answers.get('design'), '—')}")
        lines.append(f"Період: {CALENDAR_PERIODS.get(answers.get('period'), '—')}")

    lines.append(f"\nФайлів надіслано: {len(files)}")

    await bot.send_message(ADMIN_ID, "\n".join(lines))

    for f in files:
        if not f.file_id:
            continue
        caption = f.purpose + (f" — {f.caption}" if f.caption else "")
        try:
            await bot.send_photo(ADMIN_ID, f.file_id, caption=caption)
        except Exception:
            await bot.send_document(ADMIN_ID, f.file_id, caption=caption)
