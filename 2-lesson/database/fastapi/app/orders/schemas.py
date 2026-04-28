from pydantic import BaseModel, ConfigDict

class OrderBase(BaseModel):
    name: str
    description: str
    price: int

class OrderCreate(OrderBase):
    pass

class OrderRead(OrderBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

    