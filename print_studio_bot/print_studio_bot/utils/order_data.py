import json


def get_answers(order) -> dict:
    return json.loads(order.answers_json or "{}")


def set_answers(order, data: dict):
    order.answers_json = json.dumps(data, ensure_ascii=False)
    order.save()
