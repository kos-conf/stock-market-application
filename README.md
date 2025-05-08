# Real-Time Stock Market Dashboard

A real-time stock market monitoring application built with FastAPI backend and Streamlit frontend, featuring live price updates through Kafka integration.

## 🚀 Features

- Real-time stock price monitoring
- Interactive buy/sell interface
- Historical price visualization
- Live price updates via Kafka
- RESTful API endpoints for stock data
- Streamlit-based responsive dashboard

## 🛠 Tech Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Message Broker**: Confluent Kafka
- **Stream Processing**: Confluent Flink
- **Database**: SQLAlchemy with SQLite
- **Data Visualization**: Plotly

## 📋 Prerequisites

- Python 3.8+
- Confluent Kafka
- ConfluentApache Flink
- pip (Python package manager)

## 🔧 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock-market-application
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
    # Database
    DATABASE_URL=sqlite:///./stock_market.db

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS=pkc-xxxxx.xxxxxx.xxx.confluent.cloud:9092
    KAFKA_ORDERS_TOPIC=orders
    KAFKA_STOCK_PRICE_TOPIC=stock_prices
    KAFKA_CONSUMER_GROUP=order_processor_group
    KAFKA_API_KEY=xxxxxx
    KAFKA_API_SECRET=xxxxxxxx
   ```

## 🚀 Running the Application

1. **Start the FastAPI backend**
   ```bash
   cd app
   uvicorn fastapi_app.main:app --reload --port 8000
   ```

2. **Start the Streamlit frontend**
   ```bash
   cd app/streamlit_app
   streamlit run main.py
   ```

3. **Access the applications**
   - Frontend Dashboard: http://localhost:8501
   - API Documentation: http://localhost:8000/docs

## 🔄 Confluent Flink Configuration

Add your Flink SQL statements below:

```sql
-- Create source table for stock prices
CREATE TABLE orders (
    order_id INT,
    stock_id INT,
    order_type STRING,
    price DOUBLE,
    quantity BIGINT,
    created_at STRING,
    ts AS TO_TIMESTAMP(created_at, 'yyyy-mm-dd hh:mm:ss'),
    WATERMARK FOR ts AS ts - INTERVAL '5' SECOND
) WITH (
  'value.format'='json-registry'
);

-- Create sink table for processed data
CREATE TABLE stock_prices (
  stock_id INT,
  price DOUBLE,
  ts TIMESTAMP(3)
) WITH (
  'changelog.mode'='append',
  'value.format'='json-registry'
);

-- Add your custom Flink SQL statements below:
INSERT INTO `stock_prices1`
SELECT
  stock_id,
  CASE
    WHEN SUM(CASE WHEN order_type = 'BUY' THEN 1 ELSE 0 END)
       > SUM(CASE WHEN order_type = 'SELL' THEN 1 ELSE 0 END)
      THEN AVG(price) * 1.10

    WHEN SUM(CASE WHEN order_type = 'SELL' THEN 1 ELSE 0 END)
       > SUM(CASE WHEN order_type = 'BUY' THEN 1 ELSE 0 END)
      THEN AVG(price) * 0.90

    ELSE AVG(price)
  END AS adjusted_price,
  window_end AS ts
FROM TABLE(
  HOP(
    TABLE orders4,
    DESCRIPTOR(ts),
    INTERVAL '1' SECONDS,   -- Slide interval
    INTERVAL '5' SECONDS    -- Window size
  )
)
GROUP BY
  stock_id,
  window_start,
  window_end;

```

## 📊 API Endpoints

- `GET /stocks/stocks`: List all available stocks
- `GET /stocks/stocks/{stock_id}`: Get specific stock details
- `GET /stocks/stocks/{stock_id}/history`: Get price history
- `POST /trades/orders`: Place buy/sell orders

## 🔍 Monitoring

1. **Application Logs**
   - Backend logs: `logs/app.log`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

