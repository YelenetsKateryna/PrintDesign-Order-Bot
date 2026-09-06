import asyncio
import os
import sys
import unittest
from unittest.mock import patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "print_studio_bot"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from print_studio_bot.utils.report import send_order_report


class FakeClient:
    def __init__(self):
        self.full_name = "Маряни Симоненко"
        self.phone = "+380954327837"
        self.telegram_id = 123456


class FakeOrder:
    def __init__(self):
        self.client = FakeClient()
        self.product_type = "journal"
        self.subcategory = "gift"


class FakeFile:
    def __init__(self, file_id, purpose, caption=None):
        self.file_id = file_id
        self.purpose = purpose
        self.caption = caption


class FakeBot:
    def __init__(self):
        self.messages = []
        self.photos = []
        self.documents = []

    async def send_message(self, chat_id, text):
        self.messages.append((chat_id, text))

    async def send_photo(self, chat_id, file_id, caption=None):
        self.photos.append((chat_id, file_id, caption))

    async def send_document(self, chat_id, file_id, caption=None):
        self.documents.append((chat_id, file_id, caption))


class FakeQuery:
    def __init__(self, results):
        self.results = results

    def where(self, *args, **kwargs):
        return self.results


class SendOrderReportTests(unittest.TestCase):
    def test_text_material_without_file_id_is_sent_to_admin(self):
        order = FakeOrder()
        bot = FakeBot()
        article_file = FakeFile("", "article_material", "article_01: текст для статті")

        with patch("utils.report.ADMIN_ID", 999999), \
             patch("utils.report.get_answers", return_value={
                 "pages": 12,
                 "selected_articles": ["article_01"],
             }), \
             patch("utils.report.OrderFile.select", return_value=FakeQuery([article_file])):
            asyncio.run(send_order_report(bot, order))

        self.assertTrue(any("📝 article material" in text and "article_01: текст для статті" in text for _, text in bot.messages))
        self.assertEqual(len(bot.photos), 0)
        self.assertEqual(len(bot.documents), 0)

    def test_photo_material_still_uses_photo_send_path(self):
        order = FakeOrder()
        bot = FakeBot()
        photo = FakeFile("telegram_photo_id", "cover_photo", "передня обкладинка")

        with patch("utils.report.ADMIN_ID", 999999), \
             patch("utils.report.get_answers", return_value={
                 "pages": 12,
                 "selected_articles": ["article_01"],
             }), \
             patch("utils.report.OrderFile.select", return_value=FakeQuery([photo])):
            asyncio.run(send_order_report(bot, order))

        self.assertTrue(any(file_id == "telegram_photo_id" for _, file_id, _ in bot.photos))


if __name__ == "__main__":
    unittest.main()
