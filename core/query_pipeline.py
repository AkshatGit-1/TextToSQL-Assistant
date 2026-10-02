from typing import Any

from core.conversation_memory import ConversationMemory
from core.question_analyzer import QuestionAnalyzer
from core.query_executor import QueryExecutor
from core.query_generator import QueryGenerator
from core.query_retry import QueryRetryController


class QueryPipeline:
    """Run the complete natural-language-to-SQL query workflow."""

    def __init__(
        self,
        query_generator: QueryGenerator | None = None,
        query_executor: QueryExecutor | None = None,
        retry_controller: QueryRetryController | None = None,
        question_analyzer: QuestionAnalyzer | None = None,
        conversation_memory: ConversationMemory | None = None,
    ):
        self.query_generator = query_generator or QueryGenerator()
        self.query_executor = query_executor or QueryExecutor()
        self.retry_controller = retry_controller or QueryRetryController()
        self.question_analyzer = question_analyzer or QuestionAnalyzer()
        self.conversation_memory = (
            conversation_memory or ConversationMemory()
        )

    @staticmethod
    def _is_follow_up_question(question: str) -> bool:
        """Detect short follow-up instructions that depend on prior context."""
        normalized_question = question.strip().lower()

        follow_up_patterns = (
            "show only the top",
            "show the top",
            "top ",
            "show only",
            "limit to",
            "only show",
        )

        return any(
            pattern in normalized_question
            for pattern in follow_up_patterns
        )

    def run(self, question: str) -> dict[str, Any]:
        conversation_context = self.conversation_memory.format_context()
        has_previous_conversation = bool(
            self.conversation_memory.get_turns()
        )

        analysis = self.question_analyzer.analyze(question)

        is_follow_up = (
            has_previous_conversation
            and self._is_follow_up_question(question)
        )

        if analysis.is_ambiguous and not is_follow_up:
            return {
                "question": question.strip(),
                "status": "clarification_required",
                "reason": analysis.reason,
                "sql": None,
                "results": [],
                "attempts": 0,
            }

        if not analysis.is_answerable and not is_follow_up:
            return {
                "question": question.strip(),
                "status": "insufficient_data",
                "reason": analysis.reason,
                "sql": None,
                "results": [],
                "attempts": 0,
            }

        feedback: str | None = None
        attempts = 0

        def attempt() -> dict[str, Any]:
            nonlocal feedback, attempts

            attempts += 1

            sql = self.query_generator.generate_sql(
                question,
                error_feedback=feedback,
                conversation_context=conversation_context,
            )

            try:
                results = self.query_executor.execute(sql)

                self.conversation_memory.add_turn(
                    question=question,
                    sql=sql,
                )

                return {
                    "question": question.strip(),
                    "status": "success",
                    "sql": sql,
                    "results": results,
                    "attempts": attempts,
                }

            except Exception as exc:
                feedback = str(exc)
                raise

        return self.retry_controller.run(attempt)

    def clear_memory(self) -> None:
        """Clear the current conversation history."""
        self.conversation_memory.clear()