from typing import Annotated
from pydantic import BaseModel
from fastapi import FastAPI, Path, Query
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


# using mix of path and query parameters 

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

class User(BaseModel):
    username: str
    full_name: str | None = None

@app.put("/items/{item_id}")
async def update_item(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    item: Item,
    user: User,
    q: Annotated[str | None, Query(min_length=3, max_length=50)] = None
):
    result = {"item_id": item_id, "item": item}
    if q:
        result.update({"q": q})
    if user:
        result.update({"user": user})
    return result