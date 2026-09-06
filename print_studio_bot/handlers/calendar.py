from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database.models import Client, Order, OrderFile
from states.calendar import CalendarOrder
from catalog import CALENDAR_TYPES, CALENDAR_DESIGNS, CALENDAR_PERIODS
from keyboards.calendar import (
    calendar_type_keyboard, calendar_design_keyboard,
    calendar_period_keyboard, calendar_photo_done_keyboard,
)
from keyboards.completeness import completeness_keyboard, confirm_keyboard
from utils.order_data import get_answers, set_answers
from utils.validators import check_calendar_completeness

router = Router()


async def start_calendar_flow(callback: CallbackQuery, state: FSMContext):
    """Викликається з головного меню при виборі Календаря."""
    client = Client.get(Client.telegram_id == callback.from_user.id)
    order = Order.create(client=client, product_type="calendar")
    await state.update_data(order_id=order.id)
    await state.set_state(CalendarOrder.choosing_type)
    await callback.message.answer("Оберіть тип календаря:", reply_markup=calendar_type_keyboard())


@router.callback_query(CalendarOrder.choosing_type, F.data.startswith("cal_type:"))
async def choose_type(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    order.subcategory = key
    order.save()

    await state.set_state(CalendarOrder.choosing_design)
    await callback.message.answer(
        f"Обрано: {CALENDAR_TYPES[key]}\n\nОберіть варіант дизайну:",
        reply_markup=calendar_design_keyboard(),
    )
    await callback.answer()


@router.callback_query(CalendarOrder.choosing_design, F.data == "cal_back:type")
async def back_to_type(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CalendarOrder.choosing_type)
    await callback.message.answer("Оберіть тип календаря:", reply_markup=calendar_type_keyboard())
    await callback.answer()


@router.callback_query(CalendarOrder.choosing_design, F.data.startswith("cal_design:"))
async def choose_design(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    answers = get_answers(order)
    answers["design"] = key
    set_answers(order, answers)

    await state.set_state(CalendarOrder.choosing_period)
    await callback.message.answer(
        f"Обрано: {CALENDAR_DESIGNS[key]}\n\nОберіть період:",
        reply_markup=calendar_period_keyboard(),
    )
    await callback.answer()


@router.callback_query(CalendarOrder.choosing_period, F.data == "cal_back:design")
async def back_to_design(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CalendarOrder.choosing_design)
    await callback.message.answer("Оберіть варіант дизайну:", reply_markup=calendar_design_keyboard())
    await callback.answer()


@router.callback_query(CalendarOrder.choosing_period, F.data.startswith("cal_period:"))
async def choose_period(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    answers = get_answers(order)
    answers["period"] = key
    set_answers(order, answers)

    await state.set_state(CalendarOrder.collecting_photo)
    await callback.message.answer(
        f"Обрано: {CALENDAR_PERIODS[key]}\n\n"
        "Надішліть фото для календаря. Коли завершите — натисніть «Готово».",
        reply_markup=calendar_photo_done_keyboard(),
    )
    await callback.answer()


@router.message(CalendarOrder.collecting_photo, F.photo)
async def collect_calendar_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    OrderFile.create(order=order, file_id=message.photo[-1].file_id, purpose="calendar_photo")
    await message.answer("Фото додано ✅ (надішліть ще або натисніть «Готово»)")


@router.callback_query(CalendarOrder.collecting_photo, F.data == "calendar_photos_done")
async def calendar_photos_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    await state.set_state(CalendarOrder.review)

    result = check_calendar_completeness(order)
    critical = result["critical"]

    text = "🔍 Перевірка комплекту матеріалів:\n\n"
    if critical:
        text += "❌ Критично відсутнє:\n" + "\n".join(f"— {c}" for c in critical)
    else:
        text += "Усі матеріали на місці ✅"

    await callback.message.answer(text, reply_markup=completeness_keyboard(has_critical=bool(critical)))
    await callback.answer()


@router.callback_query(CalendarOrder.review, F.data == "add_materials")
async def add_more_calendar_photos(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CalendarOrder.collecting_photo)
    await callback.message.answer(
        "Надішліть додаткові фото для календаря. Коли завершите — натисніть «Готово».",
        reply_markup=calendar_photo_done_keyboard(),
    )
    await callback.answer()


@router.callback_query(CalendarOrder.review, F.data == "continue_warning")
async def calendar_continue_warning(callback: CallbackQuery, state: FSMContext):
    await _show_calendar_confirmation(callback.message, state)
    await callback.answer()


async def _show_calendar_confirmation(message: Message, state: FSMContext):
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    answers = get_answers(order)

    summary = (
        "📦 Підсумок замовлення:\n\n"
        f"Продукт: Календар ({CALENDAR_TYPES.get(order.subcategory, order.subcategory)})\n"
        f"Дизайн: {CALENDAR_DESIGNS.get(answers.get('design'), '—')}\n"
        f"Період: {CALENDAR_PERIODS.get(answers.get('period'), '—')}\n\n"
        "Підтвердіть замовлення для передачі дизайнеру:"
    )
    await message.answer(summary, reply_markup=confirm_keyboard())
