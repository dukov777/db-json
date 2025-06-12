from fastapi import APIRouter, HTTPException, status
from typing import List
from loguru import logger

from app.schemas.item import Item, ItemCreate, ItemUpdate
from app.database.connection import get_db_connection

router = APIRouter(prefix="/items", tags=["items"])

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    logger.info(f"Creating new item: {item.name}")
    
    db = get_db_connection()
    item_data = item.model_dump()
    created_item = db.create_item(item_data)
    
    return Item(**created_item)

@router.get("/", response_model=List[Item])
async def get_all_items():
    logger.info("Retrieving all items")
    
    db = get_db_connection()
    items = db.get_all_items()
    return [Item(**item) for item in items]

@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int):
    logger.info(f"Retrieving item with id: {item_id}")
    
    db = get_db_connection()
    item = db.get_item(item_id)
    if not item:
        logger.warning(f"Item not found: {item_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    return Item(**item)

@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item_update: ItemUpdate):
    logger.info(f"Updating item with id: {item_id}")
    
    db = get_db_connection()
    update_data = item_update.model_dump(exclude_unset=True)
    if not update_data:
        logger.warning(f"No update data provided for item: {item_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    updated_item = db.update_item(item_id, update_data)
    if not updated_item:
        logger.warning(f"Item not found for update: {item_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    return Item(**updated_item)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    logger.info(f"Deleting item with id: {item_id}")
    
    db = get_db_connection()
    success = db.delete_item(item_id)
    if not success:
        logger.warning(f"Item not found for deletion: {item_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )