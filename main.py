from typing import Annotated
from pydantic import BaseModel, Field, HttpUrl, field_validator
from fastapi import FastAPI, Path, Query, Body, Cookie,Header, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.exceptions import RequestValidationError
from uuid import UUID
from datetime import datetime, time, timedelta
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


app = FastAPI(
    title="FastAPI Tutorial",
    description="A comprehensive FastAPI tutorial with various endpoint examples",
    version="1.0.0",
    tags=[
        {"name": "items", "description": "Operations with items - CRUD operations for managing items"},
        {"name": "files", "description": "File upload and management operations"},
        {"name": "users", "description": "User-related operations"},
        {"name": "offers", "description": "Offer and pricing operations"},
        {"name": "images", "description": "Image handling operations"},
        {"name": "exceptions", "description": "Exception handling examples"},
        {"name": "utilities", "description": "Utility and helper endpoints"}
    ]
)


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


@app.post(
    "/items/",
    response_model=Item,
    summary="Create an item",
    response_description="The created item",
)
async def create_item(item: Item):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    return item

@app.put("/items/{item_id}", tags=["items"])
async def update_item(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    item: Item,
    user: User,
    importance: Annotated[int, Body(gt=0, lt=6, description="The importance of the item",
    examples=[
        {"importance": 345},
    ])],
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
@app.put("/items/item2/{item_id}", tags=["items"])
async def update_item2(item_id: int, 
item:Annotated[Item2, Body(openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },)] ):
    result = {"item_id": item_id, "item": item}
    return result


# body fields

class Item3(BaseModel):
    name: str = Field(min_length=3, max_length=15)
    description: str | None = Field(
        default=None,
        title="The description of the item",
        max_length=300,
        examples=[
            {"description": "A very nice item"},
         ]
    )
    price: float = Field(gt=0, description="The price of the item")
    tax: float | None = None


@app.put("/items/item3/{item_id}", tags=["items"])
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

@app.put("/items/item4/{item_id}", tags=["items"])
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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "The Foo fighters",
                    "price": 42.0,
                    "images": [
                        {
                            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
                            "name": "The logo of the project"
                        }
                    ]
                }
            ]
        }
    }

class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items:list[Item5]
@app.put("/items/item5/{item_id}", tags=["items"])
async def update_item5(item_id: int, item: Item5):
    result = {"item_id": item_id, "item": item}
    return result

@app.post("/offers", tags=["offers"])
async def create_offer(offer: Offer):
    return offer

# Bodies of pure lists

@app.post("/images/multiple", tags=["images"])
async def create_multiple_images(images: list[Image]):

    return images

@app.post("/index-weights/", tags=["utilities"])
async def create_index_weights(weights: dict[int, float]):
    return weights

# using more data types
@app.put("/items/item6/{item_id}", tags=["items"])
async def read_items(
    item_id: UUID,
    start_datetime:Annotated[datetime,Body()],
    end_datetime:Annotated[datetime,Body()],
    process_after:Annotated[timedelta,Body()],
    repeat_at:Annotated[time|None,Body()]=None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }



@app.get("/items1/", tags=["utilities"])
async def read_items1(ads_id:Annotated[str|None,Cookie()]=None):
    print(ads_id)
    return {"ads_id": ads_id}


@app.get("/items2/", tags=["utilities"])
async def read_items2(
    user_agent:Annotated[str|None,Header(convert_underscores=True)]=None
):
    return {"user_agent": user_agent}


## file upload
@app.post("/files1/", tags=["files"])
async def create_file(file:bytes=File(...)):
    return {
        "file_size": len(file)
    }


@app.post("/uploadfile1/", tags=["files"])
async def create_upload_file(file:UploadFile=File()):
    return {
        "filename": file.filename,
        "content_type": file.content_type,
    }
# using annotation 
@app.post("/files2/", tags=["files"])
async def create_files2(
    file:Annotated[bytes,File()],
):
    return {
        "file_size": len(file),
    }

@app.post("/uploadfile2/", tags=["files"])
async def create_upload_file2(
    file:Annotated[UploadFile,File()],
):
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size": len(await file.read()),
        "file_content": await file.read(),
        "file_content_type": file.content_type,
        "file_content_length": len(await file.read()),
    }




@app.get("/", tags=["utilities"])
def main():
    content = """
        <body>
        <form action="/files/" enctype="multipart/form-data" method="post">
        <input name="files" type="file" multiple>
        <input type="submit">
        </form>
        <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
        <input name="files" type="file" multiple>
        <input type="submit">
        </form>
        </body>
        """
    return HTMLResponse(content=content)

@app.post("/files4", tags=["files"])
async def create_files4(
    file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File(alias="fileb2")],
    token: Annotated[str, Form(alias="token2")],
):
    return {
        "file_size": len(file),
        "fileb_content_type": fileb.content_type,
        "token": token,
    }


# exampl to test Exception handling
items = {"foo": "The Foo fighters"}

@app.get("/read_items6/{item_id}", tags=["exceptions"])
async def read_items6(item_id:str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found",
        headers={"X-Error": "There goes my error"},
        )
    return {"item": items[item_id]}


class UnicornException(Exception):
    def __init__(self, name:str):
        self.name = name

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


@app.get("/unicorns/{name}", tags=["exceptions"])
async def read_unicorn(name:str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)

@app.get("/items8/{item_id}", tags=["exceptions"],deprecated=True)
async def read_item8(item_id: int):
    """Endpoint to demonstrate raising an HTTPException for a specific item_id.

    Args:
        item_id (int): The ID of the item to retrieve.

    Returns:
        dict: A dictionary containing the item_id if no exception is raised.

    Raises:
        HTTPException: If item_id is 3, returns a 418 status code with a custom message.
    """
    if item_id == 3:
        raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
    return {"item_id": item_id}