from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select

class BaseMerchant(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str
    merchant_type: str
    location: str
    tax_id: str | None = None

class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    owner: str
    balance: float

class BaseTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sender: str
    receiver: str
    amount: float

class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str | None = None
    price: float = 0.12
    tax: float | None = None
    merchant_id: int | None = None

class CreatedItem(BaseItem):
    pass

class UpdatedItem(BaseItem):
    pass

class CreatedMerchant(BaseMerchant):
    pass

class UpdateMerchant(BaseMerchant):
    pass

class CreatedTransaction(BaseTransaction):
    pass

class CreatedWallet(BaseWallet):
    pass

class UpdateWallet(BaseWallet):
    pass

class Merchant(BaseMerchant):
    id: int

class Wallet(BaseWallet):
    id: int

class Transaction(BaseTransaction):
    id: int

class Item(BaseItem):
    id: int
    merchant_id: int

class DBItem(Item, SQLModel, table=True):
    __tablename__ = 'items'
    id: int = Field(default=None, primary_key=True)
    merchant_id: int = Field(default=None, foreign_key="merchants.id")

class DBMerchant(Merchant, SQLModel, table=True):
    __tablename__ = "merchants"
    id: Optional[int] = Field(default=None, primary_key=True)

class DBWallet(Wallet, SQLModel, table=True):
    __tablename__ = "wallets"
    id: Optional[int] = Field(default=None, primary_key=True)

class DBTransaction(Transaction, SQLModel, table=True):
    __tablename__ = "transactions"
    id: Optional[int] = Field(default=None, primary_key=True)

class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[Item]
    page: int
    page_size: int
    size_per_page: int

class MerchantList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    merchants: list[Merchant]
    page: int
    page_size: int
    size_per_page: int

class TransactionList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    transactions: list[Transaction]
    page: int
    page_size: int
    size_per_page: int

class WalletList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    wallets: list[Wallet]
    page: int
    page_size: int
    size_per_page: int

# Create an engine and initialize the database
connect_args = {}
engine = create_engine(
    "postgresql+pg8000://postgres:098765@localhost/digimondb",
    echo=True,
    connect_args=connect_args,
)

SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/merchants")
async def create_merchant(merchant: CreatedMerchant) -> Merchant:
    data = merchant.dict()
    db_item = DBMerchant(**data)
    with Session(engine) as session:
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
    return Merchant.from_orm(db_item)

@app.get("/merchants")
async def read_merchants() -> MerchantList:
    with Session(engine) as session:
        merchants = session.exec(select(DBMerchant)).all()
    return MerchantList.from_orm(dict(merchants=merchants, page_size=0, page=0, size_per_page=0))

@app.get("/merchants/{merchant_id}")
async def read_merchant(merchant_id: int) -> Merchant:
    with Session(engine) as session:
        db_item = session.get(DBMerchant, merchant_id)
        if db_item:
            return Merchant.from_orm(db_item)
    raise HTTPException(status_code=404, detail="Merchant not found")

@app.put("/merchants/{merchant_id}")
async def update_merchant(merchant_id: int, item: UpdateMerchant) -> Merchant:
    data = item.dict()
    with Session(engine) as session:
        db_item = session.get(DBMerchant, merchant_id)
        if db_item:
            for key, value in data.items():
                setattr(db_item, key, value)
            session.add(db_item)
            session.commit()
            session.refresh(db_item)
            return Merchant.from_orm(db_item)
    raise HTTPException(status_code=404, detail="Merchant not found")

@app.delete("/merchants/{merchant_id}")
async def delete_merchant(merchant_id: int) -> dict:
    with Session(engine) as session:
        db_item = session.get(DBMerchant, merchant_id)
        if db_item:
            session.delete(db_item)
            session.commit()
            return dict(message="delete success")
    raise HTTPException(status_code=404, detail="Merchant not found")

@app.post("/items")
async def create_item(item: CreatedItem) -> Item:
    data = item.dict()
    db_item = DBItem(**data)
    with Session(engine) as session:
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
    return Item.from_orm(db_item)

@app.get("/items")
async def read_items() -> ItemList:
    with Session(engine) as session:
        items = session.exec(select(DBItem)).all()
    return ItemList.from_orm(dict(items=items, page_size=0, page=0, size_per_page=0))

@app.get("/items/{item_id}")
async def read_item(item_id: int) -> Item:
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if db_item:
            return Item.from_orm(db_item)
    raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: UpdatedItem) -> Item:
    data = item.dict()
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if db_item:
            for key, value in data.items():
                setattr(db_item, key, value)
            session.add(db_item)
            session.commit()
            session.refresh(db_item)
            return Item.from_orm(db_item)
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{item_id}")
async def delete_item(item_id: int) -> dict:
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if db_item:
            session.delete(db_item)
            session.commit()
            return dict(message="delete success")
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/wallets")
async def create_wallet(wallet: CreatedWallet) -> Wallet:
    data = wallet.dict()
    db_item = DBWallet(**data)
    with Session(engine) as session:
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
    return Wallet.from_orm(db_item)

@app.get("/wallets")
async def read_wallets() -> WalletList:
    with Session(engine) as session:
        wallets = session.exec(select(DBWallet)).all()
    return WalletList.from_orm(dict(wallets=wallets, page_size=0, page=0, size_per_page=0))

@app.get("/wallets/{wallet_id}")
async def read_wallet(wallet_id: int) -> Wallet:
    with Session(engine) as session:
        db_item = session.get(DBWallet, wallet_id)
        if db_item:
            return Wallet.from_orm(db_item)
    raise HTTPException(status_code=404, detail="Wallet not found")

@app.put("/wallets/{wallet_id}")
async def update_wallet(wallet_id: int, item: UpdateWallet) -> Wallet:
    data = item.dict()
    with Session(engine) as session:
        db_item = session.get(DBWallet, wallet_id)
        if db_item:
            for key, value in data.items():
                setattr(db_item, key, value)
            session.add(db_item)
            session.commit()
            session.refresh(db_item)
            return Wallet.from_orm(db_item)
    raise HTTPException(status_code=404, detail="Wallet not found")

@app.delete("/wallets/{wallet_id}")
async def delete_wallet(wallet_id: int) -> dict:
    with Session(engine) as session:
        db_item = session.get(DBWallet, wallet_id)
        if db_item:
            session.delete(db_item)
            session.commit()
            return dict(message="delete success")
    raise HTTPException(status_code=404, detail="Wallet not found")

@app.post("/transactions")
async def create_transaction(transaction: CreatedTransaction) -> Transaction:
    data = transaction.dict()
    db_item = DBTransaction(**data)
    with Session(engine) as session:
        session.add(db_item)
        session.commit
