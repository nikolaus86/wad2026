from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ShipmentBase(BaseModel):
    description: str
    dt: datetime

class ShipmentCreate(ShipmentBase):
    pass

class ShipmentRead(ShipmentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)