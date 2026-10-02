from dataclasses import dataclass


@dataclass(frozen=True)
class QuestionAnalysis:
    """Result of analyzing a user's business question."""

    is_ambiguous: bool
    is_answerable: bool
    reason: str | None = None


class QuestionAnalyzer:
    """Analyze business questions before SQL generation."""

    AMBIGUOUS_TERMS = {
        "best": "Please specify what 'best' means, such as highest sales, highest quantity, or highest review score.",
        "worst": "Please specify what 'worst' means, such as lowest sales, lowest quantity, or lowest review score.",
        "top": "Please specify the metric used to rank the results.",
        "most popular": "Please specify how popularity should be measured.",
        "successful": "Please specify the metric used to measure success.",
        "performing": "Please specify the metric used to measure performance.",
    }

    UNSUPPORTED_METRICS = {
        "customer lifetime value": "Customer lifetime value is not defined as an approved business metric.",
        "clv": "Customer lifetime value is not defined as an approved business metric.",
        "profit": "Profit is not defined as an approved business metric.",
        "profit margin": "Profit margin is not defined as an approved business metric.",
        "conversion rate": "Conversion rate is not defined as an approved business metric.",
        "customer acquisition cost": "Customer acquisition cost is not defined as an approved business metric.",
        "cac": "Customer acquisition cost is not defined as an approved business metric.",
    }

    def analyze(self, question: str) -> QuestionAnalysis:
        if not isinstance(question, str):
            raise TypeError("Question must be a string.")

        question = question.strip()

        if not question:
            raise ValueError("Question cannot be empty.")

        normalized_question = question.lower()

        for term, reason in self.AMBIGUOUS_TERMS.items():
            if term in normalized_question:
                return QuestionAnalysis(
                    is_ambiguous=True,
                    is_answerable=False,
                    reason=reason,
                )

        for metric, reason in self.UNSUPPORTED_METRICS.items():
            if metric in normalized_question:
                return QuestionAnalysis(
                    is_ambiguous=False,
                    is_answerable=False,
                    reason=reason,
                )

        return QuestionAnalysis(
            is_ambiguous=False,
            is_answerable=True,
        )