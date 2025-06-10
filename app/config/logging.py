from loguru import logger
import sys
from pathlib import Path

def setup_logging():
    logger.remove()
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="1 week",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )
    
    return logger