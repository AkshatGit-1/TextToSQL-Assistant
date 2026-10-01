from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SCHEMA_FILE = BASE_DIR / "config" / "schema_context.md"


def load_schema_context() -> str:
    """Load the approved analytics schema context."""
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(
            f"Schema context file not found: {SCHEMA_FILE}"
        )

    return SCHEMA_FILE.read_text(encoding="utf-8")


def get_schema_context() -> str:
    """Return the schema context used by the Text-to-SQL pipeline."""
    return load_schema_context()


if __name__ == "__main__":
    context = get_schema_context()

    print("Schema context loaded successfully.")
    print(f"Characters: {len(context):,}")
    print(f"Lines: {len(context.splitlines()):,}")