from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database.models import Client, Order, OrderFile
from states.journal import JournalOrder
from catalog import JOURNAL_SUBCATEGORIES, JOURNAL_ARTICLES
from keyboards.journal import subcategory_keyboard, pages_keyboard, articles_keyboard
from keyboards.materials import content_done_keyboard, article_material_skip_keyboard
from keyboards.completeness import completeness_keyboard, confirm_keyboard
from utils.order_data import get_answers, set_answers
from utils.validators import check_journal_completeness

router = Router()


async def start_journal_flow(callback: CallbackQuery, state: FSMContext):
    """Викликається з головного меню при виборі Журналу."""
    client = Client.get(Client.telegram_id == callback.from_user.id)
    order = Order.create(client=client, product_type="journal")
    await state.update_data(order_id=order.id)
    await state.set_state(JournalOrder.choosing_subcategory)
    await callback.message.answer("Оберіть вид журналу:", reply_markup=subcategory_keyboard())


@router.callback_query(JournalOrder.choosing_subcategory, F.data.startswith("journal_sub:"))
async def choose_subcategory(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    order.subcategory = key
    order.save()

    await state.set_state(JournalOrder.choosing_pages)
    await callback.message.answer(
        f"Обрано: {JOURNAL_SUBCATEGORIES[key]}\n\nОберіть кількість сторінок:",
        reply_markup=pages_keyboard(),
    )
    await callback.answer()


@router.callback_query(JournalOrder.choosing_pages, F.data.startswith("journal_pages:"))
async def choose_pages(callback: CallbackQuery, state: FSMContext):
    pages = int(callback.data.split(":")[1])
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    answers = get_answers(order)
    answers["pages"] = pages
    answers["selected_articles"] = []
    set_answers(order, answers)

    await state.update_data(selected_articles=[])
    await state.set_state(JournalOrder.choosing_articles)
    await callback.message.answer(
        f"Обрано: {pages} сторінок\n\nОберіть статті для журналу (можна декілька):",
        reply_markup=articles_keyboard(set()),
    )
    await callback.answer()


@router.callback_query(JournalOrder.choosing_articles, F.data.startswith("journal_article:"))
async def toggle_article(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    data = await state.get_data()
    selected = set(data.get("selected_articles", []))

    if key in selected:
        selected.remove(key)
    else:
        selected.add(key)

    await state.update_data(selected_articles=list(selected))
    await callback.message.edit_reply_markup(reply_markup=articles_keyboard(selected))
    await callback.answer()


@router.callback_query(JournalOrder.choosing_articles, F.data == "journal_articles_done")
async def articles_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    selected = data.get("selected_articles", [])

    answers = get_answers(order)
    answers["selected_articles"] = selected
    set_answers(order, answers)

    await state.set_state(JournalOrder.collecting_cover)
    await callback.message.answer(
        "Статті обрано ✅\n\nНадішліть, будь ласка, фото для передньої обкладинки:"
    )
    await callback.answer()


@router.message(JournalOrder.collecting_cover, F.photo)
async def collect_cover(message: Message, state: FSMContext):
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    OrderFile.create(order=order, file_id=message.photo[-1].file_id, purpose="cover_photo")

    await state.set_state(JournalOrder.collecting_back_cover)
    await message.answer("Дякуємо! Тепер надішліть фото для зворотної обкладинки:")


@router.message(JournalOrder.collecting_back_cover, F.photo)
async def collect_back_cover(message: Message, state: FSMContext):
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    OrderFile.create(order=order, file_id=message.photo[-1].file_id, purpose="back_cover_photo")

    await state.set_state(JournalOrder.collecting_content)
    await message.answer(
        "Чудово! Тепер надсилайте фото для сторінок журналу.\n"
        "Коли завершите — натисніть «Готово».",
        reply_markup=content_done_keyboard(),
    )


@router.message(JournalOrder.collecting_content, F.photo)
async def collect_content(message: Message, state: FSMContext):
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    OrderFile.create(order=order, file_id=message.photo[-1].file_id, purpose="content_photo")
    await message.answer("Фото додано ✅ (надішліть ще або натисніть «Готово»)")


@router.callback_query(JournalOrder.collecting_content, F.data == "content_photos_done")
async def content_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    articles = data.get("selected_articles", [])
    await state.update_data(articles_queue=articles, current_article_index=0)

    if articles:
        await state.set_state(JournalOrder.collecting_article_material)
        first_article = JOURNAL_ARTICLES[articles[0]]
        await callback.message.answer(
            f"Тепер надішліть матеріал (текст або файл) для статті «{first_article}»:",
            reply_markup=article_material_skip_keyboard(),
        )
    else:
        await _finish_materials_collection(callback.message, state)

    await callback.answer()


@router.message(JournalOrder.collecting_article_material)
async def collect_article_material(message: Message, state: FSMContext):
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    queue = data.get("articles_queue", [])
    index = data.get("current_article_index", 0)
    article_key = queue[index]

    file_id = None
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id

    OrderFile.create(
        order=order,
        file_id=file_id or "",
        purpose="article_material",
        caption=f"{article_key}: {message.text or message.caption or ''}",
    )

    await _next_article_or_finish(message, state, queue, index + 1)


@router.callback_query(JournalOrder.collecting_article_material, F.data == "skip_article_material")
async def skip_article_material(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    queue = data.get("articles_queue", [])
    index = data.get("current_article_index", 0)
    await callback.answer()
    await _next_article_or_finish(callback.message, state, queue, index + 1)


async def _next_article_or_finish(message: Message, state: FSMContext, queue, next_index):
    if next_index < len(queue):
        await state.update_data(current_article_index=next_index)
        next_article = JOURNAL_ARTICLES[queue[next_index]]
        await message.answer(
            f"Матеріал для статті «{next_article}»:",
            reply_markup=article_material_skip_keyboard(),
        )
    else:
        await _finish_materials_collection(message, state)


async def _finish_materials_collection(message: Message, state: FSMContext):
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    await state.set_state(JournalOrder.review)
    await _show_completeness(message, order)


async def _show_completeness(message: Message, order: Order):
    result = check_journal_completeness(order)
    critical, warnings = result["critical"], result["warnings"]

    text = "🔍 Перевірка комплекту матеріалів:\n\n"
    if critical:
        text += "❌ Критично відсутнє:\n" + "\n".join(f"— {c}" for c in critical) + "\n\n"
    if warnings:
        text += "⚠️ Бажано додати:\n" + "\n".join(f"— {w}" for w in warnings) + "\n\n"
    if not critical and not warnings:
        text += "Усі матеріали на місці ✅"

    await message.answer(text, reply_markup=completeness_keyboard(has_critical=bool(critical)))


@router.callback_query(JournalOrder.review, F.data == "add_materials")
async def add_materials(callback: CallbackQuery, state: FSMContext):
    await state.set_state(JournalOrder.collecting_content)
    await callback.message.answer(
        "Надішліть додаткові фото для сторінок. Коли завершите — натисніть «Готово».",
        reply_markup=content_done_keyboard(),
    )
    await callback.answer()


@router.callback_query(JournalOrder.review, F.data == "continue_warning")
async def continue_with_warning(callback: CallbackQuery, state: FSMContext):
    await _show_confirmation(callback.message, state)
    await callback.answer()


async def _show_confirmation(message: Message, state: FSMContext):
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    answers = get_answers(order)

    summary = (
        "📦 Підсумок замовлення:\n\n"
        f"Продукт: Журнал ({JOURNAL_SUBCATEGORIES.get(order.subcategory, order.subcategory)})\n"
        f"Кількість сторінок: {answers.get('pages')}\n"
        f"Статті: {', '.join(JOURNAL_ARTICLES.get(a, a) for a in answers.get('selected_articles', [])) or '—'}\n\n"
        "Підтвердіть замовлення для передачі дизайнеру:"
    )
    await message.answer(summary, reply_markup=confirm_keyboard())
