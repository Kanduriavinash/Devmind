import json

from devmind.failure_analysis import (
    analyze_test_failure,
    build_failure_retrieval_query,
    provider_failure_feedback,
)


def test_failure_analysis_extracts_test_names_frames_and_error_classes():
    result = {
        "executed": True,
        "passed": False,
        "runner": "pytest",
        "exit_code": 1,
        "stdout": "FAILED tests/test_cart.py::test_cart_persists_after_reload - AssertionError",
        "stderr": (
            'Traceback (most recent call last):\n'
            '  File "/workspace/cart.py", line 41, in restore_cart\n'
            "AssertionError: expected cart to survive reload\n"
        ),
    }

    analysis = analyze_test_failure(result)

    assert analysis.failed_tests == ["tests/test_cart.py::test_cart_persists_after_reload"]
    assert {"path": "cart.py", "line": 41, "function": "restore_cart"} in analysis.stack_frames
    assert analysis.error_types == ["AssertionError"]
    assert "restore_cart" in analysis.retrieval_terms
    query = build_failure_retrieval_query("cart is empty after reload", analysis)
    assert "test_cart_persists_after_reload" in query
    assert "cart.py" in query


def test_provider_feedback_excludes_raw_sandbox_output():
    result = {
        "executed": True,
        "passed": False,
        "exit_code": 1,
        "runner": "pytest",
        "stdout": "FAILED tests/test_secret.py::test_secret_is_redacted",
        "stderr": "AssertionError: API_KEY=do-not-send-this-value",
    }
    failure = analyze_test_failure(result)

    feedback = provider_failure_feedback(result, failure)

    serialized = json.dumps(feedback)
    assert "do-not-send-this-value" not in serialized
    assert "API_KEY" not in serialized
    assert "test_secret_is_redacted" in serialized
    assert "stdout" not in feedback
    assert "stderr" not in feedback


def test_failure_analysis_handles_javascript_stack_frames():
    analysis = analyze_test_failure({
        "stdout": "not ok 1 - cart reload restores saved items\n",
        "stderr": "    at restoreCart (/workspace/src/cart.js:18:7)\n",
    })

    assert analysis.failed_tests == ["cart reload restores saved items"]
    assert {"path": "src/cart.js", "line": 18, "function": "restoreCart"} in analysis.stack_frames

