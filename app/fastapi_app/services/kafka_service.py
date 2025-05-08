import json
from confluent_kafka import Producer, Consumer
from app.fastapi_app.config.config import settings
from app.fastapi_app.db import database, models
from app.fastapi_app.logging.logger import logger
import time
import datetime

KAFKA_BOOTSTRAP_SERVERS = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_ORDERS_TOPIC = getattr(settings, 'KAFKA_ORDERS_TOPIC', 'orders')
KAFKA_CONSUMER_GROUP = getattr(settings, 'KAFKA_CONSUMER_GROUP', 'order_processor_group')
KAFKA_STOCK_PRICE_TOPIC = getattr(settings, 'KAFKA_STOCK_PRICE_TOPIC', 'stock_prices')

producer_conf = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': settings.KAFKA_API_KEY,
    'sasl.password': settings.KAFKA_API_SECRET,
}
producer = Producer(producer_conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"Failed to deliver message: {msg}: {err}")
    else:
        print(f"Message produced: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def publish_order(order_data: dict):
    producer.produce(
        KAFKA_ORDERS_TOPIC,
        json.dumps(order_data).encode('utf-8'),
        callback=delivery_report
    )
    producer.poll(1)

def consume_stock_price_updates(stop_after: int = 0, stop_event=None):
    consumer_conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': f"{KAFKA_CONSUMER_GROUP}_stock_price1",
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': settings.KAFKA_API_KEY,
        'sasl.password': settings.KAFKA_API_SECRET,
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe([KAFKA_STOCK_PRICE_TOPIC])
    logger.info(f"Consuming stock price updates from topic: {KAFKA_STOCK_PRICE_TOPIC}")
    count = 0
    try:
        while stop_after == 0 or count < stop_after:
            if stop_event and stop_event.is_set():
                logger.info("Stop event set, shutting down stock price consumer.")
                break
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Stock price consumer error: {msg.error()}")
                continue
            try:
                price_update = json.loads(msg.value()[5:].decode('utf-8'))
                symbol = price_update.get('stock_id')
                price = price_update.get('price')
                ts_long = price_update.get('ts')
                print(symbol, price, ts_long)
                if symbol and price is not None and ts_long is not None:
                    db = database.SessionLocal()
                    stock = db.query(models.Stock).filter(models.Stock.id == symbol).first()
                    if stock:
                        stock.price = price
                        db.commit()
                        logger.info(f"Updated price for {symbol}: {price}")
                        # Insert into StockPriceHistory
                        ts_dt = datetime.datetime.utcfromtimestamp(ts_long / 1000.0)
                        history = models.StockPriceHistory(
                            stock_id=symbol,
                            price=price,
                            timestamp=ts_dt
                        )
                        db.add(history)
                        db.commit()
                        consumer.commit()
                    db.close()
            except Exception as e:
                logger.error(f"Failed to process stock price update: {e}")
            count += 1
    finally:
        consumer.close()
