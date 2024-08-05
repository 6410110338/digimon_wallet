from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session, select

# Import โมดูลที่จำเป็นจากโฟลเดอร์ปัจจุบัน
from .items import DBItem 
from .merchants import DBMerchant
from .wallets import DBWallet
from .transactions import DBTransaction

# กำหนดการตั้งค่าเชื่อมต่อฐานข้อมูล
connect_args = {}

# สร้าง engine สำหรับเชื่อมต่อกับฐานข้อมูล PostgreSQL
engine = create_engine(
    "postgresql+pg8000://postgres:123456@localhost/digimondb",
    echo=True,
    connect_args=connect_args,
)

# ฟังก์ชันสำหรับสร้างตารางในฐานข้อมูล
def init_db():
    SQLModel.metadata.create_all(engine)

# ฟังก์ชันสำหรับการใช้ session ในการเชื่อมต่อฐานข้อมูล
def get_session():
    with Session(engine) as session:
        yield session
