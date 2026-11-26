"""Index source spans for Python, JavaScript, Java, C, C++, Go, Rust, C#, Ruby, PHP, Kotlin, and Swift without executing repository code."""

from __future__ import annotations

import ast
import os
import re
from collections.abc import Iterator
from pathlib import Path

from devmind.models import CodeChunk

_IGNORED_DIRS = {".git", ".venv", "venv", ".devmind", "__pycache__", "node_modules", ".next", ".turbo", "coverage", "dist", "build", "target", "bin", "obj", ".gradle", ".idea", ".vs"}

# All source file extensions supported by DevMind indexing.
_PYTHON_EXTENSIONS = {".py"}
_JS_TS_EXTENSIONS = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}
_HTML_EXTENSIONS = {".html", ".htm"}
_JAVA_EXTENSIONS = {".java"}
_C_CPP_EXTENSIONS = {".c", ".h", ".cpp", ".hpp", ".cc", ".cxx", ".hxx", ".hh"}
_GO_EXTENSIONS = {".go"}
_RUST_EXTENSIONS = {".rs"}
_CSHARP_EXTENSIONS = {".cs"}
_RUBY_EXTENSIONS = {".rb"}
_PHP_EXTENSIONS = {".php"}
_KOTLIN_EXTENSIONS = {".kt", ".kts"}
_SWIFT_EXTENSIONS = {".swift"}

_ALL_EXTENSIONS = (
    _PYTHON_EXTENSIONS | _JS_TS_EXTENSIONS | _HTML_EXTENSIONS | _JAVA_EXTENSIONS | _C_CPP_EXTENSIONS
    | _GO_EXTENSIONS | _RUST_EXTENSIONS | _CSHARP_EXTENSIONS | _RUBY_EXTENSIONS
    | _PHP_EXTENSIONS | _KOTLIN_EXTENSIONS | _SWIFT_EXTENSIONS
)


def index_repository(repository: str | Path, *, max_files: int = 5000) -> list[CodeChunk]:
    """Index functions/classes across all supported languages without importing/evaluating files."""
    root = Path(repository).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"Repository path is not a directory: {root}")
    if max_files < 1:
        raise ValueError("max_files must be positive.")
    files: list[Path] = []
    for path in _source_files(root):
        files.append(path)
        if len(files) > max_files:
                raise ValueError(f"Repository exceeds the eligible source file limit of {max_files}.")
    files.sort()
    chunks: list[CodeChunk] = []
    for path in files:
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        lines = source.splitlines()
        relative = path.relative_to(root).as_posix()
        suffix = path.suffix.lower()
        if suffix in _PYTHON_EXTENSIONS:
            try:
                tree = ast.parse(source, filename=str(path))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    start = node.lineno
                    end = getattr(node, "end_lineno", start)
                    chunks.append(CodeChunk(relative, node.name, type(node).__name__, start, end, "\n".join(lines[start - 1:end])))
        elif suffix in _JS_TS_EXTENSIONS:
            chunks.extend(_javascript_chunks(relative, source, lines))
        elif suffix in _HTML_EXTENSIONS:
            chunks.extend(_inline_javascript_chunks(relative, source))
        elif suffix in _JAVA_EXTENSIONS:
            chunks.extend(_java_chunks(relative, source, lines))
        elif suffix in _C_CPP_EXTENSIONS:
            chunks.extend(_c_cpp_chunks(relative, source, lines))
        elif suffix in _GO_EXTENSIONS:
            chunks.extend(_go_chunks(relative, source, lines))
        elif suffix in _RUST_EXTENSIONS:
            chunks.extend(_rust_chunks(relative, source, lines))
        elif suffix in _CSHARP_EXTENSIONS:
            chunks.extend(_csharp_chunks(relative, source, lines))
        elif suffix in _RUBY_EXTENSIONS:
            chunks.extend(_ruby_chunks(relative, source, lines))
        elif suffix in _PHP_EXTENSIONS:
            chunks.extend(_php_chunks(relative, source, lines))
        elif suffix in _KOTLIN_EXTENSIONS:
            chunks.extend(_kotlin_chunks(relative, source, lines))
        elif suffix in _SWIFT_EXTENSIONS:
            chunks.extend(_swift_chunks(relative, source, lines))
    return chunks


