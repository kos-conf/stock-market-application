from sqlalchemy.orm import Session
from app.fastapi_app.db import models

def get_all_stocks(db: Session):
    return db.query(models.Stock).all()

def create_stock(db: Session, symbol: str, name: str, price: float):
    db_stock = models.Stock(symbol=symbol, name=name, price=price)
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock
