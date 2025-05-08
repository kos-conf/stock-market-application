from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", enqueue=True, backtrace=True, diagnose=True)

# Optionally, add file logging with rotation
logger.add("logs/app.log", rotation="10 MB", retention="10 days", level="INFO", encoding="utf-8") 