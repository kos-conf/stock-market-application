from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.fastapi_app.db import schemas, database, models
from app.fastapi_app.services import stock_service
from typing import List
from app.fastapi_app.logging.logger import logger

router = APIRouter()

@router.get("/stocks", response_model=List[schemas.StockResponse])
def list_stocks(db: Session = Depends(database.get_db)):
    logger.info(f"Stock list requested.")
    try:
        return stock_service.get_all_stocks(db)
    except Exception as e:
        logger.error(f"Stock list error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stocks")

@router.post("/stocks", response_model=schemas.StockResponse)
def add_stock(stock: schemas.StockCreate, db: Session = Depends(database.get_db)):
    logger.info(f"Add stock requested for symbol: {stock.symbol}")
    try:
        db_stock = stock_service.create_stock(db, stock.symbol, stock.name, stock.price)
        logger.info(f"Stock added: {stock.symbol}")
        return db_stock
    except Exception as e:
        logger.error(f"Add stock error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add stock")

@router.get("/stocks/{stock_id}/history", response_model=List[schemas.StockPriceHistoryResponse])
def get_stock_price_history(stock_id: int, db: Session = Depends(database.get_db)):
    logger.info(f"Stock price history requested for stock_id: {stock_id}")
    try:
        history = db.query(models.StockPriceHistory).filter(models.StockPriceHistory.stock_id == stock_id).order_by(models.StockPriceHistory.timestamp.desc()).all()
        return history
    except Exception as e:
        logger.error(f"Stock price history fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock price history")
