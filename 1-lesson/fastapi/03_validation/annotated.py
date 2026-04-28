from fastapi import FastAPI, Path
from typing import Annotated

app = FastAPI()

@app.get("/items/count")
def read_item_count():
    return {"count": 100}

@app.get("/items/{item_id}")
def read_item(item_id: Annotated[int, Path(gt=0, le=1000)]):
    return {"item_id": item_id}

