from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select

# Define base item model
class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: Optional[str] = None
    price: float = 0.12
    tax: Optional[float] = None

# Define created item model
class CreatedItem(BaseItem):
    pass

# Define updated item model
class UpdatedItem(BaseItem):
    pass

# Define item model with ID
class Item(BaseItem):
    id: int

# Define database item model
class DBItem(Item, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

# Define item list model for pagination
class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[Item]
    page: int
    page_size: int
    size_per_page: int

# Database connection setup
connect_args = {}
engine = create_engine(
    "postgresql+pg8000://postgres:123456@localhost/digimondb",
    echo=True,
    connect_args=connect_args,
)

# Create database tables
SQLModel.metadata.create_all(engine)

# FastAPI application instance
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/items", response_model=Item)
async def create_item(item: CreatedItem) -> Item:
    dbitem = DBItem(**item.dict())
    with Session(engine) as session:
        session.add(dbitem)
        session.commit()
        session.refresh(dbitem)
    return Item.from_orm(dbitem)

@app.get("/items", response_model=ItemList)
async def read_items(page: int = 1, page_size: int = 10) -> ItemList:
    with Session(engine) as session:
        stmt = select(DBItem).offset((page - 1) * page_size).limit(page_size)
        items = session.exec(stmt).all()
        total_items = session.exec(select(DBItem)).count()  # Count total items for pagination
    return ItemList(items=items, page=page, page_size=page_size, size_per_page=total_items)

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int) -> Item:
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if db_item:
            return Item.from_orm(db_item)
    raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: UpdatedItem) -> Item:
    data = item.dict()
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        for key, value in data.items():
            setattr(db_item, key, value)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
    return Item.from_orm(db_item)

@app.delete("/items/{item_id}")
async def delete_item(item_id: int) -> dict:
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        session.delete(db_item)
        session.commit()
    return {"message": "delete success"}
