from sqlglot import exp, parse
from sqlglot.errors import ParseError

from config.schema_allowlist import ALLOWED_SCHEMA, ALLOWED_TABLES


class SQLValidationError(ValueError):
    """Raised when generated SQL violates safety rules."""


def _validate_no_comments(sql: str) -> None:
    """Reject SQL containing comments."""
    if "--" in sql or "/*" in sql or "*/" in sql:
        raise SQLValidationError("SQL comments are not allowed.")


def _validate_single_statement(sql: str) -> exp.Expression:
    """Parse SQL and ensure exactly one statement exists."""
    try:
        statements = parse(sql, read="postgres")
    except ParseError as exc:
        raise SQLValidationError(f"Invalid SQL syntax: {exc}") from exc

    if len(statements) != 1:
        raise SQLValidationError(
            "Multiple SQL statements are not allowed."
        )

    return statements[0]


def _validate_select_only(expression: exp.Expression) -> None:
    """Allow only SELECT statements."""
    if not isinstance(expression, exp.Select):
        raise SQLValidationError(
            "Only SELECT statements are allowed."
        )


def _get_cte_names(expression: exp.Expression) -> set[str]:
    """Return all CTE names."""
    return {
        cte.alias_or_name.lower()
        for cte in expression.find_all(exp.CTE)
        if cte.alias_or_name
    }


def _validate_tables(expression: exp.Expression) -> None:
    """Validate all physical table references."""
    cte_names = _get_cte_names(expression)

    for table in expression.find_all(exp.Table):
        table_name = table.name.lower()

        if table_name in cte_names and not table.db:
            continue

        schema = table.db

        if not schema:
            raise SQLValidationError(
                f"Table '{table.name}' must use the "
                f"'{ALLOWED_SCHEMA}' schema."
            )

        if schema.lower() != ALLOWED_SCHEMA:
            raise SQLValidationError(
                f"Table '{table.name}' uses forbidden schema "
                f"'{schema}'. Only '{ALLOWED_SCHEMA}' is allowed."
            )

        if table_name not in ALLOWED_TABLES:
            raise SQLValidationError(
                f"Table '{table.name}' is not allowed."
            )


def _nearest_select(node: exp.Expression) -> exp.Select | None:
    """Return the nearest SELECT ancestor."""
    current = node.parent

    while current is not None:
        if isinstance(current, exp.Select):
            return current
        current = current.parent

    return None


def _get_local_physical_tables(select: exp.Select) -> dict[str, str]:
    """Return physical table aliases belonging directly to this SELECT."""
    relations: dict[str, str] = {}

    for table in select.find_all(exp.Table):
        if _nearest_select(table) is not select:
            continue

        table_name = table.name.lower()

        if table_name not in ALLOWED_TABLES:
            continue

        if not table.db:
            continue

        alias = table.alias_or_name.lower()
        relations[alias] = table_name

    return relations


def _get_select_outputs(select: exp.Select) -> set[str]:
    """Return columns exposed by a SELECT."""
    outputs: set[str] = set()

    for projection in select.expressions:
        if isinstance(projection, exp.Alias):
            outputs.add(projection.alias.lower())

        elif isinstance(projection, exp.Column):
            outputs.add(projection.name.lower())

        elif isinstance(projection, exp.Star):
            outputs.add("*")

    return outputs


def _get_cte_outputs(expression: exp.Expression) -> dict[str, set[str]]:
    """Return output columns for every CTE."""
    outputs: dict[str, set[str]] = {}

    for cte in expression.find_all(exp.CTE):
        name = cte.alias_or_name

        if not name:
            continue

        query = cte.this

        if isinstance(query, exp.Select):
            outputs[name.lower()] = _get_select_outputs(query)

    return outputs


def _get_subquery_outputs(expression: exp.Expression) -> dict[str, set[str]]:
    """Return output columns for every aliased subquery."""
    outputs: dict[str, set[str]] = {}

    for subquery in expression.find_all(exp.Subquery):
        alias = subquery.alias_or_name

        if not alias:
            continue

        query = subquery.this

        if isinstance(query, exp.Select):
            outputs[alias.lower()] = _get_select_outputs(query)

    return outputs


