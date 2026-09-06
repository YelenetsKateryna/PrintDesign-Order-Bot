from database.models import OrderFile
from utils.order_data import get_answers


def check_journal_completeness(order) -> dict:
    critical = []
    warnings = []

    files = list(OrderFile.select().where(OrderFile.order == order))
    purposes = [f.purpose for f in files]

    if "cover_photo" not in purposes:
        critical.append("фото передньої обкладинки")
    if "back_cover_photo" not in purposes:
        critical.append("фото зворотної обкладинки")

    content_count = purposes.count("content_photo")
    if content_count < 3:
        warnings.append(f"мало фото для сторінок (наявно {content_count}, бажано від 3)")

    answers = get_answers(order)
    selected_articles = answers.get("selected_articles", [])
    provided_articles = {
        f.caption.split(":")[0] for f in files if f.purpose == "article_material" and f.caption
    }
    missing_articles = [a for a in selected_articles if a not in provided_articles]
    if missing_articles:
        warnings.append(f"немає матеріалу для {len(missing_articles)} обраних статей")

    return {"critical": critical, "warnings": warnings}


def check_calendar_completeness(order) -> dict:
    critical = []
    files = list(
        OrderFile.select().where(OrderFile.order == order, OrderFile.purpose == "calendar_photo")
    )
    if not files:
        critical.append("фото для календаря")

    return {"critical": critical, "warnings": []}
