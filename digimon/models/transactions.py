from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select

# Import โมดูลที่เกี่ยวข้องภายในโปรเจกต์
from . import items, merchants, wallets

# Base model สำหรับ Transaction
class BaseTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sender: str
    receiver: str
    amount: float

# Model สำหรับสร้าง Transaction ใหม่
class CreatedTransaction(BaseTransaction):
    pass

# Model สำหรับอัปเดตข้อมูล Transaction
class UpdatedTransaction(BaseTransaction):
    pass

# Model สำหรับข้อมูล Transaction พร้อม ID
class Transaction(BaseTransaction):
    id: int

# Model สำหรับตารางในฐานข้อมูล
class DBTransaction(SQLModel, table=True):
    __tablename__ = "transaction"
    id: Optional[int] = Field(default=None, primary_key=True)
    sender: str
    receiver: str
    amount: float

# Model สำหรับรายการ Transaction พร้อม pagination
class TransactionList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    transactions: List[Transaction]
    page: int
    page_size: int
    total_items: int