_INLINE_SCRIPT = re.compile(r"<script\b[^>]*>(.*?)</script\s*>", re.IGNORECASE | re.DOTALL)


def _inline_javascript_chunks(path: str, source: str) -> list[CodeChunk]:
    """Extract function spans from inline HTML scripts without executing markup."""
    chunks: list[CodeChunk] = []
    for match in _INLINE_SCRIPT.finditer(source):
        body = match.group(1)
        # Skip non-JavaScript script payloads such as JSON-LD and templates.
        opening = source[source.rfind("<script", 0, match.start()):match.start()]
        if re.search(r"\btype\s*=\s*['\"](?:application/(?:ld\+json|json)|text/template)['\"]", opening, re.I):
            continue
        lines = body.splitlines()
        line_offset = source.count("\n", 0, match.start(1))
        chunks.extend(
            CodeChunk(path, chunk.name, chunk.kind,
                      chunk.start_line + line_offset, chunk.end_line + line_offset,
                      chunk.content)
            for chunk in _javascript_chunks(path, body, lines)
        )
    return chunks


def _source_files(root: Path) -> Iterator[Path]:
    """Walk eligible source files while pruning generated and symlinked directories."""
    for current, directory_names, file_names in os.walk(root, followlinks=False):
        directory_names[:] = sorted(
            name for name in directory_names
            if name not in _IGNORED_DIRS and not (Path(current) / name).is_symlink()
        )
        for name in file_names:
            if Path(name).suffix.lower() in _ALL_EXTENSIONS:
                path = Path(current) / name
                if _is_inside_repository(path, root):
                    yield path


