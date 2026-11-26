from devmind.indexer import index_repository
from devmind.retrieval import TfidfIndex, retrieve
import pytest


def test_indexer_records_python_function_lines_without_importing(tmp_path):
    source = tmp_path / "sample.py"
    source.write_text("def parse_value(text):\n    return int(text)\n", encoding="utf-8")
    chunks = index_repository(tmp_path)
    assert len(chunks) == 1
    assert (chunks[0].name, chunks[0].start_line, chunks[0].end_line) == ("parse_value", 1, 2)


def test_indexer_skips_generated_directories_and_bad_syntax(tmp_path):
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "cache.py").write_text("def hidden(): pass", encoding="utf-8")
    (tmp_path / ".devmind" / "repositories" / "download").mkdir(parents=True)
    (tmp_path / ".devmind" / "repositories" / "download" / "snapshot.py").write_text("def cached_snapshot(): pass", encoding="utf-8")
    (tmp_path / "broken.py").write_text("def broken(:", encoding="utf-8")
    assert index_repository(tmp_path) == []


def test_indexer_records_javascript_function_spans_without_execution(tmp_path):
    source = """function addRun(run) {
    const note = "brace } inside string";
    if (run > 0) {
        return run + 1;
    }
    return 0;
}

const formatOvers = (balls) => {
    return `${Math.floor(balls / 6)}.${balls % 6}`;
};
"""
    (tmp_path / "script.js").write_text(source, encoding="utf-8")
    chunks = index_repository(tmp_path)
    assert [(chunk.name, chunk.start_line, chunk.end_line) for chunk in chunks] == [
        ("addRun", 1, 7),
        ("formatOvers", 9, 11),
    ]
    assert chunks[0].path == "script.js"
    assert "return run + 1" in chunks[0].content


def test_indexer_extracts_inline_javascript_from_html_with_original_line_numbers(tmp_path):
    source = """<!doctype html>
<html>
<body>
  <button>Add</button>
  <script>
    function addToCart(item) {
      return item.name;
    }
  </script>
  <script type="application/ld+json">{"name": "not executable code"}</script>
</body>
</html>
"""
    (tmp_path / "index.html").write_text(source, encoding="utf-8")
    chunks = index_repository(tmp_path)
    assert [(c.name, c.start_line, c.end_line) for c in chunks] == [("addToCart", 6, 8)]
    assert chunks[0].path == "index.html"


def test_indexer_ignores_js_arrow_expression_without_braced_function(tmp_path):
    (tmp_path / "helper.mjs").write_text("export const value = (x) => x + 1;\n", encoding="utf-8")
    assert index_repository(tmp_path) == []


def test_indexer_ignores_symlink_to_source_outside_repository(tmp_path):
    repository = tmp_path / "repo"
    repository.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("def secret_function(): pass\n", encoding="utf-8")
    try:
        (repository / "linked.py").symlink_to(outside)
    except OSError as error:
        pytest.skip(f"Symlink creation is not available in this environment: {error}")
    assert index_repository(repository) == []


def test_indexer_stops_at_configured_file_limit(tmp_path):
    (tmp_path / "one.py").write_text("def one(): pass\n", encoding="utf-8")
    (tmp_path / "two.py").write_text("def two(): pass\n", encoding="utf-8")
    with pytest.raises(ValueError, match="limit"):
        index_repository(tmp_path, max_files=1)


def test_retrieval_returns_ranked_traceable_evidence():
    from devmind.models import CodeChunk

    chunks = [
        CodeChunk("parser.py", "parse_value", "FunctionDef", 1, 2, "def parse_value(text): return int(text)"),
        CodeChunk("render.py", "render_page", "FunctionDef", 4, 5, "def render_page(): return 'ok'"),
    ]
    result = retrieve("parser parse value", chunks)
    assert result[0].chunk.path == "parser.py"
    assert result[0].score > 0


def test_tfidf_index_scores_in_unit_interval_and_excludes_no_overlap():
    from devmind.models import CodeChunk

    chunks = [
        CodeChunk("parser.py", "parse_value", "FunctionDef", 1, 2, "def parse_value(text): return int(text)"),
        CodeChunk("render.py", "render_page", "FunctionDef", 4, 5, "def render_page(): return 'ok'"),
    ]
    index = TfidfIndex(chunks)
    result = index.search("parse value")
    assert result[0].chunk.path == "parser.py"
    assert 0 < result[0].score <= 1
    assert index.search("unrelated_xyz") == []


def test_tfidf_index_validates_limit():
    with pytest.raises(ValueError):
        TfidfIndex([]).search("query", limit=0)


def test_tfidf_query_singularizes_plural_bug_report_terms():
    from devmind.models import CodeChunk

    chunks = [
        CodeChunk(
            "django/db/models/base.py", "delete", "FunctionDef", 10, 15,
            "def delete(self): assert self.pk is not None; collector.delete()",
        ),
        CodeChunk(
            "tests/test_delete.py", "test_delete", "FunctionDef", 1, 5,
            "delete test verifies related rows are removed",
        ),
    ]
    query = "delete() on instances of models without any dependencies doesn't clear PKs"
    results = TfidfIndex(chunks).search(query)

    assert results[0].chunk.path == "django/db/models/base.py"

