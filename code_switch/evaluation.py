from deepeval import evaluate
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase


def evaluate_code(output_code):
    # Define your test case
    test_case = LLMTestCase(
        input="Evaluate the generated code.",
        actual_output=output_code,
        context=["Code evaluation"],
    )

    correctness_metric = GEval(
        name="Correctness",
        criteria="Determine if the generated code is correct and functional.",
    )
    # Add more metrics if needed, like readability, maintainability, etc.
    # quality_metric = AnotherMetric(name="Code Quality")

    # Evaluate the test case
    results = evaluate([test_case], [correctness_metric])
    return results
