from aiogram.fsm.state import State, StatesGroup


class JournalOrder(StatesGroup):
    choosing_subcategory = State()
    choosing_pages = State()
    choosing_articles = State()
    collecting_cover = State()
    collecting_back_cover = State()
    collecting_content = State()
    collecting_article_material = State()
    review = State()
