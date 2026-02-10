import src.utils.syspath
import random
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from faker import Faker
from pydantic import BaseModel

router = APIRouter()
faker = Faker()

class Item(BaseModel):
    id: str | None = None # Allow id to be None when submitting
    name: str

@router.get("/all", response_class=JSONResponse)
async def get_all(request: Request):
    # Generate random data
    items = [
        {"id": i, "name": faker.name()}
        for i in range(1, random.randint(5, 15))  # Generate 5 to 15 items
    ]
    return JSONResponse(items)


@router.post("/add", response_class=JSONResponse)
async def post_add(new_item: Item):
    return JSONResponse(content=new_item.dict(), status_code=201)
