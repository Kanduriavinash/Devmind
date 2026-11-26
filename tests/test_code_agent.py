import pytest

from devmind.code_agent import InvalidCandidatePatch, generate_candidate_patch, validate_unified_diff, write_candidate_patch

VALID_DIFF = (
    "diff --git a/calc.py b/calc.py\n"
    "--- a/calc.py\n"
    "+++ b/calc.py\n"
    "@@ -1 +1 @@\n"
    "-def calculate(): return 1\n"
    "+def calculate(): return 2\n"
)


class Provider:
    def __init__(self, response):
        self.response = response
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        return self.response


def test_code_agent_returns_valid_diff_grounded_in_evidence_and_investigation():
    provider = Provider(VALID_DIFF)
    evidence = [{"path": "calc.py", "start_line": 2, "end_line": 3, "content": "def calculate(): return 1"}]
    patch = generate_candidate_patch(
        "calculate is wrong",
        evidence,
        provider,
        investigation=["[E1] calculate may return an incorrect value"],
        repository_metadata={"language": "Python", "root_name": "sample"},
    )
    assert patch == VALID_DIFF.strip()
    assert validate_unified_diff(patch) == ["calc.py"]
    assert "calc.py:2-3" in provider.prompts[0]
    assert "calculate may return an incorrect value" in provider.prompts[0]
    assert '"root_name": "sample"' in provider.prompts[0]
    assert "diff --git a/<path> b/<path>" in provider.prompts[0]
    assert "--- a/<path>" in provider.prompts[0]
    assert "+++ b/<path>" in provider.prompts[0]
    assert "Do not omit any original line between changed lines, including docstrings" in provider.prompts[0]
    assert "never repeat that old line as context" in provider.prompts[0]
    assert "complete the operation successfully before clearing or changing" in provider.prompts[0]


def test_code_agent_respects_configured_evidence_context_limit():
    provider = Provider(VALID_DIFF)
    evidence = [{"path": "calc.py", "start_line": 1, "end_line": 1, "content": "x" * 100}]
    generate_candidate_patch("bug", evidence, provider, max_evidence_chars=20)
    assert "x" * 20 in provider.prompts[0]
    assert "x" * 21 not in provider.prompts[0]


def test_code_agent_preserves_trailing_blank_context_line_in_diff():
    diff_with_context = VALID_DIFF.replace("@@ -1 +1 @@", "@@ -1,2 +1,2 @@") + " "
    provider = Provider(diff_with_context)
    evidence = [{"path": "calc.py", "start_line": 1, "end_line": 1, "content": "def calculate(): return 1"}]
    patch = generate_candidate_patch("calculate is wrong", evidence, provider)
    assert patch == diff_with_context
    assert patch.endswith(" ")
    assert validate_unified_diff(patch) == ["calc.py"]


def test_code_agent_corrects_mismatched_hunk_line_counts():
    response = (
        "--- a/calculator.py\n"
        "+++ b/calculator.py\n"
        "@@ -4,7 +4,7 @@\n"
        " def safe_divide(numerator, denominator):\n"
        "-    return numerator / denominator\n"
        "+    if denominator == 0:\n"
        "+        return None\n"
        "+    return numerator / denominator\n"
        "\nINSUFFICIENT_EVIDENCE\nThe code change is explained here."
    )
    provider = Provider(response)
    evidence = [{"path": "calculator.py", "start_line": 4, "end_line": 6, "content": "def safe_divide(...): return numerator / denominator"}]

    patch = generate_candidate_patch("zero denominator returns None", evidence, provider)

    assert patch is not None
    assert "@@ -4,2 +4,4 @@" in patch
    assert validate_unified_diff(patch) == ["calculator.py"]
    assert "INSUFFICIENT_EVIDENCE" not in patch


def test_code_agent_sends_prior_test_feedback():
    provider = Provider("not a diff")
    evidence = [{"path": "calc.py", "start_line": 1, "end_line": 1, "content": "pass"}]
    result = generate_candidate_patch("bug", evidence, provider, test_feedback={"passed": False})
    assert result is None
    assert '"passed": false' in provider.prompts[0]


def test_code_agent_skips_provider_when_evidence_is_empty():
    provider = Provider(VALID_DIFF)
    assert generate_candidate_patch("bug", [], provider) is None
    assert provider.prompts == []


@pytest.mark.parametrize("patch", [
    "diff --git a/../outside.py b/../outside.py\n--- a/../outside.py\n+++ b/../outside.py\n@@ -1 +1 @@\n-a\n+b\n",
    "diff --git a/C:/outside.py b/C:/outside.py\n--- a/C:/outside.py\n+++ b/C:/outside.py\n@@ -1 +1 @@\n-a\n+b\n",
    "diff --git a/config.txt b/config.txt\n--- a/config.txt\n+++ b/config.txt\n@@ -1 +1 @@\n-a\n+b\n",
    "diff --git a/calc.py b/calc.py\n--- a/calc.py\n+++ b/calc.py\n@@ -1 +1 @@\n def calculate(): return 1\n",
    "Here is your patch:\ndiff --git a/calc.py b/calc.py\n",
])
def test_diff_validator_rejects_unsafe_or_malformed_patches(patch):
    with pytest.raises(InvalidCandidatePatch):
        validate_unified_diff(patch)


def test_diff_validator_rejects_no_op_patch():
    no_op = "diff --git a/calc.py b/calc.py\n--- a/calc.py\n+++ b/calc.py\n@@ -1 +1 @@\n def calculate(): return 1\n"
    with pytest.raises(InvalidCandidatePatch, match="No-op"):
        validate_unified_diff(no_op)


def test_code_agent_rejects_changes_to_paths_without_retrieved_evidence():
    provider = Provider(VALID_DIFF.replace("calc.py", "other.py"))
    evidence = [{"path": "calc.py", "start_line": 1, "end_line": 1, "content": "def calculate(): return 1"}]
    assert generate_candidate_patch("bug", evidence, provider) is None


def test_validator_accepts_evidence_grounded_javascript_diff():
    patch = (
        "diff --git a/script.js b/script.js\n"
        "--- a/script.js\n"
        "+++ b/script.js\n"
        "@@ -1 +1 @@\n"
        "-function addRun(run) { return run; }\n"
        "+function addRun(run) { return run + 1; }\n"
    )
    evidence = [{"path": "script.js", "start_line": 1, "end_line": 1, "content": "function addRun(run) { return run; }"}]
    provider = Provider(patch)
    assert generate_candidate_patch("addRun is wrong", evidence, provider) == patch.strip()


def test_validator_accepts_evidence_grounded_inline_javascript_html_diff():
    patch = (
        "diff --git a/index.html b/index.html\n"
        "--- a/index.html\n"
        "+++ b/index.html\n"
        "@@ -1 +1 @@\n"
        "-function loadCart() { return []; }\n"
        "+function loadCart() { return JSON.parse(localStorage.getItem('cart') || '[]'); }\n"
    )
    evidence = [{"path": "index.html", "start_line": 3, "end_line": 3,
                 "content": "function loadCart() { return []; }"}]
    assert validate_unified_diff(patch, allowed_paths={"index.html"}) == ["index.html"]


def test_candidate_patch_is_saved_separately_and_never_inside_source_repo(tmp_path):
    repository = tmp_path / "repo"
    repository.mkdir()
    saved = write_candidate_patch(VALID_DIFF, tmp_path / "review" / "candidate.patch", repository)
    assert saved.read_text(encoding="utf-8") == VALID_DIFF
    with pytest.raises(ValueError, match="outside"):
        write_candidate_patch(VALID_DIFF, repository / "candidate.patch", repository)
