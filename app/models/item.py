from datetime import datetime
from typing import Dict, Any

class ItemModel:
    def __init__(self, name: str, description: str = None, price: float = None, id: int = None):
        self.name = name
        self.description = description
        self.price = price
        self.id = id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ItemModel':
        item = cls(
            name=data["name"],
            description=data.get("description"),
            price=data.get("price"),
            id=data.get("id")
        )
        if "created_at" in data:
            item.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            item.updated_at = datetime.fromisoformat(data["updated_at"])
        return item