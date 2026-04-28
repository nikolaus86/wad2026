from enum import StrEnum
from pydantic import BaseModel


class Status(StrEnum):
    new = "new"
    in_progress = "in_progress"


class Task(BaseModel):
    id: int
    title: str
    description: str
    deadline: str
    priority: int
    status: str


    