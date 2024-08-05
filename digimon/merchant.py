from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select

# Define base models
class BaseProduct(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: Optional[str] = None
    price: float = 0.00
    tax: Optional[float] = None
    supplier_id: Optional[int] = None

class BaseSupplier(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: Optional[str] = None
    supplier_type: str
    location: str

class BaseAccount(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    owner: str
    balance: float

class BaseTransfer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sender: str
    receiver: str
    amount: float

# Define CRUD models
class NewProduct(BaseProduct):
    pass

class EditProduct(BaseProduct):
    pass

class NewSupplier(BaseSupplier):
    pass

class EditSupplier(BaseSupplier):
    pass

class NewAccount(BaseAccount):
    pass

class EditAccount(BaseAccount):
    pass

class NewTransfer(BaseTransfer):
    pass

class EditTransfer(BaseTransfer):
    pass

# Define models with IDs
class Product(BaseProduct):
    id: int
    supplier_id: int

class Supplier(BaseSupplier):
    id: int

class Account(BaseAccount):
    id: int

class Transfer(BaseTransfer):
    id: int

# Define database models
class DBProduct(Product, SQLModel, table=True):
    __tablename__ = "product"
    id: Optional[int] = Field(default=None, primary_key=True)
    supplier_id: Optional[int] = Field(default=None, foreign_key="supplier.id")

class DBSupplier(Supplier, SQLModel, table=True):
    __tablename__ = "supplier"
    id: Optional[int] = Field(default=None, primary_key=True)

class DBAccount(Account, SQLModel, table=True):
    __tablename__ = "account"
    id: Optional[int] = Field(default=None, primary_key=True)

class DBTransfer(Transfer, SQLModel, table=True):
    __tablename__ = "transfer"
    id: Optional[int] = Field(default=None, primary_key=True)

# Define paginated response models
class ProductList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    products: List[Product]
    page: int
    page_size: int
    total_items: int

class SupplierList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    suppliers: List[Supplier]
    page: int
    page_size: int
    total_items: int

class AccountList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    accounts: List[Account]
    page: int
    page_size: int
    total_items: int

class TransferList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    transfers: List[Transfer]
    page: int
    page_size: int
    total_items: int

# Database setup
connect_args = {}
engine = create_engine(
    "postgresql+pg8000://postgres:123456@localhost/digimondb",
    echo=True,
    connect_args=connect_args,
)
SQLModel.metadata.create_all(engine)

# Create FastAPI app instance
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

# Product endpoints
@app.get("/products", response_model=ProductList)
async def read_products(page: int = 1, page_size: int = 10) -> ProductList:
    with Session(engine) as session:
        stmt = select(DBProduct).offset((page - 1) * page_size).limit(page_size)
        products = session.exec(stmt).all()
        total_products = session.exec(select(DBProduct)).count()
    return ProductList(products=products, page=page, page_size=page_size, total_items=total_products)

@app.post("/products", response_model=Product)
async def create_product(product: NewProduct) -> Product:
    db_product = DBProduct(**product.dict())
    with Session(engine) as session:
        session.add(db_product)
        session.commit()
        session.refresh(db_product)
    return Product.from_orm(db_product)

@app.get("/products/{product_id}", response_model=Product)
async def read_product(product_id: int) -> Product:
    with Session(engine) as session:
        db_product = session.get(DBProduct, product_id)
        if db_product:
            return Product.from_orm(db_product)
    raise HTTPException(status_code=404, detail="Product not found")

@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, product: EditProduct) -> Product:
    data = product.dict()
    with Session(engine) as session:
        db_product = session.get(DBProduct, product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        for key, value in data.items():
            setattr(db_product, key, value)
        session.add(db_product)
        session.commit()
        session.refresh(db_product)
    return Product.from_orm(db_product)

@app.delete("/products/{product_id}")
async def delete_product(product_id: int) -> dict:
    with Session(engine) as session:
        db_product = session.get(DBProduct, product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        session.delete(db_product)
        session.commit()
    return {"message": "delete success"}

# Supplier endpoints
@app.get("/suppliers", response_model=SupplierList)
async def read_suppliers(page: int = 1, page_size: int = 10) -> SupplierList:
    with Session(engine) as session:
        stmt = select(DBSupplier).offset((page - 1) * page_size).limit(page_size)
        suppliers = session.exec(stmt).all()
        total_suppliers = session.exec(select(DBSupplier)).count()
    return SupplierList(suppliers=suppliers, page=page, page_size=page_size, total_items=total_suppliers)

@app.post("/suppliers", response_model=Supplier)
async def create_supplier(supplier: NewSupplier) -> Supplier:
    db_supplier = DBSupplier(**supplier.dict())
    with Session(engine) as session:
        session.add(db_supplier)
        session.commit()
        session.refresh(db_supplier)
    return Supplier.from_orm(db_supplier)

@app.get("/suppliers/{supplier_id}", response_model=Supplier)
async def read_supplier(supplier_id: int) -> Supplier:
    with Session(engine) as session:
        db_supplier = session.get(DBSupplier, supplier_id)
        if db_supplier:
            return Supplier.from_orm(db_supplier)
    raise HTTPException(status_code=404, detail="Supplier not found")

@app.put("/suppliers/{supplier_id}", response_model=Supplier)
async def update_supplier(supplier_id: int, supplier: EditSupplier) -> Supplier:
    data = supplier.dict()
    with Session(engine) as session:
        db_supplier = session.get(DBSupplier, supplier_id)
        if not db_supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        for key, value in data.items():
            setattr(db_supplier, key, value)
        session.add(db_supplier)
        session.commit()
        session.refresh(db_supplier)
    return Supplier.from_orm(db_supplier)

@app.delete("/suppliers/{supplier_id}")
async def delete_supplier(supplier_id: int) -> dict:
    with Session(engine) as session:
        db_supplier = session.get(DBSupplier, supplier_id)
        if not db_supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        session.delete(db_supplier)
        session.commit()
    return {"message": "delete success"}

# Account endpoints
@app.get("/accounts", response_model=AccountList)
async def read_accounts(page: int = 1, page_size: int = 10) -> AccountList:
    with Session(engine) as session:
        stmt = select(DBAccount).offset((page - 1) * page_size).limit(page_size)
        accounts = session.exec(stmt).all()
        total_accounts = session.exec(select(DBAccount)).count()
    return AccountList(accounts=accounts, page=page, page_size=page_size, total_items=total_accounts)

@app.post("/accounts", response_model=Account)
async def create_account(account: NewAccount) -> Account:
    db_account = DBAccount(**account.dict())
    with Session(engine) as session:
        session.add(db_account)
        session.commit()
        session.refresh(db_account)
    return Account.from_orm(db_account)

@app.get("/accounts/{account_id}", response_model=Account)
async def read_account(account_id: int) -> Account:
    with Session(engine) as session:
        db_account = session.get(DBAccount, account_id)
        if db_account:
            return Account.from_orm(db_account)
    raise HTTPException(status_code=404, detail="Account not found")

@app.put("/accounts/{account_id}", response_model=Account)
async def update_account(account_id: int, account: EditAccount) -> Account:
    data = account.dict()
    with Session(engine) as session:
        db_account = session.get(DBAccount, account_id)
        if not db_account:
            raise HTTPException(status_code=404, detail="Account not found")
