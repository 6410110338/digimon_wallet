from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select, Relationship

from . import users
from . import merchants


class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: Optional[str] = None
    price: float = 0.12
    tax: Optional[float] = None
    merchant_id: Optional[int] = None
    user_id: Optional[int] = 1


class CreatedItem(BaseItem):
    pass


class UpdatedItem(BaseItem):
    pass


class Item(BaseItem):
    id: int
    merchant_id: int
    # merchant: Optional[merchants.Merchant] = None


class DBItem(SQLModel, BaseItem, table=True):
    __tablename__ = "items"
    id: Optional[int] = Field(default=None, primary_key=True)
    merchant_id: int = Field(default=None, foreign_key="merchants.id")
    merchant: Optional[merchants.DBMerchant] = Relationship()

    user_id: int = Field(default=None, foreign_key="users.id")
    user: Optional[users.DBUser] = Relationship()


class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[Item]
    page: int
    page_count: int
    size_per_page: int
