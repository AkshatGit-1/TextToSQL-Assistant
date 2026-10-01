from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


def load_dimensions():
    with engine.begin() as conn:

        # Date dimension
        conn.execute(text("""
            INSERT INTO analytics.dim_date (
                date_key,
                full_date,
                year,
                quarter,
                month,
                month_name,
                week,
                day,
                day_name
            )
            SELECT DISTINCT
                TO_CHAR(d::date, 'YYYYMMDD')::INTEGER,
                d::date,
                EXTRACT(YEAR FROM d)::INTEGER,
                EXTRACT(QUARTER FROM d)::INTEGER,
                EXTRACT(MONTH FROM d)::INTEGER,
                TO_CHAR(d::date, 'FMMonth'),
                EXTRACT(WEEK FROM d)::INTEGER,
                EXTRACT(DAY FROM d)::INTEGER,
                TO_CHAR(d::date, 'FMDay')
            FROM generate_series(
                '2016-01-01'::date,
                '2020-12-31'::date,
                '1 day'
            ) AS d
            ON CONFLICT (date_key) DO NOTHING;
        """))

        # Customer dimension
        conn.execute(text("""
            INSERT INTO analytics.dim_customer (
                customer_id,
                customer_unique_id,
                customer_zip_code_prefix,
                customer_city,
                customer_state
            )
            SELECT
                customer_id,
                customer_unique_id,
                customer_zip_code_prefix,
                customer_city,
                customer_state
            FROM raw_customers
            ON CONFLICT (customer_id) DO NOTHING;
        """))

        # Product dimension
        conn.execute(text("""
            INSERT INTO analytics.dim_product (
                product_id,
                product_category_name,
                product_category_name_english,
                product_name_length,
                product_description_length,
                product_photos_qty,
                product_weight_g,
                product_length_cm,
                product_height_cm,
                product_width_cm
            )
            SELECT
                p.product_id,
                p.product_category_name,
                t.product_category_name_english,
                p.product_name_lenght::INTEGER,
                p.product_description_lenght::INTEGER,
                p.product_photos_qty::INTEGER,
                p.product_weight_g,
                p.product_length_cm,
                p.product_height_cm,
                p.product_width_cm
            FROM raw_products p
            LEFT JOIN raw_product_category_translation t
                ON p.product_category_name = t.product_category_name
            ON CONFLICT (product_id) DO NOTHING;
        """))

        # Seller dimension
        conn.execute(text("""
            INSERT INTO analytics.dim_seller (
                seller_id,
                seller_zip_code_prefix,
                seller_city,
                seller_state
            )
            SELECT
                seller_id,
                seller_zip_code_prefix,
                seller_city,
                seller_state
            FROM raw_sellers
            ON CONFLICT (seller_id) DO NOTHING;
        """))

        # Order status dimension
        conn.execute(text("""
            INSERT INTO analytics.dim_order_status (order_status)
            SELECT DISTINCT order_status
            FROM raw_orders
            WHERE order_status IS NOT NULL
            ON CONFLICT (order_status) DO NOTHING;
        """))

        # Payment type dimension
        conn.execute(text("""
            INSERT INTO analytics.dim_payment_type (payment_type)
            SELECT DISTINCT payment_type
            FROM raw_order_payments
            WHERE payment_type IS NOT NULL
            ON CONFLICT (payment_type) DO NOTHING;
        """))


