"""Tests for multi-language source indexing."""
import pytest
from devmind.indexer import index_repository


def test_indexer_records_java_method_and_class(tmp_path):
    source = """public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }

    private static double divide(double num, double den) {
        if (den == 0) {
            throw new ArithmeticException("Division by zero");
        }
        return num / den;
    }
}
"""
    (tmp_path / "Calculator.java").write_text(source, encoding="utf-8")
    chunks = index_repository(tmp_path)
    names = [(c.name, c.kind) for c in chunks]
    assert ("Calculator", "ClassDef") in names
    assert ("add", "Function") in names
    assert ("divide", "Function") in names


def test_indexer_records_c_function(tmp_path):
    source = """int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

static void helper(void) {
    printf("hello");
}
"""
    (tmp_path / "math_utils.c").write_text(source, encoding="utf-8")
    chunks = index_repository(tmp_path)
    names = [c.name for c in chunks]
    assert "factorial" in names
    assert "helper" in names


def test_indexer_records_cpp_class_and_method(tmp_path):
    source = """class Stack {
public:
    void push(int val) {
        data.push_back(val);
    }

    int pop() {
        int top = data.back();
        data.pop_back();
        return top;
    }

private:
    std::vector<int> data;
};
"""
    (tmp_path / "stack.cpp").write_text(source, encoding="utf-8")
    chunks = index_repository(tmp_path)
    names = [(c.name, c.kind) for c in chunks]
    assert ("Stack", "ClassDef") in names
    assert ("push", "Function") in names
    assert ("pop", "Function") in names


def test_indexer_records_go_function_and_struct(tmp_path):
    source = """package main

func Add(a, b int) int {
    return a + b
}

type Calculator struct {
    Result int
}

func (c *Calculator) Multiply(a, b int) int {
    c.Result = a * b
    return c.Result
}
"""
    (tmp_path / "calc.go").write_text(source, encoding="utf-8")
    chunks = index_repository(tmp_path)
    names = [(c.name, c.kind) for c in chunks]
    assert ("Add", "Function") in names
    assert ("Calculator", "ClassDef") in names
    assert ("Multiply", "Function") in names


def test_indexer_records_rust_function_and_struct(tmp_path):
    source = """pub fn calculate(x: i32) -> i32 {
    x * 2
}

pub struct Config {
    pub name: String,
    pub value: i32,
}

impl Config {
    pub fn new(name: &str, value: i32) -> Self {
        Config {
            name: name.to_string(),
            value,
        }
    }
}
"""
    (tmp_path / "lib.rs").write_text(source, encoding="utf-8")
    chunks = index_repository(tmp_path)
    names = [(c.name, c.kind) for c in chunks]
    assert ("calculate", "Function") in names
    assert ("Config", "ClassDef") in names


def test_indexer_records_csharp_class_and_method(tmp_path):
    source = """public class UserService {
    private readonly IRepository _repo;

    public async Task<User> GetUser(int id) {
        return await _repo.FindById(id);
    }

    public void DeleteUser(int id) {
        _repo.Delete(id);
    }
}
"""
    (tmp_path / "UserService.cs").write_text(source, encoding="utf-8")
    chunks = index_repository(tmp_path)
    names = [(c.name, c.kind) for c in chunks]
    assert ("UserService", "ClassDef") in names
    assert ("GetUser", "Function") in names
    assert ("DeleteUser", "Function") in names


def test_indexer_records_ruby_method_and_class(tmp_path):
    source = """class Calculator
  def add(a, b)
    a + b
  end

  def self.version
    "1.0"
  end
end
"""
    (tmp_path / "calculator.rb").write_text(source, encoding="utf-8")
    chunks = index_repository(tmp_path)
    names = [(c.name, c.kind) for c in chunks]
    assert ("Calculator", "ClassDef") in names
    assert ("add", "Function") in names
    assert ("version", "Function") in names


def test_indexer_records_php_function_and_class(tmp_path):
    source = """<?php
class MathHelper {
    public function multiply($a, $b) {
        return $a * $b;
    }

    private static function validate($input) {
        if (!is_numeric($input)) {
            throw new InvalidArgumentException("Not a number");
        }
    }
}
"""
    (tmp_path / "MathHelper.php").write_text(source, encoding="utf-8")
    chunks = index_repository(tmp_path)
    names = [(c.name, c.kind) for c in chunks]
    assert ("MathHelper", "ClassDef") in names
    assert ("multiply", "Function") in names
    assert ("validate", "Function") in names


def test_indexer_records_kotlin_function_and_class(tmp_path):
    source = """data class User(val name: String, val age: Int) {
    fun greet(): String {
        return "Hello, $name"
    }
}

fun calculateScore(points: Int, multiplier: Double): Double {
    return points * multiplier
}
"""
    (tmp_path / "User.kt").write_text(source, encoding="utf-8")
    chunks = index_repository(tmp_path)
    names = [(c.name, c.kind) for c in chunks]
    assert ("User", "ClassDef") in names
    assert ("greet", "Function") in names
    assert ("calculateScore", "Function") in names


def test_indexer_records_swift_function_and_struct(tmp_path):
    source = """struct Point {
    var x: Double
    var y: Double

    func distance(to other: Point) -> Double {
        let dx = x - other.x
        let dy = y - other.y
        return (dx * dx + dy * dy).squareRoot()
    }
}

public func createPoint(x: Double, y: Double) -> Point {
    return Point(x: x, y: y)
}
"""
    (tmp_path / "Point.swift").write_text(source, encoding="utf-8")
    chunks = index_repository(tmp_path)
    names = [(c.name, c.kind) for c in chunks]
    assert ("Point", "ClassDef") in names
    assert ("distance", "Function") in names
    assert ("createPoint", "Function") in names


