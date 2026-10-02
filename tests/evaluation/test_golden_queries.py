from tests.evaluation.evaluator import GoldenEvaluator


def test_golden_dataset_loads():
    cases = GoldenEvaluator.load_cases()

    assert len(cases) == 11


def test_golden_evaluation():
    evaluator = GoldenEvaluator()

    results = evaluator.evaluate_all()
    summary = evaluator.summary(results)

    assert summary["total"] == 11
    assert summary["errors"] == 0

    failed = [
        result
        for result in results
        if result["status"] != "PASS"
    ]

    assert not failed, failed