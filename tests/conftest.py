import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import tempfile
import os
from pathlib import Path

from app.main import app
from app.database.connection import DatabaseConnection


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db():
    """Create a temporary test database for each test."""
    # Create temporary directory for test database
    with tempfile.TemporaryDirectory() as temp_dir:
        test_db_path = Path(temp_dir) / "test_db.json"
        
        # Override the database path for testing
        original_init = DatabaseConnection.__init__
        
        def test_init(self):
            if self._initialized:
                return
                
            self.db_path = test_db_path
            test_db_path.parent.mkdir(parents=True, exist_ok=True)
            
            from tinydb import TinyDB
            from tinydb.storages import JSONStorage
            from loguru import logger
            
            self.db = TinyDB(
                str(test_db_path),
                storage=JSONStorage,
                indent=2
            )
            self.items_table = self.db.table('items')
            self._next_id = self._get_next_id()
            
            logger.info(f"Test database initialized at {test_db_path}")
            self._initialized = True
        
        # Patch the DatabaseConnection for this test
        DatabaseConnection.__init__ = test_init
        DatabaseConnection._instance = None
        DatabaseConnection._initialized = False
        
        yield test_db_path
        
        # Restore original initialization
        DatabaseConnection.__init__ = original_init
        DatabaseConnection._instance = None
        DatabaseConnection._initialized = False


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
async def async_client(test_db):
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_item():
    """Sample item data for testing."""
    return {
        "name": "Test Item",
        "description": "A test item for unit testing",
        "price": 29.99
    }


@pytest.fixture
def sample_items():
    """Multiple sample items for testing."""
    return [
        {
            "name": "Laptop",
            "description": "Gaming laptop",
            "price": 1299.99
        },
        {
            "name": "Mouse",
            "description": "Wireless mouse",
            "price": 49.99
        },
        {
            "name": "Keyboard",
            "description": "Mechanical keyboard",
            "price": 129.99
        }
    ]