def _get_local_derived_relations(
    select: exp.Select,
    derived_outputs: dict[str, set[str]],
) -> dict[str, set[str]]:
    """Return CTE/subquery relations visible directly to a SELECT."""
    relations: dict[str, set[str]] = {}

    for table in select.find_all(exp.Table):
        if _nearest_select(table) is not select:
            continue

        if table.db:
            continue

        relation_name = table.name.lower()

        if relation_name in derived_outputs:
            alias = table.alias_or_name.lower()
            relations[alias] = derived_outputs[relation_name]

    for subquery in select.find_all(exp.Subquery):
        if _nearest_select(subquery) is not select:
            continue

        alias = subquery.alias_or_name

        if not alias:
            continue

        query = subquery.this

        if isinstance(query, exp.Select):
            relations[alias.lower()] = _get_select_outputs(query)

    return relations


def _is_select_alias_reference(
    column: exp.Column,
    select: exp.Select,
    output_columns: set[str],
) -> bool:
    """
    Allow SELECT aliases in ORDER BY, GROUP BY and HAVING.
    """
    column_name = column.name.lower()

    if column_name not in output_columns:
        return False

    current = column.parent

    while current is not None and current is not select:
        if isinstance(
            current,
            (
                exp.Order,
                exp.Group,
                exp.Having,
            ),
        ):
            return True

        current = current.parent

    return False


def _validate_select_columns(
    select: exp.Select,
    root_expression: exp.Expression,
) -> None:
    """Validate all column references in one SELECT scope."""
    physical_tables = _get_local_physical_tables(select)

    cte_outputs = _get_cte_outputs(root_expression)
    subquery_outputs = _get_subquery_outputs(root_expression)

    derived_outputs = {
        **cte_outputs,
        **subquery_outputs,
    }

    derived_relations = _get_local_derived_relations(
        select,
        derived_outputs,
    )

    output_columns = _get_select_outputs(select)

    for column in select.find_all(exp.Column):
        if _nearest_select(column) is not select:
            continue

        column_name = column.name.lower()

        if column_name == "*":
            continue

        table_reference = column.table

        if table_reference:
            relation_name = table_reference.lower()

            if relation_name in derived_relations:
                allowed_columns = derived_relations[relation_name]

                if "*" not in allowed_columns and column_name not in allowed_columns:
                    raise SQLValidationError(
                        f"Column '{column.name}' is not available "
                        f"from derived relation '{relation_name}'."
                    )

                continue

            physical_table = physical_tables.get(relation_name)

            if physical_table is None:
                raise SQLValidationError(
                    f"Unknown table or alias '{column.table}'."
                )

            if column_name not in ALLOWED_TABLES[physical_table]:
                raise SQLValidationError(
                    f"Column '{column.name}' is not allowed "
                    f"for table '{physical_table}'."
                )

            continue

        if _is_select_alias_reference(
            column,
            select,
            output_columns,
        ):
            continue

        matching_physical_tables = [
            table_name
            for table_name in physical_tables.values()
            if column_name in ALLOWED_TABLES[table_name]
        ]

        matching_derived_relations = [
            relation_name
            for relation_name, columns in derived_relations.items()
            if "*" in columns or column_name in columns
        ]

        if not matching_physical_tables and not matching_derived_relations:
            raise SQLValidationError(
                f"Column '{column.name}' is not allowed."
            )

        if len(matching_physical_tables) > 1 and not matching_derived_relations:
            raise SQLValidationError(
                f"Column '{column.name}' is ambiguous and must be "
                "qualified with a table or alias."
            )


def _validate_columns(expression: exp.Expression) -> None:
    """Validate columns in every SELECT scope."""
    for select in expression.find_all(exp.Select):
        _validate_select_columns(select, expression)


def validate_sql(sql: str) -> str:
    """
    Validate generated SQL against the project's safety rules.

    Returns normalized SQL when validation succeeds.
    """
    if not isinstance(sql, str):
        raise TypeError("SQL must be a string.")

    sql = sql.strip()

    if not sql:
        raise SQLValidationError("SQL cannot be empty.")

    _validate_no_comments(sql)

    expression = _validate_single_statement(sql)

    _validate_select_only(expression)

    _validate_tables(expression)

    _validate_columns(expression)

    return expression.sql(dialect="postgres")


if __name__ == "__main__":
    valid_sql = """
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
    """

    print("Validated SQL:")
    print(validate_sql(valid_sql))