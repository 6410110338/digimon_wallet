from typing import Optional, List

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, Relationship

from . import users


class BaseMerchant(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: Optional[str] = None
    tax_id: Optional[str] = None
    user_id: Optional[int] = 0


class CreatedMerchant(BaseMerchant):
    pass


class UpdatedMerchant(BaseMerchant):
    pass


class Merchant(BaseMerchant):
    id: int


class DBMerchant(SQLModel, BaseMerchant, table=True):
    __tablename__ = "merchants"
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(default=None, foreign_key="users.id")
    user: Optional[users.DBUser] = Relationship()


class MerchantList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    merchants: List[Merchant]
    page: int
    page_size: int
    size_per_page: int
