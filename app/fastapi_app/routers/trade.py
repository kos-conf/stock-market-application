from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.fastapi_app.db import schemas, database
from app.fastapi_app.services import trade_service
from typing import List
from app.fastapi_app.logging.logger import logger

router = APIRouter()

@router.post("/orders", response_model=schemas.OrderResponse)
def place_order(order: schemas.OrderCreate, db: Session = Depends(database.get_db)):
    logger.info(f"Order placement requested for stock_id: {order.stock_id}")
    try:
        db_order = trade_service.create_order(db, order)
        logger.info(f"Order placed: order_id={db_order.id}")
        return db_order
    except Exception as e:
        logger.error(f"Order placement error: {e}")
        raise HTTPException(status_code=500, detail="Failed to place order")

@router.get("/transactions", response_model=List[schemas.TransactionResponse])
def get_transactions(db: Session = Depends(database.get_db)):
    logger.info(f"Transaction history requested.")
    try:
        transactions = trade_service.get_all_transactions(db)
        logger.info(f"Transactions fetched.")
        return transactions
    except Exception as e:
        logger.error(f"Transaction fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch transactions")