def load_fact_orders():
    query = """
        INSERT INTO analytics.fact_orders (
            order_id,
            customer_key,
            order_status_key,
            purchase_date_key,
            approved_date_key,
            delivered_carrier_date_key,
            delivered_customer_date_key,
            estimated_delivery_date_key,
            order_purchase_timestamp,
            order_approved_at,
            order_delivered_carrier_date,
            order_delivered_customer_date,
            order_estimated_delivery_date
        )
        SELECT
            o.order_id,
            c.customer_key,
            s.order_status_key,

            TO_CHAR(
                o.order_purchase_timestamp::timestamp,
                'YYYYMMDD'
            )::INTEGER,

            CASE
                WHEN o.order_approved_at IS NOT NULL
                THEN TO_CHAR(
                    o.order_approved_at::timestamp,
                    'YYYYMMDD'
                )::INTEGER
            END,

            CASE
                WHEN o.order_delivered_carrier_date IS NOT NULL
                THEN TO_CHAR(
                    o.order_delivered_carrier_date::timestamp,
                    'YYYYMMDD'
                )::INTEGER
            END,

            CASE
                WHEN o.order_delivered_customer_date IS NOT NULL
                THEN TO_CHAR(
                    o.order_delivered_customer_date::timestamp,
                    'YYYYMMDD'
                )::INTEGER
            END,

            CASE
                WHEN o.order_estimated_delivery_date IS NOT NULL
                THEN TO_CHAR(
                    o.order_estimated_delivery_date::timestamp,
                    'YYYYMMDD'
                )::INTEGER
            END,

            o.order_purchase_timestamp::timestamp,
            NULLIF(o.order_approved_at, '')::timestamp,
            NULLIF(o.order_delivered_carrier_date, '')::timestamp,
            NULLIF(o.order_delivered_customer_date, '')::timestamp,
            NULLIF(o.order_estimated_delivery_date, '')::timestamp

        FROM raw_orders o
        JOIN analytics.dim_customer c
            ON o.customer_id = c.customer_id
        JOIN analytics.dim_order_status s
            ON o.order_status = s.order_status
        ON CONFLICT (order_id) DO NOTHING;
    """

    with engine.begin() as conn:
        conn.execute(text(query))


def load_fact_order_items():
    query = """
        INSERT INTO analytics.fact_order_items (
            order_id,
            order_item_id,
            product_key,
            seller_key,
            shipping_limit_date,
            price,
            freight_value
        )
        SELECT
            i.order_id,
            i.order_item_id::INTEGER,
            p.product_key,
            s.seller_key,
            NULLIF(i.shipping_limit_date, '')::timestamp,
            i.price::NUMERIC(12,2),
            i.freight_value::NUMERIC(12,2)
        FROM raw_order_items i
        JOIN analytics.dim_product p
            ON i.product_id = p.product_id
        JOIN analytics.dim_seller s
            ON i.seller_id = s.seller_id
        JOIN analytics.fact_orders o
            ON i.order_id = o.order_id
        ON CONFLICT (order_id, order_item_id) DO NOTHING;
    """

    with engine.begin() as conn:
        conn.execute(text(query))


def load_fact_payments():
    query = """
        INSERT INTO analytics.fact_payments (
            order_id,
            payment_sequential,
            payment_type_key,
            payment_installments,
            payment_value
        )
        SELECT
            p.order_id,
            p.payment_sequential::INTEGER,
            pt.payment_type_key,
            p.payment_installments::INTEGER,
            p.payment_value::NUMERIC(12,2)
        FROM raw_order_payments p
        JOIN analytics.dim_payment_type pt
            ON p.payment_type = pt.payment_type
        JOIN analytics.fact_orders o
            ON p.order_id = o.order_id
        ON CONFLICT (order_id, payment_sequential) DO NOTHING;
    """

    with engine.begin() as conn:
        conn.execute(text(query))


def load_fact_reviews():
    query = """
        INSERT INTO analytics.fact_reviews (
            review_id,
            order_id,
            review_score,
            review_comment_title,
            review_comment_message,
            review_creation_date,
            review_answer_timestamp
        )
        SELECT
            r.review_id,
            r.order_id,
            r.review_score::INTEGER,
            r.review_comment_title,
            r.review_comment_message,
            NULLIF(r.review_creation_date, '')::timestamp,
            NULLIF(r.review_answer_timestamp, '')::timestamp
        FROM raw_order_reviews r
        JOIN analytics.fact_orders o
            ON r.order_id = o.order_id
        ON CONFLICT (review_id, order_id) DO NOTHING;
    """

    with engine.begin() as conn:
        conn.execute(text(query))


def main():
    print("Loading dimensions...")
    load_dimensions()

    print("Loading fact_orders...")
    load_fact_orders()

    print("Loading fact_order_items...")
    load_fact_order_items()

    print("Loading fact_payments...")
    load_fact_payments()

    print("Loading fact_reviews...")
    load_fact_reviews()

    print("\nAnalytics star schema loaded successfully.")


if __name__ == "__main__":
    main()