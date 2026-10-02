from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationTurn:
    """A single question and SQL result from the conversation."""

    question: str
    sql: str


class ConversationMemory:
    """Store a bounded history of recent successful SQL turns."""

    def __init__(self, max_turns: int = 5):
        if not isinstance(max_turns, int) or isinstance(max_turns, bool):
            raise TypeError("max_turns must be an integer.")

        if max_turns <= 0:
            raise ValueError("max_turns must be greater than zero.")

        self.max_turns = max_turns
        self._turns: list[ConversationTurn] = []

    def add_turn(self, question: str, sql: str) -> None:
        """Add a successful question and generated SQL."""
        if not isinstance(question, str):
            raise TypeError("question must be a string.")

        if not isinstance(sql, str):
            raise TypeError("sql must be a string.")

        question = question.strip()
        sql = sql.strip()

        if not question:
            raise ValueError("question cannot be empty.")

        if not sql:
            raise ValueError("sql cannot be empty.")

        self._turns.append(
            ConversationTurn(
                question=question,
                sql=sql,
            )
        )

        self._turns = self._turns[-self.max_turns :]

    def get_turns(self) -> list[ConversationTurn]:
        """Return a copy of the stored conversation turns."""
        return list(self._turns)

    def clear(self) -> None:
        """Clear the conversation history."""
        self._turns.clear()

    def format_context(self) -> str:
        """Format recent conversation history for the SQL prompt."""
        if not self._turns:
            return "No previous conversation."

        sections = []

        for index, turn in enumerate(self._turns, start=1):
            sections.append(
                f"""TURN {index}
QUESTION:
{turn.question}

SQL:
{turn.sql}"""
            )

        return "\n\n".join(sections)