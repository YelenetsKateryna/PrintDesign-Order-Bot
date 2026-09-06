from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from database.models import Order

router = Router()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data.get("order_id")

    if order_id:
        order = Order.get_or_none(Order.id == order_id)
        if order:
            order.status = "cancelled"
            order.save()

    await state.clear()
    await message.answer(
        "Замовлення скасовано ❌\nЩоб почати нове замовлення, натисніть /start.",
        reply_markup=ReplyKeyboardRemove(),
    )
