from fastapi import APIRouter
from sqlalchemy import select
from ..database import SessionDep
from .schemas import ShipmentRead, ShipmentCreate
from .models import Shipment

router = APIRouter()

@router.post("/", response_model=ShipmentRead)
async def create_shipment(shipment: ShipmentCreate, db: SessionDep):


@router.get("/", response_model=list[ShipmentRead])
async def get_shipments(db: SessionDep):
    shipments = await db.execute(select(Shipment))
    return shipments.scalars().all()