_JS_FUNCTION = re.compile(
    r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\*?\s+([\w$]+)\s*\(|"
    r"^\s*(?:export\s+)?(?:const|let|var)\s+([\w$]+)\s*=\s*(?:async\s*)?(?:function\b|\([^\n]*\)\s*=>|[\w$]+\s*=>)"
)


def _javascript_chunks(path: str, source: str, lines: list[str]) -> list[CodeChunk]:
    """Extract braced JavaScript/TypeScript functions using lexical brace counting."""
    chunks: list[CodeChunk] = []
    for start_index, line in enumerate(lines):
        match = _JS_FUNCTION.match(line)
        if match is None:
            continue
        name = match.group(1) or match.group(2)
        end_index = _braced_end(lines, start_index)
        if end_index is not None:
            chunks.append(CodeChunk(path, name, "Function", start_index + 1, end_index + 1, "\n".join(lines[start_index:end_index + 1])))
    return chunks


def _braced_end(lines: list[str], start: int) -> int | None:
    """Return the closing-brace line while ignoring braces in strings and comments."""
    depth = 0
    opened = False
    quote: str | None = None
    block_comment = False
    for line_index in range(start, len(lines)):
        line = lines[line_index]
        index = 0
        while index < len(line):
            char = line[index]
            next_char = line[index + 1] if index + 1 < len(line) else ""
            if block_comment:
                if char == "*" and next_char == "/":
                    block_comment = False
                    index += 2
                    continue
                index += 1
                continue
            if quote is not None:
                if char == "\\":
                    index += 2
                    continue
                if char == quote:
                    quote = None
                index += 1
                continue
            if char == "/" and next_char == "/":
                break
            if char == "/" and next_char == "*":
                block_comment = True
                index += 2
                continue
            if char in {"'", '"', "`"}:
                quote = char
            elif char == "{":
                depth += 1
                opened = True
            elif char == "}":
                depth -= 1
                if opened and depth == 0:
                    return line_index
            index += 1
    return None


# --- Java -------------------------------------------------------------------

_JAVA_METHOD = re.compile(
    r"^\s*(?:(?:public|private|protected|static|final|abstract|synchronized|native|default)\s+)*"
    r"(?:[\w<>\[\]?,\s]+)\s+(\w+)\s*\("
)
_JAVA_CLASS = re.compile(
    r"^\s*(?:(?:public|private|protected|static|final|abstract)\s+)*class\s+(\w+)"
)
_JAVA_INTERFACE = re.compile(
    r"^\s*(?:(?:public|private|protected|static)\s+)*interface\s+(\w+)"
)


def _java_chunks(path: str, source: str, lines: list[str]) -> list[CodeChunk]:
    """Extract Java methods, classes, and interfaces using brace counting."""
    chunks: list[CodeChunk] = []
    for start_index, line in enumerate(lines):
        kind = "Function"
        match = _JAVA_CLASS.match(line)
        if match:
            kind = "ClassDef"
        elif _JAVA_INTERFACE.match(line):
            match = _JAVA_INTERFACE.match(line)
            kind = "ClassDef"
        else:
            match = _JAVA_METHOD.match(line)
        if match is None:
            continue
        name = match.group(1)
        # Skip control flow keywords that look like method signatures.
        if name in {"if", "else", "for", "while", "switch", "catch", "return", "new", "throw", "try"}:
            continue
        end_index = _braced_end(lines, start_index)
        if end_index is not None:
            chunks.append(CodeChunk(path, name, kind, start_index + 1, end_index + 1, "\n".join(lines[start_index:end_index + 1])))
    return chunks


# --- C / C++ ----------------------------------------------------------------

_C_FUNCTION = re.compile(
    r"^\s*(?:(?:static|inline|extern|virtual|const|unsigned|signed|volatile|struct|enum)\s+)*"
    r"(?:[\w:*&<>\[\]]+)\s+\*?\s*(\w+)\s*\("
)
_C_CLASS = re.compile(
    r"^\s*(?:class|struct)\s+(\w+)"
)


def _c_cpp_chunks(path: str, source: str, lines: list[str]) -> list[CodeChunk]:
    """Extract C/C++ functions, classes, and structs using brace counting."""
    chunks: list[CodeChunk] = []
    for start_index, line in enumerate(lines):
        kind = "Function"
        match = _C_CLASS.match(line)
        if match:
            kind = "ClassDef"
        else:
            match = _C_FUNCTION.match(line)
        if match is None:
            continue
        name = match.group(1)
        if name in {"if", "else", "for", "while", "switch", "case", "return", "sizeof", "typedef", "define", "include", "pragma"}:
            continue
        end_index = _braced_end(lines, start_index)
        if end_index is not None:
            chunks.append(CodeChunk(path, name, kind, start_index + 1, end_index + 1, "\n".join(lines[start_index:end_index + 1])))
    return chunks


# --- Go ---------------------------------------------------------------------

_GO_FUNCTION = re.compile(
    r"^\s*func\s+(?:\(\s*\w+\s+\*?\w+\s*\)\s+)?(\w+)\s*(?:\[.*?\])?\s*\("
)
_GO_TYPE = re.compile(
    r"^\s*type\s+(\w+)\s+struct\s*\{"
)


def _go_chunks(path: str, source: str, lines: list[str]) -> list[CodeChunk]:
    """Extract Go functions and struct types using brace counting."""
    chunks: list[CodeChunk] = []
    for start_index, line in enumerate(lines):
        kind = "Function"
        match = _GO_TYPE.match(line)
        if match:
            kind = "ClassDef"
        else:
            match = _GO_FUNCTION.match(line)
        if match is None:
            continue
        name = match.group(1)
        end_index = _braced_end(lines, start_index)
        if end_index is not None:
            chunks.append(CodeChunk(path, name, kind, start_index + 1, end_index + 1, "\n".join(lines[start_index:end_index + 1])))
    return chunks


# --- Rust -------------------------------------------------------------------

_RUST_FUNCTION = re.compile(
    r"^\s*(?:pub(?:\(crate\))?\s+)?(?:async\s+)?fn\s+(\w+)"
)
_RUST_STRUCT = re.compile(
    r"^\s*(?:pub(?:\(crate\))?\s+)?struct\s+(\w+)"
)
_RUST_IMPL = re.compile(
    r"^\s*impl(?:\s*<.*?>)?\s+(\w+)"
)


def _rust_chunks(path: str, source: str, lines: list[str]) -> list[CodeChunk]:
    """Extract Rust functions, structs, and impl blocks using brace counting."""
    chunks: list[CodeChunk] = []
    for start_index, line in enumerate(lines):
        kind = "Function"
        match = _RUST_FUNCTION.match(line)
        if match is None:
            match = _RUST_STRUCT.match(line)
            if match:
                kind = "ClassDef"
        if match is None:
            match = _RUST_IMPL.match(line)
            if match:
                kind = "ClassDef"
        if match is None:
            continue
        name = match.group(1)
        end_index = _braced_end(lines, start_index)
        if end_index is not None:
            chunks.append(CodeChunk(path, name, kind, start_index + 1, end_index + 1, "\n".join(lines[start_index:end_index + 1])))
    return chunks


# --- C# ---------------------------------------------------------------------

_CSHARP_METHOD = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|static|virtual|override|abstract|async|sealed|partial|new)\s+)*"
    r"(?:[\w<>\[\]?,\s]+)\s+(\w+)\s*\("
)
_CSHARP_CLASS = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|static|abstract|sealed|partial)\s+)*class\s+(\w+)"
)


