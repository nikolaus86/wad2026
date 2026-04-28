from ..database import Base
from sqlalchemy import Column, Integer, String, DateTime

class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=True)
    dt = Column(DateTime, nullable=False)
    