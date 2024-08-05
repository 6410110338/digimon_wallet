from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select

from .merchants import DBMerchant  # Import โมดูลที่เกี่ยวข้อง
from .wallets import DBWallet
from .transactions import DBTransaction


class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: Optional[str] = None
    price: float = 0.00
    tax: Optional[float] = None
    merchant_id: Optional[int] = None


class CreatedItem(BaseItem):
    pass


class UpdatedItem(BaseItem):
    pass


class Item(BaseItem):
    id: int
    merchant_id: int


class DBItem(Item, SQLModel, table=True):
    __tablename__ = "item"
    id: Optional[int] = Field(default=None, primary_key=True)
    merchant_id: Optional[int] = Field(default=None, foreign_key="merchant.id")


class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[Item]
    page: int
    page_size: int
    size_per_page: int
