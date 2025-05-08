from fastapi import FastAPI
import threading
from fastapi.responses import JSONResponse
from app.fastapi_app.services.kafka_service import consume_stock_price_updates
from app.fastapi_app.routers import stock, trade
from app.fastapi_app.logging.logger import logger
from app.fastapi_app.db.database import init_db

APP_NAME = "Stock Market Application"
APP_DESCRIPTION = "A stock market backend with FastAPI, Kafka, and Confluent Flink integration."
APP_VERSION = "1.0.0"

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Event to signal the consumer thread to stop
stop_event = threading.Event()
consumer_thread = None

@app.on_event("startup")
def start_stock_price_consumer():
    logger.info("Initializing database tables...")
    init_db()
    global consumer_thread
    logger.info("Starting Kafka stock price consumer background thread...")
    consumer_thread = threading.Thread(target=consume_stock_price_updates, kwargs={"stop_after": 0, "stop_event": stop_event}, daemon=True)
    consumer_thread.start()
    logger.info(f"{APP_NAME} started successfully.")

@app.on_event("shutdown")
def stop_stock_price_consumer():
    logger.info("Shutting down Kafka stock price consumer background thread...")
    stop_event.set()
    if consumer_thread is not None:
        consumer_thread.join(timeout=5)
    logger.info(f"{APP_NAME} shutdown complete.")

@app.get("/health", tags=["system"])
def health():
    logger.info("Health check endpoint called.")
    return {"status": "ok"}

@app.get("/", tags=["system"])
def root():
    logger.info("Root endpoint called.")
    return {
        "app_name": APP_NAME,
        "description": APP_DESCRIPTION,
        "version": APP_VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_url": "/health"
    }

app.include_router(stock.router, prefix="/stocks", tags=["stocks"])
app.include_router(trade.router, prefix="/trades", tags=["trades"])
