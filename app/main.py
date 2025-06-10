from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
from loguru import logger

from app.config.logging import setup_logging
from app.routers import items
from app.database.connection import get_db_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    
    # Initialize database connection
    db = get_db_connection()
    logger.info("Application startup complete")
    
    yield
    
    # Close database connection
    db.close()
    logger.info("Application shutdown")

app = FastAPI(
    title="JSON Database CRUD API",
    description="A FastAPI application with CRUD operations using TinyDB JSON storage",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} | Duration: {process_time:.4f}s")
    
    return response

app.include_router(items.router, prefix="/api")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "JSON Database CRUD API", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)