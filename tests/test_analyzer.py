import pytest

from devmind.analyzer import analyze_issue


def test_analyzer_extracts_repeated_terms_and_exception_type():
    result = analyze_issue("Parser raises exception when parser receives empty input")
    assert result.issue_type == "exception"
    assert "parser" in result.keywords
    assert result.summary.startswith("Parser raises")


@pytest.mark.parametrize("text", ["", "   ", None])
def test_analyzer_rejects_empty_or_non_string_report(text):
    with pytest.raises(ValueError):
        analyze_issue(text)


def test_analyzer_rejects_invalid_keyword_limit():
    with pytest.raises(ValueError):
        analyze_issue("something breaks", max_keywords=0)


def test_analyzer_splits_camel_case_and_keeps_component_hint():
    result = analyze_issue("matchState.balls is incremented twice in script.js")
    assert "match" in result.keywords
    assert "state" in result.keywords
    assert "balls" in result.keywords
    assert "matchState.balls" in result.component_hints
    assert "script.js" in result.component_hints


def test_analyzer_does_not_classify_substrings_as_exception_signals():
    result = analyze_issue("The package name terror is displayed in the interface")
    assert result.issue_type == "behavior"


def test_analyzer_does_not_treat_change_as_performance_signal_or_sentence_period_as_hint():
    result = analyze_issue("In addRun, change matchState.balls += 2 to += 1 for each legal delivery.")
    assert result.issue_type == "behavior"
    assert "delivery." not in result.component_hints
    assert "matchState.balls" in result.component_hints


def test_analyzer_uses_exact_performance_signal_for_issue_category():
    result = analyze_issue("The response is slow and times out under load")
    assert result.issue_type == "performance"


def test_analyzer_requires_integer_keyword_limit():
    with pytest.raises(ValueError, match="positive integer"):
        analyze_issue("a small issue", max_keywords=1.5)

