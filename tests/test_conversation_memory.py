import pytest

from core.conversation_memory import ConversationMemory


def test_memory_starts_empty():
    memory = ConversationMemory()

    assert memory.get_turns() == []
    assert memory.format_context() == "No previous conversation."


def test_memory_stores_turn():
    memory = ConversationMemory()

    memory.add_turn(
        "What are the total sales?",
        "SELECT SUM(price) AS total_sales FROM analytics.fact_order_items;",
    )

    turns = memory.get_turns()

    assert len(turns) == 1
    assert turns[0].question == "What are the total sales?"
    assert "total_sales" in turns[0].sql


def test_memory_limits_number_of_turns():
    memory = ConversationMemory(max_turns=2)

    memory.add_turn("Question 1", "SELECT 1;")
    memory.add_turn("Question 2", "SELECT 2;")
    memory.add_turn("Question 3", "SELECT 3;")

    turns = memory.get_turns()

    assert len(turns) == 2
    assert turns[0].question == "Question 2"
    assert turns[1].question == "Question 3"


def test_memory_formats_context():
    memory = ConversationMemory()

    memory.add_turn(
        "What are the total sales?",
        "SELECT SUM(price) AS total_sales FROM analytics.fact_order_items;",
    )

    context = memory.format_context()

    assert "TURN 1" in context
    assert "What are the total sales?" in context
    assert "total_sales" in context


def test_memory_can_be_cleared():
    memory = ConversationMemory()

    memory.add_turn(
        "What are the total sales?",
        "SELECT SUM(price) FROM analytics.fact_order_items;",
    )

    memory.clear()

    assert memory.get_turns() == []
    assert memory.format_context() == "No previous conversation."


def test_invalid_max_turns_is_rejected():
    with pytest.raises(ValueError):
        ConversationMemory(max_turns=0)


def test_non_integer_max_turns_is_rejected():
    with pytest.raises(TypeError):
        ConversationMemory(max_turns="5")


def test_empty_question_is_rejected():
    memory = ConversationMemory()

    with pytest.raises(ValueError):
        memory.add_turn("", "SELECT 1;")


def test_empty_sql_is_rejected():
    memory = ConversationMemory()

    with pytest.raises(ValueError):
        memory.add_turn("Question", "")


def test_non_string_question_is_rejected():
    memory = ConversationMemory()

    with pytest.raises(TypeError):
        memory.add_turn(123, "SELECT 1;")


def test_non_string_sql_is_rejected():
    memory = ConversationMemory()

    with pytest.raises(TypeError):
        memory.add_turn("Question", 123)