from fastapi import APIRouter, HTTPException
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session, select

from ..models import Merchant, CreatedMerchant, MerchantList, DBMerchant, UpdatedMerchant, engine

router = APIRouter(prefix="/merchants")

@router.get("", response_model=MerchantList)
async def read_merchants(page: int = 1, page_size: int = 10) -> MerchantList:
    with Session(engine) as session:
        stmt = select(DBMerchant).offset((page - 1) * page_size).limit(page_size)
        merchants = session.exec(stmt).all()
        total_merchants = session.exec(select(DBMerchant)).count()  # คำนวณจำนวนรายการทั้งหมด
    
    return MerchantList(merchants=merchants, page=page, page_size=page_size, size_per_page=total_merchants)

@router.post("", response_model=Merchant)
async def create_merchant(merchant: CreatedMerchant) -> Merchant:
    data = merchant.dict()
    dbmerchant = DBMerchant(**data)
    with Session(engine) as session:
        session.add(dbmerchant)
        session.commit()
        session.refresh(dbmerchant)
    return Merchant.from_orm(dbmerchant)

@router.get("/{merchant_id}", response_model=Merchant)
async def read_merchant(merchant_id: int) -> Merchant:
    with Session(engine) as session:
        db_merchant = session.get(DBMerchant, merchant_id)
        if db_merchant:
            return Merchant.from_orm(db_merchant)
    raise HTTPException(status_code=404, detail="Merchant not found")

@router.put("/{merchant_id}", response_model=Merchant)
async def update_merchant(merchant_id: int, merchant: UpdatedMerchant) -> Merchant:
    data = merchant.dict()
    with Session(engine) as session:
        db_merchant = session.get(DBMerchant, merchant_id)
        if not db_merchant:
            raise HTTPException(status_code=404, detail="Merchant not found")
        for key, value in data.items():
            setattr(db_merchant, key, value)
        session.add(db_merchant)
        session.commit()
        session.refresh(db_merchant)
    return Merchant.from_orm(db_merchant)

@router.delete("/{merchant_id}")
async def delete_merchant(merchant_id: int) -> dict:
    with Session(engine) as session:
        db_merchant = session.get(DBMerchant, merchant_id)
        if not db_merchant:
            raise HTTPException(status_code=404, detail="Merchant not found")
        session.delete(db_merchant)
        session.commit()
    return {"message": "delete success"}
