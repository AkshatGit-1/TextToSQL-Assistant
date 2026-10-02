from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from core.query_executor import QueryExecutor
from core.query_pipeline import QueryPipeline


BASE_DIR = Path(__file__).resolve().parents[2]
GOLDEN_FILE = BASE_DIR / "tests" / "evaluation" / "golden_questions.json"


class GoldenEvaluator:
    """Evaluate QueryPipeline behavior against a verified golden dataset."""

    def __init__(
        self,
        pipeline: QueryPipeline | None = None,
        query_executor: QueryExecutor | None = None,
    ):
        self.pipeline = pipeline or QueryPipeline()
        self.query_executor = query_executor or QueryExecutor()

    @staticmethod
    def load_cases() -> list[dict[str, Any]]:
        if not GOLDEN_FILE.exists():
            raise FileNotFoundError(
                f"Golden dataset not found: {GOLDEN_FILE}"
            )

        content = GOLDEN_FILE.read_text(encoding="utf-8").strip()

        if not content:
            raise ValueError("Golden dataset is empty.")

        cases = json.loads(content)

        if not isinstance(cases, list):
            raise ValueError("Golden dataset must contain a JSON list.")

        return cases

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        """Normalize database values for reliable comparison."""

        if isinstance(value, Decimal):
            return round(float(value), 10)

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, timedelta):
            return value.total_seconds()

        if isinstance(value, float):
            return round(value, 10)

        if isinstance(value, dict):
            return {
                str(key): GoldenEvaluator._normalize_value(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple)):
            return [
                GoldenEvaluator._normalize_value(item)
                for item in value
            ]

        return value

    @classmethod
    def _normalize_rows(
        cls,
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        normalized = []

        for row in rows:
            normalized.append(
                {
                    str(key): cls._normalize_value(value)
                    for key, value in row.items()
                }
            )

        return normalized

    @classmethod
    def compare_results(
        cls,
        actual: list[dict[str, Any]],
        expected: list[dict[str, Any]],
        order_sensitive: bool = False,
    ) -> bool:
        actual_normalized = cls._normalize_rows(actual)
        expected_normalized = cls._normalize_rows(expected)

        if order_sensitive:
            return actual_normalized == expected_normalized

        def canonicalize(
            rows: list[dict[str, Any]],
        ) -> list[tuple[tuple[str, str], ...]]:
            canonical_rows = []

            for row in rows:
                canonical_rows.append(
                    tuple(
                        sorted(
                            (
                                key,
                                repr(value),
                            )
                            for key, value in row.items()
                        )
                    )
                )

            return sorted(canonical_rows)

        return canonicalize(actual_normalized) == canonicalize(
            expected_normalized
        )

    @staticmethod
    def _expected_status_matches(
        response: dict[str, Any],
        expected_status: str,
    ) -> bool:
        return response.get("status") == expected_status

    def evaluate_case(
        self,
        case: dict[str, Any],
    ) -> dict[str, Any]:
        case_id = case["id"]
        question = case["question"]
        expected_status = case["expected_status"]

        response = self.pipeline.run(question)

        status_match = self._expected_status_matches(
            response,
            expected_status,
        )

        if not status_match:
            return {
                "id": case_id,
                "question": question,
                "status": "FAIL",
                "reason": (
                    f"Expected status '{expected_status}', "
                    f"got '{response.get('status')}'."
                ),
            }

        if expected_status != "success":
            return {
                "id": case_id,
                "question": question,
                "status": "PASS",
                "reason": f"Returned expected status '{expected_status}'.",
            }

        reference_sql = case.get("reference_sql")

        if not reference_sql:
            return {
                "id": case_id,
                "question": question,
                "status": "FAIL",
                "reason": "Successful case has no reference SQL.",
            }

        try:
            expected_results = self.query_executor.execute(
                reference_sql
            )
        except Exception as exc:
            return {
                "id": case_id,
                "question": question,
                "status": "ERROR",
                "reason": f"Reference SQL failed: {exc}",
            }

        actual_results = response.get("results", [])

        order_sensitive = bool(
            case.get("order_sensitive", False)
        )

        results_match = self.compare_results(
            actual=actual_results,
            expected=expected_results,
            order_sensitive=order_sensitive,
        )

        if not results_match:
            return {
                "id": case_id,
                "question": question,
                "status": "FAIL",
                "reason": "Generated query returned unexpected results.",
                "generated_sql": response.get("sql"),
                "actual_results": actual_results,
                "expected_results": expected_results,
            }

        return {
            "id": case_id,
            "question": question,
            "status": "PASS",
            "reason": "Generated query matched the reference result.",
            "generated_sql": response.get("sql"),
        }

    def evaluate_all(self) -> list[dict[str, Any]]:
        cases = self.load_cases()

        results = []

        for case in cases:
            results.append(self.evaluate_case(case))

        return results

    def summary(
        self,
        results: list[dict[str, Any]],
    ) -> dict[str, int]:
        return {
            "total": len(results),
            "passed": sum(
                result["status"] == "PASS"
                for result in results
            ),
            "failed": sum(
                result["status"] == "FAIL"
                for result in results
            ),
            "errors": sum(
                result["status"] == "ERROR"
                for result in results
            ),
        }


if __name__ == "__main__":
    evaluator = GoldenEvaluator()
    results = evaluator.evaluate_all()
    summary = evaluator.summary(results)

    print("=" * 70)
    print("GOLDEN SET EVALUATION")
    print("=" * 70)

    for result in results:
        print(
            f"{result['id']} | "
            f"{result['status']} | "
            f"{result['question']}"
        )

    print("=" * 70)
    print(
        f"TOTAL: {summary['total']} | "
        f"PASSED: {summary['passed']} | "
        f"FAILED: {summary['failed']} | "
        f"ERRORS: {summary['errors']}"
    )