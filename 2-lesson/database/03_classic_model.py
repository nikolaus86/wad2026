from sqlalchemy import MetaData, Table, Column, Integer, String

# Контейнер для моделей
metadata_obj = MetaData()

user_table = Table(
    "users",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(30), nullable=False),
    Column("fullname", String, nullable=True),
)

