from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import enum

class OrderType(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class StockBase(BaseModel):
    symbol: str
    name: str
    price: float

class StockCreate(StockBase):
    pass

class StockResponse(StockBase):
    id: int
    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    stock_id: int
    order_type: OrderType
    quantity: int
    price: float

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    buy_order_id: int
    sell_order_id: int
    stock_id: int
    quantity: int
    price: float

class TransactionResponse(TransactionBase):
    id: int
    timestamp: datetime
    class Config:
        orm_mode = True

class ErrorResponse(BaseModel):
    detail: str

class StockPriceHistoryResponse(BaseModel):
    id: int
    stock_id: int
    price: float
    timestamp: datetime
    class Config:
        orm_mode = True 