from fastapi import FastAPI
from items import router as items_router
from merchants import router as merchants_router
from wallets import router as wallets_router
from transactions import router as transactions_router

def init_router(app: FastAPI):
    app.include_router(items_router)
    app.include_router(merchants_router)
    app.include_router(wallets_router)
    app.include_router(transactions_router)
