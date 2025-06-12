import pytest
from fastapi import status
import json


class TestItemsAPI:
    """Integration tests for the Items API endpoints."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns correct information."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "docs" in data
        assert data["docs"] == "/docs"
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_create_item_success(self, client, sample_item):
        """Test creating an item successfully."""
        response = client.post("/api/items/", json=sample_item)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["name"] == sample_item["name"]
        assert data["description"] == sample_item["description"]
        assert data["price"] == sample_item["price"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["id"] == 1  # First item should have ID 1
    
    def test_create_item_minimal(self, client):
        """Test creating an item with minimal required fields."""
        minimal_item = {"name": "Minimal Item"}
        response = client.post("/api/items/", json=minimal_item)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["name"] == "Minimal Item"
        assert data["description"] is None
        assert data["price"] is None
        assert data["id"] == 1
    
    def test_create_item_invalid_data(self, client):
        """Test creating an item with invalid data."""
        invalid_item = {"description": "Missing name field"}
        response = client.post("/api/items/", json=invalid_item)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_all_items_empty(self, client):
        """Test getting all items when database is empty."""
        response = client.get("/api/items/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []
    
    def test_get_all_items_with_data(self, client, sample_items):
        """Test getting all items when database has data."""
        # Create multiple items
        created_items = []
        for item in sample_items:
            response = client.post("/api/items/", json=item)
            assert response.status_code == status.HTTP_201_CREATED
            created_items.append(response.json())
        
        # Get all items
        response = client.get("/api/items/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == len(sample_items)
        
        # Verify items are returned correctly
        for i, item in enumerate(data):
            assert item["name"] == sample_items[i]["name"]
            assert item["id"] == i + 1
    
    def test_get_item_by_id_success(self, client, sample_item):
        """Test getting a specific item by ID."""
        # Create an item
        create_response = client.post("/api/items/", json=sample_item)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Get the item by ID
        response = client.get(f"/api/items/{item_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == sample_item["name"]
        assert data["description"] == sample_item["description"]
        assert data["price"] == sample_item["price"]
    
    def test_get_item_by_id_not_found(self, client):
        """Test getting a non-existent item by ID."""
        response = client.get("/api/items/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "999" in data["detail"]
    
    def test_update_item_success(self, client, sample_item):
        """Test updating an item successfully."""
        # Create an item
        create_response = client.post("/api/items/", json=sample_item)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Update the item
        update_data = {
            "name": "Updated Item",
            "price": 39.99
        }
        response = client.put(f"/api/items/{item_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == "Updated Item"
        assert data["description"] == sample_item["description"]  # Should remain unchanged
        assert data["price"] == 39.99
        assert data["created_at"] == created_item["created_at"]  # Should remain same
        assert data["updated_at"] != created_item["updated_at"]  # Should be different
    
    def test_update_item_partial(self, client, sample_item):
        """Test updating an item with partial data."""
        # Create an item
        create_response = client.post("/api/items/", json=sample_item)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Update only the price
        update_data = {"price": 19.99}
        response = client.put(f"/api/items/{item_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == sample_item["name"]  # Should remain unchanged
        assert data["description"] == sample_item["description"]  # Should remain unchanged
        assert data["price"] == 19.99
    
    def test_update_item_not_found(self, client):
        """Test updating a non-existent item."""
        update_data = {"name": "Updated Item"}
        response = client.put("/api/items/999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "999" in data["detail"]
    
    def test_update_item_empty_data(self, client, sample_item):
        """Test updating an item with no data."""
        # Create an item
        create_response = client.post("/api/items/", json=sample_item)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Try to update with empty data
        response = client.put(f"/api/items/{item_id}", json={})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "No fields to update" in data["detail"]
    
    def test_delete_item_success(self, client, sample_item):
        """Test deleting an item successfully."""
        # Create an item
        create_response = client.post("/api/items/", json=sample_item)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Delete the item
        response = client.delete(f"/api/items/{item_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""
        
        # Verify item is deleted
        get_response = client.get(f"/api/items/{item_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_item_not_found(self, client):
        """Test deleting a non-existent item."""
        response = client.delete("/api/items/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "999" in data["detail"]
    
    def test_crud_workflow(self, client):
        """Test complete CRUD workflow with a single item."""
        # CREATE
        item_data = {
            "name": "Workflow Test Item",
            "description": "Testing CRUD workflow",
            "price": 99.99
        }
        create_response = client.post("/api/items/", json=item_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # READ (specific item)
        read_response = client.get(f"/api/items/{item_id}")
        assert read_response.status_code == status.HTTP_200_OK
        read_item = read_response.json()
        assert read_item["name"] == item_data["name"]
        
        # UPDATE
        update_data = {"price": 149.99}
        update_response = client.put(f"/api/items/{item_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        updated_item = update_response.json()
        assert updated_item["price"] == 149.99
        assert updated_item["name"] == item_data["name"]  # Should remain same
        
        # READ (verify update)
        read_updated_response = client.get(f"/api/items/{item_id}")
        assert read_updated_response.status_code == status.HTTP_200_OK
        assert read_updated_response.json()["price"] == 149.99
        
        # DELETE
        delete_response = client.delete(f"/api/items/{item_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # READ (verify deletion)
        final_read_response = client.get(f"/api/items/{item_id}")
        assert final_read_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_multiple_items_operations(self, client, sample_items):
        """Test operations with multiple items."""
        # Create multiple items
        item_ids = []
        for item in sample_items:
            response = client.post("/api/items/", json=item)
            assert response.status_code == status.HTTP_201_CREATED
            item_ids.append(response.json()["id"])
        
        # Get all items
        all_items_response = client.get("/api/items/")
        assert all_items_response.status_code == status.HTTP_200_OK
        all_items = all_items_response.json()
        assert len(all_items) == len(sample_items)
        
        # Update middle item
        middle_id = item_ids[1]
        update_response = client.put(f"/api/items/{middle_id}", json={"price": 999.99})
        assert update_response.status_code == status.HTTP_200_OK
        
        # Delete first item
        first_id = item_ids[0]
        delete_response = client.delete(f"/api/items/{first_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify final state
        final_items_response = client.get("/api/items/")
        assert final_items_response.status_code == status.HTTP_200_OK
        final_items = final_items_response.json()
        assert len(final_items) == len(sample_items) - 1  # One item deleted
        
        # Find the updated item
        updated_item = next(item for item in final_items if item["id"] == middle_id)
        assert updated_item["price"] == 999.99