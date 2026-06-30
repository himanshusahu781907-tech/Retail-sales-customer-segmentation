-- schema.sql
-- Run this first to create tables, then load data/raw/customers.csv and orders.csv
-- (e.g. via MySQL Workbench "Table Data Import Wizard", or pgAdmin's \copy, or sqlite3 .import)

CREATE TABLE customers (
    customer_id   VARCHAR(10) PRIMARY KEY,
    city          VARCHAR(50),
    city_tier     VARCHAR(10),
    signup_date   DATE
);

CREATE TABLE orders (
    order_id        VARCHAR(10) PRIMARY KEY,
    customer_id     VARCHAR(10) REFERENCES customers(customer_id),
    order_date      DATE,
    category        VARCHAR(50),
    product         VARCHAR(100),
    unit_price      DECIMAL(10,2),
    quantity        INT,
    discount_pct    INT,
    gross_amount    DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    net_amount      DECIMAL(10,2),
    payment_method  VARCHAR(30),
    order_status    VARCHAR(20)
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_category ON orders(category);
