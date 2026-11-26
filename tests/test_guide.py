from devmind.guide import PARAMETER_GUIDE


def test_parameter_guide_covers_all_ui_controls():
    expected_keys = {
        "preset",
        "repository",
        "embedding_model",
        "vector_index",
        "top_k",
        "issue_text",
        "workflow_mode",
        "model_investigation",
        "max_attempts",
    }
    assert expected_keys.issubset(set(PARAMETER_GUIDE.keys()))
    for key, data in PARAMETER_GUIDE.items():
        assert "title" in data
        assert "summary" in data
        assert "viva_talking_point" in data
        assert len(data["summary"]) > 10
