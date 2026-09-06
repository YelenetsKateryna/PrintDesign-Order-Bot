from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models import Order
from utils.report import send_order_report

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


@router.callback_query(F.data == "ask_admin")
async def ask_admin(callback: CallbackQuery):
    await callback.message.answer(
        "Ваше питання передано адміністратору. Очікуйте на відповідь."
    )
    await callback.answer()