def _csharp_chunks(path: str, source: str, lines: list[str]) -> list[CodeChunk]:
    """Extract C# methods and classes using brace counting."""
    chunks: list[CodeChunk] = []
    for start_index, line in enumerate(lines):
        kind = "Function"
        match = _CSHARP_CLASS.match(line)
        if match:
            kind = "ClassDef"
        else:
            match = _CSHARP_METHOD.match(line)
        if match is None:
            continue
        name = match.group(1)
        if name in {"if", "else", "for", "foreach", "while", "switch", "catch", "return", "new", "throw", "try", "using", "lock"}:
            continue
        end_index = _braced_end(lines, start_index)
        if end_index is not None:
            chunks.append(CodeChunk(path, name, kind, start_index + 1, end_index + 1, "\n".join(lines[start_index:end_index + 1])))
    return chunks


# --- Ruby -------------------------------------------------------------------

_RUBY_METHOD = re.compile(
    r"^\s*def\s+(?:self\.)?(\w+[?!=]?)"
)
_RUBY_CLASS = re.compile(
    r"^\s*class\s+(\w+)"
)
_RUBY_MODULE = re.compile(
    r"^\s*module\s+(\w+)"
)


def _ruby_end_block(lines: list[str], start: int) -> int | None:
    """Find the matching ``end`` for a Ruby ``def``/``class``/``module`` block."""
    depth = 0
    block_keywords = {"def", "class", "module", "do", "if", "unless", "case", "while", "until", "for", "begin"}
    for line_index in range(start, len(lines)):
        stripped = lines[line_index].strip()
        # Skip comments and blank lines for keyword counting.
        if stripped.startswith("#") or not stripped:
            continue
        # Count block openers — only at start of statement (simplified heuristic).
        first_word = stripped.split()[0] if stripped.split() else ""
        if first_word in block_keywords:
            depth += 1
        # "end" at the start of a line closes a block.
        if stripped == "end" or stripped.startswith("end ") or stripped.startswith("end;"):
            depth -= 1
            if depth == 0:
                return line_index
    return None


def _ruby_chunks(path: str, source: str, lines: list[str]) -> list[CodeChunk]:
    """Extract Ruby methods, classes, and modules using end-keyword matching."""
    chunks: list[CodeChunk] = []
    for start_index, line in enumerate(lines):
        kind = "Function"
        match = _RUBY_CLASS.match(line)
        if match:
            kind = "ClassDef"
        elif _RUBY_MODULE.match(line):
            match = _RUBY_MODULE.match(line)
            kind = "ClassDef"
        else:
            match = _RUBY_METHOD.match(line)
        if match is None:
            continue
        name = match.group(1)
        end_index = _ruby_end_block(lines, start_index)
        if end_index is not None:
            chunks.append(CodeChunk(path, name, kind, start_index + 1, end_index + 1, "\n".join(lines[start_index:end_index + 1])))
    return chunks


