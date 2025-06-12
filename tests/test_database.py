import pytest
from datetime import datetime
import tempfile
from pathlib import Path

from app.database.connection import DatabaseConnection


class TestDatabaseConnection:
    """Unit tests for the DatabaseConnection class."""
    
    def test_database_initialization(self, test_db):
        """Test database initialization creates correct structure."""
        db = DatabaseConnection()
        assert hasattr(db, 'db')
        assert hasattr(db, 'items_table')
        assert hasattr(db, '_next_id')
        assert db._next_id == 1  # Should start at 1 for empty database
    
    def test_singleton_pattern(self, test_db):
        """Test that DatabaseConnection follows singleton pattern."""
        db1 = DatabaseConnection()
        db2 = DatabaseConnection()
        assert db1 is db2  # Should be the same instance
    
    def test_create_item(self, test_db):
        """Test creating an item in the database."""
        db = DatabaseConnection()
        item_data = {
            "name": "Test Item",
            "description": "A test item",
            "price": 29.99
        }
        
        created_item = db.create_item(item_data)
        
        assert created_item["id"] == 1
        assert created_item["name"] == "Test Item"
        assert created_item["description"] == "A test item"
        assert created_item["price"] == 29.99
        assert "created_at" in created_item
        assert "updated_at" in created_item
        
        # Verify timestamps are ISO format
        datetime.fromisoformat(created_item["created_at"])
        datetime.fromisoformat(created_item["updated_at"])
    
    def test_create_multiple_items(self, test_db):
        """Test creating multiple items with incrementing IDs."""
        db = DatabaseConnection()
        
        items = [
            {"name": "Item 1", "price": 10.00},
            {"name": "Item 2", "price": 20.00},
            {"name": "Item 3", "price": 30.00}
        ]
        
        created_items = []
        for item in items:
            created_item = db.create_item(item)
            created_items.append(created_item)
        
        # Verify IDs increment correctly
        for i, item in enumerate(created_items):
            assert item["id"] == i + 1
        
        # Verify next_id is updated
        assert db._next_id == 4
    
    def test_get_item_exists(self, test_db):
        """Test getting an existing item."""
        db = DatabaseConnection()
        
        # Create an item
        item_data = {"name": "Get Test Item", "price": 15.99}
        created_item = db.create_item(item_data)
        item_id = created_item["id"]
        
        # Get the item
        retrieved_item = db.get_item(item_id)
        
        assert retrieved_item is not None
        assert retrieved_item["id"] == item_id
        assert retrieved_item["name"] == "Get Test Item"
        assert retrieved_item["price"] == 15.99
    
    def test_get_item_not_exists(self, test_db):
        """Test getting a non-existent item."""
        db = DatabaseConnection()
        
        retrieved_item = db.get_item(999)
        assert retrieved_item is None
    
    def test_get_all_items_empty(self, test_db):
        """Test getting all items from empty database."""
        db = DatabaseConnection()
        
        items = db.get_all_items()
        assert items == []
    
    def test_get_all_items_with_data(self, test_db):
        """Test getting all items when database has data."""
        db = DatabaseConnection()
        
        # Create multiple items
        test_items = [
            {"name": "Item A", "price": 10.00},
            {"name": "Item B", "price": 20.00},
            {"name": "Item C", "price": 30.00}
        ]
        
        for item in test_items:
            db.create_item(item)
        
        # Get all items
        all_items = db.get_all_items()
        
        assert len(all_items) == 3
        for i, item in enumerate(all_items):
            assert item["name"] == test_items[i]["name"]
            assert item["price"] == test_items[i]["price"]
    
    def test_update_item_exists(self, test_db):
        """Test updating an existing item."""
        db = DatabaseConnection()
        
        # Create an item
        item_data = {"name": "Update Test", "price": 25.00}
        created_item = db.create_item(item_data)
        item_id = created_item["id"]
        original_updated_at = created_item["updated_at"]
        
        # Update the item
        update_data = {"name": "Updated Name", "price": 35.00}
        updated_item = db.update_item(item_id, update_data)
        
        assert updated_item is not None
        assert updated_item["id"] == item_id
        assert updated_item["name"] == "Updated Name"
        assert updated_item["price"] == 35.00
        assert updated_item["created_at"] == created_item["created_at"]  # Should not change
        assert updated_item["updated_at"] != original_updated_at  # Should be updated
    
    def test_update_item_partial(self, test_db):
        """Test partially updating an item."""
        db = DatabaseConnection()
        
        # Create an item
        item_data = {"name": "Partial Update Test", "description": "Original description", "price": 40.00}
        created_item = db.create_item(item_data)
        item_id = created_item["id"]
        
        # Update only the price
        update_data = {"price": 45.00}
        updated_item = db.update_item(item_id, update_data)
        
        assert updated_item["name"] == "Partial Update Test"  # Should remain unchanged
        assert updated_item["description"] == "Original description"  # Should remain unchanged
        assert updated_item["price"] == 45.00  # Should be updated
    
    def test_update_item_not_exists(self, test_db):
        """Test updating a non-existent item."""
        db = DatabaseConnection()
        
        update_data = {"name": "Non-existent"}
        result = db.update_item(999, update_data)
        
        assert result is None
    
    def test_delete_item_exists(self, test_db):
        """Test deleting an existing item."""
        db = DatabaseConnection()
        
        # Create an item
        item_data = {"name": "Delete Test", "price": 50.00}
        created_item = db.create_item(item_data)
        item_id = created_item["id"]
        
        # Verify item exists
        assert db.get_item(item_id) is not None
        
        # Delete the item
        result = db.delete_item(item_id)
        assert result is True
        
        # Verify item is deleted
        assert db.get_item(item_id) is None
    
    def test_delete_item_not_exists(self, test_db):
        """Test deleting a non-existent item."""
        db = DatabaseConnection()
        
        result = db.delete_item(999)
        assert result is False
    
    def test_database_persistence(self, test_db):
        """Test that data persists in the database file."""
        db = DatabaseConnection()
        
        # Create an item
        item_data = {"name": "Persistence Test", "price": 60.00}
        created_item = db.create_item(item_data)
        
        # Close and recreate database connection
        db.close()
        DatabaseConnection._instance = None
        DatabaseConnection._initialized = False
        
        # Create new connection
        new_db = DatabaseConnection()
        
        # Verify item still exists
        retrieved_item = new_db.get_item(created_item["id"])
        assert retrieved_item is not None
        assert retrieved_item["name"] == "Persistence Test"
        assert retrieved_item["price"] == 60.00
    
    def test_next_id_persistence(self, test_db):
        """Test that next_id is calculated correctly after restart."""
        db = DatabaseConnection()
        
        # Create multiple items
        for i in range(3):
            db.create_item({"name": f"Item {i+1}", "price": float(i+1)})
        
        assert db._next_id == 4
        
        # Close and recreate database connection
        db.close()
        DatabaseConnection._instance = None
        DatabaseConnection._initialized = False
        
        # Create new connection
        new_db = DatabaseConnection()
        
        # Verify next_id is calculated correctly
        assert new_db._next_id == 4
        
        # Create new item and verify ID
        new_item = new_db.create_item({"name": "Item 4", "price": 4.0})
        assert new_item["id"] == 4