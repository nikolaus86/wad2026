from fastapi import APIRouter
from sqlalchemy import select
from ..database import SessionDep
from .schemas import OrderRead, OrderCreate
from .models import Order

router = APIRouter()

@router.post("/", response_model=OrderRead)
async def create_order(order: OrderCreate, db: SessionDep):
    new_order = Order(**order.model_dump())
    db.add(new_order)
    await db.commit()
    # for getting id of new order
    await db.refresh(new_order)

    return new_order

@router.get("/", response_model=list[OrderRead])
async def get_orders(db: SessionDep):
    orders = await db.execute(select(Order))
    return orders.scalars().all()