# --- PHP --------------------------------------------------------------------

_PHP_FUNCTION = re.compile(
    r"^\s*(?:(?:public|private|protected|static|final|abstract)\s+)*function\s+(\w+)\s*\("
)
_PHP_CLASS = re.compile(
    r"^\s*(?:(?:abstract|final)\s+)?class\s+(\w+)"
)


def _php_chunks(path: str, source: str, lines: list[str]) -> list[CodeChunk]:
    """Extract PHP functions and classes using brace counting."""
    chunks: list[CodeChunk] = []
    for start_index, line in enumerate(lines):
        kind = "Function"
        match = _PHP_CLASS.match(line)
        if match:
            kind = "ClassDef"
        else:
            match = _PHP_FUNCTION.match(line)
        if match is None:
            continue
        name = match.group(1)
        end_index = _braced_end(lines, start_index)
        if end_index is not None:
            chunks.append(CodeChunk(path, name, kind, start_index + 1, end_index + 1, "\n".join(lines[start_index:end_index + 1])))
    return chunks


# --- Kotlin -----------------------------------------------------------------

_KOTLIN_FUNCTION = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|open|override|abstract|suspend|inline|infix|operator|tailrec)\s+)*fun\s+(?:<.*?>\s+)?(?:\w+\.)?(\w+)\s*\("
)
_KOTLIN_CLASS = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|open|abstract|sealed|data|enum|inner|annotation)\s+)*class\s+(\w+)"
)


def _kotlin_chunks(path: str, source: str, lines: list[str]) -> list[CodeChunk]:
    """Extract Kotlin functions and classes using brace counting."""
    chunks: list[CodeChunk] = []
    for start_index, line in enumerate(lines):
        kind = "Function"
        match = _KOTLIN_CLASS.match(line)
        if match:
            kind = "ClassDef"
        else:
            match = _KOTLIN_FUNCTION.match(line)
        if match is None:
            continue
        name = match.group(1)
        end_index = _braced_end(lines, start_index)
        if end_index is not None:
            chunks.append(CodeChunk(path, name, kind, start_index + 1, end_index + 1, "\n".join(lines[start_index:end_index + 1])))
    return chunks


# --- Swift ------------------------------------------------------------------

_SWIFT_FUNCTION = re.compile(
    r"^\s*(?:(?:public|private|fileprivate|internal|open|static|class|override|mutating|nonmutating|@objc)\s+)*func\s+(\w+)"
)
_SWIFT_CLASS = re.compile(
    r"^\s*(?:(?:public|private|fileprivate|internal|open|final)\s+)?(?:class|struct|enum|protocol)\s+(\w+)"
)


def _swift_chunks(path: str, source: str, lines: list[str]) -> list[CodeChunk]:
    """Extract Swift functions, classes, structs, and enums using brace counting."""
    chunks: list[CodeChunk] = []
    for start_index, line in enumerate(lines):
        kind = "Function"
        match = _SWIFT_CLASS.match(line)
        if match:
            kind = "ClassDef"
        else:
            match = _SWIFT_FUNCTION.match(line)
        if match is None:
            continue
        name = match.group(1)
        end_index = _braced_end(lines, start_index)
        if end_index is not None:
            chunks.append(CodeChunk(path, name, kind, start_index + 1, end_index + 1, "\n".join(lines[start_index:end_index + 1])))
    return chunks


def _is_inside_repository(path: Path, root: Path) -> bool:
    """Reject symlinks that resolve to source files outside the selected repository."""
    try:
        return path.resolve(strict=True).is_relative_to(root)
    except (OSError, RuntimeError):
        return False

