import re
from pathlib import Path

from core.schema_context import load_schema_context


BASE_DIR = Path(__file__).resolve().parents[1]


TABLE_KEYWORDS = {
    "orders": [
        "order",
        "orders",
        "purchase",
        "delivery",
        "delivered",
        "status",
    ],
    "order_items": [
        "item",
        "items",
        "product",
        "products",
        "sales",
        "revenue",
        "price",
        "freight",
    ],
    "payments": [
        "payment",
        "payments",
        "paid",
        "installment",
        "installments",
    ],
    "reviews": [
        "review",
        "reviews",
        "rating",
        "score",
    ],
    "customers": [
        "customer",
        "customers",
        "buyer",
        "buyers",
        "state",
        "city",
    ],
    "products": [
        "product",
        "products",
        "category",
        "categories",
    ],
    "sellers": [
        "seller",
        "sellers",
        "vendor",
        "vendors",
    ],
    "date": [
        "date",
        "year",
        "month",
        "quarter",
        "weekly",
        "monthly",
        "daily",
        "trend",
    ],
    "order_status": [
        "status",
        "delivered",
        "shipped",
        "canceled",
        "cancelled",
        "processing",
        "approved",
        "invoiced",
        "unavailable",
        "created",
    ],
    
    "payment_type": [
        "payment type",
        "payment method",
        "credit card",
        "debit card",
        "boleto",
        "voucher",
    ],
}


TABLE_SECTIONS = {
    "orders": "### analytics.fact_orders",
    "order_items": "### analytics.fact_order_items",
    "payments": "### analytics.fact_payments",
    "reviews": "### analytics.fact_reviews",
    "customers": "### analytics.dim_customer",
    "products": "### analytics.dim_product",
    "sellers": "### analytics.dim_seller",
    "date": "### analytics.dim_date",
    "order_status": "### analytics.dim_order_status",
    "payment_type": "### analytics.dim_payment_type",
}


# Direct relationships between logical table names.
RELATIONSHIPS = {
    "orders": {
        "customers",
        "date",
        "order_items",
        "payments",
        "reviews",
        "order_status",
    },
    "order_items": {"orders", "products", "sellers"},
    "payments": {"orders", "payment_type"},
    "reviews": {"orders"},
    "customers": {"orders"},
    "products": {"order_items"},
    "sellers": {"order_items"},
    "date": {"orders"},
    "order_status": {"orders"},
    "payment_type": {"payments"},
}


def normalize_text(text: str) -> str:
    """Normalize text for simple keyword matching."""
    return re.sub(r"[^a-z0-9_ ]+", " ", text.lower()).strip()


def find_relevant_tables(question: str) -> list[str]:
    """Find tables directly related to the user's question."""
    normalized_question = normalize_text(question)

    matched_tables = []

    for table_name, keywords in TABLE_KEYWORDS.items():
        if any(keyword in normalized_question for keyword in keywords):
            matched_tables.append(table_name)

    return matched_tables


def find_path(
    start: str,
    target: str,
) -> list[str] | None:
    """Find the shortest relationship path between two tables."""
    if start == target:
        return [start]

    queue = [[start]]
    visited = {start}

    while queue:
        path = queue.pop(0)
        current = path[-1]

        for neighbor in RELATIONSHIPS.get(current, set()):
            if neighbor in visited:
                continue

            new_path = path + [neighbor]

            if neighbor == target:
                return new_path

            visited.add(neighbor)
            queue.append(new_path)

    return None


def add_required_relationship_tables(
    tables: list[str],
) -> list[str]:
    """
    Add intermediate tables required to connect all selected tables.
    Uses shortest relationship paths between selected tables.
    """
    if len(tables) <= 1:
        return tables

    selected = set(tables)

    for index in range(len(tables)):
        for other_index in range(index + 1, len(tables)):
            start = tables[index]
            target = tables[other_index]

            path = find_path(start, target)

            if path:
                selected.update(path)

    return [
        table_name
        for table_name in TABLE_SECTIONS
        if table_name in selected
    ]
    
def extract_table_section(schema_text: str, section_heading: str) -> str:
    """Extract one table section without including global sections."""
    lines = schema_text.splitlines()

    start_index = None

    for index, line in enumerate(lines):
        if line.strip() == section_heading:
            start_index = index
            break

    if start_index is None:
        return ""

    collected = []

    for line in lines[start_index:]:
        stripped = line.strip()

        # Stop at another table section or a global section
        if (
            stripped.startswith("### ")
            and stripped != section_heading
        ):
            break

        if stripped.startswith("## "):
            break

        collected.append(line)

    return "\n".join(collected).strip()


def build_schema_context(question: str) -> str:
    """Build a focused, relationship-aware schema context."""
    schema_text = load_schema_context()

    direct_tables = find_relevant_tables(question)

    if not direct_tables:
        return schema_text

    relevant_tables = add_required_relationship_tables(
        direct_tables
    )

    sections = []

    for table_name in relevant_tables:
        heading = TABLE_SECTIONS[table_name]
        section = extract_table_section(schema_text, heading)

        if section:
            sections.append(section)

    return "\n\n".join(sections)


if __name__ == "__main__":
    test_questions = [
        "What are the total sales by customer state?",
        "Which payment type has the highest payment value?",
        "What is the average review score by product category?",
        "How many orders were delivered each month?",
    ]

    for question in test_questions:
        print("\n" + "=" * 70)
        print(f"Question: {question}")

        direct_tables = find_relevant_tables(question)
        final_tables = add_required_relationship_tables(
            direct_tables
        )

        print(f"Direct tables: {direct_tables}")
        print(f"Final tables: {final_tables}")

        print("\nFocused schema:")
        print(build_schema_context(question))