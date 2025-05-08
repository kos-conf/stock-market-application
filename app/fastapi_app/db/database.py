from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Stock, Order, Transaction
from app.fastapi_app.config.config import settings
from app.fastapi_app.logging.logger import logger
import os

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    logger.info(f"Running init_db(). DB URL: {SQLALCHEMY_DATABASE_URL}")
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
        logger.info(f"Expected SQLite DB file path: {os.path.abspath(db_path)}")
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

get_db = get_db
