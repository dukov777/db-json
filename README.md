# Python CRUD REST API with JSON Database

A complete FastAPI application implementing CRUD operations using TinyDB for JSON-based data persistence. Features structured logging, automatic API documentation, and request validation.

## Features

- ✅ **FastAPI** - High-performance web framework with automatic API docs
- ✅ **TinyDB** - Lightweight JSON database with persistent storage
- ✅ **CRUD Operations** - Create, Read, Update, Delete with REST endpoints
- ✅ **Pydantic Validation** - Automatic request/response validation
- ✅ **Structured Logging** - Request/response logging with Loguru
- ✅ **Auto Documentation** - Interactive API docs at `/docs`
- ✅ **Database Persistence** - Data survives server restarts
- ✅ **Error Handling** - Proper HTTP status codes and error responses

## Requirements

- Python 3.8+
- Virtual environment (recommended)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/dukov777/db-json.git
cd db-json
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Alternative start method
python app/main.py
```

The API will be available at:
- **API Base:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description | Status Code |
|--------|----------|-------------|-------------|
| `GET` | `/` | Root endpoint with API info | 200 |
| `GET` | `/health` | Health check | 200 |
| `POST` | `/api/items/` | Create a new item | 201 |
| `GET` | `/api/items/` | Get all items | 200 |
| `GET` | `/api/items/{id}` | Get item by ID | 200 |
| `PUT` | `/api/items/{id}` | Update item by ID | 200 |
| `DELETE` | `/api/items/{id}` | Delete item by ID | 204 |

## Data Model

### Item Schema

```json
{
  "name": "string",
  "description": "string (optional)",
  "price": "number (optional)",
  "id": "integer (auto-generated)",
  "created_at": "datetime (auto-generated)",
  "updated_at": "datetime (auto-generated)"
}
```

## API Examples

### Create Item

```bash
curl -X POST "http://localhost:8000/api/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "Gaming laptop",
    "price": 1299.99
  }'
```

**Response:**
```json
{
  "name": "Laptop",
  "description": "Gaming laptop",
  "price": 1299.99,
  "id": 1,
  "created_at": "2024-01-01T12:00:00.000000",
  "updated_at": "2024-01-01T12:00:00.000000"
}
```

### Get All Items

```bash
curl -X GET "http://localhost:8000/api/items/"
```

**Response:**
```json
[
  {
    "name": "Laptop",
    "description": "Gaming laptop",
    "price": 1299.99,
    "id": 1,
    "created_at": "2024-01-01T12:00:00.000000",
    "updated_at": "2024-01-01T12:00:00.000000"
  }
]
```

### Get Item by ID

```bash
curl -X GET "http://localhost:8000/api/items/1"
```

### Update Item

```bash
curl -X PUT "http://localhost:8000/api/items/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Laptop",
    "price": 1199.99
  }'
```

### Delete Item

```bash
curl -X DELETE "http://localhost:8000/api/items/1"
```

## Testing the API

### Manual Testing with cURL

1. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Create test items:**
   ```bash
   # Create first item
   curl -X POST "http://localhost:8000/api/items/" \
     -H "Content-Type: application/json" \
     -d '{"name": "Phone", "description": "Smartphone", "price": 699.99}'
   
   # Create second item
   curl -X POST "http://localhost:8000/api/items/" \
     -H "Content-Type: application/json" \
     -d '{"name": "Tablet", "description": "10-inch tablet", "price": 399.99}'
   ```

3. **Test all CRUD operations:**
   ```bash
   # Get all items
   curl -X GET "http://localhost:8000/api/items/"
   
   # Get specific item
   curl -X GET "http://localhost:8000/api/items/1"
   
   # Update item
   curl -X PUT "http://localhost:8000/api/items/1" \
     -H "Content-Type: application/json" \
     -d '{"price": 649.99}'
   
   # Delete item
   curl -X DELETE "http://localhost:8000/api/items/2"
   ```

### Interactive Testing

Visit http://localhost:8000/docs for the interactive Swagger UI where you can:
- View all available endpoints
- Test API calls directly in the browser
- See request/response schemas
- Download OpenAPI specification

## Project Structure

```
db-json/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   └── logging.py          # Logging configuration
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py       # TinyDB database connection
│   │   └── db.json            # JSON database file (auto-created)
│   ├── models/
│   │   ├── __init__.py
│   │   └── item.py            # Data models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── items.py           # API route handlers
│   └── schemas/
│       ├── __init__.py
│       └── item.py            # Pydantic schemas
├── logs/
│   └── app.log                # Application logs (auto-created)
├── .gitignore
├── requirements.txt
└── README.md
```

## Configuration

### Environment Variables

You can configure the application using environment variables:

- `LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

### Database Location

The JSON database file is created at `app/database/db.json`. This file persists all your data and is automatically created when the application starts.

## Logging

The application includes comprehensive logging:

- **Console Output**: Colored logs for development
- **File Logging**: Structured logs saved to `logs/app.log`
- **Request/Response**: All HTTP requests and responses are logged
- **Database Operations**: Create, read, update, delete operations are logged
- **Log Rotation**: Automatic log file rotation (10MB, 1 week retention)

## Development

### Adding New Endpoints

1. Create new schema in `app/schemas/`
2. Add database operations in `app/database/connection.py`
3. Create route handlers in `app/routers/`
4. Register router in `app/main.py`

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when implemented)
pytest
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Kill process using port 8000
   lsof -ti:8000 | xargs kill
   ```

2. **Permission denied on database file:**
   ```bash
   # Ensure write permissions to app/database/ directory
   chmod 755 app/database/
   ```

3. **Module not found errors:**
   ```bash
   # Ensure virtual environment is activated
   source .venv/bin/activate
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/)** - Web framework
- **[TinyDB](https://tinydb.readthedocs.io/)** - JSON database
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Data validation
- **[Loguru](https://loguru.readthedocs.io/)** - Logging
- **[Uvicorn](https://www.uvicorn.org/)** - ASGI server