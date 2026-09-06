from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.journal import start_journal_flow
from handlers.calendar import start_calendar_flow

router = Router()


@router.callback_query(F.data == "product_journal")
async def choose_journal(callback: CallbackQuery, state: FSMContext):
    await start_journal_flow(callback, state)
    await callback.answer()


@router.callback_query(F.data == "product_calendar")
async def choose_calendar(callback: CallbackQuery, state: FSMContext):
    await start_calendar_flow(callback, state)
    await callback.answer()
