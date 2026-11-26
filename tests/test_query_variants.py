import pytest

from devmind.query_variants import TRANSFORMATION_VERSION, build_query_variants, normalize_issue_text


def test_query_variants_are_ordered_traceable_and_repeatable():
    issue = "Cart does not restore matchState after refresh. See src/cartStore.js"
    variants = build_query_variants(issue)
    assert [variant.variant for variant in variants] == ["raw", "normalized", "keywords_identifiers", "structured"]
    assert all(variant.original_text == issue for variant in variants)
    assert all(variant.transformation_version == TRANSFORMATION_VERSION for variant in variants)
    assert [variant.to_dict() for variant in variants] == [
        variant.to_dict() for variant in build_query_variants(issue)
    ]
    assert variants[0].generated_query == issue
    assert variants[1].generated_query == "cart does not restore matchstate after refresh. see src/cartstore.js"
    assert "matchState" in variants[2].identifiers
    assert "src/cartStore.js" in variants[3].component_hints


def test_structured_query_uses_observed_category_and_never_invents_hints():
    variants = build_query_variants("Parser raises an exception in parse_value")
    structured = variants[-1]
    assert structured.category == "exception"
    assert structured.generated_query.endswith("exception")
    assert "database" not in structured.generated_query


def test_default_behavior_category_is_recorded_but_not_added_as_a_signal():
    variants = build_query_variants("The blue header is shifted")
    structured = variants[-1]
    assert structured.category == "behavior"
    assert not structured.generated_query.endswith("behavior")


@pytest.mark.parametrize("text", ["", "  ", None])
def test_query_normalization_rejects_empty_reports(text):
    with pytest.raises(ValueError, match="non-empty"):
        normalize_issue_text(text)

