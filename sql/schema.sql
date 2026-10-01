CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week INTEGER NOT NULL,
    day INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.dim_customer (
    customer_key BIGSERIAL PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE,
    customer_unique_id TEXT,
    customer_zip_code_prefix INTEGER,
    customer_city TEXT,
    customer_state TEXT
);

CREATE TABLE IF NOT EXISTS analytics.dim_product (
    product_key BIGSERIAL PRIMARY KEY,
    product_id TEXT NOT NULL UNIQUE,
    product_category_name TEXT,
    product_category_name_english TEXT,
    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,
    product_weight_g NUMERIC,
    product_length_cm NUMERIC,
    product_height_cm NUMERIC,
    product_width_cm NUMERIC
);

CREATE TABLE IF NOT EXISTS analytics.dim_seller (
    seller_key BIGSERIAL PRIMARY KEY,
    seller_id TEXT NOT NULL UNIQUE,
    seller_zip_code_prefix INTEGER,
    seller_city TEXT,
    seller_state TEXT
);

CREATE TABLE IF NOT EXISTS analytics.dim_order_status (
    order_status_key SMALLSERIAL PRIMARY KEY,
    order_status TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS analytics.dim_payment_type (
    payment_type_key SMALLSERIAL PRIMARY KEY,
    payment_type TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS analytics.fact_orders (
    order_key BIGSERIAL PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE,

    customer_key BIGINT NOT NULL,
    order_status_key SMALLINT NOT NULL,

    purchase_date_key INTEGER,
    approved_date_key INTEGER,
    delivered_carrier_date_key INTEGER,
    delivered_customer_date_key INTEGER,
    estimated_delivery_date_key INTEGER,

    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,

    FOREIGN KEY (customer_key)
        REFERENCES analytics.dim_customer(customer_key),

    FOREIGN KEY (order_status_key)
        REFERENCES analytics.dim_order_status(order_status_key),

    FOREIGN KEY (purchase_date_key)
        REFERENCES analytics.dim_date(date_key),

    FOREIGN KEY (approved_date_key)
        REFERENCES analytics.dim_date(date_key),

    FOREIGN KEY (delivered_carrier_date_key)
        REFERENCES analytics.dim_date(date_key),

    FOREIGN KEY (delivered_customer_date_key)
        REFERENCES analytics.dim_date(date_key),

    FOREIGN KEY (estimated_delivery_date_key)
        REFERENCES analytics.dim_date(date_key)
);


CREATE TABLE IF NOT EXISTS analytics.fact_order_items (
    order_item_key BIGSERIAL PRIMARY KEY,

    order_id TEXT NOT NULL,
    order_item_id INTEGER NOT NULL,

    product_key BIGINT NOT NULL,
    seller_key BIGINT NOT NULL,

    shipping_limit_date TIMESTAMP,
    price NUMERIC(12,2),
    freight_value NUMERIC(12,2),

    FOREIGN KEY (order_id)
        REFERENCES analytics.fact_orders(order_id),

    FOREIGN KEY (product_key)
        REFERENCES analytics.dim_product(product_key),

    FOREIGN KEY (seller_key)
        REFERENCES analytics.dim_seller(seller_key),

    UNIQUE (order_id, order_item_id)
);


CREATE TABLE IF NOT EXISTS analytics.fact_payments (
    payment_key BIGSERIAL PRIMARY KEY,

    order_id TEXT NOT NULL,
    payment_sequential INTEGER NOT NULL,

    payment_type_key SMALLINT NOT NULL,

    payment_installments INTEGER,
    payment_value NUMERIC(12,2),

    FOREIGN KEY (order_id)
        REFERENCES analytics.fact_orders(order_id),

    FOREIGN KEY (payment_type_key)
        REFERENCES analytics.dim_payment_type(payment_type_key),

    UNIQUE (order_id, payment_sequential)
);


CREATE TABLE IF NOT EXISTS analytics.fact_reviews (
    review_key BIGSERIAL PRIMARY KEY,

    review_id TEXT NOT NULL,
    order_id TEXT NOT NULL,

    review_score INTEGER,

    review_comment_title TEXT,
    review_comment_message TEXT,

    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP,

    FOREIGN KEY (order_id)
        REFERENCES analytics.fact_orders(order_id),

    UNIQUE (review_id, order_id)
);