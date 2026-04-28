from ..database import Base
from sqlalchemy import Column, Integer, String

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)