from peewee import (
    Model, SqliteDatabase, CharField, BigIntegerField,
    ForeignKeyField, DateTimeField, TextField, BooleanField
)
import datetime

db = SqliteDatabase("studio.db")


class BaseModel(Model):
    class Meta:
        database = db


class Client(BaseModel):
    telegram_id = BigIntegerField(unique=True)
    full_name = CharField(null=True)
    phone = CharField(null=True)
    terms_accepted = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)


class Order(BaseModel):
    client = ForeignKeyField(Client, backref="orders")
    product_type = CharField(null=True)      # journal / calendar
    subcategory = CharField(null=True)       # gift / turnkey / photo / limited / concept ...
    status = CharField(default="draft")      # draft / submitted
    answers_json = TextField(default="{}")   # усі відповіді клієнта (JSON)
    created_at = DateTimeField(default=datetime.datetime.now)


class OrderFile(BaseModel):
    order = ForeignKeyField(Order, backref="files")
    file_id = CharField()                    # telegram file_id
    purpose = CharField()                    # cover_photo / back_cover_photo / content_photo / article_material / calendar_photo / reference
    caption = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)


def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([Client, Order, OrderFile])
