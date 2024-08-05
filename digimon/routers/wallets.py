from fastapi import APIRouter, HTTPException
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session, select

from ..models import Wallet, CreatedWallet, WalletList, DBWallet, UpdatedWallet, engine

router = APIRouter(prefix="/wallets")

@router.get("", response_model=WalletList)
async def read_wallets(page: int = 1, page_size: int = 10) -> WalletList:
    with Session(engine) as session:
        stmt = select(DBWallet).offset((page - 1) * page_size).limit(page_size)
        wallets = session.exec(stmt).all()
        total_wallets = session.exec(select(DBWallet)).count()  # คำนวณจำนวนรายการทั้งหมด
    
    return WalletList(wallets=wallets, page=page, page_size=page_size, size_per_page=total_wallets)

@router.post("", response_model=Wallet)
async def create_wallet(wallet: CreatedWallet) -> Wallet:
    data = wallet.dict()
    dbwallet = DBWallet(**data)
    with Session(engine) as session:
        session.add(dbwallet)
        session.commit()
        session.refresh(dbwallet)
    return Wallet.from_orm(dbwallet)

@router.get("/{wallet_id}", response_model=Wallet)
async def read_wallet(wallet_id: int) -> Wallet:
    with Session(engine) as session:
        db_wallet = session.get(DBWallet, wallet_id)
        if db_wallet:
            return Wallet.from_orm(db_wallet)
    raise HTTPException(status_code=404, detail="Wallet not found")

@router.put("/{wallet_id}", response_model=Wallet)
async def update_wallet(wallet_id: int, wallet: UpdatedWallet) -> Wallet:
    data = wallet.dict()
    with Session(engine) as session:
        db_wallet = session.get(DBWallet, wallet_id)
        if not db_wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        for key, value in data.items():
            setattr(db_wallet, key, value)
        session.add(db_wallet)
        session.commit()
        session.refresh(db_wallet)
    return Wallet.from_orm(db_wallet)

@router.delete("/{wallet_id}")
async def delete_wallet(wallet_id: int) -> dict:
    with Session(engine) as session:
        db_wallet = session.get(DBWallet, wallet_id)
        if not db_wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        session.delete(db_wallet)
        session.commit()
    return {"message": "delete success"}
