# Analytics Schema Context

## Schema

All approved Text-to-SQL queries must use the `analytics` schema.

## Dimensions

### analytics.dim_date
Grain: One row per calendar date.

Columns:
- date_key: INTEGER, primary key
- full_date: DATE
- year: INTEGER
- quarter: INTEGER
- month: INTEGER
- month_name: VARCHAR
- week: INTEGER
- day: INTEGER
- day_name: VARCHAR

### analytics.dim_customer
Grain: One row per customer_id.

Columns:
- customer_key: BIGINT, primary key
- customer_id: TEXT, unique
- customer_unique_id: TEXT
- customer_zip_code_prefix: INTEGER
- customer_city: TEXT
- customer_state: TEXT

### analytics.dim_product
Grain: One row per product.

Columns:
- product_key: BIGINT, primary key
- product_id: TEXT, unique
- product_category_name: TEXT
- product_category_name_english: TEXT
- product_name_length: INTEGER
- product_description_length: INTEGER
- product_photos_qty: INTEGER
- product_weight_g: NUMERIC
- product_length_cm: NUMERIC
- product_height_cm: NUMERIC
- product_width_cm: NUMERIC

### analytics.dim_seller
Grain: One row per seller.

Columns:
- seller_key: BIGINT, primary key
- seller_id: TEXT, unique
- seller_zip_code_prefix: INTEGER
- seller_city: TEXT
- seller_state: TEXT

### analytics.dim_order_status
Grain: One row per order status.

Columns:
- order_status_key: SMALLINT, primary key
- order_status: TEXT, unique

### analytics.dim_payment_type
Grain: One row per payment type.

Columns:
- payment_type_key: SMALLINT, primary key
- payment_type: TEXT, unique

## Facts

### analytics.fact_orders
Grain: One row per order.

Important columns:
- order_id: TEXT, unique
- customer_key: BIGINT
- order_status_key: SMALLINT
- purchase_date_key: INTEGER
- approved_date_key: INTEGER
- delivered_carrier_date_key: INTEGER
- delivered_customer_date_key: INTEGER
- estimated_delivery_date_key: INTEGER
- order_purchase_timestamp: TIMESTAMP
- order_approved_at: TIMESTAMP
- order_delivered_carrier_date: TIMESTAMP
- order_delivered_customer_date: TIMESTAMP
- order_estimated_delivery_date: TIMESTAMP

### analytics.fact_order_items
Grain: One row per order item.

Important columns:
- order_id: TEXT
- order_item_id: INTEGER
- product_key: BIGINT
- seller_key: BIGINT
- shipping_limit_date: TIMESTAMP
- price: NUMERIC
- freight_value: NUMERIC

### analytics.fact_payments
Grain: One row per payment.

Important columns:
- order_id: TEXT
- payment_sequential: INTEGER
- payment_type_key: SMALLINT
- payment_installments: INTEGER
- payment_value: NUMERIC

### analytics.fact_reviews
Grain: One row per review_id + order_id.

Important columns:
- review_id: TEXT
- order_id: TEXT
- review_score: INTEGER
- review_comment_title: TEXT
- review_comment_message: TEXT
- review_creation_date: TIMESTAMP
- review_answer_timestamp: TIMESTAMP

## Relationships

fact_orders.customer_key
→ dim_customer.customer_key

fact_orders.order_status_key
→ dim_order_status.order_status_key

fact_orders.purchase_date_key
→ dim_date.date_key

fact_orders.approved_date_key
→ dim_date.date_key

fact_orders.delivered_carrier_date_key
→ dim_date.date_key

fact_orders.delivered_customer_date_key
→ dim_date.date_key

fact_orders.estimated_delivery_date_key
→ dim_date.date_key

fact_order_items.order_id
→ fact_orders.order_id

fact_order_items.product_key
→ dim_product.product_key

fact_order_items.seller_key
→ dim_seller.seller_key

fact_payments.order_id
→ fact_orders.order_id

fact_payments.payment_type_key
→ dim_payment_type.payment_type_key

fact_reviews.order_id
→ fact_orders.order_id

## Query Rules

1. Use only the `analytics` schema for generated business queries.
2. Prefer dimension attributes instead of raw-table columns.
3. Use fact table grain correctly.
4. Use `COUNT(DISTINCT order_id)` for order counts.
5. Use `fact_order_items.price` for product sales.
6. Use `fact_payments.payment_value` for payment value.
7. Use appropriate date keys or timestamps for date analysis.
8. Do not invent columns or relationships.
9. When a requested metric is unavailable, do not fabricate it.