from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database.models import Client, Order, ClientQuestion
from states.admin_question import AdminQuestion
from config import ADMIN_ID

router = Router()


@router.callback_query(F.data == "ask_admin")
async def ask_admin_start(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    await state.update_data(previous_state=current_state)
    await state.set_state(AdminQuestion.waiting_question)
    await callback.message.answer("Напишіть ваше питання адміністратору:")
    await callback.answer()


@router.message(AdminQuestion.waiting_question, F.text)
async def receive_question(message: Message, state: FSMContext):
    data = await state.get_data()
    client = Client.get(Client.telegram_id == message.from_user.id)
    order_id = data.get("order_id")
    order = Order.get_or_none(Order.id == order_id) if order_id else None

    ClientQuestion.create(client=client, order=order, question_text=message.text)

    await message.bot.send_message(
        ADMIN_ID,
        "❓ Питання від клієнта\n"
        f"Ім'я: {client.full_name or '—'}\n"
        f"Телефон: {client.phone or '—'}\n"
        f"Telegram ID: {client.telegram_id}\n\n"
        f"{message.text}",
    )

    previous_state = data.get("previous_state")
    if previous_state:
        await state.set_state(previous_state)
    else:
        await state.clear()

    await message.answer("Питання передано адміністратору ✅ Очікуйте на відповідь.")
