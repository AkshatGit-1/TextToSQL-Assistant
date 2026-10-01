# Business Metrics

This document defines the approved business metrics for the Text-to-SQL Analytics Assistant.

## Sales

### total_sales
Definition:
Sum of product item prices.

SQL logic:
SUM(analytics.fact_order_items.price)

Do not use payment_value for total_sales.

### total_payment_value
Definition:
Total value recorded in customer payments.

SQL logic:
SUM(analytics.fact_payments.payment_value)

This is different from total_sales.

## Orders

### order_count
Definition:
Number of unique orders.

SQL logic:
COUNT(DISTINCT analytics.fact_orders.order_id)

### item_count
Definition:
Number of order items.

SQL logic:
COUNT(*)
from analytics.fact_order_items

## Customers

### customer_count
Definition:
Number of unique customers.

SQL logic:
COUNT(DISTINCT analytics.dim_customer.customer_unique_id)

### customer_order_count
Definition:
Number of unique orders associated with customers.

SQL logic:
COUNT(DISTINCT analytics.fact_orders.order_id)

## Average Order Value

### average_order_value
Definition:
Total sales divided by unique order count.

SQL logic:
SUM(analytics.fact_order_items.price)
/
COUNT(DISTINCT analytics.fact_orders.order_id)

## Delivery

### average_delivery_days
Definition:
Average number of days between order purchase and customer delivery.

SQL logic:
AVG(
    EXTRACT(
        EPOCH FROM (
            analytics.fact_orders.order_delivered_customer_date
            -
            analytics.fact_orders.order_purchase_timestamp
        )
    ) / 86400
)

Only include records where order_delivered_customer_date IS NOT NULL.

## Reviews

### average_review_score
Definition:
Average customer review score.

SQL logic:
AVG(analytics.fact_reviews.review_score)

Valid review scores:
1 through 5.

## Important Metric Rules

1. Never treat payment_value as total_sales.
2. Use COUNT(DISTINCT order_id) for order counts.
3. Do not count order items as orders.
4. Use fact_order_items.price for product sales.
5. Use fact_payments.payment_value for payment value.
6. Use customer_unique_id when measuring unique customers across customer records.
7. Use delivered_customer_date when calculating customer delivery time.
8. If a requested metric cannot be calculated from the available schema, do not invent it.
9. If a business term is ambiguous, ask for clarification when necessary.