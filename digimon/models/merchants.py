from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select

# Import โมดูลที่เกี่ยวข้องภายในโปรเจกต์
from . import items
from . import wallets
from . import transactions

# Base model สำหรับ Merchant
class BaseMerchant(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: Optional[str] = None
    merchant_type: str
    location: str

# Model สำหรับสร้าง Merchant ใหม่
class CreatedMerchant(BaseMerchant):
    pass

# Model สำหรับอัปเดตข้อมูล Merchant
class UpdatedMerchant(BaseMerchant):
    pass

# Model สำหรับข้อมูล Merchant พร้อม ID
class Merchant(BaseMerchant):
    id: int

# Model สำหรับตารางในฐานข้อมูล
class DBMerchant(SQLModel, table=True):
    __tablename__ = "merchant"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    merchant_type: str
    location: str

# Model สำหรับรายการ Merchant พร้อม pagination
class MerchantList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    merchants: List[Merchant]
    page: int
    page_size: int
    size_per_page: int
