from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import models, deps

router = APIRouter(prefix="/merchants")

@router.post("")
async def create_merchant(
    merchant: models.CreatedMerchant,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Merchant:
    db_merchant = models.DBMerchant.model_validate(merchant)
    db_merchant.user = current_user
    session.add(db_merchant)
    await session.commit()
    await session.refresh(db_merchant)

    return models.Merchant.model_validate(db_merchant)

@router.get("")
async def read_merchants(
    session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.MerchantList:
    result = await session.exec(select(models.DBMerchant))
    merchants = result.all()

    return models.MerchantList.model_validate(
        dict(merchants=merchants, page_size=0, page=0, size_per_page=0)
    )

@router.get("/{merchant_id}")
async def read_merchant(
    merchant_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.Merchant:
    db_merchant = await session.get(models.DBMerchant, merchant_id)
    if db_merchant:
        return models.Merchant.model_validate(db_merchant)
    raise HTTPException(status_code=404, detail="Merchant not found")

@router.put("/{merchant_id}")
async def update_merchant(
    merchant_id: int,
    merchant: models.UpdatedMerchant,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Merchant:
    db_merchant = await session.get(models.DBMerchant, merchant_id)
    if not db_merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    data = merchant.model_dump()
    db_merchant.sqlmodel_update(data)
    session.add(db_merchant)
    await session.commit()
    await session.refresh(db_merchant)

    return models.Merchant.model_validate(db_merchant)

@router.delete("/{merchant_id}")
async def delete_merchant(
    merchant_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
) -> dict:
    db_merchant = await session.get(models.DBMerchant, merchant_id)
    if not db_merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    await session.delete(db_merchant)
    await session.commit()

    return {"message": "delete success"}
