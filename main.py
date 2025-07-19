from typing import Annotated
from pydantic import BaseModel, Field, HttpUrl, field_validator
from fastapi import FastAPI, Path, Query, Body
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

class Item2(BaseModel):
    name: str
    description: str | None = None
    price: float

@app.put("/items/{item_id}")
async def update_item(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    item: Item,
    user: User,
    importance: Annotated[int, Body(gt=0, lt=6, description="The importance of the item")],
    q: Annotated[str | None, Query(min_length=3, max_length=50)] = None
):
    result = {"item_id": item_id, "item": item}
    if q:
        result.update({"q": q})
    if user:
        result.update({"user": user})
    if importance:
        result.update({"importance": importance})
    return result

# using embed=True to embed the item2 object in the body
@app.put("/items/item2/{item_id}")
async def update_item2(item_id: int, 
item:Annotated[Item2, Body(embed=True)] ):
    result = {"item_id": item_id, "item": item}
    return result


# body fields

class Item3(BaseModel):
    name: str = Field(min_length=3, max_length=15)
    description: str | None = Field(
        default=None,
        title="The description of the item",
        max_length=300
    )
    price: float = Field(gt=0, description="The price of the item")
    tax: float | None = None


@app.put("/items/item3/{item_id}")
async def update_item3(item_id: int, 
    item: Annotated[Item3, Body(embed=True)]):
    result = {"item_id": item_id, "item": item}
    return result


# body nested model
class Item4(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    #tags: list[str] = []
    tags:set[str] = set()

@app.put("/items/item4/{item_id}")
async def update_item4(item_id: int,item: Annotated[Item4, Body(embed=True)]):
    result = {"item_id": item_id, "item": item}
    return result

# submodels in items

class Image(BaseModel):
    url: HttpUrl
    name: str

class Item5(BaseModel):
    name: str
    description: str | None = None
    price: float
    tags: set[str] = set()
    # image: Image | None = None
    images:list[Image] | None = None

class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items:list[Item5]
@app.put("/items/item5/{item_id}")
async def update_item5(item_id: int, item: Item5):
    result = {"item_id": item_id, "item": item}
    return result

@app.post("/offers")
async def create_offer(offer: Offer):
    return offer

# Bodies of pure lists

@app.post("/images/multiple")
async def create_multiple_images(images: list[Image]):

    return images

@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):
    return weights