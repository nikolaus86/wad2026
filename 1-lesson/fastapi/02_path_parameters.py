from fastapi import FastAPI

app = FastAPI()

@app.get("/items/count")
def read_item_count():
    return {"count": 100}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
