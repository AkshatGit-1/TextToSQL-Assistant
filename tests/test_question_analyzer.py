import pytest

from core.question_analyzer import (
    QuestionAnalyzer,
    QuestionAnalysis,
)


def test_clear_question_is_answerable():
    analyzer = QuestionAnalyzer()

    result = analyzer.analyze(
        "What are the total sales by customer state?"
    )

    assert isinstance(result, QuestionAnalysis)
    assert result.is_ambiguous is False
    assert result.is_answerable is True
    assert result.reason is None


def test_ambiguous_best_question_requires_clarification():
    analyzer = QuestionAnalyzer()

    result = analyzer.analyze(
        "What is the best product?"
    )

    assert result.is_ambiguous is True
    assert result.is_answerable is False
    assert "best" in result.reason.lower()


def test_ambiguous_top_question_requires_metric():
    analyzer = QuestionAnalyzer()

    result = analyzer.analyze(
        "Show me the top products."
    )

    assert result.is_ambiguous is True
    assert result.is_answerable is False
    assert "metric" in result.reason.lower()


def test_unsupported_customer_lifetime_value():
    analyzer = QuestionAnalyzer()

    result = analyzer.analyze(
        "What is the customer lifetime value?"
    )

    assert result.is_ambiguous is False
    assert result.is_answerable is False
    assert "customer lifetime value" in result.reason.lower()


def test_unsupported_profit_metric():
    analyzer = QuestionAnalyzer()

    result = analyzer.analyze(
        "What is the profit by product category?"
    )

    assert result.is_ambiguous is False
    assert result.is_answerable is False
    assert "profit" in result.reason.lower()


def test_supported_sales_metric_is_answerable():
    analyzer = QuestionAnalyzer()

    result = analyzer.analyze(
        "What are the total sales by product category?"
    )

    assert result.is_ambiguous is False
    assert result.is_answerable is True
    assert result.reason is None


def test_supported_review_metric_is_answerable():
    analyzer = QuestionAnalyzer()

    result = analyzer.analyze(
        "What is the average review score by product category?"
    )

    assert result.is_ambiguous is False
    assert result.is_answerable is True
    assert result.reason is None


def test_empty_question_is_rejected():
    analyzer = QuestionAnalyzer()

    with pytest.raises(
        ValueError,
        match="Question cannot be empty",
    ):
        analyzer.analyze("")


def test_whitespace_question_is_rejected():
    analyzer = QuestionAnalyzer()

    with pytest.raises(
        ValueError,
        match="Question cannot be empty",
    ):
        analyzer.analyze("   ")


def test_non_string_question_is_rejected():
    analyzer = QuestionAnalyzer()

    with pytest.raises(
        TypeError,
        match="Question must be a string",
    ):
        analyzer.analyze(None)