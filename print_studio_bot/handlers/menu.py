from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "product_journal")
async def choose_journal(callback: CallbackQuery):
    await callback.message.answer(
        "📖 Ви обрали Журнал.\n(Вибір підкатегорії буде додано на наступному етапі)"
    )
    await callback.answer()


@router.callback_query(F.data == "product_calendar")
async def choose_calendar(callback: CallbackQuery):
    await callback.message.answer(
        "📅 Ви обрали Календар.\n(Вибір типу календаря буде додано на наступному етапі)"
    )
    await callback.answer()
