# Few-Shot SQL Examples

These examples are used to guide the LLM when generating SQL
for the Olist analytics schema.

## Example 1 — Total Sales

Question:
What are the total sales?

SQL:
SELECT ROUND(SUM(i.price), 2) AS total_sales
FROM analytics.fact_order_items i;


## Example 2 — Sales by Customer State

Question:
What are the total sales by customer state?

SQL:
SELECT
    c.customer_state,
    ROUND(SUM(i.price), 2) AS total_sales
FROM analytics.fact_order_items i
JOIN analytics.fact_orders o
    ON i.order_id = o.order_id
JOIN analytics.dim_customer c
    ON o.customer_key = c.customer_key
GROUP BY c.customer_state
ORDER BY total_sales DESC;


## Example 3 — Orders by Month

Question:
How many orders were placed each month?

SQL:
SELECT
    d.year,
    d.month,
    COUNT(DISTINCT o.order_id) AS order_count
FROM analytics.fact_orders o
JOIN analytics.dim_date d
    ON o.purchase_date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;


## Example 4 — Sales by Product Category

Question:
What are the total sales by product category?

SQL:
SELECT
    p.product_category_name_english AS product_category,
    ROUND(SUM(i.price), 2) AS total_sales
FROM analytics.fact_order_items i
JOIN analytics.dim_product p
    ON i.product_key = p.product_key
GROUP BY p.product_category_name_english
ORDER BY total_sales DESC;


## Example 5 — Payment Type

Question:
Which payment type has the highest payment value?

SQL:
SELECT
    p.payment_type,
    ROUND(SUM(f.payment_value), 2) AS total_payment_value
FROM analytics.fact_payments f
JOIN analytics.dim_payment_type p
    ON f.payment_type_key = p.payment_type_key
GROUP BY p.payment_type
ORDER BY total_payment_value DESC
LIMIT 1;


## Example 6 — Average Review Score

Question:
What is the average review score?

SQL:
SELECT
    ROUND(AVG(review_score), 2) AS average_review_score
FROM analytics.fact_reviews;


## Example 7 — Review Score by Product Category

Question:
What is the average review score by product category?

SQL:
SELECT
    p.product_category_name_english AS product_category,
    ROUND(AVG(r.review_score), 2) AS average_review_score
FROM analytics.fact_reviews r
JOIN analytics.fact_orders o
    ON r.order_id = o.order_id
JOIN analytics.fact_order_items i
    ON o.order_id = i.order_id
JOIN analytics.dim_product p
    ON i.product_key = p.product_key
GROUP BY p.product_category_name_english
ORDER BY average_review_score DESC;


## Example 8 — Orders by Status

Question:
How many orders are there by order status?

SQL:
SELECT
    s.order_status,
    COUNT(DISTINCT o.order_id) AS order_count
FROM analytics.fact_orders o
JOIN analytics.dim_order_status s
    ON o.order_status_key = s.order_status_key
GROUP BY s.order_status
ORDER BY order_count DESC;


## Example 9 — Average Delivery Time

Question:
What is the average delivery time in days?

SQL:
SELECT
    ROUND(
        AVG(
            EXTRACT(
                EPOCH FROM (
                    o.order_delivered_customer_date
                    - o.order_purchase_timestamp
                )
            ) / 86400
        ),
        2
    ) AS average_delivery_days
FROM analytics.fact_orders o
WHERE o.order_delivered_customer_date IS NOT NULL;


## Example 10 — Sales by Seller State

Question:
What are the total sales by seller state?

SQL:
SELECT
    s.seller_state,
    ROUND(SUM(i.price), 2) AS total_sales
FROM analytics.fact_order_items i
JOIN analytics.dim_seller s
    ON i.seller_key = s.seller_key
GROUP BY s.seller_state
ORDER BY total_sales DESC;