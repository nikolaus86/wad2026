import json
from schemas import Task

async def fetch_data() -> list[dict]:
    with open("tasks.json", encoding="utf-8") as file:
        return json.load(file)

async def insert_data(task: dict):
    tasks = await fetch_data()
    tasks.append(task.dict())
    with open("tasks.json", "w", encoding="utf-8") as file:
        return json.dump(tasks, file)

async def get_tasks_from_db(task_id: int = None, order_by: str = None, status: list = None):
    tasks = await fetch_data()

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