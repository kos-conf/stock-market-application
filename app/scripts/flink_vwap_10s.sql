-- Flink SQL: 10-second VWAP Calculation

CREATE TABLE orders (
  order_id STRING,
  user_id STRING,
  stock_symbol STRING,
  order_type STRING, -- 'buy' or 'sell'
  order_price DOUBLE,
  order_volume INT,
  event_time TIMESTAMP(3),
  WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
) WITH (
  'connector' = 'kafka',
  'topic' = 'order',
  'properties.bootstrap.servers' = '<KAFKA_BOOTSTRAP_SERVERS>',
  'format' = 'json',
  'scan.startup.mode' = 'earliest-offset'
);
-- Source table: trade_event
CREATE TABLE trade_event (
  stock_symbol STRING,
  trade_price DOUBLE,
  trade_volume INT,
  event_time TIMESTAMP(3),
  WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
) WITH (
  'connector' = 'kafka',
  'topic' = 'trade_event',
  'properties.bootstrap.servers' = '<KAFKA_BOOTSTRAP_SERVERS>',
  'properties.group.id' = 'flink-trade-consumer',
  'format' = 'json',
  'scan.startup.mode' = 'earliest-offset'
);

-- Naive matching: match buy and sell at same price, symbol, and window
INSERT INTO trade_event
SELECT
  b.stock_symbol,
  b.order_price AS trade_price,
  LEAST(b.order_volume, s.order_volume) AS trade_volume,
  b.event_time AS event_time
FROM
  orders b
JOIN
  orders s
ON
  b.stock_symbol = s.stock_symbol
  AND b.order_price = s.order_price
  AND b.order_type = 'buy'
  AND s.order_type = 'sell'
  AND TUMBLE(b.event_time, INTERVAL '10' SECOND) = TUMBLE(s.event_time, INTERVAL '10' SECOND)
WHERE
  b.user_id <> s.user_id;

-- Sink table: stock_price
CREATE TABLE stock_price (
  stock_symbol STRING,
  vwap DOUBLE,
  window_end TIMESTAMP(3),
  PRIMARY KEY (stock_symbol) NOT ENFORCED
) WITH (
  'connector' = 'upsert-kafka',
  'topic' = 'stock_price',
  'properties.bootstrap.servers' = '<KAFKA_BOOTSTRAP_SERVERS>',
  'key.format' = 'json',
  'value.format' = 'json'
);

-- VWAP calculation with 10-second tumbling window
INSERT INTO stock_price
SELECT
  stock_symbol,
  SUM(trade_price * trade_volume) / SUM(trade_volume) AS vwap,
  TUMBLE_END(event_time, INTERVAL '10' SECOND) AS window_end
FROM trade_event
GROUP BY
  stock_symbol,
  TUMBLE(event_time, INTERVAL '10' SECOND);

-- Replace <KAFKA_BOOTSTRAP_SERVERS> with your Kafka broker address. 