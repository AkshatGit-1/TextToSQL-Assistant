-- Minimal deterministic database fixture for CI.
-- This is not the production Olist dataset.

BEGIN;

TRUNCATE
    analytics.fact_reviews,
    analytics.fact_payments,
    analytics.fact_order_items,
    analytics.fact_orders,
    analytics.dim_payment_type,
    analytics.dim_order_status,
    analytics.dim_seller,
    analytics.dim_product,
    analytics.dim_customer,
    analytics.dim_date
RESTART IDENTITY CASCADE;

INSERT INTO analytics.dim_customer (
    customer_key,
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
)
VALUES
    (1, 'cust_001', 'unique_001', 10001, 'city_a', 'SP'),
    (2, 'cust_002', 'unique_002', 20002, 'city_b', 'RJ'),
    (3, 'cust_003', 'unique_003', 30003, 'city_c', 'MG'),
    (4, 'cust_004', 'unique_004', 40004, 'city_d', 'RS'),
    (5, 'cust_005', 'unique_005', 50005, 'city_e', 'PR'),
    (6, 'cust_006', 'unique_006', 60006, 'city_f', 'BA');

INSERT INTO analytics.dim_product (
    product_key,
    product_id,
    product_category_name,
    product_category_name_english
)
VALUES
    (1, 'prod_001', 'eletronicos', 'electronics'),
    (2, 'prod_002', 'livros', 'books'),
    (3, 'prod_003', 'esporte', 'sports');

INSERT INTO analytics.dim_seller (
    seller_key,
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
)
VALUES
    (1, 'seller_001', 11111, 'seller_a', 'SP'),
    (2, 'seller_002', 22222, 'seller_b', 'RJ'),
    (3, 'seller_003', 33333, 'seller_c', 'MG');

INSERT INTO analytics.dim_order_status (
    order_status_key,
    order_status
)
VALUES
    (1, 'delivered'),
    (2, 'shipped'),
    (3, 'canceled');

INSERT INTO analytics.dim_payment_type (
    payment_type_key,
    payment_type
)
VALUES
    (1, 'credit_card'),
    (2, 'boleto');

INSERT INTO analytics.fact_orders (
    order_id,
    customer_key,
    order_status_key,
    order_purchase_timestamp,
    order_delivered_customer_date
)
VALUES
    ('order_001', 1, 1, '2018-01-10 10:00:00', '2018-01-15 10:00:00'),
    ('order_002', 1, 1, '2018-01-20 11:00:00', '2018-01-24 11:00:00'),
    ('order_003', 2, 1, '2018-02-05 09:00:00', '2018-02-12 09:00:00'),
    ('order_004', 2, 2, '2018-02-15 12:00:00', NULL),
    ('order_005', 3, 1, '2018-03-03 13:00:00', '2018-03-10 13:00:00'),
    ('order_006', 3, 1, '2018-03-18 14:00:00', '2018-03-23 14:00:00'),
    ('order_007', 4, 1, '2018-04-02 15:00:00', '2018-04-08 15:00:00'),
    ('order_008', 5, 3, '2018-04-20 16:00:00', NULL),
    ('order_009', 6, 1, '2018-05-01 17:00:00', '2018-05-06 17:00:00'),
    ('order_010', 6, 1, '2018-05-15 18:00:00', '2018-05-22 18:00:00');

INSERT INTO analytics.fact_order_items (
    order_id,
    order_item_id,
    product_key,
    seller_key,
    price,
    freight_value
)
VALUES
    ('order_001', 1, 1, 1, 100.00, 10.00),
    ('order_002', 1, 2, 2, 200.00, 15.00),
    ('order_003', 1, 1, 1, 300.00, 20.00),
    ('order_004', 1, 3, 3, 150.00, 12.00),
    ('order_005', 1, 2, 2, 250.00, 18.00),
    ('order_006', 1, 1, 1, 350.00, 25.00),
    ('order_007', 1, 3, 3, 175.00, 14.00),
    ('order_008', 1, 2, 2, 225.00, 16.00),
    ('order_009', 1, 1, 1, 400.00, 30.00),
    ('order_010', 1, 3, 3, 125.00, 11.00);

INSERT INTO analytics.fact_payments (
    order_id,
    payment_sequential,
    payment_type_key,
    payment_installments,
    payment_value
)
SELECT
    order_id,
    1,
    CASE
        WHEN order_id IN ('order_001', 'order_003', 'order_005', 'order_007', 'order_009')
        THEN 1
        ELSE 2
    END,
    1,
    (
        SELECT SUM(price)
        FROM analytics.fact_order_items oi
        WHERE oi.order_id = o.order_id
    )
FROM analytics.fact_orders o;

INSERT INTO analytics.fact_reviews (
    review_id,
    order_id,
    review_score
)
VALUES
    ('review_001', 'order_001', 5),
    ('review_002', 'order_002', 4),
    ('review_003', 'order_003', 5),
    ('review_004', 'order_004', 3),
    ('review_005', 'order_005', 4),
    ('review_006', 'order_006', 5),
    ('review_007', 'order_007', 4),
    ('review_008', 'order_008', 2),
    ('review_009', 'order_009', 5),
    ('review_010', 'order_010', 4);

COMMIT;