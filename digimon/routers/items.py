from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Annotated
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
import math
import logging

from .. import models, deps

router = APIRouter(prefix="/items")

SIZE_PER_PAGE = 50
logger = logging.getLogger(__name__)

@router.get("")
async def read_items(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: Optional[int] = Query(1, ge=1),
) -> models.ItemList:
    offset = (page - 1) * SIZE_PER_PAGE

    result = await session.exec(
        select(models.DBItem).offset(offset).limit(SIZE_PER_PAGE)
    )
    items = result.all()

    total_items = await session.exec(select(func.count(models.DBItem.id)))
    page_count = math.ceil(total_items.first() / SIZE_PER_PAGE)

    logger.debug("page_count: %d", page_count)
    logger.debug("items: %s", items)
    
    return models.ItemList.from_orm(
        dict(items=items, page_count=page_count, page=page, size_per_page=SIZE_PER_PAGE)
    )

@router.post("")
async def create_item(
    item: models.CreatedItem,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Item:
    dbitem = models.DBItem.validate_model(item)
    session.add(dbitem)
    await session.commit()
    await session.refresh(dbitem)

    return models.Item.from_orm(dbitem)

@router.get("/{item_id}")
async def read_item(
    item_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.Item:
    db_item = await session.get(models.DBItem, item_id)
    if db_item:
        return models.Item.from_orm(db_item)

    raise HTTPException(status_code=404, detail="Item not found")

@router.put("/{item_id}")
async def update_item(
    item_id: int,
    item: models.UpdatedItem,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Item:
    logger.debug("update_item data: %s", item)
    db_item = await session.get(models.DBItem, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    data = item.model_dump()
    db_item.sqlmodel_update(data)
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)

    return models.Item.from_orm(db_item)

@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    current_user: Annotated[models.User, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict:
    db_item = await session.get(models.DBItem, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    await session.delete(db_item)
    await session.commit()

    return {"message": "delete success"}
