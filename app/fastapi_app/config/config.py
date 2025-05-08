from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./stock_market.db"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_ORDERS_TOPIC: str = "orders"
    KAFKA_STOCK_PRICE_TOPIC: str = "stock_prices1"
    KAFKA_CONSUMER_GROUP: str = "order_processor_group"
    DEFAULT_CASH_BALANCE: float = 10000.0
    KAFKA_API_KEY: str = ""
    KAFKA_API_SECRET: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
