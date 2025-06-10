from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

class DatabaseConnection:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        db_path = Path("app/database/db.json").resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.db = TinyDB(
            str(db_path),
            storage=JSONStorage,
            indent=2
        )
        self.items_table = self.db.table('items')
        self._next_id = self._get_next_id()
        
        logger.info(f"Database initialized at {db_path}")
        self._initialized = True
    
    def _get_next_id(self) -> int:
        all_items = self.items_table.all()
        if not all_items:
            return 1
        return max(item.get('id', 0) for item in all_items) + 1
    
    def create_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        item_data['id'] = self._next_id
        item_data['created_at'] = datetime.now().isoformat()
        item_data['updated_at'] = datetime.now().isoformat()
        
        self.items_table.insert(item_data)
        self.db.storage.flush()
        self._next_id += 1
        
        logger.info(f"Created item with id: {item_data['id']}")
        return item_data
    
    def get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        Item = Query()
        result = self.items_table.search(Item.id == item_id)
        
        if result:
            logger.debug(f"Retrieved item with id: {item_id}")
            return result[0]
        
        logger.warning(f"Item not found with id: {item_id}")
        return None
    
    def get_all_items(self) -> List[Dict[str, Any]]:
        items = self.items_table.all()
        logger.debug(f"Retrieved {len(items)} items")
        return items
    
    def update_item(self, item_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        Item = Query()
        existing_item = self.get_item(item_id)
        
        if not existing_item:
            return None
        
        update_data['updated_at'] = datetime.now().isoformat()
        self.items_table.update(update_data, Item.id == item_id)
        self.db.storage.flush()
        
        updated_item = self.get_item(item_id)
        logger.info(f"Updated item with id: {item_id}")
        return updated_item
    
    def delete_item(self, item_id: int) -> bool:
        Item = Query()
        existing_item = self.get_item(item_id)
        
        if not existing_item:
            return False
        
        self.items_table.remove(Item.id == item_id)
        self.db.storage.flush()
        logger.info(f"Deleted item with id: {item_id}")
        return True
    
    def close(self):
        if hasattr(self, 'db'):
            self.db.close()
            logger.info("Database connection closed")

def get_db_connection():
    return DatabaseConnection()