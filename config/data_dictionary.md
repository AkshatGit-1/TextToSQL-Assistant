# Text-to-SQL Analytics Assistant — Data Dictionary

## Raw Layer

### raw_orders
| Column | Type | Description |
|---|---|---|
| order_id | TEXT | Unique order identifier |
| customer_id | TEXT | Customer identifier |
| order_status | TEXT | Current order status |
| order_purchase_timestamp | TEXT | Order purchase timestamp |
| order_approved_at | TEXT | Order approval timestamp |
| order_delivered_carrier_date | TEXT | Date order was handed to carrier |
| order_delivered_customer_date | TEXT | Date order was delivered to customer |
| order_estimated_delivery_date | TEXT | Estimated delivery date |

### raw_order_items
| Column | Type | Description |
|---|---|---|
| order_id | TEXT | Order identifier |
| order_item_id | BIGINT | Item sequence within an order |
| product_id | TEXT | Product identifier |
| seller_id | TEXT | Seller identifier |
| shipping_limit_date | TEXT | Shipping deadline |
| price | DOUBLE PRECISION | Product item price |
| freight_value | DOUBLE PRECISION | Freight/shipping cost |

### raw_order_payments
| Column | Type | Description |
|---|---|---|
| order_id | TEXT | Order identifier |
| payment_sequential | BIGINT | Payment sequence within an order |
| payment_type | TEXT | Payment method |
| payment_installments | BIGINT | Number of installments |
| payment_value | DOUBLE PRECISION | Payment amount |

### raw_order_reviews
| Column | Type | Description |
|---|---|---|
| review_id | TEXT | Review identifier |
| order_id | TEXT | Order identifier |
| review_score | BIGINT | Customer review score from 1 to 5 |
| review_comment_title | TEXT | Review title |
| review_comment_message | TEXT | Review message |
| review_creation_date | TEXT | Review creation timestamp |
| review_answer_timestamp | TEXT | Review answer timestamp |

### raw_customers
| Column | Type | Description |
|---|---|---|
| customer_id | TEXT | Customer identifier |
| customer_unique_id | TEXT | Unique customer identifier across orders |
| customer_zip_code_prefix | BIGINT | Customer ZIP code prefix |
| customer_city | TEXT | Customer city |
| customer_state | TEXT | Customer state |

### raw_products
| Column | Type | Description |
|---|---|---|
| product_id | TEXT | Product identifier |
| product_category_name | TEXT | Original product category |
| product_name_lenght | DOUBLE PRECISION | Product name length |
| product_description_lenght | DOUBLE PRECISION | Product description length |
| product_photos_qty | DOUBLE PRECISION | Number of product photos |
| product_weight_g | DOUBLE PRECISION | Product weight in grams |
| product_length_cm | DOUBLE PRECISION | Product length |
| product_height_cm | DOUBLE PRECISION | Product height |
| product_width_cm | DOUBLE PRECISION | Product width |

### raw_sellers
| Column | Type | Description |
|---|---|---|
| seller_id | TEXT | Seller identifier |
| seller_zip_code_prefix | BIGINT | Seller ZIP code prefix |
| seller_city | TEXT | Seller city |
| seller_state | TEXT | Seller state |

### raw_product_category_translation
| Column | Type | Description |
|---|---|---|
| product_category_name | TEXT | Original Portuguese category name |
| product_category_name_english | TEXT | English category name |

---

# Analytics Layer

## Dimensions

### dim_date
**Grain:** One row per calendar date.

| Column | Description |
|---|---|
| date_key | Integer date key in YYYYMMDD format |
| full_date | Calendar date |
| year | Calendar year |
| quarter | Calendar quarter |
| month | Month number |
| month_name | Month name |
| week | Week number |
| day | Day of month |
| day_name | Day name |

### dim_customer
**Grain:** One row per customer_id.

| Column | Description |
|---|---|
| customer_key | Surrogate customer key |
| customer_id | Source customer identifier |
| customer_unique_id | Unique customer identifier |
| customer_zip_code_prefix | Customer ZIP code prefix |
| customer_city | Customer city |
| customer_state | Customer state |

### dim_product
**Grain:** One row per product.

| Column | Description |
|---|---|
| product_key | Surrogate product key |
| product_id | Source product identifier |
| product_category_name | Original category |
| product_category_name_english | English category |
| product_name_length | Product name length |
| product_description_length | Product description length |
| product_photos_qty | Number of product photos |
| product_weight_g | Product weight |
| product_length_cm | Product length |
| product_height_cm | Product height |
| product_width_cm | Product width |

### dim_seller
**Grain:** One row per seller.

| Column | Description |
|---|---|
| seller_key | Surrogate seller key |
| seller_id | Source seller identifier |
| seller_zip_code_prefix | Seller ZIP code prefix |
| seller_city | Seller city |
| seller_state | Seller state |

### dim_order_status
**Grain:** One row per order status.

| Column | Description |
|---|---|
| order_status_key | Surrogate status key |
| order_status | Order status |

### dim_payment_type
**Grain:** One row per payment type.

| Column | Description |
|---|---|
| payment_type_key | Surrogate payment type key |
| payment_type | Payment method |

---

# Fact Tables

### fact_orders
**Grain:** One row per order.

| Column | Description |
|---|---|
| order_key | Surrogate order key |
| order_id | Source order identifier |
| customer_key | Customer dimension key |
| order_status_key | Order status dimension key |
| purchase_date_key | Purchase date dimension key |
| approved_date_key | Approval date dimension key |
| delivered_carrier_date_key | Carrier delivery date key |
| delivered_customer_date_key | Customer delivery date key |
| estimated_delivery_date_key | Estimated delivery date key |
| order_purchase_timestamp | Purchase timestamp |
| order_approved_at | Approval timestamp |
| order_delivered_carrier_date | Carrier delivery timestamp |
| order_delivered_customer_date | Customer delivery timestamp |
| order_estimated_delivery_date | Estimated delivery timestamp |

### fact_order_items
**Grain:** One row per order item.

| Column | Description |
|---|---|
| order_item_key | Surrogate order-item key |
| order_id | Order identifier |
| order_item_id | Item sequence within order |
| product_key | Product dimension key |
| seller_key | Seller dimension key |
| shipping_limit_date | Shipping deadline |
| price | Item price |
| freight_value | Freight cost |

### fact_payments
**Grain:** One row per payment record.

| Column | Description |
|---|---|
| payment_key | Surrogate payment key |
| order_id | Order identifier |
| payment_sequential | Payment sequence |
| payment_type_key | Payment type dimension key |
| payment_installments | Number of installments |
| payment_value | Payment amount |

### fact_reviews
**Grain:** One row per review_id + order_id combination.

| Column | Description |
|---|---|
| review_key | Surrogate review key |
| review_id | Review identifier |
| order_id | Order identifier |
| review_score | Review score from 1 to 5 |
| review_comment_title | Review title |
| review_comment_message | Review message |
| review_creation_date | Review creation timestamp |
| review_answer_timestamp | Review answer timestamp |

---

# Key Relationships

```text
dim_customer
     |
     v
fact_orders <--------- dim_order_status
     |
     +-----------------> fact_order_items <--------- dim_product
     |                              |
     |                              +---------------> dim_seller
     |
     +-----------------> fact_payments <------------ dim_payment_type
     |
     +-----------------> fact_reviews

fact_orders
     |
     +---- purchase_date_key ------------> dim_date
     +---- approved_date_key ------------> dim_date
     +---- delivered_carrier_date_key --> dim_date
     +---- delivered_customer_date_key -> dim_date
     +---- estimated_delivery_date_key -> dim_date