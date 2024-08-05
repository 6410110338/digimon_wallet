from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select

# Import โมดูลที่เกี่ยวข้องภายในโปรเจกต์
from . import items, merchants, transactions

# Base model สำหรับ Wallet
class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    owner: str
    balance: float

# Model สำหรับสร้าง Wallet ใหม่
class CreatedWallet(BaseWallet):
    pass

# Model สำหรับอัปเดตข้อมูล Wallet
class UpdatedWallet(BaseWallet):
    pass

# Model สำหรับข้อมูล Wallet พร้อม ID
class Wallet(BaseWallet):
    id: int

# Model สำหรับตารางในฐานข้อมูล
class DBWallet(SQLModel, table=True):
    __tablename__ = "wallet"
    id: Optional[int] = Field(default=None, primary_key=True)
    owner: str
    balance: float

# Model สำหรับรายการ Wallet พร้อม pagination
class WalletList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    wallets: List[Wallet]
    page: int
    page_size: int
    total_items: int
