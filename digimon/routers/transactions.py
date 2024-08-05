from fastapi import APIRouter, HTTPException
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session, select

from ..models import Transaction, CreatedTransaction, TransactionList, DBTransaction, UpdatedTransaction, engine

router = APIRouter(prefix="/transactions")

@router.get("", response_model=TransactionList)
async def read_transactions(page: int = 1, page_size: int = 10) -> TransactionList:
    with Session(engine) as session:
        stmt = select(DBTransaction).offset((page - 1) * page_size).limit(page_size)
        transactions = session.exec(stmt).all()
        total_transactions = session.exec(select(DBTransaction)).count()  # คำนวณจำนวนรายการทั้งหมด
    
    return TransactionList(transactions=transactions, page=page, page_size=page_size, size_per_page=total_transactions)

@router.post("", response_model=Transaction)
async def create_transaction(transaction: CreatedTransaction) -> Transaction:
    data = transaction.dict()
    dbtransaction = DBTransaction(**data)
    with Session(engine) as session:
        session.add(dbtransaction)
        session.commit()
        session.refresh(dbtransaction)
    return Transaction.from_orm(dbtransaction)

@router.get("/{transaction_id}", response_model=Transaction)
async def read_transaction(transaction_id: int) -> Transaction:
    with Session(engine) as session:
        db_transaction = session.get(DBTransaction, transaction_id)
        if db_transaction:
            return Transaction.from_orm(db_transaction)
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.put("/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: int, transaction: UpdatedTransaction) -> Transaction:
    data = transaction.dict()
    with Session(engine) as session:
        db_transaction = session.get(DBTransaction, transaction_id)
        if not db_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        for key, value in data.items():
            setattr(db_transaction, key, value)
        session.add(db_transaction)
        session.commit()
        session.refresh(db_transaction)
    return Transaction.from_orm(db_transaction)

@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int) -> dict:
    with Session(engine) as session:
        db_transaction = session.get(DBTransaction, transaction_id)
        if not db_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        session.delete(db_transaction)
        session.commit()
    return {"message": "delete success"}
