from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from database.models import Order

router = Router()


def cancel_order_in_db(order_id):
    """Mark the order as cancelled without duplicating logic across handlers."""
    if not order_id:
        return False

    order = Order.get_or_none(Order.id == order_id)
    if order:
        order.status = "cancelled"
        order.save()
        return True

    return False


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data.get("order_id")

    cancel_order_in_db(order_id)
    await state.clear()
    await message.answer(
        "Замовлення скасовано ❌\nЩоб почати нове замовлення, натисніть /start.",
        reply_markup=ReplyKeyboardRemove(),
    )
