from core.providers.base import LLMProvider


class MockProvider(LLMProvider):
    """Mock provider for local development and testing."""

    def generate(self, prompt: str) -> str:
        """Generate deterministic SQL for supported development questions."""
        self.validate_prompt(prompt)

        question = self._extract_user_question(prompt)
        normalized_question = question.lower()
        
        if "average delivery time" in normalized_question:
            return (
                "SELECT "
                "AVG(order_delivered_customer_date - order_purchase_timestamp) "
                "AS average_delivery_time "
                "FROM analytics.fact_orders "
                "WHERE order_delivered_customer_date IS NOT NULL;"
            )
        
        if (
            "average review score" in normalized_question
            and "product category" not in normalized_question
        ):
            return (
                "SELECT "
                "AVG(review_score) AS average_review_score "
                "FROM analytics.fact_reviews;"
            )

        if (
            "total sales by seller state" in normalized_question
            or (
                "sales by seller state" in normalized_question
                and "seller" in normalized_question
            )
        ):
            return (
                "SELECT "
                "s.seller_state, "
                "SUM(oi.price) AS total_sales "
                "FROM analytics.fact_order_items oi "
                "JOIN analytics.dim_seller s "
                "ON oi.seller_key = s.seller_key "
                "GROUP BY s.seller_state "
                "ORDER BY total_sales DESC;"
            )
        if (
            "show only the top 5" in normalized_question
            and "customer_state" in prompt
        ):
            return (
                "SELECT "
                "c.customer_state, "
                "SUM(oi.price) AS total_sales "
                "FROM analytics.fact_order_items oi "
                "JOIN analytics.fact_orders o "
                "ON oi.order_id = o.order_id "
                "JOIN analytics.dim_customer c "
                "ON o.customer_key = c.customer_key "
                "GROUP BY c.customer_state "
                "ORDER BY total_sales DESC "
                "LIMIT 5;"
            )

        if "what are the total sales by customer state" in normalized_question:
            return (
                "SELECT "
                "c.customer_state, "
                "SUM(oi.price) AS total_sales "
                "FROM analytics.fact_order_items oi "
                "JOIN analytics.fact_orders o "
                "ON oi.order_id = o.order_id "
                "JOIN analytics.dim_customer c "
                "ON o.customer_key = c.customer_key "
                "GROUP BY c.customer_state "
                "ORDER BY total_sales DESC;"
            )

        if "what are the total sales" in normalized_question:
            return (
                "SELECT "
                "SUM(price) AS total_sales "
                "FROM analytics.fact_order_items;"
            )

        if "how many orders are there by month" in normalized_question:
            return (
                "SELECT "
                "DATE_TRUNC('month', order_purchase_timestamp) AS order_month, "
                "COUNT(DISTINCT order_id) AS order_count "
                "FROM analytics.fact_orders "
                "GROUP BY order_month "
                "ORDER BY order_month;"
            )

        if "what is the average review score by product category" in normalized_question:
            return (
                "SELECT "
                "p.product_category_name_english AS product_category, "
                "AVG(r.review_score) AS average_review_score "
                "FROM analytics.fact_reviews r "
                "JOIN analytics.fact_order_items oi "
                "ON r.order_id = oi.order_id "
                "JOIN analytics.dim_product p "
                "ON oi.product_key = p.product_key "
                "GROUP BY p.product_category_name_english "
                "ORDER BY average_review_score DESC;"
            )

        if "what are the orders by order status" in normalized_question:
            return (
                "SELECT "
                "s.order_status, "
                "COUNT(DISTINCT o.order_id) AS order_count "
                "FROM analytics.fact_orders o "
                "JOIN analytics.dim_order_status s "
                "ON o.order_status_key = s.order_status_key "
                "GROUP BY s.order_status "
                "ORDER BY order_count DESC;"
            )

        return (
            "SELECT "
            "COUNT(DISTINCT order_id) AS order_count "
            "FROM analytics.fact_orders;"
        )

    @staticmethod
    def _extract_user_question(prompt: str) -> str:
        """Extract the user question from a full prompt or plain input."""
        marker = "USER QUESTION:"

        if marker not in prompt:
            question = prompt.strip()
        else:
            question_section = prompt.split(marker, 1)[1]

            if "FOCUSED SCHEMA:" in question_section:
                question_section = question_section.split(
                    "FOCUSED SCHEMA:",
                    1,
                )[0]

            question = question_section.strip()

        if not question:
            raise ValueError("User question is empty.")

        return question