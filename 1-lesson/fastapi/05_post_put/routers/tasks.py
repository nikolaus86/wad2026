from fastapi import APIRouter, Query, Path, status
from schemas import Status
from db import get_tasks_from_db, insert_data
from typing import Annotated
from schemas import Task

router = APIRouter(
    prefix="/tasks",
)

@router.get("/")
async def get_tasks(order_by: str = None, status: Annotated[list[Status], Query()] = None):
    return await get_tasks_from_db(order_by=order_by, status=status)


@router.get("/count")
async def get_tasks_count():
    tasks = await get_tasks_from_db()
    return len(tasks)

@router.get("/{task_id}")
async def get_task(task_id: Annotated[int, Path(gt=0, le=1000)]):
    task = await get_tasks_from_db(task_id)
    return task

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Task)
async def create_task(task: Task):
    await insert_data(task)
    return task

