import sys
from pathlib import Path

# Ensure the project root is available on Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from visualization import render_visualization
from core.query_pipeline import QueryPipeline


st.set_page_config(
    page_title="Text-to-SQL Analytics Assistant",
    page_icon="📊",
    layout="wide",
)


def get_pipeline() -> QueryPipeline:
    if "query_pipeline" not in st.session_state:
        st.session_state.query_pipeline = QueryPipeline()

    return st.session_state.query_pipeline


def render_results(results: list[dict]) -> None:
    if not results:
        st.info("The query returned no results.")
        return

    st.dataframe(
        results,
        use_container_width=True,
        hide_index=True,
    )


def main() -> None:
    st.title("Text-to-SQL Analytics Assistant")

    st.caption(
        "Ask questions about the Olist e-commerce analytics database."
    )

    pipeline = get_pipeline()

    st.sidebar.header("Sample Questions")

    if st.sidebar.button(
        "Clear Conversation",
        use_container_width=True,
    ):
        pipeline.clear_memory()
        st.rerun()

    sample_questions = [
        "What are the total sales?",
        "What are the total sales by customer state?",
        "How many orders are there by month?",
        "What is the average review score by product category?",
        "What are the orders by order status?",
    ]

    selected_question = st.sidebar.selectbox(
        "Choose a question",
        [""] + sample_questions,
    )

    question = st.text_area(
        "Ask a business question",
        value=selected_question,
        placeholder="Example: What are the total sales by customer state?",
        height=100,
    )

    run_query = st.button(
        "Run Query",
        type="primary",
        use_container_width=True,
    )

    if not run_query:
        return

    if not question.strip():
        st.warning("Please enter a business question.")
        return

    with st.spinner("Generating and executing SQL..."):
        try:
            response = pipeline.run(question)
        except Exception as exc:
            st.error(f"Query failed: {exc}")
            return

    status = response.get("status")

    if status == "clarification_required":
        st.warning(
            response.get(
                "reason",
                "Please clarify your question.",
            )
        )
        return

    if status == "insufficient_data":
        st.warning(
            response.get(
                "reason",
                "The requested information is not available.",
            )
        )
        return

    if status != "success":
        st.error(
            response.get(
                "reason",
                "The query could not be completed.",
            )
        )
        return

    st.success(
        f"Query completed successfully in "
        f"{response.get('attempts', 0)} attempt(s)."
    )

    st.subheader("Generated SQL")

    st.code(
        response.get("sql", ""),
        language="sql",
    )

    st.subheader("Results")

    results = response.get("results", [])

    render_results(results)

    render_visualization(results)


if __name__ == "__main__":
    main()