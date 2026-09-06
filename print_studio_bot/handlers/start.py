from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database.models import Client
from states.registration import Registration
from keyboards.reply import terms_keyboard, phone_keyboard, remove_keyboard
from keyboards.inline import main_menu_keyboard

router = Router()

TERMS_TEXT = (
    "📋 Умови співпраці\n\n"
    "1. Студія виконує друковану продукцію за наданими клієнтом матеріалами.\n"
    "2. Бот не займається дизайном та не оцінює якість фотографій.\n"
    "3. Після формування замовлення внесення змін узгоджується з менеджером.\n"
    "4. Термін виконання розраховується після підтвердження повного комплекту матеріалів.\n\n"
    "Для продовження підтвердіть згоду з умовами."
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    client, _ = Client.get_or_create(telegram_id=message.from_user.id)

    if client.terms_accepted and client.full_name and client.phone:
        await message.answer(
            "Вітаємо знову! Оберіть продукт для замовлення:",
            reply_markup=main_menu_keyboard(),
        )
        return

    await state.set_state(Registration.waiting_terms)
    await message.answer(TERMS_TEXT, reply_markup=terms_keyboard())


@router.message(Registration.waiting_terms, F.text == "✅ Погоджуюсь")
async def terms_accepted(message: Message, state: FSMContext):
    Client.update(terms_accepted=True).where(
        Client.telegram_id == message.from_user.id
    ).execute()

    await state.set_state(Registration.waiting_name)
    await message.answer("Як до вас звертатися? Введіть ім'я:", reply_markup=remove_keyboard())


@router.message(Registration.waiting_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(Registration.waiting_phone)
    await message.answer(
        "Дякуємо! Тепер поділіться номером телефону:",
        reply_markup=phone_keyboard(),
    )


@router.message(Registration.waiting_phone, F.contact)
async def get_phone_contact(message: Message, state: FSMContext):
    await _save_phone(message, state, message.contact.phone_number)


@router.message(Registration.waiting_phone, F.text)
async def get_phone_text(message: Message, state: FSMContext):
    await _save_phone(message, state, message.text)


async def _save_phone(message: Message, state: FSMContext, phone: str):
    data = await state.get_data()

    Client.update(
        full_name=data.get("full_name"),
        phone=phone,
    ).where(Client.telegram_id == message.from_user.id).execute()

    await state.clear()
    await message.answer(
        "Реєстрацію завершено ✅\nОберіть продукт для замовлення:",
        reply_markup=main_menu_keyboard(),
    )