def test_validator_accepts_java_diff():
    """Ensure the diff validator accepts .java patch paths."""
    from devmind.code_agent import validate_unified_diff
    patch = (
        "diff --git a/Calculator.java b/Calculator.java\n"
        "--- a/Calculator.java\n"
        "+++ b/Calculator.java\n"
        "@@ -1 +1 @@\n"
        "-    return a + b;\n"
        "+    return a - b;\n"
    )
    assert validate_unified_diff(patch) == ["Calculator.java"]


def test_validator_accepts_go_diff():
    """Ensure the diff validator accepts .go patch paths."""
    from devmind.code_agent import validate_unified_diff
    patch = (
        "diff --git a/main.go b/main.go\n"
        "--- a/main.go\n"
        "+++ b/main.go\n"
        "@@ -3 +3 @@\n"
        "-    return a + b\n"
        "+    return a - b\n"
    )
    assert validate_unified_diff(patch) == ["main.go"]


def test_validator_accepts_rust_diff():
    """Ensure the diff validator accepts .rs patch paths."""
    from devmind.code_agent import validate_unified_diff
    patch = (
        "diff --git a/lib.rs b/lib.rs\n"
        "--- a/lib.rs\n"
        "+++ b/lib.rs\n"
        "@@ -1 +1 @@\n"
        "-    x * 2\n"
        "+    x * 3\n"
    )
    assert validate_unified_diff(patch) == ["lib.rs"]


def test_validator_accepts_csharp_diff():
    """Ensure the diff validator accepts .cs patch paths."""
    from devmind.code_agent import validate_unified_diff
    patch = (
        "diff --git a/Service.cs b/Service.cs\n"
        "--- a/Service.cs\n"
        "+++ b/Service.cs\n"
        "@@ -1 +1 @@\n"
        "-    return null;\n"
        "+    return new User();\n"
    )
    assert validate_unified_diff(patch) == ["Service.cs"]


def test_validator_accepts_ruby_diff():
    """Ensure the diff validator accepts .rb patch paths."""
    from devmind.code_agent import validate_unified_diff
    patch = (
        "diff --git a/app.rb b/app.rb\n"
        "--- a/app.rb\n"
        "+++ b/app.rb\n"
        "@@ -1 +1 @@\n"
        "-    a + b\n"
        "+    a - b\n"
    )
    assert validate_unified_diff(patch) == ["app.rb"]


def test_validator_accepts_kotlin_diff():
    """Ensure the diff validator accepts .kt patch paths."""
    from devmind.code_agent import validate_unified_diff
    patch = (
        "diff --git a/Main.kt b/Main.kt\n"
        "--- a/Main.kt\n"
        "+++ b/Main.kt\n"
        "@@ -1 +1 @@\n"
        "-    return x + 1\n"
        "+    return x + 2\n"
    )
    assert validate_unified_diff(patch) == ["Main.kt"]


def test_validator_accepts_swift_diff():
    """Ensure the diff validator accepts .swift patch paths."""
    from devmind.code_agent import validate_unified_diff
    patch = (
        "diff --git a/Point.swift b/Point.swift\n"
        "--- a/Point.swift\n"
        "+++ b/Point.swift\n"
        "@@ -1 +1 @@\n"
        "-    return 0\n"
        "+    return 1\n"
    )
    assert validate_unified_diff(patch) == ["Point.swift"]


def test_sandbox_rejects_unsupported_runner(tmp_path, monkeypatch):
    """Verify unknown test runners are rejected with a helpful message."""
    from devmind import sandbox
    monkeypatch.setattr(sandbox.shutil, "which", lambda _: "docker")
    with pytest.raises(ValueError, match="test_runner must be one of"):
        sandbox.run_tests(tmp_path, image="test-image", test_runner="unknown_runner")


def test_sandbox_accepts_go_runner(tmp_path, monkeypatch):
    """Verify the Go test runner is accepted and constructs the right command."""
    from io import StringIO
    from devmind import sandbox
    monkeypatch.setattr(sandbox.shutil, "which", lambda _: "docker")

    class Result:
        returncode = 0
        stdout = f"{sandbox._TEST_STARTED}\nok  \t./... 0.5s"
        stderr = ""

    captured = {}
    def fake_popen(command, **kwargs):
        captured["command"] = command
        result = Result()
        return type("Process", (), {
            "returncode": result.returncode,
            "stdout": StringIO(result.stdout),
            "stderr": StringIO(result.stderr),
            "wait": lambda self, timeout=None: self.returncode,
            "poll": lambda self: self.returncode,
            "kill": lambda self: setattr(self, "returncode", -9),
        })()

    monkeypatch.setattr(sandbox.subprocess, "Popen", fake_popen)
    patch = "diff --git a/main.go b/main.go\n--- a/main.go\n+++ b/main.go\n@@ -1 +1 @@\n-old\n+new\n"
    result = sandbox.run_tests(tmp_path, candidate_patch=patch, image="go-image", test_runner="go")
    assert result["passed"] is True
    assert result["runner"] == "go"
    assert "exec go test ./..." in captured["command"][-1]
