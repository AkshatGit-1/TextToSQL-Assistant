import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

load_dotenv()


def _get_database_url() -> str:
    """Build the PostgreSQL connection URL from environment variables."""
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "text_to_sql")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if not user:
        raise ValueError("DB_USER is not configured.")

    if not password:
        raise ValueError("DB_PASSWORD is not configured.")

    return (
        f"postgresql+psycopg://"
        f"{user}:{password}@{host}:{port}/{database}"
    )


def get_engine() -> Engine:
    """Create a SQLAlchemy engine for PostgreSQL."""
    return create_engine(
        _get_database_url(),
        pool_pre_ping=True,
    )


if __name__ == "__main__":
    engine = get_engine()

    with engine.connect() as connection:
        result = connection.exec_driver_sql(
            "SELECT current_user, current_database();"
        )

        current_user, current_database = result.fetchone()

        print(f"Database user: {current_user}")
        print(f"Database: {current_database}")