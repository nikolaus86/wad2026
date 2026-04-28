from fastapi import FastAPI
from fastapi import Depends
from .database import SessionDep, get_db_session
from sqlalchemy import text
from .orders.urls import router as orders_router
from .shipments.urls import router as shipments_router

app = FastAPI()

app.include_router(orders_router, prefix="/orders")
app.include_router(shipments_router, prefix="/shipments")


