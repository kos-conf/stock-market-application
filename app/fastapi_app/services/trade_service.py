from sqlalchemy.orm import Session
from app.fastapi_app.db import models, schemas
from fastapi import HTTPException, status
from app.fastapi_app.services import kafka_service

def create_order(db: Session, order: schemas.OrderCreate):
    stock = db.query(models.Stock).filter(models.Stock.id == order.stock_id).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")
    db_order = models.Order(
        stock_id=order.stock_id,
        order_type=order.order_type,
        quantity=order.quantity,
        price=order.price
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    # Publish to Kafka
    kafka_service.publish_order({
        "order_id": db_order.id,
        "stock_id": db_order.stock_id,
        "order_type": db_order.order_type.value,
        "quantity": db_order.quantity,
        "price": db_order.price,
        "created_at": db_order.created_at.strftime("%Y-%m-%d %H:%M:%S")
    })
    return db_order

def get_all_transactions(db: Session):
    return db.query(models.Transaction).all()
