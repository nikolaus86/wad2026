from fastapi import FastAPI
from typing import Annotated
from fastapi import Query, Path
from enum import StrEnum

app = FastAPI()



async def get_tasks_from_db(task_id: int = None, order_by: str = None, status: list = None):
    tasks = [
        {
            "id": 1,
            "title": "Задача №1",
            "description": "Написать отчет",
            "deadline": "2025-09-18 23:59:59",
            "priority": 3,
            "status": "in_progress"
        },
        {
            "id": 2,
            "title": "Задача №2",
            "description": "Зарелизить фичу",
            "deadline": "2025-09-17 23:59:59",
            "priority": 1,
            "status": "new"
        },
        {
            "id": 3,
            "title": "Задача №3",
            "description": "Написать пост мортем",
            "deadline": "2025-09-20 23:59:59",
            "priority": 2,
            "status": "new"
        },
        {
            "id": 4,
            "title": "Задача №4",
            "description": "Пофиксить баг",
            "deadline": "2025-09-18 18:59:59",
            "priority": 4,
            "status": "in_progress"
        },
        {
            "id": 5,
            "title": "Задача №5",
            "description": "Актуализировать документацию",
            "deadline": "2025-09-18 18:59:59",
            "priority": 1,
            "status": "in_progress"
        }
    ]

    if task_id:
        for task in tasks:
            if task["id"] == task_id:
                return task
        return {}
    
    if status:
        tasks = [task for task in tasks if task["status"] in status]
    
    if order_by:
        tasks.sort(key=lambda task: task[order_by])

    return tasks

class Status(StrEnum):
    new = "new"
    in_progress = "in_progress"

@app.get("/tasks/")
async def get_tasks(order_by: str = None, status: Annotated[list[Status], Query()] = None):
    return await get_tasks_from_db(order_by=order_by, status=status)


@app.get("/tasks/count")
async def get_tasks_count():
    tasks = await get_tasks_from_db()
    return len(tasks)

@app.get("/tasks/{task_id}")
async def get_task(task_id: Annotated[int, Path(gt=0, le=1000)]):
    task = await get_tasks_from_db(task_id)
    return task

