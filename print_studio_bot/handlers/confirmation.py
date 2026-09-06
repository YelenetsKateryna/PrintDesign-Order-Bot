from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models import Order
from utils.report import send_order_report
from handlers.journal import start_journal_flow
from handlers.calendar import start_calendar_flow
from handlers.cancel import cancel_order_in_db

router = Router()


@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order = Order.get_by_id(data["order_id"])
    order.status = "submitted"
    order.save()

    await send_order_report(callback.bot, order)

    await callback.message.answer(
        "Замовлення передано дизайнеру ✅\nДякуємо! Ми зв'яжемося з вами найближчим часом."
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    """Скасування поточного замовлення (п.10): статус -> cancelled, стан очищено."""
    data = await state.get_data()
    order_id = data.get("order_id")

    cancel_order_in_db(order_id)

    await state.clear()
    await callback.message.answer(
        "Замовлення скасовано ❌\nЩоб почати нове замовлення, натисніть /start."
    )
    await callback.answer()


@router.callback_query(F.data == "edit_order")
async def edit_order(callback: CallbackQuery, state: FSMContext):
    """Редагування замовлення (п.9): поточну чернетку позначаємо cancelled
    і одразу заново запускаємо сценарій того самого продукту, без /start."""
    data = await state.get_data()
    order_id = data.get("order_id")
    order = Order.get_or_none(Order.id == order_id) if order_id else None

    product_type = order.product_type if order else None
    if order:
        order.status = "cancelled"
        order.save()

    await state.clear()

    if product_type == "journal":
        await callback.message.answer("Почнемо оформлення журналу заново.")
        await start_journal_flow(callback, state)
    elif product_type == "calendar":
        await callback.message.answer("Почнемо оформлення календаря заново.")
        await start_calendar_flow(callback, state)
    else:
        await callback.message.answer("Почніть оформлення замовлення знову через /start.")

    await callback.answer()
